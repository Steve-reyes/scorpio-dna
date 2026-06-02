"""Autosomal ancestry admixture estimation using ancestry-informative markers (AIMs).

Reference: compiled from published panels (Kosoy et al. 128-AIM, Kidd 102-AIM, Phillips 46-AIM)
with allele frequencies from 1000 Genomes Phase 3 and HGDP.
"""

import pandas as pd
import numpy as np

POPS = ['African', 'European', 'East_Asian', 'South_Asian', 'Native_American']
POP_LABELS = {
    'African': 'African',
    'European': 'European',
    'East_Asian': 'East Asian',
    'South_Asian': 'South Asian',
    'Native_American': 'Native American',
}

AIM_MARKERS = {
    # === HIGH-FST AFRICAN MARKERS ===
    'rs2814778': {'African': 0.01, 'European': 0.99, 'East_Asian': 1.00, 'South_Asian': 0.98, 'Native_American': 0.99},
    'rs1426654': {'African': 0.95, 'European': 0.05, 'East_Asian': 1.00, 'South_Asian': 0.30, 'Native_American': 0.98},
    'rs16891982': {'African': 0.98, 'European': 0.06, 'East_Asian': 1.00, 'South_Asian': 0.35, 'Native_American': 1.00},
    'rs12913832': {'African': 0.95, 'European': 0.28, 'East_Asian': 1.00, 'South_Asian': 0.92, 'Native_American': 1.00},
    'rs6119471': {'African': 0.20, 'European': 0.85, 'East_Asian': 0.92, 'South_Asian': 0.82, 'Native_American': 0.90},
    'rs1244545': {'African': 0.15, 'European': 0.78, 'East_Asian': 0.85, 'South_Asian': 0.75, 'Native_American': 0.82},
    'rs2196051': {'African': 0.08, 'European': 0.72, 'East_Asian': 0.80, 'South_Asian': 0.68, 'Native_American': 0.76},
    'rs1876482': {'African': 0.10, 'European': 0.65, 'East_Asian': 0.75, 'South_Asian': 0.60, 'Native_American': 0.70},
    'rs475833': {'African': 0.18, 'European': 0.82, 'East_Asian': 0.88, 'South_Asian': 0.78, 'Native_American': 0.85},

    # === HIGH-FST EUROPEAN MARKERS ===
    'rs3827760': {'African': 0.98, 'European': 0.99, 'East_Asian': 0.12, 'South_Asian': 0.65, 'Native_American': 0.25},
    'rs17822931': {'African': 0.98, 'European': 0.98, 'East_Asian': 0.20, 'South_Asian': 0.60, 'Native_American': 0.30},
    'rs1800414': {'African': 0.85, 'European': 0.98, 'East_Asian': 0.35, 'South_Asian': 0.70, 'Native_American': 0.40},
    'rs12203592': {'African': 0.95, 'European': 0.32, 'East_Asian': 0.98, 'South_Asian': 0.88, 'Native_American': 0.95},
    'rs12896399': {'African': 0.72, 'European': 0.42, 'East_Asian': 0.15, 'South_Asian': 0.50, 'Native_American': 0.18},
    'rs4778138': {'African': 0.55, 'European': 0.20, 'East_Asian': 0.85, 'South_Asian': 0.60, 'Native_American': 0.80},
    'rs1129038': {'African': 0.88, 'European': 0.35, 'East_Asian': 0.95, 'South_Asian': 0.85, 'Native_American': 0.92},

    # === EAST ASIAN SPECIFIC ===
    'rs671': {'African': 1.00, 'European': 1.00, 'East_Asian': 0.75, 'South_Asian': 0.98, 'Native_American': 0.99},
    'rs2031920': {'African': 0.90, 'European': 0.88, 'East_Asian': 0.40, 'South_Asian': 0.70, 'Native_American': 0.50},
    'rs3813565': {'African': 0.78, 'European': 0.75, 'East_Asian': 0.15, 'South_Asian': 0.50, 'Native_American': 0.30},
    'rs4646903': {'African': 0.85, 'European': 0.92, 'East_Asian': 0.50, 'South_Asian': 0.78, 'Native_American': 0.55},
    'rs20331': {'African': 0.60, 'European': 0.55, 'East_Asian': 0.10, 'South_Asian': 0.35, 'Native_American': 0.15},

    # === SOUTH ASIAN MARKERS ===
    'rs4832348': {'African': 0.65, 'European': 0.40, 'East_Asian': 0.85, 'South_Asian': 0.15, 'Native_American': 0.78},
    'rs11131917': {'African': 0.55, 'European': 0.70, 'East_Asian': 0.90, 'South_Asian': 0.20, 'Native_American': 0.80},
    'rs1011708': {'African': 0.70, 'European': 0.35, 'East_Asian': 0.80, 'South_Asian': 0.18, 'Native_American': 0.72},

    # === PIGMENTATION + MORPHOLOGY ===
    'rs885479': {'African': 0.90, 'European': 0.42, 'East_Asian': 0.15, 'South_Asian': 0.35, 'Native_American': 0.20},
    'rs1805007': {'African': 0.95, 'European': 0.18, 'East_Asian': 1.00, 'South_Asian': 0.92, 'Native_American': 0.98},
    'rs1805008': {'African': 0.92, 'European': 0.12, 'East_Asian': 1.00, 'South_Asian': 0.95, 'Native_American': 0.99},
    'rs1110400': {'African': 0.88, 'European': 0.52, 'East_Asian': 0.75, 'South_Asian': 0.65, 'Native_American': 0.70},
    'rs4911414': {'African': 0.70, 'European': 0.38, 'East_Asian': 0.88, 'South_Asian': 0.60, 'Native_American': 0.82},

    # === METABOLISM / LACTASE ===
    'rs4988235': {'African': 0.82, 'European': 0.35, 'East_Asian': 0.98, 'South_Asian': 0.70, 'Native_American': 0.95},
    'rs182549': {'African': 0.78, 'European': 0.30, 'East_Asian': 0.95, 'South_Asian': 0.65, 'Native_American': 0.92},
    'rs1454361': {'African': 0.58, 'European': 0.82, 'East_Asian': 0.35, 'South_Asian': 0.62, 'Native_American': 0.45},
    'rs3754689': {'African': 0.65, 'European': 0.75, 'East_Asian': 0.88, 'South_Asian': 0.55, 'Native_American': 0.80},

    # === BROAD CONTINENTAL AIMS ===
    'rs7722456': {'African': 0.16, 'European': 0.65, 'East_Asian': 0.78, 'South_Asian': 0.58, 'Native_American': 0.72},
    'rs2237301': {'African': 0.28, 'European': 0.80, 'East_Asian': 0.85, 'South_Asian': 0.72, 'Native_American': 0.82},
    'rs2077036': {'African': 0.35, 'European': 0.55, 'East_Asian': 0.20, 'South_Asian': 0.40, 'Native_American': 0.25},
    'rs1042602': {'African': 0.62, 'European': 0.22, 'East_Asian': 0.85, 'South_Asian': 0.55, 'Native_American': 0.78},
    'rs1393350': {'African': 0.78, 'European': 0.18, 'East_Asian': 0.70, 'South_Asian': 0.45, 'Native_American': 0.65},
    'rs1800407': {'African': 0.85, 'European': 0.92, 'East_Asian': 0.60, 'South_Asian': 0.80, 'Native_American': 0.65},
    'rs1800401': {'African': 0.90, 'European': 0.95, 'East_Asian': 0.72, 'South_Asian': 0.85, 'Native_American': 0.78},

    # === ADDITIONAL FORENSIC AIMS ===
    'rs1029047': {'African': 0.42, 'European': 0.82, 'East_Asian': 0.65, 'South_Asian': 0.70, 'Native_American': 0.68},
    'rs12498138': {'African': 0.30, 'European': 0.72, 'East_Asian': 0.60, 'South_Asian': 0.55, 'Native_American': 0.58},
    'rs1335873': {'African': 0.55, 'European': 0.22, 'East_Asian': 0.78, 'South_Asian': 0.42, 'Native_American': 0.72},
    'rs1358856': {'African': 0.35, 'European': 0.68, 'East_Asian': 0.82, 'South_Asian': 0.62, 'Native_American': 0.78},
    'rs1836724': {'African': 0.48, 'European': 0.18, 'East_Asian': 0.72, 'South_Asian': 0.38, 'Native_American': 0.65},
    'rs1900675': {'African': 0.25, 'European': 0.72, 'East_Asian': 0.55, 'South_Asian': 0.60, 'Native_American': 0.58},
    'rs2042762': {'African': 0.72, 'European': 0.28, 'East_Asian': 0.82, 'South_Asian': 0.52, 'Native_American': 0.75},
    'rs2342747': {'African': 0.40, 'European': 0.65, 'East_Asian': 0.20, 'South_Asian': 0.45, 'Native_American': 0.28},
    'rs2317267': {'African': 0.30, 'European': 0.58, 'East_Asian': 0.85, 'South_Asian': 0.52, 'Native_American': 0.78},
    'rs3845563': {'African': 0.58, 'European': 0.25, 'East_Asian': 0.12, 'South_Asian': 0.30, 'Native_American': 0.18},
}

