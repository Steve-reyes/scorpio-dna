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

    for line in file_lines:
        line = line.strip()
        if not line or line.startswith('#') or line.startswith('[') or line.startswith('@') or line.startswith('---'):
            continue

        # Split on whitespace OR commas
        parts = re.split(r'[\t, ]+', line)

        # Must start with rs
        if not parts[0].startswith('rs'):
            continue

        try:
            rsid = parts[0].strip()
            chrom = parts[1].strip()
            pos = int(parts[2].strip())
        except (IndexError, ValueError):
            continue

        # --- 5-part format (AncestryDNA / MyHeritage) ---
        # rsid, chrom, pos, allele1, allele2
        if len(parts) >= 5:
            a1 = re.sub(r'[^ACGT\-]', '', parts[3].strip().upper())
            a2 = re.sub(r'[^ACGT\-]', '', parts[4].strip().upper())
            if len(a1) == 1 and len(a2) == 1:
                genotype = ''.join(sorted(a1 + a2))
                lines.append((rsid, chrom, pos, genotype))
                continue

        # --- 4-part format (23andMe standard) ---
        # rsid, chrom, pos, genotype
        # Also handles: rsid, chrom, pos, genotype, extras (ignore extras)
        if len(parts) >= 4:
            genotype = re.sub(r'[^ACGT\-]', '', parts[3].strip().upper())
            if len(genotype) == 2:
                genotype = ''.join(sorted(genotype))
                lines.append((rsid, chrom, pos, genotype))
                continue
            # Handle single-letter genotype (unlikely but possible)
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
