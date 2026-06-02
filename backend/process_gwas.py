"""Process GWAS Catalog TSV files → new reference entries."""
import csv, re, os, sqlite3

GWAS_FILES = [
    "/tmp/gwas/gwas-catalog-download-associations-v1.0.2025.tsv",
    "/tmp/gwas/gwas-catalog-download-associations-v1.0.2026.tsv",
]

DB_PATH = "/root/scorpio-dna/backend/data/scorpio_dna.db"

# Map GWAS Catalog traits to our 7 categories + description templates
# Keywords → category mapping
CATEGORY_MAP = [
    (r'cancer|tumor|malignant|neoplasm|carcinoma|melanoma|leukemia|lymphoma', 'Health', 'Cancer'),
    (r'diabetes|glucose|insulin|HbA1c|glycemic|metabolic syndrome', 'Health', 'Metabolic'),
    (r'hypertension|blood pressure|systolic|diastolic', 'Health', 'Cardiovascular'),
    (r'coronary|heart attack|myocardial|cardiac|heart disease|atrial fibrillation|arrhythmia', 'Health', 'Cardiovascular'),
    (r'stroke|ischemic|cerebrovascular', 'Health', 'Cardiovascular'),
    (r'cholesterol|lipid|triglyceride|LDL|HDL|lipoprotein', 'Health', 'Cardiovascular'),
    (r'obesity|BMI|weight|adiposity|body fat|waist', 'Health', 'Metabolic'),
    (r'asthma|COPD|lung function|FEV|pulmonary', 'Health', 'Respiratory'),
    (r'Alzheimer|cognitive|dementia|brain volume|hippocampal', 'Health', 'Neurological'),
    (r'Parkinson|multiple sclerosis|epilepsy|migraine|neuro', 'Health', 'Neurological'),
    (r'depression|bipolar|schizophrenia|psychiatric|anxiety|neuroticism|mood', 'Personality', 'Mental Health'),
    (r'autism|ADHD|behavioral|personality', 'Personality', 'Behavioral'),
    (r'thyroid|autoimmune|lupus|rheumatoid|celiac|inflammatory bowel|Crohn|colitis', 'Health', 'Autoimmune'),
    (r'osteoporosis|bone mineral density|fracture|osteopenia', 'Health', 'Musculoskeletal'),
    (r'vitamin|folate|B12|iron|ferritin|calcium|magnesium|zinc|selenium', 'Nutrition', 'Nutrition'),
    (r'caffeine|coffee|tea|alcohol|alcoholism|smoking|nicotine', 'Health', 'Substance Use'),
    (r'height|hair|eye color|skin pigmentation|baldness|earwax|freckle', 'Traits', 'Physical Traits'),
    (r'lactose|dairy|milk', 'Nutrition', 'Digestion'),
    (r'athlete|endurance|VO2|sprint|power|muscle|strength|exercise response', 'Fitness', 'Fitness'),
    (r'warfarin|clopidogrel|statin|metformin|CYP|pharmaco|drug response|drug metabolism', 'Drug Response', 'Pharmacogenetics'),
    (r'birth weight|birth length|gestational|preterm', 'Health', 'Developmental'),
    (r'kidney|renal|creatinine|eGFR|urate|gout', 'Health', 'Renal'),
    (r'liver|bilirubin|ALT|AST|GGT|hepatic|NAFLD', 'Health', 'Liver'),
    (r'bone density|osteoporosis|fracture|sarcopenia', 'Health', 'Musculoskeletal'),
    (r'psoriasis|eczema|atopic|allergy|hay fever', 'Health', 'Immunological'),
    (r'age-related macular|glaucoma|cataract|intraocular', 'Health', 'Ophthalmological'),
    (r'hearing|hearing loss|otosclerosis', 'Health', 'Auditory'),
    (r'cystic fibrosis|sickle cell|thalassemia|hemochromatosis|hemophilia', 'Carrier', 'Genetic Carrier'),
    (r'menopause|puberty|menarche|androgen|testosterone', 'Health', 'Endocrine'),
    (r'longevity|aging|lifespan|frailty', 'Health', 'Aging'),
]

def map_category(trait):
    trait_lower = trait.lower()
    for pattern, category, sub in CATEGORY_MAP:
        if re.search(pattern, trait_lower):
            return category
    return None

def extract_rsid_allele(snp_string):
    """Parse 'rs1234567-A' → (rs1234567, A)"""
    if not snp_string or snp_string == 'NR':
        return None, None
    # Format: rs1234567-A or rs1234567-A/G or multiple
    parts = snp_string.split('-')
    if len(parts) == 2 and parts[0].startswith('rs'):
        rsid = parts[0].strip()
        allele = parts[1].strip().upper()
        # Only single allele or valid genotype
        allele = re.sub(r'[^ACGT]', '', allele)
        if len(allele) >= 1:
            return rsid, allele[:2]  # max 2 chars for genotype
    return None, None

