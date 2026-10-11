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


def test_production_secrets_validation():
    from app.core.config import Settings

    # Production environment with default secret must fail validation
    with pytest.raises(ValueError, match="Insecure default SECRET_KEY"):
        Settings(ENVIRONMENT="production", SECRET_KEY="change_this_to_a_secure_random_secret_key_in_production")

    # Production environment with default JWT secret must fail validation
    with pytest.raises(ValueError, match="Insecure default JWT_SECRET_KEY"):
        Settings(ENVIRONMENT="production", SECRET_KEY="strong_custom_secret", JWT_SECRET_KEY="super_secret_jwt_key_please_change_in_production")


def test_cors_origins_configuration():
    from app.core.config import Settings

    # Test comma-separated string parsing
    s1 = Settings(CORS_ORIGINS="https://app.pages.dev, https://corp.com")
    assert s1.CORS_ORIGINS == ["https://app.pages.dev", "https://corp.com"]

    # Test list parsing
    s2 = Settings(CORS_ORIGINS=["https://custom.domain.com"])
    assert s2.CORS_ORIGINS == ["https://custom.domain.com"]


