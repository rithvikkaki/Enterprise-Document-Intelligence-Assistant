from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.core.dependencies import get_current_user, require_org_role
from app.models.user import User
from app.models.membership import RoleEnum
from app.schemas.chat import ChatQueryRequest, ChatQueryResponse
from app.services.rag_service import RAGService

router = APIRouter(prefix="/chat", tags=["RAG Chat"])


@router.post("", response_model=ChatQueryResponse)
async def chat_rag(
    request: ChatQueryRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Verify user multi-tenant membership & RBAC role
    service_dep = require_org_role([RoleEnum.VIEWER, RoleEnum.EDITOR, RoleEnum.ADMIN, RoleEnum.OWNER])
    await service_dep(request.organization_id, current_user, db)

    rag_service = RAGService(db)
    return await rag_service.answer_question(request)
