import pytest
from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.dashboard_service import DashboardService
from app.models.incident import Incident
from app.models.slick_detection import SlickDetection
from app.models.attribution import AttributionScore
from app.models.vessel import Vessel
from app.models.drift_result import DriftResult
from app.models.ais_track import AISTrack
from app.models.spill_region import SpillRegion


@pytest.mark.asyncio
async def test_dashboard_overview_empty_db():
    """Test dashboard overview with empty database."""
    # Mock database session
    db = AsyncMock(spec=AsyncSession)

    # Mock all count queries to return 0
    mock_result = MagicMock()
    mock_result.scalar.return_value = 0
    db.execute.return_value = mock_result

    service = DashboardService(db)
    result = await service.get_overview()

    assert result.total_incidents == 0
    assert result.active_incidents == 0
    assert result.detected_spills == 0
    assert result.total_spill_area_km2 == 0.0
    assert result.analyses_completed == 0
    assert result.analyses_processing == 0
    assert result.analyses_failed == 0
    assert result.high_confidence_spills == 0


@pytest.mark.asyncio
async def test_dashboard_overview_with_data():
    """Test dashboard overview with sample data."""
    # Mock database session
    db = AsyncMock(spec=AsyncSession)

    # Mock different count queries to return different values in order
    call_count = 0
    def mock_execute_side_effect(*args, **kwargs):
        nonlocal call_count
        mock_result = MagicMock()

        # Return values in the order the queries are executed
        if call_count == 0:
            mock_result.scalar.return_value = 10  # total_incidents
        elif call_count == 1:
            mock_result.scalar.return_value = 3   # active_incidents
        elif call_count == 2:
            mock_result.scalar.return_value = 8   # detected_spills (count)
        elif call_count == 3:
            mock_result.scalar.return_value = 150.5  # total_spill_area (sum)
        elif call_count == 4:
            mock_result.scalar.return_value = 6      # analyses_completed (confidence >= 0.8)
        elif call_count == 5:
            mock_result.scalar.return_value = 2      # analyses_processing (confidence < 0.8)
        elif call_count == 6:
            mock_result.scalar.return_value = 6      # high_confidence_spills (confidence >= 0.8) - duplicate
        else:
            mock_result.scalar.return_value = 0      # default

        call_count += 1
        return mock_result

    db.execute.side_effect = mock_execute_side_effect

    service = DashboardService(db)
    result = await service.get_overview()

    assert result.total_incidents == 10
    assert result.active_incidents == 3
    assert result.detected_spills == 8
    assert result.total_spill_area_km2 == 150.5
    assert result.analyses_completed == 6
    assert result.analyses_processing == 2
    assert result.analyses_failed == 0
    assert result.high_confidence_spills == 6


@pytest.mark.asyncio
async def test_dashboard_incidents_pagination():
    """Test dashboard incidents with pagination."""
    # Mock database session
    db = AsyncMock(spec=AsyncSession)

    # Mock count query
    count_result = MagicMock()
    count_result.scalar.return_value = 25  # 25 total incidents

    # Mock data query
    from datetime import datetime, timezone
    data_result = MagicMock()
    data_result.all.return_value = [
        (uuid4(), "DETECTED", datetime(2026, 8, 29, 10, 32, 0, tzinfo=timezone.utc), 0.94, 12.4, None),  # location is None for simplicity
        (uuid4(), "INVESTIGATING", datetime(2026, 8, 29, 9, 15, 0, tzinfo=timezone.utc), 0.87, 8.2, None)
    ]

    # Configure mock to return count first, then data
    db.execute.side_effect = [count_result, data_result]

    service = DashboardService(db)
    result = await service.get_incidents(page=1, page_size=20)

    assert result.page == 1
    assert result.page_size == 20
    assert result.total == 25
    assert len(result.items) == 2

    # Check first item
    assert result.items[0].status == "DETECTED"
    assert result.items[0].confidence == 0.94
    assert result.items[0].area_km2 == 12.4
    assert result.items[0].detected_at == "2026-08-29T10:32:00+00:00"


@pytest.mark.asyncio
async def test_dashboard_spills_geojson():
    """Test dashboard spills returns valid GeoJSON."""
    # Mock database session
    db = AsyncMock(spec=AsyncSession)

    # Mock spill regions query result
    mock_result = MagicMock()
    mock_result.all.return_value = [
        (uuid4(), uuid4(), 0, None, 12400000.0, 0.94, uuid4(), uuid4(), uuid4())  # area_m2 = 12.4 km2
    ]
    db.execute.return_value = mock_result

    service = DashboardService(db)
    result = await service.get_spills()

    assert result.type == "FeatureCollection"
    assert len(result.features) == 1

    feature = result.features[0]
    assert feature["type"] == "Feature"
    assert feature["geometry"]["type"] == "Polygon"
    assert "properties" in feature
    assert feature["properties"]["incident_id"] is not None
    assert feature["properties"]["area_km2"] == 12.4  # Converted from m2 to km2
    assert feature["properties"]["confidence"] == 0.94


@pytest.mark.asyncio
async def test_dashboard_vessels_ranking():
    """Test dashboard vessels returns properly ranked candidates."""
    # Mock database session
    db = AsyncMock(spec=AsyncSession)

    # Mock count query
    count_result = MagicMock()
    count_result.scalar.return_value = 3

    # Mock data query - ordered by score descending
    vessel1 = MagicMock()
    vessel1.mmsi = "123456789"
    vessel1.name = "MSC ELSA III"

    vessel2 = MagicMock()
    vessel2.mmsi = "987654321"
    vessel2.name = "MAERSK EMPRESS"

    data_result = MagicMock()
    data_result.all.return_value = [
        (uuid4(), uuid4(), 0.92, vessel1.mmsi, vessel1.name, 0.95, 0.90, 0.88, 0.10, False),  # score 0.92 (proximity=0.95, temporality=0.90, trajectory=0.88, anomaly=0.10, flag=False)
        (uuid4(), uuid4(), 0.78, vessel2.mmsi, vessel2.name, 0.80, 0.85, 0.70, 0.05, True),   # score 0.78 (proximity=0.80, temporality=0.85, trajectory=0.70, anomaly=0.05, flag=True)
        (uuid4(), uuid4(), 0.65, vessel1.mmsi, vessel1.name, 0.70, 0.75, 0.60, 0.20, False)   # score 0.65 (proximity=0.70, temporality=0.75, trajectory=0.60, anomaly=0.20, flag=False)
    ]

    db.execute.side_effect = [count_result, data_result]

    service = DashboardService(db)
    result = await service.get_vessel_candidates(page=1, page_size=20)

    assert result.page == 1
    assert result.page_size == 20
    assert result.total == 3
    assert len(result.items) == 3

    # Check ranking (should be descending by score)
    assert result.items[0].rank == 1
    assert result.items[0].attribution_score == 0.92
    assert result.items[0].name == "MSC ELSA III"
    assert result.items[0].confidence == "HIGH"  # score >= 0.8

    assert result.items[1].rank == 2
    assert result.items[1].attribution_score == 0.78
    assert result.items[1].name == "MAERSK EMPRESS"
    assert result.items[1].confidence == "MEDIUM"  # 0.5 <= score < 0.8

    assert result.items[2].rank == 3
    assert result.items[2].attribution_score == 0.65
    assert result.items[2].name == "MSC ELSA III"  # same vessel as first but different score
    assert result.items[2].confidence == "MEDIUM"  # 0.5 <= score < 0.8


if __name__ == "__main__":
    pytest.main([__file__])