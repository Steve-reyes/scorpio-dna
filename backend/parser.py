"""Parse raw DNA files (23andMe, AncestryDNA, MyHeritage formats)"""
import pandas as pd
import re

def parse_dna_file(filepath: str) -> pd.DataFrame:
    """Parse a raw DNA file into a DataFrame with columns: rsid, chromosome, position, genotype."""
    lines = []
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    # Handle different line endings
    content = content.replace('\r\n', '\n').replace('\r', '\n')
    file_lines = content.split('\n')

    # Detect format
    format_type = _detect_format(file_lines)
    print(f"[Parser] Detected format: {format_type}")

    for line in file_lines:
        line = line.strip()
        if not line or line.startswith('#') or line.startswith('[') or line.startswith('@') or line.startswith('---'):
            continue

        if format_type == 'ancestry' or format_type == 'myheritage':
            # CSV format: rsid,chromosome,position,allele1,allele2
            csv_parts = re.split(r'[,\t]', line)
            if len(csv_parts) >= 5 and csv_parts[0].startswith('rs'):
                rsid = csv_parts[0].strip()
                chrom = csv_parts[1].strip()
                pos = csv_parts[2].strip()
                a1 = csv_parts[3].strip().upper()
                a2 = csv_parts[4].strip().upper()
                # Clean alleles
                a1 = re.sub(r'[^ACGT\-]', '', a1)
                a2 = re.sub(r'[^ACGT\-]', '', a2)
                # Handle heterozygous notation: AT means A and T
                if len(a1) == 1 and len(a2) == 1:
                    # Sort alphabetically for consistent matching
                    genotype = ''.join(sorted(a1 + a2))
                    try:
                        lines.append((rsid, chrom, int(pos), genotype))
                    except ValueError:
                        pass
        else:
            # Tab/space format (23andMe): rsid\tchrom\tpos\tgenotype
            parts = re.split(r'\s+', line)
            if len(parts) >= 4 and parts[0].startswith('rs'):
                rsid = parts[0].strip()
                chrom = parts[1].strip()
                pos = parts[2].strip()
                genotype = parts[3].strip().upper()
                # Clean genotype
                genotype = re.sub(r'[^ACGT\-]', '', genotype)
                if len(genotype) == 2:
                    # Sort alleles for consistency
                    genotype = ''.join(sorted(genotype))
                    try:
                        lines.append((rsid, chrom, int(pos), genotype))
                    except ValueError:
                        pass

    df = pd.DataFrame(lines, columns=['rsid', 'chromosome', 'position', 'genotype'])
    print(f"[Parser] Parsed {len(df)} SNPs from {len(file_lines)} lines")
    return df

def _detect_format(lines: list) -> str:
    """Detect DNA file format by examining first 20 data lines."""
    data_lines = []
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#') or line.startswith('[') or line.startswith('@'):
            continue
        data_lines.append(line)
        if len(data_lines) >= 20:
            break

    if not data_lines:
        return '23andme'  # default

    # Check for CSV format: comma-separated with rsid as first field
    for line in data_lines:
        if ',' in line:
            parts = line.split(',')
            # Ancestry: rsid,chrom,position,allele1,allele2
            if len(parts) >= 5 and parts[0].strip().startswith('rs'):
                return 'ancestry'
            # Could also be MyHeritage format
            if len(parts) >= 4 and parts[0].strip().startswith('rs'):
                return 'myheritage'

    # Check for tab-separated (23andMe format)
    for line in data_lines:
        parts = re.split(r'\s+', line)
        if len(parts) >= 4 and parts[0].startswith('rs') and len(parts[3]) in (1, 2):
            return '23andme'

    return '23andme'  # default

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
