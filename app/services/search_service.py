import uuid
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.repositories.search_repository import SearchRepository
from app.services.embedding_service import EmbeddingService
from app.providers.rerank.cross_encoder import CrossEncoderReranker
from app.schemas.search import SearchQueryRequest, SearchResultChunk, HybridSearchResponse


class SearchService:
    def __init__(self, session: AsyncSession):
        self.search_repo = SearchRepository(session)
        self.embedding_service = EmbeddingService()
        self.reranker = CrossEncoderReranker() if settings.RERANKING_ENABLED else None

    async def perform_hybrid_search(self, request: SearchQueryRequest) -> HybridSearchResponse:
        # 1. Generate Query Vector Embedding
        query_vector = self.embedding_service.generate_embedding(request.query)

        # 2. Candidate Retrieval via Hybrid Search (Vector + FTS RRF)
        candidate_limit = max(request.limit * 2, 20)
        results = await self.search_repo.hybrid_search_rrf(
            query_vector=query_vector,
            query_text=request.query,
            org_id=request.organization_id,
            project_id=request.project_id,
            document_id=request.document_id,
            candidate_limit=candidate_limit,
        )

        # 3. Optional CrossEncoder Reranking
        if self.reranker and results:
            candidates = [r.content for r in results]
            ranked_pairs = self.reranker.rerank(request.query, candidates)

            reranked_results: List[SearchResultChunk] = []
            for candidate_idx, rerank_score in ranked_pairs:
                res = results[candidate_idx]
                res.score = float(rerank_score)
                reranked_results.append(res)

            results = reranked_results

        # 4. Limit to requested top K
        final_results = results[: request.limit]

        return HybridSearchResponse(
            query=request.query,
            organization_id=request.organization_id,
            project_id=request.project_id,
            total_results=len(final_results),
            results=final_results,
        )
