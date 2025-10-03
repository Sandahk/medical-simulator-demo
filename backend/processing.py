from io import BytesIO
from typing import Tuple
from PIL import Image, ImageFilter, ImageOps, ImageEnhance


def load_image(file_bytes: bytes) -> Image.Image:
    """Load an uploaded image (PNG/JPG) as an 8-bit grayscale PIL image."""
    im = Image.open(BytesIO(file_bytes)).convert("L")  # convert to grayscale
    return im


def simulate_arterial(img: Image.Image) -> Image.Image:
    """
    'Arterial phase' simulation.
    Simple, deterministic approximation: increase local contrast and sharpness a bit.
    Steps:
      1) Histogram equalization (better global contrast).
      2) Mild unsharp masking to crisp up edges.
      3) Slight brightness/contrast boost.
    """
    # Global contrast via equalization
    eq = ImageOps.equalize(img)

    # Unsharp mask
    sharp = eq.filter(ImageFilter.UnsharpMask(radius=2, percent=125, threshold=3))

    # Slight brightness/contrast boost
    bright = ImageEnhance.Brightness(sharp).enhance(1.05)
    contrast = ImageEnhance.Contrast(bright).enhance(1.35)
    return contrast


def simulate_venous(img: Image.Image) -> Image.Image:
    """
    'Venous phase' simulation.
    Smooth the image using a gaussian blur; keep intensity range.
    """
    # Gaussian blur with moderate radius
    blur = img.filter(ImageFilter.GaussianBlur(radius=2.0))
    return blur


def to_png_bytes(img: Image.Image) -> bytes:
    """Encode PIL image to PNG bytes."""
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def to_data_uri(png_bytes: bytes) -> str:
    """Return a data URI string suitable for direct <img src="..."> usage."""
    b64 = base64.b64encode(png_bytes).decode("ascii")
    return f"data:image/png;base64,{b64}"
