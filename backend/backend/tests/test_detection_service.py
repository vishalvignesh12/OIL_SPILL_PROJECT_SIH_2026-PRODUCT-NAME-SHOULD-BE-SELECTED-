"""
Unit tests for the detection service.
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from uuid import uuid4
from datetime import datetime, UTC

from app.services.detection_service import analyze_slick
from app.models.slick_detection import SlickDetection
from app.models.inference_log import MLInferenceLog
from app.models.incident import Incident
from app.models.satellite_scene import SatelliteScene
from app.schemas.detection import AnalyzeRequest
from app.schemas.scene import GeoJSONPolygon


@pytest.mark.asyncio
async def test_analyze_slick_creates_incident_and_scene():
    """Test that analyze_slick creates incident and scene when they don't exist."""
    # Setup
    db = AsyncMock()
    req = AnalyzeRequest(
        scene_id="test_scene_001",
        image_url="http://example.com/image.jpg",
        timestamp=datetime.now(UTC)
    )
    
    # Mock database query results - return None for existing incident/scene
    async def mock_execute(stmt):
        mock_result = Mock()
        mock_result.scalars.return_value.first.return_value = None
        return mock_result
    
    db.execute.side_effect = mock_execute
    db.flush = AsyncMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()
    
    # Mock satellite adapter
    with patch('app.services.detection_service.FixtureSatelliteAdapter') as mock_adapter_class:
        mock_adapter = AsyncMock()
        mock_adapter.analyze_scene.return_value = {
            "detection_id": uuid4(),
            "slick_polygon": {
                "type": "Polygon",
                "coordinates": [[
                    [76.10, 9.80],
                    [76.12, 9.81],
                    [76.15, 9.85],
                    [76.13, 9.86],
                    [76.09, 9.82],
                    [76.10, 9.80]
                ]]
            },
            "area_km2": 12.42,
            "length_km": 8.21,
            "width_km": 1.42,
            "orientation_deg": 73.0,
            "confidence": 0.94,
            "age_estimate_hours": 18.0,
            "age_confidence": "HIGH"
        }
        mock_adapter_class.return_value = mock_adapter
        
        # Execute
        result = await analyze_slick(db, req)
        
        # Verify
        assert isinstance(result, SlickDetection)
        assert result.confidence == 0.94
        assert result.area_km2 == 12.42
        assert result.length_km == 8.21
        assert result.width_km == 1.42
        assert result.orientation_deg == 73.0
        assert result.age_estimate_hours == 18.0
        assert result.age_confidence == "HIGH"
        
        # Verify that incident and scene were created
        assert db.add.call_count >= 2  # At least incident and scene
        assert db.commit.called


@pytest.mark.asyncio
async def test_analyze_slick_uses_existing_incident_and_scene():
    """Test that analyze_slick uses existing incident and scene when they exist."""
    # Setup
    db = AsyncMock()
    existing_incident_id = uuid4()
    existing_scene_id = uuid4()
    
    req = AnalyzeRequest(
        scene_id=str(existing_scene_id),
        image_url="http://example.com/image.jpg",
        timestamp=datetime.now(UTC)
    )
    
    # Mock existing incident and scene
    existing_incident = Mock(spec=Incident)
    existing_incident.id = existing_incident_id
    
    existing_scene = Mock(spec=SatelliteScene)
    existing_scene.id = existing_scene_id
    
    # Mock database query results
    async def mock_execute(stmt):
        mock_result = Mock()
        if "Incident" in str(stmt) and "name.like" in str(stmt):
            mock_result.scalars.return_value.first.return_value = existing_incident
        elif "SatelliteScene" in str(stmt) and "id==" in str(stmt):
            mock_result.scalars.return_value.first.return_value = existing_scene
        else:
            mock_result.scalars.return_value.first.return_value = None
        return mock_result
    
    db.execute.side_effect = mock_execute
    db.flush = AsyncMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()
    
    # Mock satellite adapter
    with patch('app.services.detection_service.FixtureSatelliteAdapter') as mock_adapter_class:
        mock_adapter = AsyncMock()
        mock_adapter.analyze_scene.return_value = {
            "detection_id": uuid4(),
            "slick_polygon": {
                "type": "Polygon",
                "coordinates": [[
                    [76.10, 9.80],
                    [76.12, 9.81],
                    [76.15, 9.85],
                    [76.13, 9.86],
                    [76.09, 9.82],
                    [76.10, 9.80]
                ]]
            },
            "area_km2": 12.42,
            "length_km": 8.21,
            "width_km": 1.42,
            "orientation_deg": 73.0,
            "confidence": 0.94,
            "age_estimate_hours": 18.0,
            "age_confidence": "HIGH"
        }
        mock_adapter_class.return_value = mock_adapter
        
        # Execute
        result = await analyze_slick(db, req)
        
        # Verify
        assert isinstance(result, SlickDetection)
        assert result.incident_id == existing_incident_id
        assert result.scene_id == existing_scene_id
        assert result.confidence == 0.94


if __name__ == "__main__":
    pytest.main([__file__])
