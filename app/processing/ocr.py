import io
from typing import Optional
from PIL import Image
import pytesseract
from app.core.logging import logger


def run_ocr_on_image(image_bytes: bytes) -> str:
    """Run Tesseract OCR on raw image bytes."""
    try:
        image = Image.open(io.BytesIO(image_bytes))
        # Convert image to RGB if needed
        if image.mode not in ("L", "RGB"):
            image = image.convert("RGB")
        text = pytesseract.image_to_string(image, lang="eng")
        return text.strip()
    except Exception as e:
        logger.warning(f"Tesseract OCR execution failed: {str(e)}")
        return ""
