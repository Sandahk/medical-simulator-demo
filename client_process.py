#!/usr/bin/env python3
"""
Client for the MedTech Mini Backend.
Uploads an image and phase ("arterial" or "venous") to the /process endpoint
and saves the returned PNG.
"""

import argparse
import pathlib
import requests
import base64
import sys

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default="http://127.0.0.1:7860", help="Backend base URL")
    ap.add_argument("--image", help="Path to input image (JPG/PNG)")
    ap.add_argument("--phase", choices=["arterial", "venous"], default="venous")
    ap.add_argument("--out", default="processed2.png", help="Output PNG file")
    args = ap.parse_args()

    # If no image passed, fall back to default CTA_Slice.jpg in current dir
    if args.image:
        img_path = pathlib.Path(args.image)
    else:
        img_path = pathlib.Path("CTA_Slice.jpg")
        if not img_path.exists():
            print("[!] No --image provided and default CTA_Slice.jpg not found.", file=sys.stderr)
            sys.exit(1)
        print(f"[*] Using default image: {img_path}")

    endpoint = args.url.rstrip("/") + "/process"

    files = {"file": (img_path.name, img_path.read_bytes(), "image/jpeg")}
    data = {"phase": args.phase}
    print(f"[*] Uploading {img_path} with phase={args.phase} to {endpoint} ...")

    r = requests.post(endpoint, files=files, data=data)
    r.raise_for_status()

    b64 = r.json()["processed_image_base64"]
    with open(args.out, "wb") as f:
        f.write(base64.b64decode(b64))
    print(f"[✓] Saved processed image → {args.out}")

if __name__ == "__main__":
    main()
