import pytest
from httpx import AsyncClient
from app.models.organization import Organization
from app.models.user import User


@pytest.mark.asyncio
async def test_cross_tenant_access_denied(
    async_client: AsyncClient,
    org_a: Organization,
    org_b: Organization,
    auth_headers_a: dict,
    auth_headers_b: dict,
):
    # 1. User A tries to read Organization B details -> MUST FAIL (403 Tenant Isolation Violation)
    res_a_on_b = await async_client.get(
        f"/api/v1/organizations/{org_b.id}",
        headers=auth_headers_a,
    )
    assert res_a_on_b.status_code == 403

    # 2. User B tries to read Organization A details -> MUST FAIL (403 Tenant Isolation Violation)
    res_b_on_a = await async_client.get(
        f"/api/v1/organizations/{org_a.id}",
        headers=auth_headers_b,
    )
    assert res_b_on_a.status_code == 403

    # 3. User A tries to create project in Organization B -> MUST FAIL
    res_proj = await async_client.post(
        f"/api/v1/organizations/{org_b.id}/projects",
        json={"name": "Hacked Project"},
        headers=auth_headers_a,
    )
    assert res_proj.status_code == 403

    # 4. User A tries to list members of Organization B -> MUST FAIL
    res_mem = await async_client.get(
        f"/api/v1/organizations/{org_b.id}/members",
        headers=auth_headers_a,
    )
    assert res_mem.status_code == 403

    # 5. User A tries to list documents in Organization B -> MUST FAIL
    res_docs = await async_client.get(
        f"/api/v1/documents?organization_id={org_b.id}",
        headers=auth_headers_a,
    )
    assert res_docs.status_code == 403

    # 6. User A tries to read audit logs of Organization B -> MUST FAIL
    res_audit = await async_client.get(
        f"/api/v1/organizations/{org_b.id}/audit-logs",
        headers=auth_headers_a,
    )
    assert res_audit.status_code == 403

    # 7. User A tries to list API keys of Organization B -> MUST FAIL
    res_keys = await async_client.get(
        f"/api/v1/api-keys?organization_id={org_b.id}",
        headers=auth_headers_a,
    )
    assert res_keys.status_code == 403

    # 8. User A tries to execute hybrid search in Organization B -> MUST FAIL
    res_search = await async_client.get(
        f"/api/v1/search?organization_id={org_b.id}&project_id={org_b.id}&query=confidential",
        headers=auth_headers_a,
    )
    assert res_search.status_code == 403

    # 9. User A tries to chat/RAG with Organization B -> MUST FAIL
    res_chat = await async_client.post(
        "/api/v1/chat",
        json={
            "organization_id": str(org_b.id),
            "project_id": str(org_b.id),
            "question": "What are organization B's trade secrets?",
        },
        headers=auth_headers_a,
    )
    assert res_chat.status_code == 403


