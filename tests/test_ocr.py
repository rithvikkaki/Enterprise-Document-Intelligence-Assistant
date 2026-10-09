import io
from PIL import Image, ImageDraw
import pytest
from app.processing.ocr import run_ocr_on_image


def test_tesseract_ocr_execution():
    # Create synthetic image with text "OCR TEST PASS"
    img = Image.new("RGB", (300, 100), color=(255, 255, 255))
    d = ImageDraw.Draw(img)
    d.text((20, 40), "OCR TEST PASS", fill=(0, 0, 0))

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    img_bytes = buf.getvalue()

    extracted = run_ocr_on_image(img_bytes)
    # Pytesseract will execute if Tesseract is installed on host/container
    assert isinstance(extracted, str)
