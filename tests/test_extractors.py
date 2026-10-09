import io
import zipfile
import pytest
from app.processing.extractors.text_extractor import TextExtractor
from app.processing.extractors.html_extractor import HTMLExtractor
from app.processing.extractors.eml_extractor import EMLExtractor
from app.processing.extractors.zip_handler import SafeZipHandler
from app.core.exceptions import FileValidationError


def test_text_extractor():
    extractor = TextExtractor()
    sample = "Hello World! This is plain text document."
    res = extractor.extract(sample.encode("utf-8"), "test.txt")
    assert "Hello World!" in res.text
    assert len(res.pages) == 1


def test_html_extractor():
    extractor = HTMLExtractor()
    html = "<html><head><title>Test Page</title></head><body><h1>Heading</h1><p>Paragraph text.</p></body></html>"
    res = extractor.extract(html.encode("utf-8"), "test.html")
    assert "Heading" in res.text
    assert "Paragraph text." in res.text


def test_eml_extractor():
    extractor = EMLExtractor()
    eml_raw = b"From: sender@acme.com\nTo: recv@acme.com\nSubject: Test Email\n\nEmail body content goes here."
    res = extractor.extract(eml_raw, "test.eml")
    assert "Test Email" in res.text
    assert "Email body content" in res.text


def test_safe_zip_extraction():
    zip_handler = SafeZipHandler()

    # Create in-memory valid zip
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("doc1.txt", "Document 1 content")
        zf.writestr("doc2.txt", "Document 2 content")
    zip_bytes = buf.getvalue()

    files = zip_handler.extract_files(zip_bytes)
    assert len(files) == 2
    filenames = [f[0] for f in files]
    assert "doc1.txt" in filenames
    assert "doc2.txt" in filenames


def test_zip_slip_prevention():
    zip_handler = SafeZipHandler()

    # Create zip with malicious Zip Slip path traversal member "../../outside.txt"
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("../../outside.txt", "Malicious content")
    zip_bytes = buf.getvalue()

    with pytest.raises(FileValidationError):
        zip_handler.extract_files(zip_bytes)
