from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from pydantic import BaseModel


class PageContent(BaseModel):
    page_number: int
    text: str
    ocr_used: bool = False


class ExtractionResult(BaseModel):
    text: str
    pages: List[PageContent] = []
    metadata: Dict[str, Any] = {}
    extraction_method: str = "native"
    used_ocr: bool = False
    warnings: List[str] = []
    errors: List[str] = []


class BaseExtractor(ABC):
    @abstractmethod
    def extract(self, file_bytes: bytes, filename: str) -> ExtractionResult:
        """Extract text and metadata from file bytes."""
        pass
