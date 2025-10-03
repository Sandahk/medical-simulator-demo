# backend/app.py
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from typing import Literal
from pathlib import Path

from backend.processing import (
    load_image, simulate_arterial, simulate_venous, to_png_bytes
)

app = FastAPI(title="MedTech Mini Backend", version="1.0.0")

# (Optional) in dev you can leave CORS = "*" — when serving frontend via FastAPI,
# you can remove/limit this.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

# --- Serve the frontend folder as static files ---
PROJECT_ROOT = Path(__file__).resolve().parents[1]
FRONTEND_DIR = PROJECT_ROOT / "frontend"

# /static/* will serve CSS/JS assets
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

# / -> serve index.html
@app.get("/")
def index():
    return FileResponse(FRONTEND_DIR / "index.html")
# -------------------------------------------------

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/process")
async def process_image(
    file: UploadFile = File(...),
    phase: Literal["arterial", "venous"] = Form(...),
):
    if file.content_type not in {"image/jpeg", "image/png", "image/jpg"}:
        raise HTTPException(status_code=400, detail="Only JPG/PNG images are supported.")
    img_bytes = await file.read()
    pil = load_image(img_bytes)
    out = simulate_arterial(pil) if phase == "arterial" else simulate_venous(pil)
    png = to_png_bytes(out)
    import base64
    return {"phase": phase, "format": "png", "processed_image_base64": base64.b64encode(png).decode()}
