"""Generate plain-language summaries for all entries."""
import sqlite3

DB_PATH = "/app/data/scorpio_dna.db"

# Plain-language summaries keyed by rsid + trait (some rsids have multiple traits)
# Each summary translates the scientific description into everyday language
SUMMARIES = {
    "rs9939609_Obesity / BMI": "Your DNA has a version of the FTO gene that's linked to higher body weight. Having this gene doesn't mean you'll be overweight — diet, exercise, and habits still matter most — but your body may find it naturally harder to maintain a low BMI.",
    "rs1801133_MTHFR Deficiency": "Your body may have trouble processing folic acid (vitamin B9) efficiently. This can raise homocysteine levels, which is linked to heart and pregnancy health. Many people take methylfolate instead of regular folic acid to work around this.",
    "rs7412_Alzheimer's Risk (APOE)": "You have the protective APOE ε2 version. This is actually good news — it's linked to lower Alzheimer's risk than the general population.",
    "rs429358_Alzheimer's Risk (APOE)": "You carry the APOE ε4 variant, the strongest single gene factor for late-onset Alzheimer's. It raises risk but isn't a diagnosis — many people with it never develop the disease. A brain-healthy lifestyle (diet, exercise, mental stimulation) may help.",
    "rs1799943_Hemochromatosis (HFE)": "You may have a mild tendency to absorb more iron than usual. This is common and usually not a problem, but it's good to know so you can avoid unnecessary iron supplements. A simple blood test (ferritin) can check your levels.",
    "rs1800562_Hemochromatosis (HFE)": "You have the main genetic variant for hereditary iron overload. Your body may store too much iron over time. This is easily managed — just avoid iron supplements, limit vitamin C supplements, and donate blood regularly to lower iron levels.",
    "rs328_Lipoprotein(a) / Heart Disease": "Your body may produce higher levels of Lp(a), a type of cholesterol particle that increases heart disease risk. Unlike regular cholesterol, Lp(a) is mostly genetic and doesn't change much with diet. Talk to your doctor about monitoring it.",
    "rs662799_Triglycerides": "You may have a genetic tendency toward higher triglyceride levels, a type of blood fat. Regular exercise, low sugar intake, and omega-3s (fish oil) can help keep these in check.",
    "rs7903146_Type 2 Diabetes": "Your DNA has the strongest common genetic marker for type 2 diabetes. This doesn't mean you'll get it — lifestyle is a huge factor — but staying active, eating well, and maintaining a healthy weight matters extra for you.",
    "rs5219_Type 2 Diabetes": "Your pancreas may produce insulin a bit less efficiently. Combined with a healthy lifestyle, this is manageable, but keeping physically active and avoiding excess sugar is especially important.",
    "rs12255372_Type 2 Diabetes": "Another gene variant related to diabetes risk. Works similarly to the main TCF7L2 variant — lifestyle habits matter more than genetics here.",
    "rs1800629_TNF-alpha / Inflammation": "Your body may produce higher levels of TNF-alpha, an inflammation signal. This can mean a stronger inflammatory response to triggers. Anti-inflammatory habits (omega-3s, exercise, less processed food) can help balance this.",
    "rs16944_IL-1B / Inflammation": "You may produce more IL-1β, a key inflammatory protein. Chronic inflammation is linked to many health issues. Diet rich in anti-inflammatory foods (berries, fatty fish, greens) may be especially helpful.",
    "rs1800795_IL-6 / Inflammation": "Your body may produce more IL-6, an inflammation marker. On the flip side, this can also mean a stronger immune response. Balanced lifestyle habits matter.",
    "rs1801131_MTHFR A1298C": "A second MTHFR variant that reduces folate processing ability, but milder than the C677T version. If you also have the C677T variant (compound heterozygote), the combined effect is similar to having two copies of C677T.",
    "rs1042713_Asthma / ADRB2": "Your lung's response to asthma medications (bronchodilators) may differ. If you have asthma, this can affect how well rescue inhalers work for you.",
    "rs1051730_Nicotine Dependence": "Your brain's nicotine receptors work differently. If you smoke, this variant makes quitting harder because you get stronger reward signals from nicotine. Patches or medication may help more than willpower alone.",
    "rs16969968_Nicotine Dependence": "Similar to the CHRNA3 variant — your brain responds more strongly to nicotine, making smoking more addictive. Good to know if you smoke or ever plan to quit.",
    "rs1544410_Vitamin D / Osteoporosis": "Your vitamin D receptors may not work as efficiently. This means your body may need more vitamin D to maintain strong bones. Getting enough sun, vitamin D foods, or supplements matters a bit more for you.",
    "rs2228570_Vitamin D / Autoimmunity": "Your vitamin D receptor is more active, which can influence immune system regulation. This is linked to slightly higher autoimmune tendencies. Adequate vitamin D levels are especially important.",
    "rs4988235_Lactose Intolerance": "Your body may not produce enough lactase enzyme to digest milk sugar (lactose). This is normal — most of the world is lactose intolerant as adults. Lactose-free milk or lactase pills are easy solutions.",
    "rs182549_Lactose Intolerance": "Another marker for lactase persistence. Same as above — if you can't tolerate milk well, lactose-free options work fine.",
    "rs738409_NAFLD / Fatty Liver": "Your liver may be more prone to accumulating fat. This is the strongest gene variant for fatty liver disease. Avoiding excess sugar (especially fructose), limiting alcohol, and staying active are especially important for you.",
    "rs58542926_NAFLD / Liver Disease": "Your liver handles fats differently, which can increase fatty liver risk. Same advice — watch sugar and alcohol intake.",
    "rs2066844_Crohn's Disease / NOD2": "Your immune system's ability to detect gut bacteria may be altered, slightly raising Crohn's disease risk. This is a rare variant — only about 4% of people carry it.",
    "rs2066845_Crohn's Disease / NOD2": "Another NOD2 variant that slightly affects gut immune function. Very few people carry this (about 2%).",
    "rs2004640_Autoimmunity / TYK2": "This variant actually protects against autoimmune diseases. Your immune signaling is more balanced.",
    "rs1333049_Coronary Artery Disease": "Your DNA has a version of the 9p21 region — the strongest genetic marker for heart disease risk. It affects how your artery walls repair themselves. Keep blood pressure, cholesterol, and lifestyle factors well-managed.",
    "rs10757278_Heart Attack / CAD": "Another 9p21 heart risk marker. Same advice — watch your heart health proactively.",
    "rs328_Heart Disease / LPL": "Your body processes blood fats more efficiently. This variant actually lowers triglycerides and reduces heart disease risk — a beneficial version.",
    "rs6311_Serotonin / Mood": "Your serotonin receptors may be set differently, which can affect mood regulation. It may influence how you respond to certain antidepressants (SSRIs).",
    "rs6313_Serotonin / Depression": "Your serotonin receptor function may change with seasons slightly. This variant is linked to seasonal mood patterns and how well antidepressants work.",
    "rs4680_COMT / Stress Response": "This affects how your brain clears dopamine. The Met version (slow COMT) means dopamine hangs around longer — better focus under stress but may feel things more intensely. The Val version clears it faster — more resilient but slightly worse detailed cognition.",
    "rs6265_BDNF / Memory & Mood": "Your brain may produce less BDNF, a protein that helps brain cells grow and connect. This is linked to memory performance and mood regulation. Aerobic exercise is one of the best ways to boost BDNF naturally.",
    "rs1815739_ACTN3 / Muscle Performance": "This determines whether your muscles produce alpha-actinin-3, a protein for fast-twitch (sprint/power) muscle fibers. If you have the XX version, you lack it — you may be better at endurance than sprinting.",
    "rs334_Sickle Cell Anemia": "You carry the sickle cell trait. This means you won't have sickle cell disease yourself, but if your partner also carries it, your child could inherit the disease. Carriers actually have some natural protection against malaria.",
    "rs6025_Factor V Leiden": "Your blood may clot more easily than normal (Factor V Leiden). This raises the risk of deep vein thrombosis (DVT), especially during surgery, pregnancy, or long flights. Something to mention to your doctor.",
    "rs1799963_Prothrombin / Clotting": "Your body may produce more prothrombin, a clotting factor, slightly increasing thrombosis risk. Similar precautions as Factor V Leiden — mention it before surgery or long travel.",
    "rs121908001_Cystic Fibrosis (ΔF508)": "You may carry the most common cystic fibrosis mutation. Carriers don't have CF but could pass it to children if their partner also carries a CF mutation.",
    "rs1800078_Cystic Fibrosis (G551D)": "Another CF mutation. Same — carriers are fine but the combination matters for children.",
    "rs1800137_Cystic Fibrosis (W1282X)": "Another CF mutation, more common in Ashkenazi Jewish populations. Same carrier principle.",
    "rs137852587_Tay-Sachs (HEXA)": "You may carry the Tay-Sachs mutation. This is relevant for Ashkenazi Jewish heritage — carriers don't have the disease but children could if both parents carry it.",
    "rs28942079_G6PD Deficiency": "Your red blood cells may be more sensitive to certain triggers (certain foods like fava beans, some medications). This is X-linked, so it affects males more. Avoid known triggers and mention it before taking new meds.",
    "rs1042822_Hemochromatosis (HFE)": "A milder form of the iron-overload gene. Less impactful than the main C282Y variant.",
    "rs28934574_BRCA1 / Breast Cancer": "You may carry a BRCA1 mutation, which significantly raises breast and ovarian cancer risk. This is relevant regardless of gender — men can carry it too and may have higher prostate cancer risk. Genetic counseling is recommended.",
    "rs80357906_BRCA2 / Breast Cancer": "You may carry a BRCA2 mutation, raising risk for breast, ovarian, and pancreatic cancers. Same recommendation — genetic counseling is worth pursuing.",
    "rs1801028_Maple Syrup Urine Disease": "Carrier status for MSUD. Very rare — carriers have no symptoms but could pass it on if both parents are carriers.",
    "rs6443349_Spinal Muscular Atrophy": "Carrier for SMA, a serious nerve condition. About 1 in 50 people carry this. Only matters if planning children with another carrier.",
    "rs2071128_Wilson Disease": "Carrier for Wilson disease. Affects copper processing. Carriers are healthy — only matters for family planning.",
    "rs80338902_Gaucher Disease": "Carrier for Gaucher disease, more common in Ashkenazi Jewish populations. Carriers are healthy — matters only for family planning.",
    "rs9923231_Warfarin Sensitivity": "Your body may need a lower dose of warfarin (blood thinner) because your target enzyme works less efficiently. Your starting dose should be lower than average to avoid bleeding risk.",
    "rs1799853_Warfarin Sensitivity": "You may process warfarin more slowly. Your doctor should start you on a lower dose and monitor closely.",
    "rs1057910_Warfarin Sensitivity": "You process warfarin very slowly — you'll likely need a significantly lower dose than most people. Important info for your doctor.",
    "rs28399433_CYP2A6 / Nicotine Metabolism": "Your body breaks down nicotine slowly. This may make you smoke less since nicotine stays in your system longer. Also affects how well nicotine patches work.",
    "rs3892097_Codeine Efficacy (CYP2D6)": "Your body can't convert codeine into its active pain-relieving form (morphine). Codeine and tramadol won't work well for you as painkillers. Ask your doctor about alternatives.",
    "rs3892097_Tamoxifen Metabolism": "Same CYP2D6 variant — your body also can't activate tamoxifen properly. If you're prescribed tamoxifen for breast cancer, your doctor needs to know. Aromatase inhibitors may be a better option.",
    "rs1065852_CYP2D6 / Drug Metabolism": "Your CYP2D6 enzyme works at reduced capacity. This affects many common drugs — antidepressants, antipsychotics, beta-blockers, opioids. Your doctor may need to adjust doses.",
    "rs1695_GSTP1 / Chemotherapy": "Your body's detoxification system works differently, which can affect how you handle chemotherapy drugs. This varies by specific drug — your oncologist can factor this in.",
    "rs1042522_TP53 / Chemotherapy": "Your p53 tumor suppressor — a key cancer-fighting protein — may function slightly differently. Can influence how well certain chemotherapies work.",
    "rs1801159_TPMT / Azathioprine": "Your body can't break down thiopurine drugs (azathioprine, 6-MP) properly. If you need these for autoimmune conditions or after organ transplant, your dose must be much lower to avoid dangerous side effects.",
    "rs1800460_TPMT / Thiopurines": "A milder TPMT variant. Your thiopurine metabolism is somewhat reduced. Still worth testing before starting these meds.",
    "rs2066853_AHR / Detoxification": "Your body's ability to process certain environmental toxins may be altered. This is a minor factor — healthy diet and avoiding known toxins is general good advice regardless.",
    "rs762551_Caffeine Metabolism (CYP1A2)": "This tells you if you're a fast or slow caffeine metabolizer. Fast metabolizers: 4+ cups of coffee daily is fine. Slow metabolizers: more than 2 cups is linked to higher heart risk and sleep issues.",
    "rs776746_CYP3A5 / Drug Metabolism": "Your body doesn't produce functional CYP3A5 enzyme. This affects how you process many common drugs including tacrolimus (transplant med), some statins, and calcium channel blockers.",
    "rs4149056_Statins / SLCO1B1": "Your liver may not absorb statins efficiently, causing higher levels in your bloodstream. This sharply increases the risk of muscle pain and damage with simvastatin (Zocor). Rosuvastatin or low-dose alternatives may work better.",
    "rs12248560_CYP2C19 / Clopidogrel": "Your body activates clopidogrel (Plavix) faster than usual. This means better protection against blood clots but higher bleeding risk. Your doctor should know before prescribing it.",
    "rs4244285_CYP2C19 / Clopidogrel": "Your body can't activate clopidogrel (Plavix) properly — it won't protect you from blood clots effectively. Ticagrelor or prasugrel are better alternatives. Very important if you have a heart stent.",
    "rs4986893_CYP2C19 / Clopidogrel": "Another loss-of-function CYP2C19 variant, common in East Asians. Same as above — clopidogrel won't work well. Ask about alternatives.",
    "rs7495174_Eye Color": "This gene helps determine your eye color. The variant you have is part of what makes your eyes their specific shade.",
    "rs12913832_Eye Color (Blue/Brown)": "This is the single most important gene for eye color. Your version tells whether your eyes lean toward blue or brown.",
    "rs1805007_Hair Color (Red)": "This is one of the main genes behind red hair. If you have it, you may have red hair, fair skin, and be more sensitive to sun exposure.",
    "rs1805008_Hair Color (Red)": "Another red hair gene (MC1R). Even if you don't have red hair, carrying this means fairer skin and higher sun sensitivity.",
    "rs1805009_Hair Color (Red)": "A rarer red hair variant. Same MC1R gene, same effects — red hair tendency and fair skin.",
    "rs17822931_Earwax Type": "A fun one — your version determines whether you have wet or dry earwax. Wet is common in Europeans and Africans, dry in East Asians. No health concern either way.",
    "rs3827760_Hair Thickness": "This affects your hair thickness, tooth shape, and sweat glands. The variant you have influences these physical traits.",
    "rs16891982_Skin Pigmentation": "Part of what determines your natural skin tone. This variant is nearly universal in European populations and contributes to lighter skin.",
    "rs1426654_Skin Pigmentation": "Another major skin color gene. Your version influences how light or dark your skin is naturally.",
    "rs4988235_Lactose Tolerance": "Whether you can digest milk as an adult comes down to this gene. The lactase persistence version evolved in dairy-farming populations.",
    "rs621922_Freckles": "Your skin may have a tendency to develop freckles, especially with sun exposure. Not a health concern — just a skin trait.",
    "rs10756819_Male Pattern Baldness": "This variant on the X chromosome (passed from mother to son) affects your risk of male pattern baldness. A major factor in hair loss timing.",
    "rs2180439_Male Pattern Baldness": "Another baldness-related variant. Having both makes early hair loss more likely.",
    "rs28777_Hair Type (Straight/Curly)": "This gene affects whether your hair is straight or curly. The variant you have shapes your hair texture.",
    "rs11803731_Hair Graying": "This variant affects when your hair starts turning gray. Some people's hair grays earlier due to this gene.",
    "rs1801133_Folate Metabolism": "Your body may struggle to convert folic acid (synthetic) into its active form (methylfolate). Taking methylfolate supplements instead of regular folic acid bypasses this issue. Important during pregnancy.",
    "rs1801131_Folate Metabolism (A1298C)": "A second MTHFR variant affecting folate processing. Milder than C677T but still worth knowing for supplement choices.",
    "rs762551_Caffeine Metabolism": "Tells you if coffee is processed fast or slow in your body. Fast: coffee is fine. Slow: 2+ cups daily may raise heart risk slightly.",
    "rs705381_Vitamin B12 Levels": "Your body may absorb vitamin B12 less efficiently, leading to naturally lower B12 levels. B12-rich foods (meat, eggs, dairy) or supplements can help maintain healthy levels.",
    "rs2297518_Vitamin A / Iron": "This variant affects how your body handles vitamin A and iron. May influence your dietary needs for these nutrients.",
    "rs3750941_Iron Status": "Your body may hold onto iron more efficiently, with higher than average iron levels. Good to know — monitoring iron is easier than fixing deficiency.",
    "rs602662_Vitamin B12 Status": "Your body absorbs B12 well — this variant is linked to higher B12 levels. That's generally a positive thing.",
    "rs12794714_Vitamin D Metabolism": "Your body may convert vitamin D into its active form less efficiently. You might need a bit more sun exposure or vitamin D supplements than average to maintain healthy levels.",
    "rs1993116_Saturated Fat Sensitivity": "Your weight may be more affected by saturated fat intake than average. If you carry this variant, limiting saturated fat (butter, fatty meats, fried foods) is extra important for weight management.",
    "rs1535_Fatty Acid Metabolism": "Your body converts omega-3 and omega-6 fatty acids more efficiently. Getting plant-based omega-3s (flax, walnuts) may benefit you more than average.",
    "rs174547_Omega-3 / Omega-6 Balance": "Your body's balance of omega-3 to omega-6 fatty acids is influenced by this gene. Eating fatty fish or taking fish oil may be especially beneficial.",
    "rs1784753_Sodium Sensitivity": "Your blood pressure may be more sensitive to salt intake. If you have this variant, reducing sodium is extra important for keeping blood pressure healthy.",
    "rs5186_Salt / Blood Pressure": "Your blood pressure regulation is more sensitive to the renin-angiotensin system. A lower-sodium, higher-potassium diet (fruits, veggies) may help more than average.",
    "rs1799752_ACE / Blood Pressure": "Your ACE enzyme activity level is influenced by this variant. Higher activity (D-allele) means tighter blood vessel tone. Aerobic exercise and a heart-healthy diet are especially beneficial.",
    "rs1815739_ACTN3 / Sprint Performance": "One of the most-studied fitness genes. Your version affects whether you have fast-twitch muscle fibers for sprinting/power or are more built for endurance. This doesn't limit you — training trumps genetics for most people.",
    "rs8192678_Aerobic Fitness / PPARGC1A": "This affects how well your cardiovascular fitness responds to training. If you have the A-variant, you may need more consistent endurance training to see the same aerobic gains.",
    "rs4253778_PPARA / Endurance": "Your body's fat-burning efficiency during exercise may be better. Associated with better endurance performance and heart function.",
    "rs1800795_IL-6 / Recovery": "Your body's inflammatory response to exercise may be lower, which can mean faster recovery between workouts.",
    "rs4646994_ACE / Endurance vs Power": "ACE I/D variant affects whether you're naturally inclined toward endurance (I-allele) or power/sprint (D-allele) activities. Fun to know — but training matters more than genes.",
    "rs3764675_Muscle Mass / MSTN": "Your muscle-building potential may be influenced by this gene. Myostatin limits muscle growth — some variants reduce this limit slightly.",
    "rs1805086_VO2 Max / VEGFR2": "Your blood vessel growth response to exercise may be better, helping you improve aerobic capacity more with consistent training.",
    "rs1049434_Lactate / MCT1": "Your body may clear lactate (the 'burning' feeling during exercise) more slowly. You might fatigue a bit faster during high-intensity efforts.",
    "rs2014355_Injury Risk / COL5A1": "Your collagen type V structure may make your Achilles tendon slightly more injury-prone. Good warm-up, stretching, and not overdoing high-impact activities is extra important.",
    "rs12722_Tendon Injury / COL5A1": "Your collagen structure may protect against tendon injuries slightly better than average.",
    "rs4680_COMT / Worrier vs Warrior": "This famous 'worrier vs warrior' gene affects your baseline dopamine levels. Worrier (Met) version: sharper focus, more cautious, feels pain more. Warrior (Val) version: more resilient, less affected by stress, processes pain better. Neither is better — different trade-offs.",
    "rs6311_Anxiety / HTR2A": "Your serotonin system may be set to a more cautious baseline. You may naturally be more aware of risks and potential threats — a useful trait in the right environment.",
    "rs25531_SERT / Stress Sensitivity": "Your serotonin transporter handles stress differently. The short version makes you more sensitive to stressful life events but also more responsive to supportive environments. Gene × environment interaction matters a lot here.",
    "rs6265_BDNF / Neuroticism": "This BDNF variant affects how your brain grows and adapts. Linked to slightly higher anxiety and emotional sensitivity. Exercise is one of the best natural BDNF boosters.",
    "rs6313_HTR2A / Personality": "Your serotonin receptor variant influences your behavioral tendencies, including how cautious or novelty-seeking you are.",
    "rs1800497_DRD2 / Reward Seeking": "Your brain has fewer D2 dopamine receptors, which means your reward system responds differently. Linked to novelty-seeking, higher addiction risk, and needing more stimulation to feel satisfied.",
    "rs1611115_DBH / Norepinephrine": "Your body produces less norepinephrine due to lower DBH enzyme activity. This affects attention, focus, and how your body responds to stress.",
    "rs53576_OXTR / Empathy & Social": "One of the most interesting social behavior genes. Your oxytocin receptor variant influences empathy, trust, and bonding. The G-version is linked to higher empathy and social sensitivity.",
    "rs5443_GNB3 / Mood": "Your cell signaling systems may work differently, affecting mood regulation and antidepressant response. Not a diagnosis — just a piece of the mood puzzle.",
    "rs324981_TAS2R38 / Bitter Taste": "This determines whether you're a 'supertaster' who's very sensitive to bitter flavors or a 'non-taster'. It affects food preferences — supertasters often dislike broccoli, coffee, and dark chocolate because they taste extra bitter.",
}

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# Check which keys in SUMMARIES don't match any DB entries
c.execute("SELECT rsid, trait FROM reference_snps")
existing = {(r[0], r[1]) for r in c.fetchall()}
summary_keys = set()
for k in SUMMARIES:
    parts = k.split("_", 1)
    summary_keys.add((parts[0], parts[1] if len(parts) > 1 else ""))

missing_from_db = summary_keys - existing
extra_in_db = existing - summary_keys

if missing_from_db:
    print(f"WARNING: {len(missing_from_db)} summaries have no matching DB entry:")
    for r in missing_from_db:
        print(f"  {r[0]} - {r[1]}")

if extra_in_db:
    print(f"WARNING: {len(extra_in_db)} DB entries have no summary:")
    for r in sorted(extra_in_db):
        print(f"  {r[0]} - {r[1]}")

# Update with proper summaries
updated = 0
for key, summary in SUMMARIES.items():
    parts = key.split("_", 1)
    rsid = parts[0]
    trait = parts[1] if len(parts) > 1 else ""
    c.execute("UPDATE reference_snps SET summary = ? WHERE rsid = ? AND trait = ?", (summary, rsid, trait))
    if c.rowcount > 0:
        updated += 1

conn.commit()
print(f"\nUpdated {updated} out of {len(SUMMARIES)} summaries")
conn.close()
