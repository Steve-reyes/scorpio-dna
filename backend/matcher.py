"""Match parsed SNPs against reference database"""
import sqlite3
import os
import pandas as pd

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "scorpio_dna.db")

def match_snps(df: pd.DataFrame) -> list:
    """Match parsed DNA against reference DB. Returns list of matched conditions."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM reference_snps")
    columns = [desc[0] for desc in cursor.description]
    ref_rows = cursor.fetchall()
    conn.close()

    # Build rsid lookup
    ref_by_rsid = {}
    for row in ref_rows:
        r = dict(zip(columns, row))
        rsid = r['rsid']
        if rsid not in ref_by_rsid:
            ref_by_rsid[rsid] = []
        ref_by_rsid[rsid].append(r)

    # User data lookups
    user_snp_map = dict(zip(df['rsid'], df['genotype']))

    results = []
    matched_rsids = set()
    seen_matches = set()

    for rsid, conditions in ref_by_rsid.items():
        if rsid not in user_snp_map:
            continue

        user_genotype = user_snp_map[rsid].upper()
        for condition in conditions:
            match_key = (rsid, condition['trait'])
            if match_key in seen_matches:
                continue
            seen_matches.add(match_key)
            matched_rsids.add(rsid)

            risk_geno = condition['risk_genotype'].upper()
            risk_allele = condition['risk_allele'].upper()

            # Determine match
            is_match = False
            result = "typical"
            note = condition['note'] or ""

            if 'D' in risk_geno or 'I' in risk_geno:
                if user_genotype == risk_geno:
                    is_match = True
                    result = condition['risk_level']
            elif '?' in user_genotype or len(user_genotype) < 2:
                continue
            else:
                if user_genotype == risk_geno:
                    is_match = True
                    result = condition['risk_level']
                elif risk_allele and risk_allele in user_genotype:
                    is_match = True
                    result = "elevated"
                else:
                    is_match = True
                    result = "typical"

            if is_match:
                geno_display = f"{user_genotype}"
                status_text = {
                    "high": "Higher Risk",
                    "elevated": "Elevated",
                    "typical": "Typical",
                    "carrier": "Carrier",
                    "defining": "Detected",
                }.get(result, "Typical")

                color = {
                    "high": "red",
                    "elevated": "amber",
                    "typical": "green",
                    "carrier": "blue",
                    "defining": "purple",
                }.get(result, "gray")

                results.append({
                    "rsid": rsid,
                    "category": condition['category'],
                    "trait": condition['trait'],
                    "description": condition['description'],
                    "summary": condition['summary'],
                    "health_tips": condition.get('health_tips', ''),
                    "risk_factors": condition.get('risk_factors', ''),
                    "if_untreated": condition.get('if_untreated', ''),
                    "genotype": geno_display,
                    "risk_allele": risk_allele,
                    "risk_genotype": risk_geno,
                    "result": result,
                    "status_text": status_text,
                    "color": color,
                    "population_freq": condition['population_freq'],
                    "study_url": condition['study_url'],
                    "note": note
                })

    return results


def get_report_summary(results: list) -> dict:
    """Build summary report by category."""
    categories = {}
    for r in results:
        cat = r['category']
        if cat not in categories:
            categories[cat] = {"count": 0, "risk": [], "high_count": 0}
        categories[cat]["count"] += 1
        categories[cat]["risk"].append(r["result"])
        if r["result"] in ("high", "carrier"):
            categories[cat]["high_count"] += 1

    return {
        "total_matched": len(results),
        "categories": categories,
        "results": results
    }
