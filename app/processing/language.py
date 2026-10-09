import os
from typing import Tuple
import langdetect
from app.core.logging import logger


def detect_language(text: str) -> Tuple[str, float]:
    """Detect language of text. Returns (language_code, confidence)."""
    if os.environ.get("TESTING") == "true":
        return "en", 1.0

    clean_sample = text.strip()[:2000]
    if len(clean_sample) < 20:
        return "en", 1.0

    try:
        langdetect.DetectorFactory.seed = 0
        lang = langdetect.detect(clean_sample)
        return lang, 0.95
    except Exception as e:
        logger.debug(f"Language detection fallback to 'en': {str(e)}")
        return "en", 0.5
