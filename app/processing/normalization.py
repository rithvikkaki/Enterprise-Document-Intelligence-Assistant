import re
import unicodedata


def normalize_text(text: str) -> str:
    """Normalize extracted text (Unicode NFKC, whitespace, line endings)."""
    if not text:
        return ""

    # Unicode NFKC normalization
    text = unicodedata.normalize("NFKC", text)

    # Normalize line endings
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Remove excessive blank lines (> 2 consecutive blank lines)
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Strip inline multi-spaces but preserve single space
    lines = [re.sub(r"[ \t]+", " ", line).strip() for line in text.split("\n")]

    normalized = "\n".join(lines).strip()
    return normalized
