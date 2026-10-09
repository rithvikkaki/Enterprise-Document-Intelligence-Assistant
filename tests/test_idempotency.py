import io
import pytest
from httpx import AsyncClient
from app.models.organization import Organization


@pytest.mark.asyncio
async def test_upload_idempotency(
    async_client: AsyncClient,
    org_a: Organization,
    auth_headers_a: dict,
):
    # 1. Create Project
    p_res = await async_client.post(
        f"/api/v1/organizations/{org_a.id}/projects",
        json={"name": "Idempotency Project"},
        headers=auth_headers_a,
    )
    assert p_res.status_code == 201
    proj_id = p_res.json()["id"]

    idempotency_key = "idemp_unique_key_12345"
    data = {"organization_id": str(org_a.id), "project_id": str(proj_id)}
    headers = {**auth_headers_a, "Idempotency-Key": idempotency_key}

    # 2. First Upload Request
    files1 = {"file": ("test_file.txt", io.BytesIO(b"Document content for idempotency test"), "text/plain")}
    res1 = await async_client.post("/api/v1/documents/upload", data=data, files=files1, headers=headers)
    assert res1.status_code == 202
    data1 = res1.json()

    # 3. Second Upload Request with SAME Idempotency-Key -> MUST return SAME job_id & version_id
    files2 = {"file": ("test_file.txt", io.BytesIO(b"Document content for idempotency test"), "text/plain")}
    res2 = await async_client.post("/api/v1/documents/upload", data=data, files=files2, headers=headers)
    assert res2.status_code == 202
    data2 = res2.json()

    assert data1["version_id"] == data2["version_id"]
    assert data1["job_id"] == data2["job_id"]
