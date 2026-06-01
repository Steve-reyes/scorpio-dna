"""Upload routes — accept DNA files, parse, match, return report"""
import os
import uuid
import json
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse

from parser import parse_dna_file, validate_dna
from matcher import match_snps, get_report_summary

router = APIRouter()
UPLOAD_DIR = "/tmp/scorpio-dna-uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_EXTENSIONS = {'.txt', '.csv', '.tsv', '.zip'}

@router.post("/upload")
async def upload_dna(file: UploadFile = File(...)):
    ext = os.path.splitext(file.filename or "dna.txt")[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Unsupported file format: {ext}. Accepted: .txt, .csv, .tsv")

    session_id = uuid.uuid4().hex[:12]
    save_path = os.path.join(UPLOAD_DIR, f"{session_id}_{file.filename}")

    content = await file.read()
    with open(save_path, 'wb') as f:
        f.write(content)

    # Parse
    df = parse_dna_file(save_path)
    if len(df) == 0:
        os.remove(save_path)
        raise HTTPException(status_code=400, detail="No valid SNPs found in file. Is this a 23andMe/AncestryDNA format?")

    validation = validate_dna(df)

    # Match
    results = match_snps(df)
    summary = get_report_summary(results)

    # Clean up uploaded file
    os.remove(save_path)

    return JSONResponse({
        "session_id": session_id,
        "filename": file.filename,
        "validation": validation,
        "report": summary
    })

@router.post("/upload-with-password")
async def upload_with_password(
    file: UploadFile = File(...),
    password: str = Form(...),
):
    # Simple password check
    expected = os.getenv("APP_PASSWORD", "scorpiodna2024")
    if password != expected:
        raise HTTPException(status_code=403, detail="Invalid password")
    return await upload_dna(file)

@router.get("/ping")
async def ping():
    return {"status": "ok", "app": "scorpio-dna"}

@router.get("/stats")
async def stats():
    from matcher import DB_PATH
    import sqlite3
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT category, COUNT(*) FROM reference_snps GROUP BY category")
    rows = c.fetchall()
    conn.close()
    return {"categories": {r[0]: r[1] for r in rows}}
