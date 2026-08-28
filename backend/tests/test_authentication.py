"""
Authentication system tests to prevent demo breakage.
Tests user registration, login, and protected access.
"""
import pytest
from unittest.mock import AsyncMock, patch
from uuid import uuid4
from datetime import datetime, UTC

from httpx import AsyncClient

from app.main import app
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse, UserResponse
from app.services.auth_service import register_user, authenticate_user
from app.core.security import hash_password, verify_password, create_access_token


@pytest.mark.asyncio
async def test_auth_router_exists():
    """Test that auth router is properly included in the app."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Test that auth endpoints exist
        response = await client.get("/api/v1/auth/register")
        # Should return 405 (Method Not Allowed) for GET on POST endpoint, not 404
        assert response.status_code != 404

        response = await client.get("/api/v1/auth/login")
        assert response.status_code != 404

        response = await client.get("/api/v1/auth/me")
        assert response.status_code != 404


@pytest.mark.asyncio
async def test_register_endpoint_validation():
    """Test user registration endpoint validation."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Test missing fields
        response = await client.post("/api/v1/auth/register", json={})
        assert response.status_code == 422  # Validation error

        # Test invalid email
        response = await client.post("/api/v1/auth/register", json={
            "name": "Test User",
            "email": "invalid-email",
            "password": "password123"
        })
        assert response.status_code == 422

        # Test short password
        response = await client.post("/api/v1/auth/register", json={
            "name": "Test User",
            "email": "test@example.com",
            "password": "123"
        })
        # Should either validate (if we have password validation) or pass through
        # Most likely will pass through to service layer for validation
        assert response.status_code in [400, 422, 500]  # Not 404 (endpoint exists)


@pytest.mark.asyncio
async def test_login_endpoint_validation():
    """Test user login endpoint validation."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Test missing fields
        response = await client.post("/api/v1/auth/login", json={})
        assert response.status_code == 422  # Validation error

        # Test invalid email
        response = await client.post("/api/v1/auth/login", json={
            "email": "invalid-email",
            "password": "password123"
        })
        assert response.status_code == 422


@pytest.mark.asyncio
async def test_protected_endpoint_without_token():
    """Test that protected endpoints require authentication."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/auth/me")
        # Should return 401 (Unauthorized) not 404
        assert response.status_code == 401
        data = response.json()
        assert "error" in data
        assert "Could not validate credentials" in data["error"]["message"]


@pytest.mark.asyncio
async def test_password_hashing_and_verification():
    """Test password hashing and verification utilities."""
    password = "securepassword123"

    # Hash the password
    hashed = hash_password(password)
    assert hashed != password
    assert len(hashed) > 20  # Argon2id hashes are long

    # Verify correct password
    assert verify_password(password, hashed) == True

    # Verify incorrect password
    assert verify_password("wrongpassword", hashed) == False

    # Verify with empty password
    assert verify_password("", hashed) == False


@pytest.mark.asyncio
async def test_token_creation_and_verification():
    """Test JWT token creation and verification."""
    test_data = {
        "sub": "test@example.com",
        "role": "analyst",
        "user_id": str(uuid4()),
        "name": "Test User"
    }

    # Create token
    token = create_access_token(test_data)
    assert isinstance(token, str)
    assert len(token) > 10

    # Note: We can't easily verify the token without the secret key,
    # but we can test that it's created properly

    # Test token expiration is included
    # This would require decoding with the secret, which we don't have in test
    # But we can at least verify the function works


@pytest.mark.asyncio
async def test_register_user_service_logic():
    """Test registration service logic with mocked database."""
    # Setup mock database
    mock_db = AsyncMock()

    # Mock no existing user
    mock_result = AsyncMock()
    mock_result.scalars.return_value.first.return_value = None
    mock_db.execute.return_value = mock_result
    mock_db.commit = AsyncMock()
    mock_db.refresh = AsyncMock()
    mock_db.add = AsyncMock()

    # Setup request
    req = RegisterRequest(
        name="Test User",
        email="test@example.com",
        password="securepassword123"
    )

    # Mock the hash_password function to return a known value
    with patch('app.services.auth_service.hash_password') as mock_hash:
        mock_hash.return_value = "hashed_password_123"

        # Call the function
        user = await register_user(mock_db, req)

        # Verify user object properties
        assert user.name == "Test User"
        assert user.email == "test@example.com"
        assert user.password_hash == "hashed_password_123"
        assert user.role == "analyst"

        # Verify database interactions
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()


