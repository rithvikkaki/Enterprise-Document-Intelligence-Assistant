import uuid
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class SearchQueryRequest(BaseModel):
    query: str = Field(..., min_length=1)
    organization_id: uuid.UUID
    project_id: uuid.UUID
    document_id: Optional[uuid.UUID] = None
    limit: int = Field(10, ge=1, le=100)


class SearchResultChunk(BaseModel):
    chunk_id: uuid.UUID
    document_id: uuid.UUID
    document_version_id: uuid.UUID
    document_name: str
    version_number: int
    chunk_index: int
    content: str
    score: float
    metadata: Dict[str, Any] = {}


class HybridSearchResponse(BaseModel):
    query: str
    organization_id: uuid.UUID
    project_id: uuid.UUID
    total_results: int
    results: List[SearchResultChunk]
