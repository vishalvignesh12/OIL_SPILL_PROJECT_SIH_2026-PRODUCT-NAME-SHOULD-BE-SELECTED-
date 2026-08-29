"""
Unit tests for the attribution service.
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from uuid import uuid4, UUID
from datetime import datetime, timedelta, UTC
from shapely.geometry import Point, LineString

from app.services.attribution_service import calculate_attribution_scores
from app.models.attribution import AttributionScore
from app.models.vessel import Vessel
from app.models.drift_result import DriftResult
from app.schemas.attribution import ScoreRequest
from app.schemas.incident import GeoJSONPoint


def _stmt_target_type(stmt):
    """Return the mapped class that a SQLAlchemy select() targets, or None."""
    cd = getattr(stmt, "column_descriptions", None)
    if cd:
        return cd[0].get("type")
    return None


def _stmt_where_id(stmt) -> UUID | None:
    """Extract the UUID bound value from a single-column WHERE id=:id_1 clause, or None."""
    try:
        wc = stmt.whereclause
        if wc is not None and hasattr(wc, "right") and hasattr(wc.right, "value"):
            return wc.right.value
    except Exception:
        pass
    return None


@pytest.mark.asyncio
async def test_calculate_attribution_scores_basic():
    """Test basic attribution score calculation."""
    # Setup
    incident_id = uuid4()
    db = AsyncMock()
    db.add = Mock()

    # Mock drift result
    drift_result = Mock(spec=DriftResult)
    drift_result.hindcast_path = None  # No hindcast path to test fallback

    # Mock vessels
    vessel1 = Mock(spec=Vessel)
    vessel1.id = uuid4()
    vessel1.mmsi = "232003423"
    vessel1.name = "MSC ELSA III"

    vessel2 = Mock(spec=Vessel)
    vessel2.id = uuid4()
    vessel2.mmsi = "311000124"
    vessel2.name = "OCEAN VOYAGER"

    vessel_map = {vessel1.id: vessel1, vessel2.id: vessel2}

    # Structural database query dispatch using SQLAlchemy Select AST inspection
    async def mock_execute(stmt):
        mock_result = Mock()
        target = _stmt_target_type(stmt)

        if target is DriftResult:
            mock_result.scalars.return_value.first.return_value = drift_result
        elif target is Vessel:
            where_id = _stmt_where_id(stmt)
            mock_result.scalars.return_value.first.return_value = vessel_map.get(where_id)
        else:
            mock_result.scalars.return_value.first.return_value = None
        return mock_result

    db.execute.side_effect = mock_execute

    # Mock AIS service responses
    with patch('app.services.attribution_service.query_ais_tracks') as mock_query_tracks, \
         patch('app.services.attribution_service.detect_ais_gaps') as mock_detect_gaps:

        # Real Shapely Point positions for realistic geometry testing
        track1 = Mock()
        track1.vessel_id = vessel1.id
        track1.timestamp = datetime.now(UTC)
        track1.position = Point(75.98, 9.72)

        track2 = Mock()
        track2.vessel_id = vessel2.id
        track2.timestamp = datetime.now(UTC)
        track2.position = Point(76.05, 9.75)

        mock_query_tracks.return_value = [track1, track2]
        mock_detect_gaps.return_value = []  # No gaps

        # Create request
        req = ScoreRequest(
            incident_id=incident_id,
            origin_point=GeoJSONPoint(coordinates=(75.98, 9.72)),
            origin_time_start=datetime.now(UTC) - timedelta(hours=2),
            origin_time_end=datetime.now(UTC)
        )

        # Execute
        results = await calculate_attribution_scores(db, req)

        # Verify
        assert len(results) == 2  # Two vessels
        assert all(isinstance(score, AttributionScore) for score in results)
        assert all(0 <= score.score <= 1 for score in results)
        assert all(hasattr(score, 'proximity_score') for score in results)
        assert all(hasattr(score, 'temporality_score') for score in results)
        assert all(hasattr(score, 'trajectory_score') for score in results)
        assert all(hasattr(score, 'anomaly_score') for score in results)


@pytest.mark.asyncio
async def test_calculate_attribution_scores_with_drift_path():
    """Test attribution score calculation with drift hindcast path."""
    # Setup
    incident_id = uuid4()
    db = AsyncMock()
    db.add = Mock()

    # Mock drift result with hindcast path
    drift_result = Mock(spec=DriftResult)
    hindcast_path = LineString([(75.98, 9.72), (76.00, 9.75)])  # Northeast direction
    drift_result.hindcast_path = hindcast_path

    # Mock vessel
    vessel = Mock(spec=Vessel)
    vessel.id = uuid4()
    vessel.mmsi = "232003423"
    vessel.name = "MSC ELSA III"

    # Structural database query dispatch using SQLAlchemy Select AST inspection
    async def mock_execute(stmt):
        mock_result = Mock()
        target = _stmt_target_type(stmt)

        if target is DriftResult:
            mock_result.scalars.return_value.first.return_value = drift_result
        elif target is Vessel:
            mock_result.scalars.return_value.first.return_value = vessel
        else:
            mock_result.scalars.return_value.first.return_value = None
        return mock_result

    db.execute.side_effect = mock_execute

    # Mock AIS service responses
    with patch('app.services.attribution_service.query_ais_tracks') as mock_query_tracks, \
         patch('app.services.attribution_service.detect_ais_gaps') as mock_detect_gaps:

        # Real Shapely Points moving northeast (aligned with drift path)
        track1 = Mock()
        track1.vessel_id = vessel.id
        track1.timestamp = datetime.now(UTC) - timedelta(minutes=30)
        track1.position = Point(75.98, 9.72)

        track2 = Mock()
        track2.vessel_id = vessel.id
        track2.timestamp = datetime.now(UTC)
        track2.position = Point(76.00, 9.75)

        mock_query_tracks.return_value = [track1, track2]
        mock_detect_gaps.return_value = []  # No gaps

        # Create request
        req = ScoreRequest(
            incident_id=incident_id,
            origin_point=GeoJSONPoint(coordinates=(75.98, 9.72)),
            origin_time_start=datetime.now(UTC) - timedelta(hours=2),
            origin_time_end=datetime.now(UTC)
        )

        # Execute
        results = await calculate_attribution_scores(db, req)

        # Verify
        assert len(results) == 1
        score = results[0]
        assert isinstance(score, AttributionScore)
        # With aligned trajectory, we should get a good trajectory score
        assert score.trajectory_score > 0.5  # Should be reasonably aligned


if __name__ == "__main__":
    pytest.main([__file__])
