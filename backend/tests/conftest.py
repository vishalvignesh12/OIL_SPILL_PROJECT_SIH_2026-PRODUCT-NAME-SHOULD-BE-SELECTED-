"""
Pytest configuration and shared fixtures.
"""

import pytest
from unittest.mock import Mock
from httpx import ASGITransport, AsyncClient


@pytest.fixture
def db_session():
    """Create a mock database session."""
    return Mock()


@pytest.fixture
def sample_incident_id():
    """Create a sample incident ID."""
    from uuid import uuid4

    return uuid4()


@pytest.fixture
def sample_geo_point():
    """Create a sample GeoJSON point."""
    from app.schemas.incident import GeoJSONPoint

    return GeoJSONPoint(
        coordinates=(75.98, 9.72)
    )


@pytest.fixture
def sample_bbox():
    """Create a sample bounding box."""
    from app.schemas.scene import GeoJSONPolygon

    return GeoJSONPolygon(
        coordinates=[[
            [75.80, 9.50],
            [76.40, 9.50],
            [76.40, 10.10],
            [75.80, 10.10],
            [75.80, 9.50],
        ]]
    )


@pytest.fixture
async def async_client():
    """Create an async HTTPX client for the FastAPI application."""
    from app.main import app

    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        yield client