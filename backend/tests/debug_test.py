from unittest.mock import Mock, AsyncMock, patch
from uuid import UUID
from datetime import datetime, UTC
from fastapi import status
from fastapi.testclient import TestClient

from app.main import app
from app.core.database import get_db
from app.core.security import require_analyst

def test_debug_scene_ingest():
    app.dependency_overrides[require_analyst] = lambda: Mock()
    app.dependency_overrides[get_db] = lambda: AsyncMock()
    client = TestClient(app)

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

    with patch('app.api.v1.scenes.ingest_satellite_scene') as mock_ingest:
        mock_ingest.return_value = {
            "success": True,
            "scene_id": "S1A_20250615_001",
            "analysis_id": "test-analysis-id",
            "status": "QUEUED",
            "message": "Satellite scene successfully ingested and queued for analysis",
            "is_duplicate": False
        }

        response = client.post(
            "/api/v1/scenes/ingest",
            json=scene_data
        )

        assert response.status_code in [200, 202]

        app.dependency_overrides.clear()
