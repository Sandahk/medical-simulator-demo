#!/usr/bin/env python3
"""
Medical Phase Simulator - Command Line Client

This script provides a command-line interface for the Medical Phase Simulator
backend. It allows users to process medical images from the command line,
uploading images to the backend and saving the processed results.

Features:
    - Support for both arterial and venous phase processing
    - Configurable backend URL
    - Automatic file format conversion
    - Error handling and validation

Usage:
    python client_process.py --image path/to/image.jpg --phase arterial
    python client_process.py --image scan.png --phase venous --out result.png

Author: Medical Phase Simulator Team
Version: 1.0.0
"""

import argparse
import pathlib
import requests
import base64
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def main():
    """
    Main function for the command-line client.
    
    Parses command-line arguments, validates the input image, sends it to the
    backend for processing, and saves the result to the specified output file.
    """
    ap = argparse.ArgumentParser(
        description="Process medical images with arterial or venous phase simulation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --image scan.jpg --phase arterial
  %(prog)s --image ct_scan.png --phase venous --out venous_result.png
  %(prog)s --url http://remote-server:7860 --image local_image.jpg
        """
    )
    ap.add_argument("--url", default="http://127.0.0.1:7860", 
                   help="Backend base URL (default: %(default)s)")
    ap.add_argument("--image", required=True, 
                   help="Path to input image (JPG/PNG format)")
    ap.add_argument("--phase", choices=["arterial", "venous"], default="venous",
                   help="Processing phase (default: %(default)s)")
    ap.add_argument("--out", default="processed.png", 
                   help="Output PNG file (default: %(default)s)")
    args = ap.parse_args()

    # Validate input image path
    img_path = pathlib.Path(args.image)
    if not img_path.exists():
        logger.error(f"Image file '{img_path}' not found")
        sys.exit(1)
    
    if not img_path.is_file():
        logger.error(f"'{img_path}' is not a file")
        sys.exit(1)
        
    logger.info(f"Processing {img_path} with {args.phase} phase...")
    logger.info(f"Backend URL: {args.url}")

    # Prepare request
    endpoint = args.url.rstrip("/") + "/process"
    files = {"file": (img_path.name, img_path.read_bytes(), "image/jpeg")}
    data = {"phase": args.phase}
    
    try:
        # Send request to backend
        logger.info(f"Sending request to {endpoint}")
        r = requests.post(endpoint, files=files, data=data, timeout=30)
        r.raise_for_status()
        
        # Process response
        response_data = r.json()
        b64_data = response_data["processed_image_base64"]
        
        # Save result
        with open(args.out, "wb") as f:
            f.write(base64.b64decode(b64_data))
            
        logger.info(f"Successfully saved processed image to {args.out}")
        print(f"Processing complete! Saved to: {args.out}")
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Network error: {e}")
        print(f"Network error: {e}")
        sys.exit(1)
    except KeyError as e:
        logger.error(f"Invalid response format: {e}")
        print(f"Invalid response from server: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
