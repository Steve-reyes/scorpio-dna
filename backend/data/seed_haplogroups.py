"""Seed haplogroup-defining SNPs into reference database.
Uses confirmed, well-documented mtDNA and Y-DNA markers.
"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "scorpio_dna.db")

# Verified mtDNA markers - chr:pos pairs for matching,
# plus the reference allele that defines the haplogroup
# Format: (rsid, chr, pos, category, trait, description, risk_allele, risk_geno, level, summary)

MARKERS = [

    # =========================
    # mtDNA HAPLOGROUPS (maternal)
    # =========================

    # K (3480G - rs28358584) - Near East / Europe
    ("rs28358584", "MT", 3480,
     "Ancestry", "K (maternal)",
     "K is a subclade of U8, common in Europe and the Near East. Associated with Neolithic farmers who spread agriculture ~8,000 years ago. ~6% of Europeans carry this lineage.",
     "G", "GG", "defining",
     "Your maternal lineage is K — associated with early European farmers from the Neolithic period."),

    # U (12308G - rs2854128) - Europe / Near East
    ("rs2854128", "MT", 12308,
     "Ancestry", "U (maternal)",
     "U is one of Europe's oldest maternal lineages, dating back ~50,000 years. Predates the last Ice Age. Subclades include U1-U8, with U5 being the oldest European lineage.",
     "G", "GG", "defining",
     "Your maternal lineage is U — one of Europe's oldest maternal lineages, predating the last glacial maximum."),

    # T (13368A - rs28357984) - Europe / Mediterranean
    ("rs28357984", "MT", 13368,
     "Ancestry", "T (maternal)",
     "T is a European and Mediterranean lineage. Subclades T1 and T2 are found across Europe, the Near East, and North Africa. T2 is one of the most common lineages in Europe.",
     "A", "AA", "defining",
     "Your maternal lineage is T — found across Europe and the Mediterranean, with deep roots in the Near East."),

    # J (13708A - rs28357980) - Mediterranean / Near East
    ("rs28357980", "MT", 13708,
     "Ancestry", "J (maternal)",
     "J is common in Mediterranean, Near Eastern, and European populations. Associated with the spread of agriculture from the Fertile Crescent. Subclades J1 and J2.",
     "A", "AA", "defining",
     "Your maternal lineage is J — common around the Mediterranean and Near East, linked to Neolithic farmers."),

    # J/T (16126C - rs41378955) - Shared J/T marker
    ("rs41378955", "MT", 16126,
     "Ancestry", "J/T (maternal)",
     "This marker at position 16126 is found in both haplogroups J and T. When combined with other markers, it helps distinguish between these two related lineages.",
     "C", "CC", "defining",
     "Your maternal lineage carries the J/T marker — further markers can distinguish between J and T subgroups."),

    # B (16189C - rs41458746) - East Asia / Americas
    ("rs41458746", "MT", 16189,
     "Ancestry", "B (maternal)",
     "B is common in East Asia, Southeast Asia, Oceania, and is one of the five founding maternal lineages of Indigenous Americans. Associated with the peopling of the Americas.",
     "C", "CC", "defining",
     "Your maternal lineage is B — common in East/Southeast Asia and a founding lineage of Indigenous Americans."),

    # L3 (16362C - rs2246754) - Africa (Out of Africa)
    ("rs2246754", "MT", 16362,
     "Ancestry", "L3 (maternal)",
     "L3 is the mtDNA haplogroup of the first humans who migrated out of Africa ~70,000 years ago. All non-African mtDNA lineages descend from L3. Also found throughout Africa.",
     "C", "CC", "defining",
     "Your maternal lineage is L3 — the lineage that left Africa ~70,000 years ago and settled the rest of the world."),

    # W (8251A - rs2853495) - Eurasia
    ("rs2853495", "MT", 8251,
     "Ancestry", "W (maternal)",
     "W is a widespread but low-frequency Eurasian mtDNA haplogroup. Found across Europe, the Near East, Central Asia, and parts of South Asia.",
     "A", "AA", "defining",
     "Your maternal lineage is W — a relatively rare but widespread Eurasian haplogroup."),

    # HV (14766T - rs193302980) - Europe
    ("rs193302980", "MT", 14766,
     "Ancestry", "HV (maternal)",
     "HV is the ancestral haplogroup of the most common European lineages (H and V). H alone makes up ~40% of European mtDNA. Originated in the Near East ~25,000 years ago.",
     "T", "TT", "defining",
     "Your maternal lineage is HV — the ancestral lineage of Europe's most common haplogroups, including H and V."),

    # T/X (8697A - rs2857285) - T / X marker
    ("rs2857285", "MT", 8697,
     "Ancestry", "T/X (maternal)",
     "This marker at position 8697 is present in haplogroup T and some X subclades.",
     "A", "AA", "defining",
     "Your maternal lineage carries the T/X marker at position 8697."),

    # C (13263G - rs28357972) - East Asia / Siberia / Americas
    ("rs28357972", "MT", 13263,
     "Ancestry", "C (maternal)",
     "C is a subclade of M, common in East Asia, Siberia, and Indigenous American populations. One of the five founding maternal lineages of the Americas.",
     "G", "GG", "defining",
     "Your maternal lineage is C — found in Siberia, East Asia, and a founding lineage of Indigenous Americans."),

    # D (5178A - rs28358575) - East Asia / Americas
    ("rs28358575", "MT", 5178,
     "Ancestry", "D (maternal)",
     "D is a subclade of M, common in East Asia, Siberia, and Indigenous American populations. One of the five founding maternal lineages of the Americas. Also associated with longevity in Japanese populations.",
     "A", "AA", "defining",
     "Your maternal lineage is D — common in East Asia and a founding lineage of Indigenous Americans."),

    # A (8794T - rs386829035) - East Asia / Americas
    ("rs386829035", "MT", 8794,
     "Ancestry", "A (maternal)",
     "A is common in East Asia, Siberia, and is one of the five founding maternal lineages of Indigenous Americans. Associated with the peopling of the Americas.",
     "T", "TT", "defining",
     "Your maternal lineage is A — common in East Asia and one of the founding maternal lineages of the Americas."),

    # =========================
    # Y-DNA HAPLOGROUPS (paternal)
    # =========================

    # A (M91 - rs16980426) - Africa
    ("rs16980426", "Y", 14249471,
     "Ancestry", "A (paternal)",
     "A is the oldest known Y-chromosome lineage, dating back ~275,000 years. Found in Southern African Khoisan populations. All other Y-lineages descend from A.",
     "T", "TT", "defining",
     "Your paternal lineage is A — the oldest known Y-chromosome lineage, dating back ~275,000 years."),

    # B (M60 - rs16979907) - Africa
    ("rs16979907", "Y", 6807670,
     "Ancestry", "B (paternal)",
     "B is an ancient African Y-lineage found in Central and East Africa, especially among Mbuti and Hadza populations.",
     "A", "AA", "defining",
     "Your paternal lineage is B — an ancient African Y-chromosome lineage."),

    # C (M130 - rs9786246) - East Asia / Oceania
    ("rs9786246", "Y", 151314280,
     "Ancestry", "C (paternal)",
     "C is an ancient Eurasian lineage. Common in East Asia, Siberia, Oceania, and Central Asia. Associated with the early peopling of the Americas and Japan.",
     "T", "TT", "defining",
     "Your paternal lineage is C — common in East Asia, Siberia, and Oceania."),

    # D (M174 - rs2032595) - Tibet / Japan
    ("rs2032595", "Y", 2427329,
     "Ancestry", "D (paternal)",
     "D is found primarily in Tibet, Japan (especially Ainu), and the Andaman Islands. One of the oldest Eurasian lineages.",
     "C", "CC", "defining",
     "Your paternal lineage is D — found in Tibet, Japan (Ainu), and the Andaman Islands."),

    # E (M96 - rs13447352) - Africa / Mediterranean
    ("rs13447352", "Y", 6672274,
     "Ancestry", "E (paternal)",
     "E is common across Africa and the Mediterranean. Subclade E1b1b is associated with the spread of agriculture and Afro-Asiatic languages. Found in ~20% of European men.",
     "A", "AA", "defining",
     "Your paternal lineage is E — common across Africa and the Mediterranean region."),

    # F (M89 - rs9785958) - Eurasia
    ("rs9785958", "Y", 17642406,
     "Ancestry", "F (paternal)",
     "F is the ancestral lineage of ~90% of men outside Africa. All non-African Y-lineages descend from a single man who carried the M89 mutation ~55,000 years ago.",
     "T", "TT", "defining",
     "Your paternal lineage is F — the ancestral lineage of ~90% of men outside Africa."),

    # G (M201 - rs9785969) - Caucasus / Mediterranean
    ("rs9785969", "Y", 12691278,
     "Ancestry", "G (paternal)",
     "G is associated with Neolithic farmers who spread agriculture from the Near East to Europe ~8,000 years ago. Found at its highest frequencies in the Caucasus.",
     "T", "TT", "defining",
     "Your paternal lineage is G — linked to the Neolithic farmers who brought agriculture to Europe."),

    # I (M170 - rs9341278) - Europe
    ("rs9341278", "Y", 15066384,
     "Ancestry", "I (paternal)",
     "I is a European-specific Y-lineage that survived the last Ice Age in Balkan and Iberian refugia. Subclades I1 and I2 are common in Northern and Western Europe.",
     "T", "TT", "defining",
     "Your paternal lineage is I — a European-specific lineage that survived the Ice Age in Southern Europe."),

    # I1 (M253 - rs2534636) - Scandinavia / Northern Europe
    ("rs2534636", "Y", 14189191,
     "Ancestry", "I1 (paternal)",
     "I1 originated in Scandinavia ~25,000 years ago. Most common in Northern Europe, especially Scandinavia and Finland. Associated with Viking-era population expansions.",
     "C", "CC", "defining",
     "Your paternal lineage is I1 — most common in Scandinavia. Likely expanded during the Viking Age."),

    # J (M304/12f2 - rs2032636) - Near East / Mediterranean
    ("rs2032636", "Y", 8614205,
     "Ancestry", "J (paternal)",
     "J originated in the Near East ~30,000 years ago. Common in Mediterranean, Middle Eastern, and Jewish populations. Subclades include J1 (Semitic) and J2 (Mesopotamian).",
     "T", "TT", "defining",
     "Your paternal lineage is J — from the Near East, common in Mediterranean and Middle Eastern populations."),

    # J1 (M267 - rs17269816) - Arabia / Caucasus
    ("rs17269816", "Y", 22922796,
     "Ancestry", "J1 (paternal)",
     "J1 is most common in the Arabian Peninsula, the Levant, and the Caucasus. Associated with Semitic-speaking populations and the spread of pastoralism.",
     "T", "TT", "defining",
     "Your paternal lineage is J1 — most common in the Arabian Peninsula and Caucasus."),

    # J2 (M172 - rs9786193) - Mediterranean / Mesopotamia
    ("rs9786193", "Y", 8585447,
     "Ancestry", "J2 (paternal)",
     "J2 is associated with ancient civilizations of Mesopotamia, Greece, and the Phoenicians. Spread by Neolithic farmers and later seafaring peoples around the Mediterranean.",
     "T", "TT", "defining",
     "Your paternal lineage is J2 — linked to ancient Mediterranean civilizations."),

    # K (M9 - rs9786139) - Eurasia
    ("rs9786139", "Y", 21035238,
     "Ancestry", "K (paternal)",
     "K is the ancestor of most Eurasian Y-lineages (L, M, N, O, P, Q, R, S, T). Originated in Central Asia or the Iranian plateau ~45,000 years ago.",
     "G", "GG", "defining",
     "Your paternal lineage is K — ancestral to most Eurasian Y-chromosome lineages."),

    # N (M231 - rs2032640) - Siberia / Northern Europe
    ("rs2032640", "Y", 43132385,
     "Ancestry", "N (paternal)",
     "N is common in Siberia and Northern Europe, especially among Uralic-speaking peoples (Finns, Saami, Yakuts). ~60% of Finnish men belong to N.",
     "C", "CC", "defining",
     "Your paternal lineage is N — common in Siberia and Northern Europe, especially Uralic populations."),

    # O (M175 - rs9786869) - East Asia
    ("rs9786869", "Y", 3095932,
     "Ancestry", "O (paternal)",
     "O is the most common Y-lineage in East and Southeast Asia. Over 50% of Chinese men belong to O. Subclades O1, O2, and O3 are associated with Sino-Tibetan, Austronesian, and Austroasiatic populations.",
     "T", "TT", "defining",
     "Your paternal lineage is O — the most common lineage in East Asia. ~30% of all men worldwide."),

    # P (M45 - rs9786054) - Eurasia
    ("rs9786054", "Y", 8163019,
     "Ancestry", "P (paternal)",
     "P is the ancestor of haplogroups Q (found in Indigenous Americans and Central Asia) and R (the most common European lineage).",
     "T", "TT", "defining",
     "Your paternal lineage is P — ancestral to Q (Americas) and R (Europe/South Asia)."),

    # Q (M242 - rs2032631) - Americas / Central Asia
    ("rs2032631", "Y", 18751822,
     "Ancestry", "Q (paternal)",
     "Q is found in Central Asia and Siberia. Subclade Q1a-M3 is the defining paternal lineage of Indigenous American populations, arriving via Beringia ~15,000 years ago.",
     "T", "TT", "defining",
     "Your paternal lineage is Q — the primary paternal lineage of Indigenous Americans."),

    # R (M207 - rs9785916) - Europe / South Asia
    ("rs9785916", "Y", 14650155,
     "Ancestry", "R (paternal)",
     "R is the most common European Y-lineage. Over 50% of European men belong to R. Subclades R1a (Eastern Europe/India) and R1b (Western Europe) dominate.",
     "T", "TT", "defining",
     "Your paternal lineage is R — the most common Y-lineage in Europe. ~50% of European men."),

    # R1a (M17/M198 - rs9785716) - Eastern Europe / India
    ("rs9785716", "Y", 20970786,
     "Ancestry", "R1a (paternal)",
     "R1a is associated with the spread of Indo-European languages. Common in Eastern Europe, Central Asia, and Northern India. ~40% of Polish and ~30% of Indian men belong to R1a.",
     "C", "CC", "defining",
     "Your paternal lineage is R1a — linked to the spread of Indo-European languages across Eurasia."),

    # R1b (M343 - rs9786140 / M269 - rs9786153) - Western Europe
    ("rs9786153", "Y", 22696017,
     "Ancestry", "R1b (paternal)",
     "R1b is the most common Y-lineage in Western Europe (~60-80% in some regions). Associated with the spread of Celtic, Germanic, and Italic peoples. Originated from the Yamnaya steppe herders ~5,000 years ago.",
     "T", "TT", "defining",
     "Your paternal lineage is R1b — the most common lineage in Western Europe."),

    # T (M70 - rs13275494) - West Asia / Mediterranean
    ("rs13275494", "Y", 15262895,
     "Ancestry", "T (paternal)",
     "T is found at low frequencies across West Asia, the Mediterranean, and East Africa. Associated with ancient Mesopotamian populations including Sumerians.",
     "C", "CC", "defining",
     "Your paternal lineage is T — a rare lineage found across West Asia and the Mediterranean."),
]


def seed():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Clear existing ancestry entries
    c.execute("DELETE FROM reference_snps WHERE category='Ancestry'")

    count = 0
    for rsid, chrom, pos, category, trait, desc, risk_allele, risk_geno, level, summary in MARKERS:
        # Avoid duplicates
        c.execute("SELECT id FROM reference_snps WHERE rsid=? AND trait=?", (rsid, trait))
        if c.fetchone():
            continue

        is_mtdna = chrom == "MT"
        prefix = "Maternal (mtDNA)" if is_mtdna else "Paternal (Y-chromosome)"

        note = (f"{prefix} haplogroup-defining SNP. "
                f"Chromosome: {chrom}, Position: {pos}. "
                f"{'Tracks the direct maternal line (mother → daughter).' if is_mtdna else 'Passed from father to son. Requires XY (male) DNA data.'} "
                "Results are based on specific SNP markers — multiple markers per haplogroup increase confidence.")

        c.execute("""INSERT INTO reference_snps
            (rsid, category, trait, description, risk_allele, risk_genotype, risk_level, population_freq, study_url, note, summary)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (rsid, category, trait, desc, risk_allele, risk_geno, level, 0.0,
             "https://phylotree.org/" if is_mtdna else "https://isogg.org/tree/", note, summary))
        count += 1

    conn.commit()
    conn.close()
    print(f"Seeded {count} haplogroup markers into reference DB.")
    print(f"  mtDNA: {sum(1 for m in MARKERS if m[1]=='MT')}")
    print(f"  Y-DNA: {sum(1 for m in MARKERS if m[1]=='Y')}")

if __name__ == "__main__":
    seed()
