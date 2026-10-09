import pytest
from httpx import AsyncClient
from app.models.organization import Organization
from app.models.membership import Membership, RoleEnum
from app.models.user import User
from app.core.security import hash_password, create_access_token


@pytest.mark.asyncio
async def test_rbac_roles_and_permissions(
    async_client: AsyncClient,
    org_a: Organization,
    db_session,
):
    # 1. Create Viewer User in Org A
    viewer_user = User(
        email="viewer@org-a.com",
        hashed_password=hash_password("Password123!"),
        full_name="Viewer User",
    )
    db_session.add(viewer_user)
    await db_session.flush()

    mem_viewer = Membership(user_id=viewer_user.id, organization_id=org_a.id, role=RoleEnum.VIEWER)
    db_session.add(mem_viewer)
    await db_session.flush()

    viewer_token = create_access_token(str(viewer_user.id))
    viewer_headers = {"Authorization": f"Bearer {viewer_token}"}

    # 2. Viewer tries to create Project -> MUST FAIL (403 Permission Denied)
    proj_res = await async_client.post(
        f"/api/v1/organizations/{org_a.id}/projects",
        json={"name": "Viewer Project Attempt"},
        headers=viewer_headers,
    )
    assert proj_res.status_code == 403

    # 3. Viewer tries to list projects -> MUST SUCCEED (200 OK)
    list_res = await async_client.get(
        f"/api/v1/organizations/{org_a.id}/projects",
        headers=viewer_headers,
    )
    assert list_res.status_code == 200