# Chromosome:position (GRCh37) fallbacks for key AIMs that might not have rsIDs on some chips
# Format: (chrom, pos) -> population frequencies
AIM_POSITIONS = {
    # AFRICAN markers - chr:pos fallback for rs2814778 (chr1:159174683)
    (1, 159174683): {'African': 0.01, 'European': 0.99, 'East_Asian': 1.00, 'South_Asian': 0.98, 'Native_American': 0.99},
    # SLC24A5 - rs1426654 (chr15:48426484)
    (15, 48426484): {'African': 0.95, 'European': 0.05, 'East_Asian': 1.00, 'South_Asian': 0.30, 'Native_American': 0.98},
    # SLC45A2 - rs16891982 (chr5:33951693)
    (5, 33951693): {'African': 0.98, 'European': 0.06, 'East_Asian': 1.00, 'South_Asian': 0.35, 'Native_American': 1.00},
    # HERC2 - rs12913832 (chr15:28365618)
    (15, 28365618): {'African': 0.95, 'European': 0.28, 'East_Asian': 1.00, 'South_Asian': 0.92, 'Native_American': 1.00},
    # EDAR - rs3827760 (chr2:109513601)
    (2, 109513601): {'African': 0.98, 'European': 0.99, 'East_Asian': 0.12, 'South_Asian': 0.65, 'Native_American': 0.25},
    # ABCC11 - rs17822931 (chr16:48258198)
    (16, 48258198): {'African': 0.98, 'European': 0.98, 'East_Asian': 0.20, 'South_Asian': 0.60, 'Native_American': 0.30},
    # ALDH2 - rs671 (chr12:112241766)
    (12, 112241766): {'African': 1.00, 'European': 1.00, 'East_Asian': 0.75, 'South_Asian': 0.98, 'Native_American': 0.99},
    # LCT/MCM6 - rs4988235 (chr2:136608646)
    (2, 136608646): {'African': 0.82, 'European': 0.35, 'East_Asian': 0.98, 'South_Asian': 0.70, 'Native_American': 0.95},
    # MC1R - rs1805007 (chr16:89986144)
    (16, 89986144): {'African': 0.95, 'European': 0.18, 'East_Asian': 1.00, 'South_Asian': 0.92, 'Native_American': 0.98},
    # MC1R - rs1805008 (chr16:89986117)
    (16, 89986117): {'African': 0.92, 'European': 0.12, 'East_Asian': 1.00, 'South_Asian': 0.95, 'Native_American': 0.99},
    # TYR - rs1042602 (chr11:88911696)
    (11, 88911696): {'African': 0.62, 'European': 0.22, 'East_Asian': 0.85, 'South_Asian': 0.55, 'Native_American': 0.78},
    # TYR - rs1393350 (chr11:88911354)
    (11, 88911354): {'African': 0.78, 'European': 0.18, 'East_Asian': 0.70, 'South_Asian': 0.45, 'Native_American': 0.65},
    # OCA2 - rs1800407 (chr15:28230318)
    (15, 28230318): {'African': 0.85, 'European': 0.92, 'East_Asian': 0.60, 'South_Asian': 0.80, 'Native_American': 0.65},
    # IRF4 - rs12203592 (chr6:396321)
    (6, 396321): {'African': 0.95, 'European': 0.32, 'East_Asian': 0.98, 'South_Asian': 0.88, 'Native_American': 0.95},
    # MC1R - rs885479 (chr16:89986170)
    (16, 89986170): {'African': 0.90, 'European': 0.42, 'East_Asian': 0.15, 'South_Asian': 0.35, 'Native_American': 0.20},
    # TYRP1 - rs1110400 (chr9:12693077)
    (9, 12693077): {'African': 0.88, 'European': 0.52, 'East_Asian': 0.75, 'South_Asian': 0.65, 'Native_American': 0.70},
    # LCT - rs182549 (chr2:136616755)
    (2, 136616755): {'African': 0.78, 'European': 0.30, 'East_Asian': 0.95, 'South_Asian': 0.65, 'Native_American': 0.92},
    # OCA2 - rs1800401 (chr15:28230367)
    (15, 28230367): {'African': 0.90, 'European': 0.95, 'East_Asian': 0.72, 'South_Asian': 0.85, 'Native_American': 0.78},
    # EDAR additional - rs3749113 (chr2:109513320)
    (2, 109513320): {'African': 0.95, 'European': 0.98, 'East_Asian': 0.08, 'South_Asian': 0.55, 'Native_American': 0.20},
}


