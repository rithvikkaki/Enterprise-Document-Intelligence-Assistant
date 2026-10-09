import uuid
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.core.dependencies import get_current_user, require_org_role
from app.models.user import User
from app.models.membership import RoleEnum
from app.schemas.search import SearchQueryRequest, HybridSearchResponse
from app.services.search_service import SearchService

router = APIRouter(prefix="/search", tags=["Search"])


@router.get("", response_model=HybridSearchResponse)
async def search_documents(
    organization_id: uuid.UUID = Query(...),
    project_id: uuid.UUID = Query(...),
    query: str = Query(..., min_length=1),
    document_id: Optional[uuid.UUID] = Query(None),
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Verify RBAC role and multi-tenant membership
    service_dep = require_org_role([RoleEnum.VIEWER, RoleEnum.EDITOR, RoleEnum.ADMIN, RoleEnum.OWNER])
    await service_dep(organization_id, current_user, db)

    request = SearchQueryRequest(
        query=query,
        organization_id=organization_id,
        project_id=project_id,
        document_id=document_id,
        limit=limit,
    )

    search_service = SearchService(db)
    return await search_service.perform_hybrid_search(request)
