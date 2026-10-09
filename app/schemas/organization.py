import uuid
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
from app.models.membership import RoleEnum


class OrganizationCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    slug: Optional[str] = Field(None, min_length=2, max_length=255)


class OrganizationUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=255)


class OrganizationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    slug: str
    created_at: datetime
    updated_at: datetime


class MemberCreate(BaseModel):
    email: str
    role: RoleEnum = RoleEnum.VIEWER


class MemberUpdate(BaseModel):
    role: RoleEnum


class MemberResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    organization_id: uuid.UUID
    role: RoleEnum
    user_email: str
    user_full_name: str
    created_at: datetime


class OrganizationStatsResponse(BaseModel):
    total_documents: int
    completed_documents: int
    processing_documents: int
    failed_documents: int
    total_projects: int
    total_members: int

