import uuid
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class ChatQueryRequest(BaseModel):
    organization_id: uuid.UUID
    project_id: uuid.UUID
    question: str = Field(..., min_length=1)
    document_id: Optional[uuid.UUID] = None


class SourceCitation(BaseModel):
    document_id: uuid.UUID
    document_name: str
    document_version: int
    page: Optional[int] = None
    chunk_id: uuid.UUID
    snippet: str


class ChatQueryResponse(BaseModel):
    answer: str
    sources: List[SourceCitation]
    question: str
    organization_id: uuid.UUID
    project_id: uuid.UUID
