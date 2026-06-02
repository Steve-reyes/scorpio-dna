"""Seed 'if untreated' scenarios for all 117 entries."""
import sqlite3

DB_PATH = "/app/data/scorpio_dna.db"

IF_UNTREATED = {
    "rs9939609_Obesity / BMI": "Without management: gradual weight gain over time, increased risk of metabolic syndrome, type 2 diabetes, heart disease, joint problems, and reduced quality of life. Weight is modifiable — small changes compound over years.",
    "rs1801133_MTHFR Deficiency": "If unaddressed: elevated homocysteine levels over years increase risk of cardiovascular disease, stroke, blood clots, pregnancy complications (neural tube defects), and cognitive decline. Easily managed with methylfolate supplementation.",
    "rs7412_Alzheimer's Risk (APOE)": "This is a protective variant — no negative scenario. Your Alzheimer's risk is lower than average regardless of lifestyle, though brain-healthy habits still matter.",
    "rs429358_Alzheimer's Risk (APOE)": "If unaddressed: higher probability of cognitive decline and Alzheimer's disease in later years (typically after 65). Brain changes begin decades before symptoms. Aggressive lifestyle management (diet, exercise, sleep, cognitive stimulation) significantly reduces absolute risk.",
    "rs1799943_Hemochromatosis (HFE)": "If unmanaged: slow accumulation of iron in organs over decades leads to liver damage (cirrhosis), diabetes, heart problems, and arthritis. Iron overload is easily treated — regular blood donation prevents all complications.",
    "rs1800562_Hemochromatosis (HFE)": "If untreated: progressive iron overload causes liver cirrhosis, hepatocellular carcinoma, diabetes (bronze diabetes), heart failure, and joint destruction. Completely preventable with regular phlebotomy — simple, effective, and widely available.",
    "rs328_Lipoprotein(a) / Heart Disease": "If unaddressed: lifelong elevated Lp(a) contributes to atherosclerosis progression, increasing heart attack, stroke, and aortic stenosis risk. Lp(a) doesn't respond to diet but other risk factors (LDL, BP, smoking) amplify its effect. Manage everything you can control.",
    "rs662799_Triglycerides": "If ignored: persistently high triglycerides increase risk of pancreatitis (painful, dangerous), fatty liver disease, and contribute to heart disease. Responds very well to lifestyle changes — sugar reduction and exercise are highly effective.",
    "rs7903146_Type 2 Diabetes": "If unaddressed: blood sugar rises over years, leading to full type 2 diabetes with complications: vision loss, kidney disease, nerve damage, amputations, heart disease, and stroke. Prediabetes and early diabetes can often be reversed with 5-10% weight loss and lifestyle changes.",
    "rs5219_Type 2 Diabetes": "If unchecked: contributes to insulin resistance progression, eventually leading to type 2 diabetes and its complications. Early intervention is highly effective at preventing progression.",
    "rs12255372_Type 2 Diabetes": "If unaddressed: same trajectory as other T2D variants — progression to full diabetes over years if lifestyle factors push in that direction. Highly preventable.",
    "rs1800629_TNF-alpha / Inflammation": "If unmanaged: chronic low-grade inflammation contributes to heart disease, insulin resistance, autoimmune flares, accelerated aging, and poor recovery from illness and injury. Anti-inflammatory habits reduce all these risks significantly.",
    "rs16944_IL-1B / Inflammation": "If unaddressed: elevated IL-1β drives chronic inflammation linked to heart disease (especially heart attack risk), arthritis, and metabolic dysfunction. The anti-inflammatory lifestyle (diet, exercise, sleep) directly counteracts this.",
    "rs1800795_IL-6 / Inflammation": "If unmanaged: elevated IL-6 contributes to chronic disease risk including cardiovascular disease, insulin resistance, and frailty in aging. Responds well to lifestyle intervention.",
    "rs1801131_MTHFR A1298C": "If unaddressed: milder elevation of homocysteine — less severe than C677T. Still contributes to cardiovascular risk over decades if combined with poor folate intake. Easily managed with diet and supplements.",
    "rs1042713_Asthma / ADRB2": "If not well-managed: asthma exacerbations, reduced lung function, emergency room visits, and lower quality of life. Proper asthma management (identifying triggers, correct inhaler use) prevents most complications regardless of this variant.",
    "rs1051730_Nicotine Dependence": "If unaddressed: continued smoking leads to lung cancer, COPD, heart disease, stroke, and 10+ years reduced life expectancy. Quitting is the single best health decision — it's hard but the benefits start within days.",
    "rs16969968_Nicotine Dependence": "If smoking continues: same consequences as above — lung cancer, heart disease, emphysema. This variant makes quitting harder but not impossible. NRT and prescription aids dramatically improve success rates.",
    "rs1544410_Vitamin D / Osteoporosis": "If unaddressed: over decades, low bone density leads to osteoporosis — fragile bones that fracture easily (hip, spine, wrist). Hip fractures in elderly significantly reduce independence and life expectancy. Preventable with vitamin D, calcium, and weight-bearing exercise.",
    "rs2228570_Vitamin D / Autoimmunity": "If unaddressed: low vitamin D combined with this variant may increase autoimmune disease risk (thyroid, lupus, MS, rheumatoid arthritis). Maintain optimal vitamin D levels to support immune regulation.",
    "rs4988235_Lactose Intolerance": "If ignored: bloating, cramps, diarrhea after dairy consumption — uncomfortable but not dangerous. Nutrient intake (calcium, vitamin D) may suffer if dairy is avoided without alternatives. Easily managed with lactase pills or lactose-free products.",
    "rs182549_Lactose Intolerance": "Same as above — digestive discomfort if dairy consumed, no long-term health damage. Easily managed with diet adjustments.",
    "rs738409_NAFLD / Fatty Liver": "If unaddressed: liver fat accumulates → inflammation (NASH) → liver scarring (fibrosis) → cirrhosis → liver failure or liver cancer. This can take 20-30 years. Early stage is fully reversible with weight loss, sugar reduction, and exercise.",
    "rs58542926_NAFLD / Liver Disease": "If unmanaged: same progression as above — from fatty liver to inflammation to cirrhosis over decades if diet and lifestyle promote fat accumulation. Reversible in early stages.",
    "rs2066844_Crohn's Disease / NOD2": "If Crohn's develops and is untreated: chronic intestinal inflammation → abdominal pain, diarrhea, malnutrition, fistulas, abscesses, and bowel obstructions. Very few carriers develop Crohn's — awareness is enough for most people.",
    "rs2066845_Crohn's Disease / NOD2": "If Crohn's develops: same as above — chronic GI inflammation requiring medical management. Extremely low individual risk with this rare variant alone.",
    "rs2004640_Autoimmunity / TYK2": "No negative scenario — this is a protective variant. Your immune signaling is more balanced and autoimmune risk is lower than average.",
    "rs1333049_Coronary Artery Disease": "If unaddressed: gradual plaque buildup in coronary arteries over decades → heart attack (often without warning), heart failure, or sudden cardiac death. This is the #1 killer worldwide. Aggressively managing cholesterol, blood pressure, lifestyle, and not smoking dramatically reduces risk.",
    "rs10757278_Heart Attack / CAD": "If unaddressed: increased risk of myocardial infarction, especially if other risk factors present. Same trajectory as other 9p21 variants — heart attack risk amplified by smoking and poor lifestyle. Highly modifiable with prevention.",
    "rs328_Heart Disease / LPL": "No negative scenario — this variant is protective. Your body processes fats efficiently and has lower cardiovascular risk. Maintain general heart-healthy habits to preserve this advantage.",
    "rs6311_Serotonin / Mood": "If unaddressed: higher baseline risk for mood disorders, especially depression and seasonal affective disorder. May experience lower quality of life from unrecognized mood issues. Highly treatable with therapy, lifestyle, and medications if needed.",
    "rs6313_Serotonin / Depression": "If unaddressed: increased risk of depression (especially seasonal pattern), reduced quality of life, and impaired function. Responds well to treatment — light therapy, exercise, and SSRIs can all be effective.",
    "rs4680_COMT / Stress Response": "If unaddressed for Met (worrier): chronic stress buildup, anxiety, burnout, pain sensitivity. For Val (warrior): may miss health warning signs, push through injuries. Both types benefit from tailored stress management strategies.",
    "rs6265_BDNF / Memory & Mood": "If unaddressed: reduced BDNF over time contributes to lower mood, poorer memory consolidation, and potentially faster age-related cognitive decline. Highly responsive to aerobic exercise — this is one of the most actionable genetic variants.",
    "rs1815739_ACTN3 / Muscle Performance": "No health risk scenario — this affects athletic performance tendencies, not disease risk. XX genotype doesn't cause health problems, just different muscle fiber composition. Train according to your goals, not your genes.",
    "rs334_Sickle Cell Anemia": "As a carrier: no health scenario — you won't develop sickle cell disease. The only risk is to your children if your partner is also a carrier (25% chance of disease per pregnancy). Genetic counseling is recommended for family planning.",
    "rs6025_Factor V Leiden": "If unaddressed: increased risk of deep vein thrombosis (DVT) and pulmonary embolism, especially during high-risk situations (surgery, pregnancy, long flights, estrogen use). A clot in the lung (PE) can be fatal. Preventable with anticoagulation during high-risk periods.",
    "rs1799963_Prothrombin / Clotting": "If unaddressed: similar risk of venous thromboembolism as Factor V Leiden. Clot risk magnified by estrogen, surgery, immobility, and age. Preventable with proper precautions and awareness.",
    "rs121908001_Cystic Fibrosis (ΔF508)": "As a carrier: no health impact — you don't have CF. The concern is only if your partner is also a carrier: 25% chance of child with CF (a life-shortening lung disease). Carrier screening and genetic counseling recommended for family planning.",
    "rs1800078_Cystic Fibrosis (G551D)": "Same as other CF mutations — carrier only, no personal health impact. Family planning implications if partner is also a carrier. CFTR modulators (ivacaftor) exist for affected individuals with this specific mutation.",
    "rs1800137_Cystic Fibrosis (W1282X)": "Same — carrier only, no symptoms. Nonsense mutation — different mechanism but same carrier implications for family planning.",
    "rs137852587_Tay-Sachs (HEXA)": "As a carrier: no health impact. If both parents carriers: 25% chance per pregnancy of a child with Tay-Sachs (fatal neurodegenerative disease, typically by age 4). Carrier screening is standard for at-risk populations.",
    "rs28942079_G6PD Deficiency": "If triggered unnecessarily: hemolytic anemia (red blood cell breakdown) causing fatigue, jaundice, dark urine. In severe cases: kidney failure. Completely avoidable by knowing and avoiding triggers (fava beans, certain medications).",
    "rs1042822_Hemochromatosis (HFE)": "If unaddressed: mild iron accumulation — much less severe than C282Y. May eventually cause slightly elevated ferritin. Monitor annually and donate blood if levels rise.",
    "rs28934574_BRCA1 / Breast Cancer": "If unaddressed: significantly elevated lifetime risk of breast cancer (up to 72%) and ovarian cancer (up to 44%), plus pancreatic and other cancers. Enhanced screening and preventive options dramatically reduce mortality. Genetic counseling is essential.",
    "rs80357906_BRCA2 / Breast Cancer": "If unaddressed: elevated risk for breast (up to 69%), ovarian, pancreatic, and prostate cancers. Also linked to male breast cancer. Enhanced surveillance and risk-reducing strategies significantly improve outcomes.",
    "rs1801028_Maple Syrup Urine Disease": "As a carrier: no health impact. If both parents carriers: 25% risk of child with MSUD (metabolic crisis in infancy, requires strict dietary management). Carrier screening available.",
    "rs6443349_Spinal Muscular Atrophy": "As a carrier: no health impact. If both parents carriers: 25% risk of child with SMA (progressive muscle weakness, #1 genetic cause of infant death). Screening recommended as ~1 in 50 people carry this.",
    "rs2071128_Wilson Disease": "As a carrier: no health impact. Extremely rare — only matters if both parents carriers (25% risk of child with Wilson disease — copper accumulation, treatable with chelation).",
    "rs80338902_Gaucher Disease": "As a carrier: no health impact. If both parents carriers: 25% risk of child with Gaucher (enzyme deficiency — treatable with enzyme replacement therapy). More common in Ashkenazi Jewish populations.",
    "rs9923231_Warfarin Sensitivity": "If ignored: standard warfarin starting dose (5mg) could cause dangerous bleeding, including intracranial hemorrhage. This is a safety variant — knowing it prevents harm. Alternative anticoagulants (DOACs) bypass this issue entirely.",
    "rs1799853_Warfarin Sensitivity": "If ignored: slower warfarin metabolism leads to excessive anticoagulation and bleeding risk at standard doses. Prevented by lower starting dose or using DOACs.",
    "rs1057910_Warfarin Sensitivity": "If ignored: severely impaired warfarin clearance — standard dose could be life-threatening. Requires very low starting dose or alternative anticoagulant. Highly actionable — just inform your doctor.",
    "rs28399433_CYP2A6 / Nicotine Metabolism": "If ignored: may affect smoking cessation strategy choice. Nicotine stays longer in your system — extended NRT may work better. This is a medication guidance variant, not a disease risk.",
    "rs3892097_Codeine Efficacy (CYP2D6)": "If ignored: codeine and tramadol provide zero pain relief after surgery or injury — you suffer unnecessarily. More critically, you may be given these drugs in the ER or post-op and sent home still in pain. Keep this in your medical records.",
    "rs3892097_Tamoxifen Metabolism": "If ignored: tamoxifen won't provide breast cancer protection or treatment benefit — you may have a higher recurrence risk while on ineffective medication. Switching to aromatase inhibitors or higher tamoxifen doses solves this.",
    "rs1065852_CYP2D6 / Drug Metabolism": "If ignored: many medications won't work at standard doses (antidepressants, painkillers, beta-blockers). You may experience side effects from normal doses. A simple genetic test guides your doctor to the right drug and dose.",
    "rs1695_GSTP1 / Chemotherapy": "If ignored during chemotherapy: may affect treatment efficacy of certain platinum-based drugs. Discuss with your oncologist before starting chemo — dose adjustment may improve outcomes.",
    "rs1042522_TP53 / Chemotherapy": "If ignored: minor effect on chemotherapy response. This is a low-impact variant — most oncologists would not change treatment based on this alone.",
    "rs1801159_TPMT / Azathioprine": "If ignored: LIFE-THREATENING. Standard azathioprine/6-MP doses cause severe bone marrow suppression — risk of fatal infection or bleeding. Pre-treatment TPMT testing is now standard — this is why testing exists. You can be safely treated with a 90% dose reduction.",
    "rs1800460_TPMT / Thiopurines": "If ignored: moderate risk of bone marrow toxicity with standard doses. Still requires dose reduction (~30-50%) but less dangerous than the *3A/*3C variants. Pre-treatment testing prevents harm.",
    "rs2066853_AHR / Detoxification": "If ignored: reduced ability to process certain environmental toxins. No acute danger — small chronic effect over years. A diet rich in cruciferous vegetables supports optimal AhR function.",
    "rs762551_Caffeine Metabolism (CYP1A2)": "If ignored (slow metabolizer): 2+ cups of coffee daily increases heart attack risk and causes sleep disruption, anxiety, and digestive issues. Switch to 1 cup or decaf — simple fix with immediate benefits.",
    "rs776746_CYP3A5 / Drug Metabolism": "If ignored: standard tacrolimus doses (transplant drug) cause toxicity. Other CYP3A5-metabolized drugs may need dose adjustment. Mostly relevant for transplant patients — others can note it for future reference.",
    "rs4149056_Statins / SLCO1B1": "If ignored: standard simvastatin (Zocor) dose causes severe muscle pain, weakness, and potentially rhabdomyolysis (kidney damage from muscle breakdown). Switch to rosuvastatin, pravastatin, or lower-dose atorvastatin — completely avoidable.",
    "rs12248560_CYP2C19 / Clopidogrel": "If ignored: ultra-rapid metabolizer — clopidogrel is effective but bleeding risk may be higher. Lower risk scenario than the *2/*3 variants. Awareness helps you and your doctor make informed decisions.",
    "rs4244285_CYP2C19 / Clopidogrel": "If ignored: clopidogrel provides ZERO protection after a heart stent — high risk of stent thrombosis (often fatal heart attack). This is one of the most actionable pharmacogenetic results. Switching to ticagrelor or prasugrel is life-saving.",
    "rs4986893_CYP2C19 / Clopidogrel": "If ignored: same as *2 variant — no antiplatelet effect from clopidogrel. Stent thrombosis risk without effective alternative. Switch to ticagrelor or prasugrel — this information can save your life.",
    "rs7495174_Eye Color": "No health scenario — this is a cosmetic trait with no medical implications.",
    "rs12913832_Eye Color (Blue/Brown)": "No health scenario — purely a physical appearance trait.",
    "rs1805007_Hair Color (Red)": "If ignored: significantly higher risk of sunburn and skin cancer (especially melanoma) if sun protection isn't used. Regular skin checks catch skin cancer early when it's easily treatable. A few minutes of SPF daily prevents most issues.",
    "rs1805008_Hair Color (Red)": "If ignored: same sun sensitivity and skin cancer risk as R151C. Daily SPF and annual skin checks recommended. MC1R-related melanoma risk is real but highly preventable with sun protection.",
    "rs1805009_Hair Color (Red)": "If ignored: same skin cancer risk as other MC1R variants. Rarer variant but similar implications. Protect skin from UV and get annual dermatology checks.",
    "rs17822931_Earwax Type": "No health scenario — harmless trait. Don't clean ear canals with cotton swabs regardless of earwax type.",
    "rs3827760_Hair Thickness": "No health scenario — normal genetic variation in physical appearance. Affects hair, teeth, and sweat glands in harmless ways.",
    "rs16891982_Skin Pigmentation": "If ignored: fair skin burns easily in sun — significantly higher skin cancer risk over a lifetime with inadequate sun protection. Preventable with daily SPF, sun-protective clothing, and regular skin checks.",
    "rs1426654_Skin Pigmentation": "If ignored: same skin cancer risk as other light-skin variants. Lighter skin needs more sun protection but also makes vitamin D more efficiently. Balance sun safety with adequate vitamin D intake.",
    "rs4988235_Lactose Tolerance": "No negative scenario — being able to digest milk as an adult is an advantage for nutrition. No health concerns from this trait itself.",
    "rs621922_Freckles": "If ignored: freckles indicate sun-sensitive skin — higher skin cancer risk with excessive sun exposure. Not the freckles themselves but what they signal about your skin type. SPF and skin checks recommended.",
    "rs10756819_Male Pattern Baldness": "No health risk — cosmetic concern only. If untreated: progressive hair loss following the typical male pattern. Treatments (finasteride, minoxidil) are most effective when started early.",
    "rs2180439_Male Pattern Baldness": "No health risk — same as other baldness variants. Hair loss may start earlier with multiple variants. Cosmetic concern only.",
    "rs28777_Hair Type (Straight/Curly)": "No health scenario — harmless trait determining hair texture.",
    "rs11803731_Hair Graying": "No health scenario — normal aging process. Premature graying is cosmetic only. If graying very early (before 20), consider checking B12 levels as a precaution.",
    "rs1801133_Folate Metabolism": "If unaddressed during pregnancy: significantly increased risk of neural tube defects (spina bifida, anencephaly) in the baby. Elevated homocysteine in adults increases cardiovascular risk over years. Completely preventable with methylfolate supplementation.",
    "rs1801131_Folate Metabolism (A1298C)": "If unaddressed: milder folate processing impairment than C677T. Still beneficial to take methylfolate, especially during pregnancy. Compound heterozygotes (C677T + A1298C) should treat as high-risk.",
    "rs762551_Caffeine Metabolism": "If ignored by slow metabolizer: increased risk of heart attack, high blood pressure, sleep disorders, and anxiety from caffeine. Fast metabolizers have no risk. Knowing your type lets you adjust intake accordingly.",
    "rs705381_Vitamin B12 Levels": "If unaddressed: over years, low B12 causes fatigue, brain fog, nerve damage (numbness/tingling), memory problems, and anemia. B12 deficiency is easily diagnosed and treated with supplements. Irreversible nerve damage can occur if deficiency is severe and prolonged.",
    "rs2297518_Vitamin A / Iron": "If unaddressed: potential for mild nutrient imbalances — unlikely to cause severe deficiency on its own. Combined with a poor diet, may contribute to iron or vitamin A insufficiency over time.",
    "rs3750941_Iron Status": "If unaddressed: higher iron levels — actually beneficial in moderation (less anemia risk). Only problematic if levels become very high (rare without supplements). Annual ferritin check keeps it in perspective.",
    "rs602662_Vitamin B12 Status": "No negative scenario — your B12 levels tend to be higher, which is favorable. Lower risk of B12 deficiency as you age.",
    "rs12794714_Vitamin D Metabolism": "If unaddressed: chronic low vitamin D over years increases risk of osteoporosis, immune dysfunction, mood disorders, and muscle weakness. Easily corrected with vitamin D3 supplementation — cheap, safe, and effective.",
    "rs1993116_Saturated Fat Sensitivity": "If ignored: higher BMI on a high-saturated-fat diet — especially weight gain around the abdomen (visceral fat), which is the most metabolically harmful. Switching to unsaturated fats (olive oil, avocado, nuts) prevents this weight gain tendency.",
    "rs1535_Fatty Acid Metabolism": "No negative scenario — this variant helps you convert plant omega-3s efficiently. Advantageous for vegetarians or those who don't eat fish.",
    "rs174547_Omega-3 / Omega-6 Balance": "If ignored: may develop an unfavorable omega-6:omega-3 ratio over time, contributing to chronic inflammation. Simple dietary shifts (eating more fish, reducing seed oils) restore balance.",
    "rs1784753_Sodium Sensitivity": "If ignored: higher blood pressure on a high-salt diet — over years, hypertension damages arteries, kidneys, heart, and brain, leading to heart attack, stroke, and kidney disease. Blood pressure responds quickly to sodium reduction.",
    "rs5186_Salt / Blood Pressure": "If ignored: progressive hypertension over years if sodium intake is high. The DASH diet (low sodium, high potassium) directly counteracts this genetic tendency. Uncontrolled hypertension is a leading cause of heart disease and stroke.",
    "rs1799752_ACE / Blood Pressure": "If ignored: higher ACE activity raises blood pressure over time, especially with high sodium intake. Annual blood pressure monitoring catches this early. Responds well to aerobic exercise and ACE inhibitor medications if needed.",
    "rs1815739_ACTN3 / Sprint Performance": "No health scenario — athletic performance genetics only. XX genotype doesn't cause health problems, just different muscle characteristics. Train for your personal goals.",
    "rs8192678_Aerobic Fitness / PPARGC1A": "If ignored: may get discouraged by slower fitness gains compared to others. The difference is small — consistent training still produces excellent results, just at a slightly different rate. Persistence pays off.",
    "rs4253778_PPARA / Endurance": "No negative scenario — favorable for endurance performance. You're genetically inclined toward efficient fat burning during exercise. Take advantage of this with regular aerobic training.",
    "rs1800795_IL-6 / Recovery": "No negative scenario — potentially better exercise recovery. Can tolerate higher training volumes with proper recovery. Still need rest days and good nutrition.",
    "rs4646994_ACE / Endurance vs Power": "If ignored: you might train against your natural strengths. I-allele favors endurance, D-allele favors power. Neither limits you — knowing your tendency helps optimize training focus.",
    "rs3764675_Muscle Mass / MSTN": "No negative scenario — slight muscle-building advantage. Results still depend on consistent resistance training and adequate protein intake.",
    "rs1805086_VO2 Max / VEGFR2": "If ignored: you have good aerobic potential but only realize it with consistent training. A sedentary lifestyle wastes this genetic advantage. Start or maintain a regular cardio routine.",
    "rs1049434_Lactate / MCT1": "If ignored: may fatigue sooner during high-intensity exercise — could affect athletic performance or enjoyment. Proper pacing and interval training with recovery periods mitigate this. Training improves lactate clearance.",
    "rs2014355_Injury Risk / COL5A1": "If ignored: higher risk of Achilles tendon injuries — a ruptured Achilles requires surgery and months of recovery. Preventable with eccentric strengthening exercises, proper warm-up, and not pushing through early tendon pain.",
    "rs12722_Tendon Injury / COL5A1": "No negative scenario — protective variant for tendon health. Lower injury risk is an advantage. Maintain good training habits to preserve this benefit.",
    "rs4680_COMT / Worrier vs Warrior": "Neither type is harmful — different trade-offs. Met (worrier): more sensitive to stress/pain but better cognition under pressure. Val (warrior): resilient but may miss subtle signals. Both types thrive with appropriate self-awareness and coping strategies.",
    "rs6311_Anxiety / HTR2A": "If unaddressed: chronic anxiety reduces quality of life, disrupts sleep, strains relationships, and increases cardiovascular strain. Highly treatable with therapy (CBT), exercise, and medication if needed. Anxiety is manageable — don't suffer in silence.",
    "rs25531_SERT / Stress Sensitivity": "If unaddressed: higher sensitivity to stress can lead to depression if negative life events accumulate. However, this variant also means you respond MORE positively to supportive environments. Building a strong social network and learning stress management are particularly effective for you.",
    "rs6265_BDNF / Neuroticism": "If unaddressed: lower BDNF contributes to higher anxiety, poorer stress resilience, and potentially faster cognitive decline with age. Highly responsive to aerobic exercise — this is one of the most actionable variants. Exercise literally grows your brain.",
    "rs6313_HTR2A / Personality": "If unaddressed: seasonal mood changes may affect quality of life without recognition. Light therapy, regular outdoor time, and consistent sleep schedule are simple, effective interventions.",
    "rs1800497_DRD2 / Reward Seeking": "If unaddressed: higher risk of addiction (smoking, alcohol, drugs, gambling, social media, food) and risk-taking behavior. Awareness is protective — knowing your tendency helps you make conscious choices. Healthy dopamine sources (exercise, achievement, creativity) satisfy the same drive without negative consequences.",
    "rs1611115_DBH / Norepinephrine": "If unaddressed: may affect attention, focus, and stress response regulation. Linked to ADHD-like symptoms in some studies. Exercise, adequate protein, and good sleep hygiene support optimal norepinephrine function.",
    "rs53576_OXTR / Empathy & Social": "No negative scenario — different social strategies, not better or worse. G-allele: deeper social connections but may be more affected by rejection. A-allele: more independent but may need to consciously invest in relationships. Both are healthy adaptations.",
    "rs5443_GNB3 / Mood": "If unaddressed: higher baseline risk for mood disorders, especially depression and anxiety. Responds well to standard treatments — therapy, exercise, medication if needed. Awareness helps you seek help early rather than struggling unnecessarily.",
    "rs324981_TAS2R38 / Bitter Taste": "If ignored: potential nutritional impact — supertasters may avoid healthy vegetables, non-tasters may overconsume alcohol. Neither is medically dangerous, but awareness helps you make better food choices regardless of your taste type.",
}

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# Check for missing
c.execute("SELECT rsid, trait FROM reference_snps")
existing = {(r[0], r[1]) for r in c.fetchall()}
keys = set()
for k in IF_UNTREATED:
    parts = k.split("_", 1)
    keys.add((parts[0], parts[1] if len(parts) > 1 else ""))

missing = keys - existing
extra = existing - keys
if missing:
    print(f"WARNING: {len(missing)} entries missing from DB:")
    for r in missing:
        print(f"  {r[0]} - {r[1]}")
if extra:
    print(f"WARNING: {len(extra)} DB entries missing 'if untreated' info:")
    for r in extra:
        print(f"  {r[0]} - {r[1]}")

updated = 0
for key, text in IF_UNTREATED.items():
    parts = key.split("_", 1)
    rsid = parts[0]
    trait = parts[1] if len(parts) > 1 else ""
    c.execute("UPDATE reference_snps SET if_untreated = ? WHERE rsid = ? AND trait = ?", (text, rsid, trait))
    if c.rowcount > 0:
        updated += 1

conn.commit()
print(f"\nUpdated {updated} of {len(IF_UNTREATED)} entries with if_untreated")
conn.close()
