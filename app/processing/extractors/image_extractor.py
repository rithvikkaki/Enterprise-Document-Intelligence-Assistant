from app.processing.extractors.base import BaseExtractor, ExtractionResult, PageContent
from app.processing.ocr import run_ocr_on_image


class ImageExtractor(BaseExtractor):
    def extract(self, file_bytes: bytes, filename: str) -> ExtractionResult:
        ocr_text = run_ocr_on_image(file_bytes)
        page = PageContent(page_number=1, text=ocr_text, ocr_used=True)

        return ExtractionResult(
            text=ocr_text,
            pages=[page],
            metadata={"filename": filename},
            extraction_method="image_tesseract_ocr",
            used_ocr=True,
        )
