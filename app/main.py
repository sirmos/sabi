import os
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from app.checker import check_pack

app = FastAPI(title="Sabi")
NAFDAC_VERIFY = "https://registration.nafdac.gov.ng"


@app.get("/api/health")
def health():
    return {"ok": True, "mode": os.getenv("SABI_MODE", "mock")}


@app.post("/api/check")
async def check(photo: UploadFile = File(...)):
    if not (photo.content_type or "").startswith("image/"):
        raise HTTPException(400, "Upload a photo (JPG or PNG).")
    data = await photo.read()
    if len(data) > 8 * 1024 * 1024:
        raise HTTPException(413, "Photo is over 8 MB. Use a smaller one.")
    try:
        result = check_pack(data, photo.content_type)
    except Exception as e:
        raise HTTPException(502, f"Check failed: {e}")
    result["verify_url"] = NAFDAC_VERIFY
    return result


@app.get("/")
def home():
    return FileResponse("static/index.html")


app.mount("/static", StaticFiles(directory="static"), name="static")
