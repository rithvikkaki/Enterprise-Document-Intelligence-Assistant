import email
from email import policy
from bs4 import BeautifulSoup
from app.processing.extractors.base import BaseExtractor, ExtractionResult, PageContent


class EMLExtractor(BaseExtractor):
    def extract(self, file_bytes: bytes, filename: str) -> ExtractionResult:
        msg = email.message_from_bytes(file_bytes, policy=policy.default)
        headers = [
            f"Subject: {msg.get('Subject', '')}",
            f"From: {msg.get('From', '')}",
            f"To: {msg.get('To', '')}",
            f"Date: {msg.get('Date', '')}",
        ]
        
        body_parts: list[str] = []

        if msg.is_multipart():
            for part in msg.walk():
                ctype = part.get_content_type()
                if ctype == "text/plain":
                    body_parts.append(part.get_content())
                elif ctype == "text/html" and not body_parts:
                    html = part.get_content()
                    soup = BeautifulSoup(html, "html.parser")
                    body_parts.append(soup.get_text(separator="\n"))
        else:
            ctype = msg.get_content_type()
            payload = msg.get_content()
            if ctype == "text/html":
                soup = BeautifulSoup(payload, "html.parser")
                body_parts.append(soup.get_text(separator="\n"))
            else:
                body_parts.append(str(payload))

        full_text = "\n".join(headers) + "\n\n" + "\n\n".join(body_parts)
        page = PageContent(page_number=1, text=full_text.strip())

        return ExtractionResult(
            text=full_text.strip(),
            pages=[page],
            metadata={"subject": msg.get("Subject", ""), "from": msg.get("From", "")},
            extraction_method="eml_python_email",
        )