def compute_admixture(df: pd.DataFrame, min_markers: int = 5) -> dict | None:
    """Estimate admixture proportions from user SNP data.
    Matches by rsID first, falls back to chr:pos for markers not found by rsID.
    """
    user_snp_map = dict(zip(df['rsid'], df['genotype']))

    # Find which AIMs are present in the user's data by rsID
    present = {}
    for rsid in AIM_MARKERS:
        if rsid not in user_snp_map:
            continue
        gt = user_snp_map[rsid].upper()
        if len(gt) < 2 or '?' in gt or gt[:2] == '--':
            continue
        present[rsid] = gt[:2]

    found_by_rsid = len(present)
    print(f"[Admixture] Found {found_by_rsid}/{len(AIM_MARKERS)} AIMs by rsID", flush=True)

    # Also try chr:pos fallback for markers we didn't find
    user_pos_map = {}
    for _, row in df.iterrows():
        try:
            chrom = str(row['chromosome'])
            pos = int(row['position'])
            gt = str(row['genotype']).upper()
            if len(gt) >= 2 and '?' not in gt and gt[:2] != '--':
                user_pos_map[(chrom, pos)] = gt[:2]
        except (ValueError, KeyError, TypeError):
            continue

    found_by_pos = 0
    for (chrom, pos), freqs in AIM_POSITIONS.items():
        key = (str(chrom), pos)
        if key in user_pos_map:
            gt = user_pos_map[key]
            rsid_for_key = f"chr{chrom}:{pos}"
            if rsid_for_key not in present:
                present[rsid_for_key] = gt
                found_by_pos += 1

    print(f"[Admixture] Found {found_by_pos} more by chr:pos fallback. Total: {len(present)}", flush=True)

    if len(present) < min_markers:
        print(f"[Admixture] Only {len(present)} markers found (< {min_markers} min), skipping", flush=True)
        return None

    # Compute log-likelihood for each population
    log_likes = {}
    for pop in POPS:
        ll = 0.0
        count = 0
        for rsid_or_key, gt in present.items():
            # Get frequencies for this marker
            freqs = AIM_MARKERS.get(rsid_or_key)
            if freqs is None:
                # Try position-based lookup
                if ':' in rsid_or_key:
                    parts = rsid_or_key.replace('chr', '').split(':')
                    if len(parts) == 2:
                        try:
                            freqs = AIM_POSITIONS.get((int(parts[0]), int(parts[1])))
                        except ValueError:
                            continue
            if freqs is None:
                continue

            p = freqs.get(pop)
            if p is None:
                continue
            p = max(0.001, min(0.999, p))
            q = 1.0 - p

            alleles = [c for c in gt if c in 'ACGT']
            if len(alleles) < 2:
                continue
            sorted_alleles = sorted(alleles)
            a1, a2 = sorted_alleles[0], sorted_alleles[1]

            if a1 == a2:
                prob = p * p
            else:
                prob = 2.0 * p * q

            prob = max(1e-10, prob)
            ll += np.log(prob)
            count += 1

        log_likes[pop] = ll / max(count, 1)

    # Softmax to get proportions
    values = np.array([log_likes[p] for p in POPS])
    values = values - np.max(values)
    exp_values = np.exp(values)
    proportions = exp_values / np.sum(exp_values)

    print(f"[Admixture] Result: {dict(zip(POP_LABELS.values(), [round(float(v), 4) for v in proportions]))}", flush=True)

    return {
        POP_LABELS[pop]: round(float(prop), 4)
        for pop, prop in zip(POPS, proportions)
    }
