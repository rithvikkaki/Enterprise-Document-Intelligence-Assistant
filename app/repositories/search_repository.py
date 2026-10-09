import uuid
from typing import List, Optional, Dict, Tuple
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.models.document import Document
from app.models.document_version import DocumentVersion
from app.models.document_chunk import DocumentChunk
from app.schemas.search import SearchResultChunk


class SearchRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    def _is_postgres(self) -> bool:
        try:
            bind = getattr(self.session, "bind", None)
            if bind is not None and hasattr(bind, "dialect"):
                return bind.dialect.name == "postgresql"
            bind = self.session.get_bind()
            if bind is not None and hasattr(bind, "dialect"):
                return bind.dialect.name == "postgresql"
        except Exception:
            pass
        return "postgresql" in settings.DATABASE_URL

    async def vector_search(
        self,
        query_vector: List[float],
        org_id: uuid.UUID,
        project_id: uuid.UUID,
        document_id: Optional[uuid.UUID] = None,
        limit: int = 20,
    ) -> List[Tuple[DocumentChunk, Document, DocumentVersion, float]]:
        is_postgres = self._is_postgres()

        conditions = [
            DocumentChunk.organization_id == org_id,
            DocumentChunk.project_id == project_id,
            Document.deleted_at.is_(None),
        ]
        if document_id:
            conditions.append(DocumentChunk.document_id == document_id)

        if is_postgres:
            distance_col = DocumentChunk.embedding.cosine_distance(query_vector)
            stmt = (
                select(DocumentChunk, Document, DocumentVersion, distance_col.label("distance"))
                .join(Document, DocumentChunk.document_id == Document.id)
                .join(DocumentVersion, DocumentChunk.document_version_id == DocumentVersion.id)
                .where(and_(*conditions))
                .order_by(distance_col.asc())
                .limit(limit)
            )
        else:
            # Fallback for SQLite in unit tests
            stmt = (
                select(DocumentChunk, Document, DocumentVersion, func.length(DocumentChunk.content).label("distance"))
                .join(Document, DocumentChunk.document_id == Document.id)
                .join(DocumentVersion, DocumentChunk.document_version_id == DocumentVersion.id)
                .where(and_(*conditions))
                .limit(limit)
            )

        result = await self.session.execute(stmt)
        return result.all()

    async def full_text_search(
        self,
        query_text: str,
        org_id: uuid.UUID,
        project_id: uuid.UUID,
        document_id: Optional[uuid.UUID] = None,
        limit: int = 20,
    ) -> List[Tuple[DocumentChunk, Document, DocumentVersion, float]]:
        is_postgres = self._is_postgres()

        conditions = [
            DocumentChunk.organization_id == org_id,
            DocumentChunk.project_id == project_id,
            Document.deleted_at.is_(None),
        ]
        if document_id:
            conditions.append(DocumentChunk.document_id == document_id)

        if is_postgres:
            formatted_query = func.websearch_to_tsquery("english", query_text)
            rank_col = func.ts_rank_cd(DocumentChunk.fts_vector, formatted_query)
            conditions.append(DocumentChunk.fts_vector.op("@@")(formatted_query))
            stmt = (
                select(DocumentChunk, Document, DocumentVersion, rank_col.label("rank"))
                .join(Document, DocumentChunk.document_id == Document.id)
                .join(DocumentVersion, DocumentChunk.document_version_id == DocumentVersion.id)
                .where(and_(*conditions))
                .order_by(rank_col.desc())
                .limit(limit)
            )
        else:
            # Fallback text query for SQLite in unit tests
            conditions.append(DocumentChunk.content.icontains(query_text))
            stmt = (
                select(DocumentChunk, Document, DocumentVersion, func.length(DocumentChunk.content).label("rank"))
                .join(Document, DocumentChunk.document_id == Document.id)
                .join(DocumentVersion, DocumentChunk.document_version_id == DocumentVersion.id)
                .where(and_(*conditions))
                .limit(limit)
            )

        result = await self.session.execute(stmt)
        return result.all()

    async def hybrid_search_rrf(
        self,
        query_vector: List[float],
        query_text: str,
        org_id: uuid.UUID,
        project_id: uuid.UUID,
        document_id: Optional[uuid.UUID] = None,
        candidate_limit: int = 20,
        rrf_k: int = settings.RRF_K,
    ) -> List[SearchResultChunk]:
        vector_results = await self.vector_search(
            query_vector=query_vector,
            org_id=org_id,
            project_id=project_id,
            document_id=document_id,
            limit=candidate_limit,
        )

        fts_results = await self.full_text_search(
            query_text=query_text,
            org_id=org_id,
            project_id=project_id,
            document_id=document_id,
            limit=candidate_limit,
        )

        # Calculate RRF Scores
        scores: Dict[uuid.UUID, float] = {}
        chunks_map: Dict[uuid.UUID, Tuple[DocumentChunk, Document, DocumentVersion]] = {}

        for rank, (chunk, doc, version, dist) in enumerate(vector_results, start=1):
            chunk_id = chunk.id
            scores[chunk_id] = scores.get(chunk_id, 0.0) + (1.0 / (rrf_k + rank))
            chunks_map[chunk_id] = (chunk, doc, version)

        for rank, (chunk, doc, version, rank_score) in enumerate(fts_results, start=1):
            chunk_id = chunk.id
            scores[chunk_id] = scores.get(chunk_id, 0.0) + (1.0 / (rrf_k + rank))
            chunks_map[chunk_id] = (chunk, doc, version)

        sorted_chunk_ids = sorted(scores.keys(), key=lambda cid: scores[cid], reverse=True)

        results: List[SearchResultChunk] = []
        for cid in sorted_chunk_ids:
            chunk, doc, version = chunks_map[cid]
            results.append(
                SearchResultChunk(
                    chunk_id=chunk.id,
                    document_id=doc.id,
                    document_version_id=version.id,
                    document_name=version.original_filename,
                    version_number=version.version_number,
                    chunk_index=chunk.chunk_index,
                    content=chunk.content,
                    score=scores[cid],
                    metadata=chunk.metadata_json or {},
                )
            )

        return results
