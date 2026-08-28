from unittest.mock import Mock, AsyncMock, patch
from uuid import UUID
from datetime import datetime, UTC
from fastapi import status
from fastapi.testclient import TestClient

from app.main import app
from app.core.security import require_analyst
from app.schemas.scene import SceneCreate, GeoJSONPolygon

# Override the authentication dependency for testing
app.dependency_overrides[require_analyst] = lambda: Mock()
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

print("Sending request with data:")
import json
print(json.dumps(scene_data, indent=2))

with patch('app.services.satellite_ingestion_service.ingest_satellite_scene') as mock_ingest:
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
    
    print(f"Status code: {response.status_code}")
    print(f"Response headers: {dict(response.headers)}")
    print(f"Response content: {response.text}")
    try:
        print(f"Response JSON: {response.json()}")
    except:
        print("Could not parse response as JSON")
    
    # Clean up
    app.dependency_overrides.clear()