def risk_level_from_freq(freq):
    """Infer risk level from allele frequency"""
    if freq is None or freq == '' or freq == 'NR':
        return 'elevated'
    try:
        f = float(freq)
        if f < 0.05:
            return 'high'
        elif f < 0.30:
            return 'elevated'
        else:
            return 'elevated'
    except:
        return 'elevated'

def main():
    print("Processing GWAS Catalog files...")
    
    # Load existing rsids to avoid duplicates
    conn = sqlite3.connect(DB_PATH)
    existing = set()
    for r in conn.execute("SELECT rsid, trait FROM reference_snps"):
        existing.add((r[0], r[1]))
    print(f"Existing entries: {len(existing)}")
    
    new_entries = []
    seen = set()
    
    for filepath in GWAS_FILES:
        if not os.path.exists(filepath):
            print(f"SKIP: {filepath} not found")
            continue
        
        count = 0
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            reader = csv.DictReader(f, delimiter='\t')
            for row in reader:
                pvalue = row.get('P-VALUE', '').strip()
                if not pvalue or pvalue == 'NR':
                    continue
                
                # Strict p-value filter
                try:
                    p = float(pvalue)
                    if p > 5e-8:
                        continue
                except:
                    continue
                
                trait = row.get('DISEASE/TRAIT', '').strip()
                if not trait or len(trait) < 3:
                    continue
                
                category = map_category(trait)
                if not category:
                    continue
                
                snp_str = row.get('STRONGEST SNP-RISK ALLELE', '').strip()
                rsid, allele = extract_rsid_allele(snp_str)
                if not rsid or not allele:
                    continue
                
                # Deduplicate
                key = (rsid, trait[:80])
                if key in seen or key in existing:
                    continue
                seen.add(key)
                
                freq = row.get('RISK ALLELE FREQUENCY', '').strip()
                risk_level = risk_level_from_freq(freq)
                
                gene = row.get('REPORTED GENE(S)', '').strip() or 'Unknown'
                or_beta = row.get('OR or BETA', '').strip()
                
                # Build genotype from allele (risk allele + risk allele for homozygous)
                risk_genotype = allele if len(allele) == 2 else allele * 2
                # Normalize to 2 chars, sorted
                risk_genotype = ''.join(sorted(risk_genotype[:2]))
                
                description = f"{gene} gene variant. {allele}-allele associated with {trait.lower()} (p={pvalue})."
                if or_beta and or_beta != 'NR':
                    description += f" OR/Beta={or_beta}."
                
                new_entries.append({
                    'rsid': rsid,
                    'category': category,
                    'trait': trait[:80],
                    'description': description[:300],
                    'risk_allele': allele[0] if len(allele) >= 1 else allele,
                    'risk_genotype': risk_genotype,
                    'risk_level': risk_level,
                    'population_freq': float(freq) if freq and freq != 'NR' else 0.5,
                    'study_url': f"https://pubmed.ncbi.nlm.nih.gov/{row.get('PUBMEDID', '')}/" if row.get('PUBMEDID') else '',
                    'note': f"GWAS Catalog: {trait[:50]}",
                    'summary': '',
                    'health_tips': '',
                    'risk_factors': '',
                    'if_untreated': '',
                })
                
                count += 1
                if count >= 500:  # Max 500 per file to keep it manageable
                    break
        
        print(f"  {os.path.basename(filepath)}: {count} new candidates")
    
    print(f"\nTotal new candidate entries: {len(new_entries)}")
    
    # Insert into database (with empty summary/tips/etc)
    inserted = 0
    for e in new_entries:
        try:
            conn.execute("""
                INSERT INTO reference_snps 
                (rsid, category, trait, description, risk_allele, risk_genotype, 
                 risk_level, population_freq, study_url, note)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (e['rsid'], e['category'], e['trait'], e['description'],
                  e['risk_allele'], e['risk_genotype'], e['risk_level'],
                  e['population_freq'], e['study_url'], e['note']))
            inserted += 1
        except Exception as ex:
            print(f"  SKIP {e['rsid']}: {ex}")
    
    conn.commit()
    conn.close()
    print(f"Inserted {inserted} new entries")
    
    # Show breakdown by category
    conn = sqlite3.connect(DB_PATH)
    for row in conn.execute("SELECT category, COUNT(*) FROM reference_snps GROUP BY category ORDER BY COUNT(*) DESC"):
        print(f"  {row[0]}: {row[1]}")
    conn.close()

if __name__ == '__main__':
    main()
