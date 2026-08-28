import pytest
from unittest.mock import Mock, AsyncMock, patch
from uuid import uuid4
from datetime import datetime, UTC

from app.services.detection_service import analyze_slick
from app.models.slick_detection import SlickDetection
from app.models.incident import Incident
from app.models.satellite_scene import SatelliteScene
from app.schemas.detection import AnalyzeRequest


def make_db_result(value):
    result = Mock()
    result.scalars.return_value.first.return_value = value
    return result


def detection_result():
    return {
        "detection_id": uuid4(),
        "slick_polygon": {
            "type": "Polygon",
            "coordinates": [[
                [76.10, 9.80],
                [76.12, 9.81],
                [76.15, 9.85],
                [76.13, 9.86],
                [76.09, 9.82],
                [76.10, 9.80],
            ]],
        },
        "area_km2": 12.42,
        "length_km": 8.21,
        "width_km": 1.42,
        "orientation_deg": 73.0,
        "confidence": 0.94,
        "age_estimate_hours": 18.0,
        "age_confidence": "HIGH",
    }


@pytest.mark.asyncio
async def test_analyze_slick_creates_incident_and_scene():
    db = AsyncMock()

    req = AnalyzeRequest(
        scene_id="test_scene_001",
        image_url="http://example.com/image.jpg",
        timestamp=datetime.now(UTC),
    )

    db.execute.side_effect = [
        make_db_result(None),
    ]

    db.flush = AsyncMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()

    with patch(
        "app.services.detection_service.FixtureSatelliteAdapter"
    ) as mock_adapter_class:

        mock_adapter = AsyncMock()
        mock_adapter.analyze_scene.return_value = detection_result()
        mock_adapter_class.return_value = mock_adapter

        result = await analyze_slick(db, req)

    assert isinstance(result, SlickDetection)
    assert result.confidence == 0.94
    assert result.area_km2 == 12.42
    assert result.length_km == 8.21
    assert result.width_km == 1.42
    assert result.orientation_deg == 73.0
    assert result.age_estimate_hours == 18.0
    assert result.age_confidence == "HIGH"

    assert db.add.call_count >= 4
    db.commit.assert_awaited_once()
    db.refresh.assert_awaited_once()


@pytest.mark.asyncio
async def test_analyze_slick_uses_existing_incident_and_scene():
    db = AsyncMock()

    existing_incident_id = uuid4()
    existing_scene_id = uuid4()

    req = AnalyzeRequest(
        scene_id=str(existing_scene_id),
        image_url="http://example.com/image.jpg",
        timestamp=datetime.now(UTC),
    )

    existing_incident = Mock(spec=Incident)
    existing_incident.id = existing_incident_id

    existing_scene = Mock(spec=SatelliteScene)
    existing_scene.id = existing_scene_id

    # First query = Incident
    # Second query = SatelliteScene
    db.execute.side_effect = [
        make_db_result(existing_incident),
        make_db_result(existing_scene),
    ]

    db.flush = AsyncMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()

    with patch(
        "app.services.detection_service.FixtureSatelliteAdapter"
    ) as mock_adapter_class:

        mock_adapter = AsyncMock()
        mock_adapter.analyze_scene.return_value = detection_result()
        mock_adapter_class.return_value = mock_adapter

        result = await analyze_slick(db, req)

    assert isinstance(result, SlickDetection)
    assert result.incident_id == existing_incident_id
    assert result.scene_id == existing_scene_id
    assert result.confidence == 0.94

    db.commit.assert_awaited_once()
    db.refresh.assert_awaited_once()