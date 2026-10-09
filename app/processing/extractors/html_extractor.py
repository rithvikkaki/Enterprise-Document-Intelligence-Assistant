from bs4 import BeautifulSoup
from app.processing.extractors.base import BaseExtractor, ExtractionResult, PageContent


class HTMLExtractor(BaseExtractor):
    def extract(self, file_bytes: bytes, filename: str) -> ExtractionResult:
        html_content = file_bytes.decode("utf-8", errors="replace")
        soup = BeautifulSoup(html_content, "html.parser")

        # Strip script and style tags
        for script in soup(["script", "style", "noscript"]):
            script.extract()

        text = soup.get_text(separator="\n")
        page = PageContent(page_number=1, text=text.strip())

        title = soup.title.string if soup.title else filename
        return ExtractionResult(
            text=text.strip(),
            pages=[page],
            metadata={"title": str(title)},
            extraction_method="html_beautifulsoup",
        )
