import json, os
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from app.checker import check_pack, match_registry

app = FastAPI(title="Sabi")
NAFDAC_VERIFY = "https://registration.nafdac.gov.ng"


async def _read(f: UploadFile) -> tuple:
    if not (f.content_type or "").startswith("image/"):
        raise HTTPException(400, "Upload photos (JPG or PNG).")
    data = await f.read()
    if len(data) > 8 * 1024 * 1024:
        raise HTTPException(413, "A photo is over 8 MB. Use a smaller one.")
    return data, f.content_type


@app.get("/api/health")
def health():
    return {"ok": True, "mode": os.getenv("SABI_MODE", "mock")}


@app.post("/api/check")
async def check(photos: list[UploadFile] = File(...)):
    imgs = [await _read(p) for p in photos[:6]]
    try:
        result = check_pack(imgs)
    except Exception as e:
        raise HTTPException(502, f"Check failed: {e}")
    result["verify_url"] = NAFDAC_VERIFY
    return result


@app.post("/api/match")
async def match(pack: str = Form(...), registry: UploadFile = File(...)):
    try:
        return match_registry(json.loads(pack), await _read(registry))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(502, f"Match failed: {e}")


@app.get("/api/diag")
def diag():
    import sys

    import openai
    from openai import OpenAI

    from app.checker import _cfg

    try:
        base, key, model = _cfg()
    except Exception as e:
        return {"config_error": str(e)}
    out = {"provider": os.getenv("SABI_PROVIDER", "meta"), "base_url": base, "model": model, "mode": os.getenv("SABI_MODE", "mock"), "key_looks_like_meta": key.startswith("LLM_"), "key_length": len(key), "sdk": openai.__version__, "python": sys.version.split()[0]}
    c = OpenAI(base_url=base, api_key=key)
    try:
        out["models"] = [x.id for x in c.models.list()][:40]
    except Exception as e:
        out["models_error"] = str(e)[:200]
    try:
        r = c.chat.completions.create(model=model, messages=[{"role": "user", "content": "Say OK"}])
        out["test_call"] = "ok: " + (r.choices[0].message.content or "")[:40]
    except Exception as e:
        out["test_call"] = "error: " + str(e)[:300]
    return out


@app.get("/play")
def play():
    return FileResponse("static/play.html")


@app.get("/")
def home():
    return FileResponse("static/index.html")


app.mount("/static", StaticFiles(directory="static"), name="static")
