# Scorpio DNA — Build Plan

## Overview
Upload raw DNA data (23andMe/AncestryDNA format) → parse 600k+ SNPs → match against public reference databases → generate health/trait/carrier/drug-response report.

## Architecture
```
User → Browser Upload (.txt/.zip) → FastAPI Parse → Pandas Match → Report JSON → Web Dashboard + PDF
```

## Tech Stack

| Component | Choice | Why |
|-----------|--------|-----|
| Backend | FastAPI (Python) | pandas integration, fast file handling |
| Parser | pandas + custom parser | handles 600k rows in <2s |
| Reference DB | SQLite, pre-loaded with GWAS Catalog + ClinVar | no external deps, fits in 200MB |
| Frontend | React + Vite + Tailwind + iOS HIG theme | matches existing leadscraper style |
| Reports | Plotly charts + PDF via weasyprint | interactive + downloadable |
| Auth | simple passkey (same as leadscraper) | keep it simple |
| Deploy | Docker Compose + nginx + sslip.io + certbot | same stack as everything else |

## Data Pipeline

### Step 1 — Upload & Parse
- accept 23andMe format (text/tsv) and AncestryDNA (txt/csv)
- validate: checksum, line count, column headers
- parse into pandas DataFrame: [rsid, chromosome, position, genotype]
- filter out non-SNP lines (comments, headers)
- store raw + parsed in SQLite session

### Step 2 — Reference Database
- **GWAS Catalog** — ~300k SNP-trait associations, free to download
- **ClinVar** — ~200k clinical variants, NIH open data
- **SNPedia dump** (if available on open snapshots) — adds ~50k health-specific entries
- store in SQLite with indexes: rsid → trait_name, risk_allele, description, confidence, study_url

### Step 3 — Match & Score
- left join: parsed SNPs × reference DB on rsid
- for each match, compare your genotype against the risk allele
- categorize into risk levels: normal / elevated / high / carrier

### Step 4 — Report Categories

| Category | Examples | # of Conditions |
|----------|----------|-----------------|
| 🩺 Health | heart disease, diabetes, Alzheimer's, cancer risks | 25-30 |
| 🧬 Carrier | cystic fibrosis, sickle cell, Tay-Sachs | 20-25 |
| 💊 Drug Response | warfarin sensitivity, caffeine metabolism, statins | 15-20 |
| 🧠 Traits | eye color, lactose intolerance, earwax type, muscle type | 15-20 |
| 🥗 Nutrition | folate metabolism, vitamin D, iron levels | 10-15 |
| 🏃 Fitness | endurance potential, injury risk, recovery | 5-10 |

### Step 5 — Display
- interactive dashboard with category tabs
- per-condition card: condition name, your risk, population avg, study link
- risk meter visualization (low → moderate → high)
- PDF download of full report
- disclaimer banner: "For educational purposes only — not medical advice"

## UI Design (iOS HIG)
- frosted glass sidebar → category navigation
- pill button tabs per category
- condition cards with SF Pro font, iOS system colors
- risk meter with gradient (#34C759 → #FF9500 → #FF3B30)
- scorpion logo + faded watermark (same as leadscraper theme)

## File Structure
```
scorpio-dna/
├── docker-compose.yml
├── nginx.conf
├── Dockerfile.backend
├── Dockerfile.frontend
├── .env.example
├── README.md
├── PLAN.md
├── backend/
│   ├── requirements.txt
│   ├── main.py
│   ├── parser.py          # DNA file parser
│   ├── matcher.py         # rsID → condition matching
│   ├── reporter.py        # PDF + JSON report builder
│   ├── models.py          # SQLAlchemy models
│   ├── routes/
│   │   ├── upload.py      # file upload endpoint
│   │   ├── report.py      # report generation endpoint
│   │   └── db.py          # reference DB endpoints
│   ├── data/
│   │   ├── seed_gwas.py   # GWAS catalog importer
│   │   ├── seed_clinvar.py# ClinVar importer
│   │   └── seed_all.py    # full DB builder
│   └── templates/
│       └── report.html    # PDF template
└── frontend/
    ├── package.json
    ├── next.config.js / vite.config.ts
    ├── src/
    │   ├── app/
    │   │   ├── page.tsx        # upload page
    │   │   ├── report/
    │   │   │   └── page.tsx    # report dashboard
    │   │   └── layout.tsx
    │   ├── components/
    │   │   ├── FileUploader.tsx
    │   │   ├── CategoryTabs.tsx
    │   │   ├── ConditionCard.tsx
    │   │   ├── RiskMeter.tsx
    │   │   └── PDFDownload.tsx
    │   └── lib/
    │       ├── api.ts
    │       └── theme.ts
    └── public/
```

## Phases

### Phase 1 — Core Pipeline (MVP)
- [ ] create scorpio-dna repo on GitHub
- [ ] FastAPI server with upload endpoint
- [ ] 23andMe file parser
- [ ] GWAS Catalog → SQLite reference DB
- [ ] basic match → return JSON of matching conditions
- [ ] Docker Compose setup (backend only)
- [ ] test with real raw DNA file

### Phase 2 — Web UI
- [ ] React/Vite frontend with iOS HIG theme
- [ ] file upload UI with drag-and-drop
- [ ] category tabs + condition cards
- [ ] risk meter visualization
- [ ] scorpion branding

### Phase 3 — PDF Reports
- [ ] PDF generation with weasyprint
- [ ] condition breakdown per category
- [ ] disclaimer pages

### Phase 4 — Production
- [ ] nginx + SSL via certbot
- [ ] deploy on IONOS
- [ ] add ClinVar data
- [ ] error handling + edge case polish

## Reference Data Sources

| Source | Size | Cost | Coverage |
|--------|------|------|----------|
| GWAS Catalog (NHGRI-EBI) | ~300k associations | free | traits, diseases, drug response |
| ClinVar (NCBI/NIH) | ~200k variants | free | clinical conditions, carrier status |
| SNPedia (if available) | ~50k health SNPs | ~free (dumps exist) | most popular health SNPs |
| OpenSNP | ~10k users' data | free | community genotype data |

Total DB size estimate: ~150-300MB SQLite.

## Deployment

| Service | Details |
|---------|---------|
| Domain | `scorpio-dna.212.227.153.56.sslip.io` |
| Containers | backend + nginx (1 container initially) |
| SSL | certbot auto-renew |
| Memory | ~200MB RAM for backend + SQLite |

## Disclaimer
This is a **educational** tool. Reports are not FDA-approved, not diagnostic, not medical advice. Users should consult a doctor before making health decisions based on results.

---

*Scorpio — June 2026*
