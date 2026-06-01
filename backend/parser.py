"""Parse raw DNA files (23andMe, AncestryDNA, MyHeritage formats)"""
import pandas as pd
import re

def parse_dna_file(filepath: str) -> pd.DataFrame:
    """Parse a raw DNA file into a DataFrame with columns: rsid, chromosome, position, genotype."""
    lines = []
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#') or line.startswith('[') or line.startswith('@'):
                continue
            parts = re.split(r'\s+', line)
            if len(parts) >= 4 and parts[0].startswith('rs'):
                rsid, chrom, pos, genotype = parts[0], parts[1], parts[2], parts[3].upper().strip()
                # Strip out deletion/insertion notation — normalize to ACTG-
                genotype = re.sub(r'[^ACGT\-]', '', genotype)
                if len(genotype) in (1, 2):
                    lines.append((rsid, chrom, int(pos), genotype))
    df = pd.DataFrame(lines, columns=['rsid', 'chromosome', 'position', 'genotype'])
    return df

def validate_dna(df: pd.DataFrame) -> dict:
    """Basic validation of parsed DNA data."""
    total = len(df)
    unique_rsids = df['rsid'].nunique()
    missing = df['genotype'].isna().sum()
    return {
        "total_snps": total,
        "unique_snps": unique_rsids,
        "missing_genotypes": int(missing)
    }
