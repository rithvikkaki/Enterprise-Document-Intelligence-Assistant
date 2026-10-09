from app.processing.extractors.base import BaseExtractor, ExtractionResult
from app.processing.extractors.pdf_extractor import PDFExtractor
from app.processing.extractors.docx_extractor import DOCXExtractor
from app.processing.extractors.pptx_extractor import PPTXExtractor
from app.processing.extractors.xlsx_extractor import XLSXExtractor
from app.processing.extractors.html_extractor import HTMLExtractor
from app.processing.extractors.eml_extractor import EMLExtractor
from app.processing.extractors.image_extractor import ImageExtractor
from app.processing.extractors.text_extractor import TextExtractor
from app.processing.normalization import normalize_text
from app.processing.language import detect_language


class ExtractionService:
    def get_extractor(self, filename: str) -> BaseExtractor:
        ext = filename.split(".")[-1].lower() if "." in filename else ""
        if ext == "pdf":
            return PDFExtractor()
        elif ext == "docx":
            return DOCXExtractor()
        elif ext == "pptx":
            return PPTXExtractor()
        elif ext == "xlsx":
            return XLSXExtractor()
        elif ext in ("html", "htm"):
            return HTMLExtractor()
        elif ext == "eml":
            return EMLExtractor()
        elif ext in ("png", "jpg", "jpeg"):
            return ImageExtractor()
        else:
            return TextExtractor()

    def process_file(self, file_bytes: bytes, filename: str) -> ExtractionResult:
        extractor = self.get_extractor(filename)
        result = extractor.extract(file_bytes, filename)
        
        # Text normalization
        result.text = normalize_text(result.text)

        # Language detection
        lang_code, confidence = detect_language(result.text)
        result.metadata["detected_language"] = lang_code
        result.metadata["language_confidence"] = confidence

        return result
