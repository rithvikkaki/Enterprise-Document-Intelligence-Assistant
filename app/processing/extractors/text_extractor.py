from app.processing.extractors.base import BaseExtractor, ExtractionResult, PageContent


class TextExtractor(BaseExtractor):
    def extract(self, file_bytes: bytes, filename: str) -> ExtractionResult:
        try:
            text = file_bytes.decode("utf-8")
        except UnicodeDecodeError:
            text = file_bytes.decode("latin-1", errors="replace")

        page = PageContent(page_number=1, text=text.strip())

        return ExtractionResult(
            text=text.strip(),
            pages=[page],
            metadata={"filename": filename},
            extraction_method="text_utf8",
        )
