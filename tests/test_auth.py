import pytest
from httpx import AsyncClient


@pytest.mark.integration
@pytest.mark.asyncio
async def test_register_and_login(async_client: AsyncClient):
    # 1. Register User
    reg_payload = {
        "email": "testuser@enterprise.com",
        "password": "SecurePassword123!",
        "full_name": "Test Engineer",
    }
    response = await async_client.post("/api/v1/auth/register", json=reg_payload)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "testuser@enterprise.com"
    assert "id" in data

    # 2. Login User
    login_payload = {
        "email": "testuser@enterprise.com",
        "password": "SecurePassword123!",
    }
    login_res = await async_client.post("/api/v1/auth/login", json=login_payload)
    assert login_res.status_code == 200
    token_data = login_res.json()
    assert "access_token" in token_data
    assert "refresh_token" in token_data

    # 3. Refresh Token
    refresh_res = await async_client.post(
        "/api/v1/auth/refresh", json={"refresh_token": token_data["refresh_token"]}
    )
    assert refresh_res.status_code == 200
    assert "access_token" in refresh_res.json()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_invalid_login(async_client: AsyncClient):
    login_payload = {
        "email": "nonexistent@enterprise.com",
        "password": "WrongPassword!",
    }
    res = await async_client.post("/api/v1/auth/login", json=login_payload)
    assert res.status_code == 401
