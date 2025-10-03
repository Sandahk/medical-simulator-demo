"""
Medical Image Processing Module

This module provides functions for loading and processing medical images
with arterial and venous phase simulation algorithms. It handles image
conversion, enhancement, and output formatting for the medical phase simulator.

Author: Medical Phase Simulator Team
Version: 1.0.0
"""

import logging
from io import BytesIO
from typing import Tuple
from PIL import Image, ImageFilter, ImageOps, ImageEnhance

# Configure logger for this module
logger = logging.getLogger(__name__)


def load_image(file_bytes: bytes) -> Image.Image:
    """
    Load an uploaded image from bytes and convert to grayscale.
    
    This function takes raw image bytes and converts them to a PIL Image
    object in grayscale mode for consistent processing.
    
    Args:
        file_bytes (bytes): Raw image data from uploaded file
        
    Returns:
        Image.Image: PIL Image object in grayscale mode ('L')
        
    Raises:
        PIL.UnidentifiedImageError: If the image format is not supported
        ValueError: If the image data is corrupted or invalid
        
    Example:
        >>> with open('image.jpg', 'rb') as f:
        ...     img_data = f.read()
        >>> img = load_image(img_data)
        >>> print(img.mode)  # 'L'
        >>> print(img.size)  # (width, height)
    """
    logger.debug(f"Loading image from {len(file_bytes)} bytes")
    im = Image.open(BytesIO(file_bytes)).convert("L")  # convert to grayscale
    logger.info(f"Image loaded successfully: {im.size} pixels, mode={im.mode}")
    return im


def simulate_arterial(img: Image.Image) -> Image.Image:
    """
    Simulate arterial phase enhancement for medical images.
    
    This function applies a series of image processing techniques to simulate
    how an image would appear during the arterial phase of contrast enhancement.
    The processing increases local contrast and sharpness to highlight
    arterial structures and improve diagnostic clarity.
    
    Processing Steps:
        1. Histogram equalization for improved global contrast
        2. Unsharp masking to enhance edge definition
        3. Brightness and contrast enhancement for optimal visualization
        
    Args:
        img (Image.Image): Input grayscale PIL Image
        
    Returns:
        Image.Image: Enhanced PIL Image with arterial phase characteristics
        
    Note:
        The enhancement parameters are optimized for medical imaging and
        may need adjustment based on specific imaging protocols.
        
    Example:
        >>> img = load_image(image_bytes)
        >>> arterial_img = simulate_arterial(img)
        >>> # Save or display the enhanced image
    """
    logger.info("Starting arterial phase processing")
    
    # Global contrast via equalization
    eq = ImageOps.equalize(img)
    logger.debug("Applied histogram equalization")

    # Unsharp mask for edge enhancement
    sharp = eq.filter(ImageFilter.UnsharpMask(radius=2, percent=125, threshold=3))
    logger.debug("Applied unsharp mask filter")

    # Brightness and contrast enhancement
    bright = ImageEnhance.Brightness(sharp).enhance(1.05)
    contrast = ImageEnhance.Contrast(bright).enhance(1.35)
    logger.info("Arterial phase processing completed")
    return contrast


def simulate_venous(img: Image.Image) -> Image.Image:
    """
    Simulate venous phase enhancement for medical images.
    
    This function applies Gaussian blur to simulate how an image would appear
    during the venous phase of contrast enhancement. The venous phase typically
    shows softer, more diffused contrast patterns compared to the arterial phase.
    
    The processing applies a moderate Gaussian blur to create a smoother
    appearance while maintaining the overall intensity range of the image.
    
    Args:
        img (Image.Image): Input grayscale PIL Image
        
    Returns:
        Image.Image: Enhanced PIL Image with venous phase characteristics
        
    Note:
        The blur radius is optimized for medical imaging visualization.
        Different imaging modalities may require parameter adjustments.
        
    Example:
        >>> img = load_image(image_bytes)
        >>> venous_img = simulate_venous(img)
        >>> # Save or display the enhanced image
    """
    logger.info("Starting venous phase processing")
    # Gaussian blur with moderate radius
    blur = img.filter(ImageFilter.GaussianBlur(radius=2.0))
    logger.info("Venous phase processing completed")
    return blur


def to_png_bytes(img: Image.Image) -> bytes:
    """
    Convert PIL Image to PNG format bytes.
    
    This function encodes a PIL Image object into PNG format and returns
    the raw bytes. PNG format is chosen for its lossless compression
    and wide browser support.
    
    Args:
        img (Image.Image): PIL Image object to encode
        
    Returns:
        bytes: PNG-encoded image data
        
    Example:
        >>> img = load_image(image_bytes)
        >>> processed_img = simulate_arterial(img)
        >>> png_data = to_png_bytes(processed_img)
        >>> len(png_data)  # Size in bytes
    """
    logger.debug("Converting image to PNG bytes")
    buf = BytesIO()
    img.save(buf, format="PNG")
    png_data = buf.getvalue()
    logger.debug(f"PNG conversion completed: {len(png_data)} bytes")
    return png_data


def to_data_uri(png_bytes: bytes) -> str:
    """
    Convert PNG bytes to data URI string for web display.
    
    This function creates a data URI string that can be used directly
    in HTML img tags or CSS background-image properties. The data URI
    format embeds the image data directly in the URL.
    
    Args:
        png_bytes (bytes): PNG-encoded image data
        
    Returns:
        str: Data URI string in format "data:image/png;base64,{base64_data}"
        
    Example:
        >>> png_data = to_png_bytes(img)
        >>> data_uri = to_data_uri(png_data)
        >>> print(data_uri[:50])  # "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA..."
    """
    import base64
    logger.debug("Converting PNG bytes to data URI")
    b64 = base64.b64encode(png_bytes).decode("ascii")
    return f"data:image/png;base64,{b64}"
