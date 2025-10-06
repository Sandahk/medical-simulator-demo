"""
Medical Phase Simulator Backend API

This module provides a FastAPI backend for processing medical images
with arterial and venous phase simulation. It serves both the API endpoints
and the frontend static files.

Author: Medical Phase Simulator Team
Version: 1.0.0
"""

import logging
import base64
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from typing import Literal
from pathlib import Path

from backend.processing import (
    load_image, simulate_arterial, simulate_venous, to_png_bytes
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # Console output
        logging.FileHandler('backend.log')  # File output
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="MedTech Mini Backend", 
    version="1.0.0",
    description="Medical image processing API with arterial and venous phase simulation",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS middleware
# Note: In production, restrict allow_origins to specific domains
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)
logger.info("CORS middleware configured")

# Configure static file serving
PROJECT_ROOT = Path(__file__).resolve().parents[1]
FRONTEND_DIR = PROJECT_ROOT / "frontend"

# Mount frontend static files (CSS, JS, images)
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


@app.get("/", tags=["Frontend"])
def index():
    """
    Serve the main frontend page.
    
    Returns:
        FileResponse: The index.html file for the medical phase simulator frontend
    """
    logger.info("Serving frontend index page")
    return FileResponse(FRONTEND_DIR / "index.html")


@app.get("/health", tags=["Health"])
def health():
    """
    Health check endpoint for monitoring and load balancers.
    
    Returns:
        dict: Status object with "ok" status
    """
    logger.debug("Health check requested")
    return {"status": "ok"}

@app.post("/process", tags=["Processing"])
async def process_image(
    file: UploadFile = File(...),
    phase: Literal["arterial", "venous"] = Form(...),
):
    """
    Process a medical image with arterial or venous phase simulation.
    
    This endpoint accepts an image file and applies medical phase simulation
    algorithms to enhance the image for diagnostic purposes.
    
    Args:
        file (UploadFile): Image file (JPG/PNG format)
        phase (str): Processing phase - either "arterial" or "venous"
        
    Returns:
        dict: Processing result containing:
            - phase: The applied processing phase
            - format: Output image format (always "png")
            - processed_image_base64: Base64-encoded processed image
            
    Raises:
        HTTPException: 400 if file format is not supported
        HTTPException: 500 if processing fails
        
    Example:
        POST /process
        Content-Type: multipart/form-data
        file: [image file]
        phase: arterial
    """
    logger.info(f"Processing image request: filename={file.filename}, content_type={file.content_type}, phase={phase}")
    
    # Validate file type
    if file.content_type not in {"image/jpeg", "image/png", "image/jpg"}:
        logger.warning(f"Invalid file type rejected: {file.content_type}")
        raise HTTPException(status_code=400, detail="Only JPG/PNG images are supported.")
    
    try:
        # Read and process image
        img_bytes = await file.read()
        logger.info(f"Image loaded: {len(img_bytes)} bytes")
        
        pil = load_image(img_bytes)
        logger.debug(f"PIL image created: {pil.size} pixels, mode={pil.mode}")
        
        # Apply phase-specific processing
        if phase == "arterial":
            logger.info("Applying arterial phase processing")
            out = simulate_arterial(pil)
        else:
            logger.info("Applying venous phase processing")
            out = simulate_venous(pil)
        
        # Convert to PNG
        png = to_png_bytes(out)
        logger.info(f"Image processed successfully: {len(png)} bytes output")
        
        # Encode to base64
        b64_data = base64.b64encode(png).decode()
        logger.debug("Image encoded to base64 successfully")
        
        return {"phase": phase, "format": "png", "processed_image_base64": b64_data}
        
    except Exception as e:
        logger.error(f"Error processing image: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error during image processing.")
