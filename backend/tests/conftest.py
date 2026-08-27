"""
Pytest configuration and shared fixtures.
"""
import pytest
import asyncio
from unittest.mock import AsyncMock

@pytest.fixture
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def db_session():
    """Create a mock database session."""
    return AsyncMock()


@pytest.fixture
def sample_incident_id():
    """Create a sample incident ID."""
    from uuid import uuid4
    return uuid4()


@pytest.fixture
def sample_geo_point():
    """Create a sample GeoJSON point."""
    from app.schemas.incident import GeoJSONPoint
    return GeoJSONPoint(coordinates=(75.98, 9.72))


@pytest.fixture
def sample_bbox():
    """Create a sample bounding box."""
    from app.schemas.scene import GeoJSONPolygon
    return GeoJSONPolygon(coordinates=[[
        [75.80, 9.50],
        [76.40, 9.50],
        [76.40, 10.10],
        [75.80, 10.10],
        [75.80, 9.50]
    ]])
