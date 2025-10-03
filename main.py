"""
Medical Phase Simulator - Application Entry Point

This module serves as the main entry point for the Medical Phase Simulator
application. It starts the FastAPI server with uvicorn in development mode
with hot reload enabled.

Usage:
    python main.py

The server will start on http://localhost:7860 with the following endpoints:
    - / : Frontend interface
    - /health : Health check
    - /process : Image processing API
    - /docs : Interactive API documentation
    - /redoc : Alternative API documentation

Author: Medical Phase Simulator Team
Version: 1.0.0
"""

import uvicorn
import logging

# Configure basic logging for the main module
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info("Starting Medical Phase Simulator server...")
    logger.info("Server will be available at: http://localhost:7860")
    logger.info("API documentation: http://localhost:7860/docs")
    
    uvicorn.run(
        "backend.app:app", 
        host="0.0.0.0", 
        port=7860, 
        reload=True,
        log_level="info"
    )
