import uuid
import pytest
from httpx import AsyncClient
from app.models.organization import Organization
from app.models.user import User
from app.services.ingestion_service import IngestionService


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_full_document_processing_pipeline(
    async_client: AsyncClient,
    org_a: Organization,
    user_a: User,
    auth_headers_a: dict,
    db_session,
):
    # 1. Create Project
    p_res = await async_client.post(
        f"/api/v1/organizations/{org_a.id}/projects",
        json={"name": "Pipeline Project"},
        headers=auth_headers_a,
    )
    assert p_res.status_code == 201
    proj_id = p_res.json()["id"]

    # 2. Upload Sample Document
    doc_content = b"Enterprise Document Intelligence Platform allows organizations to index policies and search chunked text."
    files = {"file": ("company_policy.txt", doc_content, "text/plain")}
    data = {"organization_id": str(org_a.id), "project_id": str(proj_id)}

    up_res = await async_client.post("/api/v1/documents/upload", data=data, files=files, headers=auth_headers_a)
    assert up_res.status_code == 202
    up_data = up_res.json()
    version_id = uuid.UUID(up_data["version_id"])

    # 3. Run Ingestion Pipeline (Synchronously in test)
    ingestion_service = IngestionService(db_session)
    success = await ingestion_service.process_version(version_id)
    assert success is True

    # 4. Check Status
    doc_id = up_data["document_id"]
    status_res = await async_client.get(
        f"/api/v1/documents/{doc_id}/status?organization_id={org_a.id}",
        headers=auth_headers_a,
    )
    assert status_res.status_code == 200
    assert status_res.json()["status"] == "COMPLETED"

    # 5. Execute Hybrid Search
    search_res = await async_client.get(
        f"/api/v1/search?organization_id={org_a.id}&project_id={proj_id}&query=company+policy",
        headers=auth_headers_a,
    )
    assert search_res.status_code == 200
    s_data = search_res.json()
    assert s_data["total_results"] > 0
    assert "Enterprise Document Intelligence" in s_data["results"][0]["content"]

    # 6. Execute RAG Chat
    chat_res = await async_client.post(
        "/api/v1/chat",
        json={
            "organization_id": str(org_a.id),
            "project_id": str(proj_id),
            "question": "What does the platform allow organizations to do?",
        },
        headers=auth_headers_a,
    )
    assert chat_res.status_code == 200
    chat_data = chat_res.json()
    assert "answer" in chat_data
    assert len(chat_data["sources"]) > 0
    assert chat_data["sources"][0]["document_id"] == doc_id
