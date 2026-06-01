"""Scorpio DNA — FastAPI Backend"""
import os
import json
import uuid
from datetime import datetime
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from dotenv import load_dotenv

from parser import parse_dna_file, validate_dna
from matcher import match_snps, get_report_summary
from reporter import generate_pdf_report

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
    # Password check
    expected = os.getenv("APP_PASSWORD", "scorpiodna2024")
    if password != expected:
        raise HTTPException(status_code=403, detail="Invalid password")

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
            txt_files = [f for f in z.namelist() if f.endswith(('.txt', '.csv', '.tsv'))]
            if not txt_files:
                raise HTTPException(status_code=400, detail="No text files found in zip archive")
            content = z.read(txt_files[0])
            save_path = os.path.join(UPLOAD_DIR, f"{session_id}_{txt_files[0]}")

    with open(save_path, 'wb') as f:
        f.write(content)

    df = parse_dna_file(save_path)
    os.remove(save_path)

    if len(df) == 0:
        raise HTTPException(status_code=400, detail="No valid SNPs found")

    validation = validate_dna(df)
    results = match_snps(df)
    summary = get_report_summary(results)

    return JSONResponse({
        "session_id": session_id,
        "filename": file.filename,
        "validation": validation,
        "report": summary,
        "total_snps": len(df),
        "matched_snps": len(results),
    })

@app.post("/api/report/pdf")
async def download_pdf(file: UploadFile = File(...), password: str = Form("")):
    expected = os.getenv("APP_PASSWORD", "scorpiodna2024")
    if password != expected:
        raise HTTPException(status_code=403, detail="Invalid password")

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
