"""
Test suite for scenes API endpoints.
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from uuid import UUID
from datetime import datetime, UTC
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from app.core.security import require_analyst
from app.core.database import get_db
from app.schemas.scene import SceneCreate, GeoJSONPolygon


@pytest.fixture
def mock_db_session():
    """Create a mock database session."""
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def client(mock_db_session):
    """Create test client with authentication and database overrides."""
    # Override the authentication dependency for testing
    app.dependency_overrides[require_analyst] = lambda: Mock()
    # Override the database dependency for testing
    app.dependency_overrides[get_db] = lambda: mock_db_session
    yield TestClient(app)
    # Clean up after test
    app.dependency_overrides.clear()


def test_ingest_scene_endpoint(client, mock_db_session):
    """Test the satellite scene ingestion endpoint."""
    scene_data = {
        "source": "sentinel-1-replay",
        "scene_id": "S1A_20250615_001",
        "satellite": "Sentinel-1",
        "sensor": "SAR",
        "product_type": "GRD",
        "polarization": "VV",
        "acquisition_time": datetime.now(UTC).isoformat(),
        "bbox": {
            "type": "Polygon",
            "coordinates": [[
                [74.0, 12.0],
                [74.5, 12.0],
                [74.5, 12.5],
                [74.0, 12.5],
                [74.0, 12.0]
            ]]
        },
        "image_url": "http://example.com/image.tif"
    }

    # Mock the validation to return valid data
    validated_data = {
        "source": "sentinel-1-replay",
        "scene_id": "S1A_20250615_001",
        "satellite": "Sentinel-1",
        "sensor": "SAR",
        "product_type": "GRD",
        "polarization": "VV",
        "acquisition_time": datetime.now(UTC),
        "processing_time": None,
        "bbox": GeoJSONPolygon(
            type="Polygon",
            coordinates=[[
                [74.0, 12.0],
                [74.5, 12.0],
                [74.5, 12.5],
                [74.0, 12.5],
                [74.0, 12.0]
            ]]
        ),
        "image_url": "http://example.com/image.tif",
        "thumbnail_url": None,
        "scene_metadata": {},
        "status": "RECEIVED"
    }

    # Mock the scene object that would be returned from persist_satellite_scene
    mock_scene = Mock()
    mock_scene.scene_id = "S1A_20250615_001"
    mock_scene.id = UUID("12345678-1234-5678-1234-567812345678")
    mock_scene.status = "QUEUED"

    with patch('app.services.satellite_ingestion_service.validate_scene_metadata', return_value=validated_data), \
         patch('app.services.satellite_ingestion_service.check_duplicate_scene', return_value=False), \
         patch('app.services.satellite_ingestion_service.persist_satellite_scene', return_value=mock_scene), \
         patch('app.services.satellite_ingestion_service.create_analysis_job', return_value="test-analysis-id"), \
         patch('app.services.satellite_ingestion_service.log_inference'):

        response = client.post(
            "/api/v1/scenes/ingest",
            json=scene_data
        )

        assert response.status_code == status.HTTP_202_ACCEPTED
        data = response.json()
        assert data["success"] is True
        assert data["scene_id"] == "S1A_20250615_001"
        assert data["analysis_id"] == "test-analysis-id"
        assert data["status"] == "QUEUED"
        assert data["is_duplicate"] is False


def test_ingest_scene_endpoint_duplicate(client, mock_db_session):
    """Test the satellite scene ingestion endpoint with duplicate."""
    scene_data = {
        "source": "sentinel-1-replay",
        "scene_id": "S1A_20250615_001",
        "satellite": "Sentinel-1",
        "sensor": "SAR",
        "product_type": "GRD",
        "polarization": "VV",
        "acquisition_time": datetime.now(UTC).isoformat(),
        "bbox": {
            "type": "Polygon",
            "coordinates": [[
                [74.0, 12.0],
                [74.5, 12.0],
                [74.5, 12.5],
                [74.0, 12.5],
                [74.0, 12.0]
            ]]
        },
        "image_url": "http://example.com/image.tif"
    }

    # Mock the validation to return valid data
    validated_data = {
        "source": "sentinel-1-replay",
        "scene_id": "S1A_20250615_001",
        "satellite": "Sentinel-1",
        "sensor": "SAR",
        "product_type": "GRD",
        "polarization": "VV",
        "acquisition_time": datetime.now(UTC),
        "processing_time": None,
        "bbox": GeoJSONPolygon(
            type="Polygon",
            coordinates=[[
                [74.0, 12.0],
                [74.5, 12.0],
                [74.5, 12.5],
                [74.0, 12.5],
                [74.0, 12.0]
            ]]
        ),
        "image_url": "http://example.com/image.tif",
        "thumbnail_url": None,
        "scene_metadata": {},
        "status": "RECEIVED"
    }

    # Mock existing scene
    mock_existing_scene = Mock()
    mock_existing_scene.scene_id = "S1A_20250615_001"
    mock_existing_scene.id = UUID("12345678-1234-5678-1234-567812345678")
    mock_existing_scene.status = "INGESTED"

    with patch('app.services.satellite_ingestion_service.validate_scene_metadata', return_value=validated_data), \
         patch('app.services.satellite_ingestion_service.check_duplicate_scene', return_value=True), \
         patch('app.services.satellite_ingestion_service.select') as mock_select:

        # Mock the select query for duplicate check
        mock_result = Mock()
        mock_result.scalars().first.return_value = mock_existing_scene
        mock_db_session.execute.return_value = mock_result

        response = client.post(
            "/api/v1/scenes/ingest",
            json=scene_data
        )

        assert response.status_code == status.HTTP_202_ACCEPTED
        data = response.json()
        assert data["success"] is True
        assert data["scene_id"] == "S1A_20250615_001"
        assert data["is_duplicate"] is True
        assert "already exists" in data["message"]


def test_ingest_scene_endpoint_invalid_data(client):
    """Test the satellite scene ingestion endpoint with invalid data."""
    scene_data = {
        "source": "",  # Invalid: empty source
        "scene_id": "S1A_20250615_001",
        "satellite": "Sentinel-1",
        "sensor": "SAR",
        "product_type": "GRD",
        "polarization": "VV",
        "acquisition_time": datetime.now(UTC).isoformat(),
        "bbox": {
            "type": "Polygon",
            "coordinates": [[
                [74.0, 12.0],
                [74.5, 12.0],
                [74.5, 12.5],
                [74.0, 12.5],
                [74.0, 12.0]
            ]]
        },
        "image_url": "http://example.com/image.tif"
    }

    response = client.post(
        "/api/v1/scenes/ingest",
        json=scene_data
    )

    # Should return 422 Unprocessable Entity for validation errors
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


if __name__ == "__main__":
    pytest.main([__file__, "-v"])