import pytest
from httpx import AsyncClient
from app.models.organization import Organization
from app.models.user import User


@pytest.mark.asyncio
async def test_create_and_list_organizations(
    async_client: AsyncClient, auth_headers_a: dict
):
    # Create Organization
    res = await async_client.post(
        "/api/v1/organizations",
        json={"name": "Acme Corp"},
        headers=auth_headers_a,
    )
    assert res.status_code == 201
    data = res.json()
    assert data["name"] == "Acme Corp"
    assert data["slug"] == "acme-corp"

    # List Organizations
    list_res = await async_client.get("/api/v1/organizations", headers=auth_headers_a)
    assert list_res.status_code == 200
    orgs = list_res.json()
    assert len(orgs) >= 1
    assert any(o["name"] == "Acme Corp" for o in orgs)
