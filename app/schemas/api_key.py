import uuid
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class APIKeyCreate(BaseModel):
    organization_id: uuid.UUID
    name: str = Field(..., min_length=2, max_length=255)
    scopes: Optional[List[str]] = Field(default_factory=list)
    expires_in_days: Optional[int] = Field(None, ge=1, le=365)


class APIKeyCreatedResponse(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    name: str
    key_prefix: str
    secret_key: str  # Displayed ONLY ONCE upon creation
    scopes: List[str]
    expires_at: Optional[datetime] = None
    created_at: datetime


class APIKeyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    organization_id: uuid.UUID
    name: str
    key_prefix: str
    scopes: List[str]
    created_by_id: uuid.UUID
    expires_at: Optional[datetime] = None
    revoked_at: Optional[datetime] = None
    created_at: datetime
