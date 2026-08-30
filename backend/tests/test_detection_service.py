"""
Unit tests for the detection service.
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from uuid import uuid4, UUID
from datetime import datetime, UTC

from app.services.detection_service import analyze_slick
from app.models.slick_detection import SlickDetection
from app.models.incident import Incident
from app.models.satellite_scene import SatelliteScene
from app.schemas.detection import AnalyzeRequest


def make_db_result(value):
    """Create a mock database result."""
    result = Mock()
    result.scalars.return_value.first.return_value = value
    result.scalar_one_or_none.return_value = value
    return result


def detection_result():
    """Return a sample detection result in PRD format."""
    return {
        "analysis_id": "ANL_0001",
        "scene_id": "test_scene_001",
        "status": "COMPLETED",
        "oil_spill_detected": True,
        "confidence": 0.94,
        "model_version": "test-v1",
        "processing_time_ms": 100,
        "source_scene_id": "test_scene_001",
        "length_km": 8.21,
        "width_km": 1.42,
        "orientation_deg": 73.0,
        "age_estimate_hours": 18.0,
        "age_confidence": "HIGH",
        "spill_regions": [
            {
                "region_id": "region_001",
                "confidence": 0.94,
                "area_m2": 12420000.0,  # 12.42 km2 in m2
                "centroid": {
                    "lat": 9.828,
                    "lon": 76.118
                },
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[
                        [76.10, 9.80],
                        [76.12, 9.81],
                        [76.15, 9.85],
                        [76.13, 9.86],
                        [76.09, 9.82],
                        [76.10, 9.80]  # Closed polygon
                    ]]
                },
                "bbox": {
                    "min_lat": 9.80,
                    "min_lon": 76.09,
                    "max_lat": 9.86,
                    "max_lon": 76.15
                },
                "mask_uri": "storage://predictions/test_scene_001_mask.png",
                "prediction_uri": "storage://predictions/test_scene_001_prediction.geojson"
            }
        ]
    }


def _stmt_target_type(stmt):
    """Return the mapped class that a SQLAlchemy select() targets, or None."""
    cd = getattr(stmt, "column_descriptions", None)
    if cd:
        return cd[0].get("type")
    return None


@pytest.mark.asyncio
async def test_analyze_slick_creates_incident_and_scene():
    """Test that analyze_slick creates incident and scene when they don't exist."""
    # Setup
    db = AsyncMock()
    db.add = Mock()
    req = AnalyzeRequest(
        scene_id="test_scene_001",
        image_url="http://example.com/image.jpg",
        timestamp=datetime.now(UTC)
    )

    # No existing incident or scene in the database
    async def mock_execute(stmt):
        mock_result = Mock()
        mock_result.scalars.return_value.first.return_value = None
        mock_result.scalar_one_or_none.return_value = None
        return mock_result

    db.execute.side_effect = mock_execute
    db.flush = AsyncMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()

    # Mock ML provider
    with patch('app.services.detection_service.get_ml_provider') as mock_provider_factory:
        mock_provider = AsyncMock()
        mock_provider.predict.return_value = {
            "detected": True,
            "confidence": 0.94,
            "area_km2": 12.42,
            "geometry": {
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
            "model_name": "oilspill-detector",
            "model_version": "fixture-v1",
            "length_km": 8.21,
            "width_km": 1.42,
            "orientation_deg": 73.0,
            "age_estimate_hours": 18.0,
            "age_confidence": "HIGH"
        }
        mock_provider_factory.return_value = mock_provider

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

        # Verify that incident and scene were created (add called at least twice)
        assert db.add.call_count >= 2
        assert db.commit.called


@pytest.mark.asyncio
async def test_analyze_slick_uses_existing_incident_and_scene():
    """Test that analyze_slick uses existing incident and scene when they exist."""
    # Setup
    db = AsyncMock()
    db.add = Mock()
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
    existing_incident.name = f"Incident for Scene {existing_scene_id}"

    existing_scene = Mock(spec=SatelliteScene)
    existing_scene.id = existing_scene_id
    existing_scene.scene_id = str(existing_scene_id)

    # Structural database query dispatch using SQLAlchemy Select AST inspection
    async def mock_execute(stmt):
        mock_result = Mock()
        target = _stmt_target_type(stmt)

        if target is Incident:
            mock_result.scalars.return_value.first.return_value = existing_incident
            mock_result.scalar_one_or_none.return_value = existing_incident
        elif target is SatelliteScene:
            mock_result.scalars.return_value.first.return_value = existing_scene
            mock_result.scalar_one_or_none.return_value = existing_scene
        else:
            mock_result.scalars.return_value.first.return_value = None
            mock_result.scalar_one_or_none.return_value = None
        return mock_result

    db.execute.side_effect = mock_execute
    db.flush = AsyncMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()

    # Mock ML provider
    with patch('app.services.detection_service.get_ml_provider') as mock_provider_factory:
        mock_provider = AsyncMock()
        mock_provider.predict.return_value = {
            "detected": True,
            "confidence": 0.94,
            "area_km2": 12.42,
            "geometry": {
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
            "model_name": "oilspill-detector",
            "model_version": "fixture-v1"
        }
        mock_provider_factory.return_value = mock_provider

        # Execute
        result = await analyze_slick(db, req)

        # Verify
        assert isinstance(result, SlickDetection)
        assert result.incident_id == existing_incident_id
        assert result.scene_id == existing_scene_id
        assert result.confidence == 0.94


if __name__ == "__main__":
    pytest.main([__file__])
