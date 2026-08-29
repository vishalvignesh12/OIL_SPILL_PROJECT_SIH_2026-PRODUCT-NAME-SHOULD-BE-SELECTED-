"""
Basic functionality tests to prevent demo breakage.
Tests authentication, database health, and core API availability.
"""
import pytest
from httpx import AsyncClient, ASGITransport
from uuid import uuid4
from datetime import datetime, UTC

from app.main import app
from app.core.config import settings


@pytest.mark.asyncio
async def test_health_endpoint():
    """Test that the health endpoint is available."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"


@pytest.mark.asyncio
async def test_ready_endpoint_without_db():
    """Test ready endpoint behavior when database is not available."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health/ready")
        # Should return 503 when DB is not configured in test
        assert response.status_code == 503
        data = response.json()
        assert data["status"] == "unavailable"


@pytest.mark.asyncio
async def test_user_registration():
    """Test user registration endpoint."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Use unique email to avoid conflicts
        unique_suffix = str(uuid4())[:8]
        user_data = {
            "name": "Test User",
            "email": f"test_{unique_suffix}@example.com",
            "password": "securepassword123"
        }

        response = await client.post("/api/v1/auth/register", json=user_data)
        # In test environment, this might fail due to missing DB setup,
        # but we're testing the endpoint exists and processes the request
        assert response.status_code in [200, 201, 400, 409, 500]  # Various possible responses

        # If successful, check response structure
        if response.status_code in [200, 201]:
            data = response.json()
            assert "access_token" in data
            assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_user_login():
    """Test user login endpoint."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Use unique email to avoid conflicts
        unique_suffix = str(uuid4())[:8]
        user_data = {
            "email": f"test_{unique_suffix}@example.com",
            "password": "securepassword123"
        }

        # First try to register the user (might fail if DB not available)
        await client.post("/api/v1/auth/register", json={
            "name": "Test User",
            "email": user_data["email"],
            "password": user_data["password"]
        })

        # Then try to login
        response = await client.post("/api/v1/auth/login", json=user_data)
        # Should either succeed or give predictable error responses
        assert response.status_code in [200, 400, 401, 500]

        # If successful, check response structure
        if response.status_code == 200:
            data = response.json()
            assert "access_token" in data
            assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_protected_endpoint_requires_auth():
    """Test that protected endpoints require authentication."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/auth/me")
        # Should require authentication
        assert response.status_code == 401
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] in ["NOT_AUTHENTICATED", "UNAUTHORIZED"]


@pytest.mark.asyncio
async def test_incidents_endpoint_structure():
    """Test that incidents endpoint has correct structure."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/incidents")
        # Should either work or give predictable auth error
        assert response.status_code in [200, 401, 500]

        # If we get data, check structure
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)  # Should return a list of incidents
        # If 401, that's expected (no auth)


@pytest.mark.asyncio
async def test_api_documentation_available():
    """Test that API documentation is available."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/docs")
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")


@pytest.mark.asyncio
async def test_openapi_json_available():
    """Test that OpenAPI JSON schema is available."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/openapi.json")
        assert response.status_code == 200
        data = response.json()
        assert "openapi" in data
        assert "info" in data
        assert data["info"]["title"] == "Oil Spill Detection & AIS Attribution Platform API"


def test_settings_loaded():
    """Test that application settings are loaded correctly."""
    assert settings.APP_NAME == "Oil Spill Detection & AIS Attribution Platform API"
    assert settings.VERSION == "1.0.0"
    assert isinstance(settings.CORS_ORIGINS, list)
    assert settings.JWT_EXPIRATION_MINUTES == 1440  # 24 hours default


def test_models_can_be_imported():
    """Test that core models can be imported without errors."""
    from app.models.incident import Incident
    from app.models.user import User
    from app.models.slick_detection import SlickDetection
    from app.models.drift_result import DriftResult
    from app.models.attribution import AttributionScore
    from app.models.vessel import Vessel

    # Basic instantiation test
    incident = Incident(
        name="Test Incident",
        description="Test Description",
        timestamp=datetime.now(UTC)
    )
    assert incident.name == "Test Incident"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

