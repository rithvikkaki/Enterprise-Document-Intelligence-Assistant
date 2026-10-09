import pytest
from httpx import AsyncClient
from app.models.organization import Organization
from app.models.user import User
from app.services.api_key_service import APIKeyService


@pytest.mark.asyncio
async def test_api_key_lifecycle(
    async_client: AsyncClient,
    org_a: Organization,
    org_b: Organization,
    user_a: User,
    db_session,
    auth_headers_a: dict,
):
    service = APIKeyService(db_session)

    # 1. Create API Key
    res = await async_client.post(
        "/api/v1/api-keys",
        json={"organization_id": str(org_a.id), "name": "CI Deployment Key", "scopes": ["read", "write"]},
        headers=auth_headers_a,
    )
    assert res.status_code == 201
    created_data = res.json()
    assert "secret_key" in created_data
    raw_key = created_data["secret_key"]
    assert raw_key.startswith("edip_live_")

    # 2. Authenticate with Valid Key
    auth_key = await service.authenticate_key(raw_key, required_scope="read")
    assert auth_key.organization_id == org_a.id

    # 3. Authenticate with Invalid Key
    with pytest.raises(Exception):
        await service.authenticate_key("edip_live_badprefix_badsecret")

    # 4. Revoke Key
    key_id = created_data["id"]
    del_res = await async_client.delete(
        f"/api/v1/api-keys/{key_id}?organization_id={org_a.id}",
        headers=auth_headers_a,
    )
    assert del_res.status_code == 204

    # 5. Authenticate with Revoked Key -> MUST FAIL
    with pytest.raises(Exception):
        await service.authenticate_key(raw_key)
