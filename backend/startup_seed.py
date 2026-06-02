"""Run on container first start to seed additional data into the volume."""
import os
import sqlite3
import subprocess
import sys

DB_PATH = "/app/data/scorpio_dna.db"

def needs_seeding():
    """Check if the DB has been fully seeded."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM reference_snps")
    count = c.fetchone()[0]
    conn.close()
    # If we only have the core 151 (117 + 34), we need GWAS expansion
    return count <= 160

def main():
    if not needs_seeding():
        print("DB already fully seeded — skipping startup seeding.")
        return

    print(f"DB has minimal entries — expanding from GWAS catalog...")
    
    # Run process_gwas to expand from GWAS TSV files
    gwas_dirs = ["/tmp/gwas"]
    for d in gwas_dirs:
        if os.path.exists(d) and any(f.endswith(".tsv") for f in os.listdir(d)):
            print(f"Found GWAS data in {d}")
            break
    else:
        # Try extracting from zip
        zip_path = "/app/gwas-associations.zip"
        if os.path.exists(zip_path):
            print("Extracting GWAS zip...")
            subprocess.run(["unzip", "-o", "-q", zip_path, "-d", "/tmp/gwas"], check=True)
        else:
            print("No GWAS data found — skipping expansion.")
            return

    print("Running process_gwas...")
    result = subprocess.run([sys.executable, "/app/process_gwas.py"], capture_output=True, text=True)
    print(result.stdout[-200:] if result.stdout else result.stderr[-200:])

    # Run metadata seeds
    for script in ["seed_risk_factors.py", "seed_tips.py", "seed_untreated.py", "gen_summaries.py"]:
        path = f"/app/{script}"
        if os.path.exists(path):
            print(f"Running {script}...")
            subprocess.run([sys.executable, path], capture_output=True)

    print("Startup seeding complete.")

if __name__ == "__main__":
    main()
