"""Parse raw DNA files (23andMe, AncestryDNA, MyHeritage formats)"""
import pandas as pd
import re

def parse_dna_file(filepath: str) -> pd.DataFrame:
    """Parse a raw DNA file into a DataFrame with columns: rsid, chromosome, position, genotype."""
    lines = []

    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    # Normalize line endings
    content = content.replace('\r\n', '\n').replace('\r', '\n')
    file_lines = content.split('\n')

    # CSV header check — skip header lines
    header_keywords = {'rsid', 'rs_id', 'chromosome', 'position', 'genotype', 'allele', 'result', 'chrom'}
    first_data = []
    header_line_idx = None
    for i, line in enumerate(file_lines):
        s = line.strip().lower().replace('"', '')
        if not s or s.startswith('#') or s.startswith('[') or s.startswith('@'):
            continue
        # Check if this looks like a header
        csv_parts = [x.strip().strip('"').lower() for x in s.split(',')]
        if any(kw in csv_parts for kw in header_keywords) and len(csv_parts) >= 4:
            header_line_idx = i
            break
        # First non-empty non-comment line
        if len(first_data) == 0:
            first_data = csv_parts
        if not any(kw in csv_parts for kw in {'rsid', 'chromosome', 'position'}):
            # Check if first element starts with rs
            if csv_parts[0].startswith('rs'):
                break

    for i, line in enumerate(file_lines):
        # Skip header line
        if header_line_idx is not None and i == header_line_idx:
            continue

        line = line.strip().strip('"').strip()
        if not line or line.startswith('#') or line.startswith('[') or line.startswith('@') or line.startswith('---'):
            continue

        # Split by comma first (CSV), fallback to whitespace
        if ',' in line:
            parts = [p.strip().strip('"').strip() for p in line.split(',')]
        else:
            parts = re.split(r'[\t ]+', line)
            parts = [p.strip().strip('"').strip() for p in parts]

        # Must start with rs
        if not parts[0].startswith('rs'):
            continue

        try:
            rsid = parts[0]
            chrom = parts[1]
            pos = int(parts[2])
        except (IndexError, ValueError):
            continue

        # --- 5-part format (AncestryDNA / MyHeritage tab) ---
        # rsid, chrom, pos, allele1, allele2
        if len(parts) >= 5:
            a1 = re.sub(r'[^ACGT\-]', '', parts[3].upper())
            a2 = re.sub(r'[^ACGT\-]', '', parts[4].upper())
            if len(a1) == 1 and len(a2) == 1:
                genotype = ''.join(sorted(a1 + a2))
                lines.append((rsid, chrom, pos, genotype))
                continue

        # --- 4-part format (23andMe standard OR MyHeritage CSV) ---
        # rsid, chrom, pos, genotype
        if len(parts) >= 4:
            genotype = re.sub(r'[^ACGT\-]', '', parts[3].upper())
            if len(genotype) == 2:
                genotype = ''.join(sorted(genotype))
                lines.append((rsid, chrom, pos, genotype))
                continue
            if len(genotype) == 1:
                lines.append((rsid, chrom, pos, genotype))

    df = pd.DataFrame(lines, columns=['rsid', 'chromosome', 'position', 'genotype'])
    return df

def validate_dna(df: pd.DataFrame) -> dict:
    """Basic validation of parsed DNA data."""
    total = len(df)
    unique_rsids = df['rsid'].nunique()
    count_2 = len(df[df['genotype'].str.len() == 2]) if len(df) > 0 else 0
    return {
        "total_snps": total,
        "unique_snps": unique_rsids,
        "biallelic_snps": int(count_2)
    }
