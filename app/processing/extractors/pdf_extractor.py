import fitz  # PyMuPDF
from app.processing.extractors.base import BaseExtractor, ExtractionResult, PageContent
from app.processing.ocr import run_ocr_on_image


class PDFExtractor(BaseExtractor):
    def extract(self, file_bytes: bytes, filename: str) -> ExtractionResult:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        pages: list[PageContent] = []
        full_text_list: list[str] = []
        overall_ocr_used = False

        for page_idx in range(len(doc)):
            page_num = page_idx + 1
            page = doc[page_idx]
            page_text = page.get_text("text").strip()
            ocr_used_for_page = False

            # Evaluate text quality; if low (< 50 non-whitespace chars), perform page OCR
            non_ws_count = len("".join(page_text.split()))
            if non_ws_count < 50:
                pix = page.get_pixmap(dpi=150)
                img_bytes = pix.tobytes("png")
                ocr_text = run_ocr_on_image(img_bytes)
                if ocr_text:
                    page_text = ocr_text
                    ocr_used_for_page = True
                    overall_ocr_used = True

            pages.append(PageContent(page_number=page_num, text=page_text, ocr_used=ocr_used_for_page))
            if page_text:
                full_text_list.append(f"--- Page {page_num} ---\n{page_text}")

        method = "pdf_hybrid_ocr" if overall_ocr_used else "pdf_pymupdf"
        return ExtractionResult(
            text="\n\n".join(full_text_list),
            pages=pages,
            metadata={"page_count": len(doc)},
            extraction_method=method,
            used_ocr=overall_ocr_used,
        )
