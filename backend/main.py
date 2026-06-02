"""Scorpio DNA — FastAPI Backend"""
import os
import json
import uuid
from datetime import datetime
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from dotenv import load_dotenv
import pandas as pd

from parser import parse_dna_file, validate_dna
from matcher import match_snps, get_report_summary
from reporter import generate_pdf_report
from admixture import compute_admixture

load_dotenv()

app = FastAPI(title="Scorpio DNA", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "/tmp/scorpio-dna-uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
ALLOWED_EXTENSIONS = {'.txt', '.csv', '.tsv', '.zip'}

@app.get("/api/ping")
async def ping():
    return {"status": "ok", "app": "scorpio-dna", "version": "1.0.0"}

@app.get("/api/stats")
async def stats():
    import sqlite3
    from matcher import DB_PATH
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT category, COUNT(*) FROM reference_snps GROUP BY category")
    rows = c.fetchall()
    conn.close()
    return {"categories": {r[0]: r[1] for r in rows}, "total": sum(r[1] for r in rows)}

@app.post("/api/upload")
async def upload_dna(file: UploadFile = File(...), password: str = Form("")):
    ext = os.path.splitext(file.filename or "dna.txt")[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Unsupported format: {ext}")

    session_id = uuid.uuid4().hex[:12]
    save_path = os.path.join(UPLOAD_DIR, f"{session_id}_{file.filename}")

    content = await file.read()

    # Handle zip — extract first txt/csv
    if ext == '.zip':
        import zipfile
        import io
        with zipfile.ZipFile(io.BytesIO(content)) as z:
            # Accept any text-like file inside zip
            txt_files = [f for f in z.namelist() if not f.startswith('__') and not f.startswith('.') and not f.endswith(('.jpg','.png','.gif','.pdf'))]
            if not txt_files:
                # Try all files
                txt_files = z.namelist()
            print(f"[Debug] Zip contains: {z.namelist()}, picked: {txt_files[0] if txt_files else 'none'}")
            if not txt_files:
                raise HTTPException(status_code=400, detail="No text files found in zip archive")
            content = z.read(txt_files[0])
            save_path = os.path.join(UPLOAD_DIR, f"{session_id}_{txt_files[0]}")

    print(f"[Debug] Saving to {save_path}, size={len(content)}")
    with open(save_path, 'wb') as f:
        f.write(content)

    import traceback
    try:
        df = parse_dna_file(save_path)
        print(f"[Debug] Parsed {len(df)} SNPS")
        # Debug: check which ancestry rsids are in the file
        ancestry_rsids = [
            'rs28358584','rs2854128','rs28357980','rs28357984','rs41378955',
            'rs41458746','rs2246754','rs2853495','rs193302980','rs386829035',
            'rs28357972','rs28358575','rs2857285','rs16980426','rs16979907',
            'rs9786246','rs2032595','rs13447352','rs9785958','rs9785969',
            'rs9341278','rs2534636','rs2032636','rs17269816','rs9786193',
            'rs9786139','rs2032640','rs9786869','rs9786054','rs2032631',
            'rs9785916','rs9785716','rs9786153','rs13275494'
        ]
        file_rsids = set(df['rsid'].tolist())
        found_ancestry = [r for r in ancestry_rsids if r in file_rsids]
        print(f"[Debug] Found ancestry rsids in file: {len(found_ancestry)}/{len(ancestry_rsids)}: {found_ancestry}")
        # Also list actual MT and Y chromosome rsids in file
        chroms = df['chromosome'].astype(str).str.upper().unique()
        print(f"[Debug] Chromosomes in file: {sorted(chroms)}")
        mt_rsids = df[df['chromosome'].astype(str).str.upper().isin(['MT', 'M', '25', '26'])]['rsid'].tolist()
        y_rsids = df[df['chromosome'].astype(str).str.upper().isin(['Y', '24'])]['rsid'].tolist()
        print(f"[Debug] MT-like ({len(mt_rsids)}): {mt_rsids[:50]}")
        print(f"[Debug] Y-like ({len(y_rsids)}): {y_rsids[:50]}")
    except Exception as e:
        print(f"[Debug] Parse error: {e}")
        traceback.print_exc()
        df = pd.DataFrame()
    os.remove(save_path)

    if len(df) == 0:
        raise HTTPException(status_code=400, detail="No valid SNPs found")

    validation = validate_dna(df)
    results = match_snps(df)
    summary = get_report_summary(results)

    # Compute admixture
    print(f"[Admixture] Starting admixture computation...", flush=True)
    user_rsids = set(df['rsid'].tolist())
    from admixture import AIM_MARKERS as aim_check
    found_aims = [r for r in aim_check if r in user_rsids]
    print(f"[Admixture] User has {len(found_aims)}/{len(aim_check)} AIM rsIDs", flush=True)
    admixture = compute_admixture(df)
    print(f"[Admixture] Result: {admixture}", flush=True)

    return JSONResponse({
        "session_id": session_id,
        "filename": file.filename,
        "validation": validation,
        "report": summary,
        "admixture": admixture,
        "total_snps": len(df),
        "matched_snps": len(results),
    })

@app.post("/api/report/pdf")
async def download_pdf(file: UploadFile = File(...), password: str = Form("")):
    ext = os.path.splitext(file.filename or "dna.txt")[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Unsupported format: {ext}")

    session_id = uuid.uuid4().hex[:12]
    save_path = os.path.join(UPLOAD_DIR, f"pdf_{session_id}_{file.filename}")

    content = await file.read()
    if ext == '.zip':
        import zipfile, io
        with zipfile.ZipFile(io.BytesIO(content)) as z:
            txt_files = [f for f in z.namelist() if f.endswith(('.txt', '.csv', '.tsv'))]
            if not txt_files:
                raise HTTPException(status_code=400, detail="No text files found in zip")
            content = z.read(txt_files[0])

    with open(save_path, 'wb') as f:
        f.write(content)

    df = parse_dna_file(save_path)
    os.remove(save_path)

    results = match_snps(df)
    summary = get_report_summary(results)
    pdf_bytes = generate_pdf_report(summary)

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=scorpio-dna-report.pdf"}
    )
