"""Upload routes — accept DNA files, parse, match, return report"""
import os
import uuid
import json
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse

from parser import parse_dna_file, validate_dna
from matcher import match_snps, get_report_summary
from admixture import compute_admixture

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

    # Save user rsids for AIM analysis (check which common AIMs exist)
    user_rsids = set(df['rsid'].tolist())
    from admixture import AIM_MARKERS as aim_check
    found_aims = [r for r in aim_check if r in user_rsids]
    print(f"[AIM-DEBUG] User has {len(found_aims)}/{len(aim_check)} AIM rsIDs: {found_aims}", flush=True)

    # Also check top 50 reference DB rsids as potential AIMs
    import sqlite3
    conn = sqlite3.connect('/app/data/scorpio_dna.db')
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT rsid FROM reference_snps")
    ref_rsids = set(r[0] for r in cursor.fetchall())
    conn.close()
    common_rsids = ref_rsids & user_rsids
    print(f"[AIM-DEBUG] User has {len(common_rsids)}/{len(ref_rsids)} reference DB rsids", flush=True)
    # Sample some
    sample = list(common_rsids)[:20]
    print(f"[AIM-DEBUG] Sample common rsids: {sample}", flush=True)

    # Compute admixture
    print("[Admixture] Starting admixture computation...", flush=True)
    admixture = compute_admixture(df)
    print(f"[Admixture] Result: {admixture}", flush=True)

    # Clean up uploaded file
    os.remove(save_path)

    return JSONResponse({
        "session_id": session_id,
        "filename": file.filename,
        "validation": validation,
        "report": summary,
        "admixture": admixture,
        "total_snps": validation.get("total_snps", len(df)),
        "matched_snps": summary["total_matched"],
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