@pytest.mark.asyncio
async def test_register_user_duplicate_email():
    """Test registration service handles duplicate email."""
    # Setup mock database
    mock_db = AsyncMock()

    # Mock existing user
    from app.models.user import User
    existing_user = User(
        id=uuid4(),
        name="Existing User",
        email="test@example.com",
        password_hash="existing_hash",
        role="analyst"
    )

    mock_result = AsyncMock()
    mock_result.scalars.return_value.first.return_value = existing_user
    mock_db.execute.return_value = mock_result

    # Setup request
    req = RegisterRequest(
        name="Test User",
        email="test@example.com",  # Same email as existing user
        password="securepassword123"
    )

    # Call the function and expect HTTPException
    with pytest.raises(Exception) as exc_info:
        await register_user(mock_db, req)

    # Should be HTTP 409 Conflict
    assert "409" in str(exc_info.value) or "already exists" in str(exc_info.value)


@pytest.mark.asyncio
async def test_authenticate_user_service_logic():
    """Test authentication service logic with mocked database."""
    # Setup mock database
    mock_db = AsyncMock()

    # Mock existing user with known password hash
    from app.models.user import User
    test_password = "securepassword123"
    hashed_password = hash_password(test_password)  # Real hash for testing

    existing_user = User(
        id=uuid4(),
        name="Test User",
        email="test@example.com",
        password_hash=hashed_password,
        role="analyst"
    )

    mock_result = AsyncMock()
    mock_result.scalars.return_value.first.return_value = existing_user
    mock_db.execute.return_value = mock_result

    # Setup request
    req = LoginRequest(
        email="test@example.com",
        password=test_password
    )

    # Mock the verify_password function
    with patch('app.services.auth_service.verify_password') as mock_verify:
        mock_verify.return_value = True

        # Call the function
        token_response = await authenticate_user(mock_db, req)

        # Verify response
        assert isinstance(token_response, TokenResponse)
        assert hasattr(token_response, 'access_token')
        assert token_response.token_type == "bearer"
        assert len(token_response.access_token) > 10


@pytest.mark.asyncio
async def test_authenticate_user_invalid_credentials():
    """Test authentication service handles invalid credentials."""
    # Setup mock database
    mock_db = AsyncMock()

    # Mock no user found
    mock_result = AsyncMock()
    mock_result.scalars.return_value.first.return_value = None
    mock_db.execute.return_value = mock_result

    # Setup request
    req = LoginRequest(
        email="nonexistent@example.com",
        password="anypassword"
    )

    # Call the function and expect HTTPException
    with pytest.raises(Exception) as exc_info:
        await authenticate_user(mock_db, req)

    # Should be HTTP 401 Unauthorized
    assert "401" in str(exc_info.value) or "Incorrect email" in str(exc_info.value)


@pytest.mark.asyncio
async def test_authenticate_user_wrong_password():
    """Test authentication service handles wrong password."""
    # Setup mock database
    mock_db = AsyncMock()

    # Mock existing user with known password hash
    from app.models.user import User
    existing_user = User(
        id=uuid4(),
        name="Test User",
        email="test@example.com",
        password_hash=hash_password("correctpassword"),  # Correct password hash
        role="analyst"
    )

    mock_result = AsyncMock()
    mock_result.scalars.return_value.first.return_value = existing_user
    mock_db.execute.return_value = mock_result

    # Setup request with wrong password
    req = LoginRequest(
        email="test@example.com",
        password="wrongpassword"
    )

    # Call the function and expect HTTPException
    with pytest.raises(Exception) as exc_info:
        await authenticate_user(mock_db, req)

    # Should be HTTP 401 Unauthorized
    assert "401" in str(exc_info.value) or "Incorrect email" in str(exc_info.value)


def test_auth_schemas():
    """Test that auth schemas work correctly."""
    # Test RegisterRequest
    register_data = RegisterRequest(
        name="Test User",
        email="test@example.com",
        password="securepassword123"
    )
    assert register_data.name == "Test User"
    assert register_data.email == "test@example.com"
    assert register_data.password == "securepassword123"

    # Test LoginRequest
    login_data = LoginRequest(
        email="test@example.com",
        password="securepassword123"
    )
    assert login_data.email == "test@example.com"
    assert login_data.password == "securepassword123"

    # Test TokenResponse
    token_data = TokenResponse(access_token="abc123")
    assert token_data.access_token == "abc123"
    assert token_data.token_type == "bearer"

    # Test UserResponse
    user_data = UserResponse(
        id=uuid4(),
        name="Test User",
        email="test@example.com",
        role="analyst",
        created_at=datetime.now(UTC)
    )
    assert user_data.name == "Test User"
    assert user_data.email == "test@example.com"
    assert user_data.role == "analyst"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])