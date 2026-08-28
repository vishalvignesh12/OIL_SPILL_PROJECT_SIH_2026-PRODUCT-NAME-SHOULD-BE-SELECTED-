import pytest
from unittest.mock import Mock, AsyncMock, patch
from uuid import uuid4
from datetime import datetime, timedelta, UTC
from shapely.geometry import Point

from app.services.attribution_service import calculate_attribution_scores
from app.models.attribution import AttributionScore
from app.models.vessel import Vessel
from app.schemas.attribution import ScoreRequest
from app.schemas.incident import GeoJSONPoint


def make_db_result(value):
    result = Mock()
    result.scalars.return_value.first.return_value = value
    return result


@pytest.mark.asyncio
async def test_calculate_attribution_scores_basic():
    incident_id = uuid4()
    db = AsyncMock()

    vessel1 = Mock(spec=Vessel)
    vessel1.id = uuid4()
    vessel1.mmsi = "232003423"
    vessel1.name = "MSC ELSA III"

    vessel2 = Mock(spec=Vessel)
    vessel2.id = uuid4()
    vessel2.mmsi = "311000124"
    vessel2.name = "OCEAN VOYAGER"

    # Calls:
    # vessel1 lookup
    # existing attribution lookup
    # vessel2 lookup
    # existing attribution lookup
    db.execute.side_effect = [
        make_db_result(vessel1),
        make_db_result(None),
        make_db_result(vessel2),
        make_db_result(None),
    ]

    track1 = Mock()
    track1.vessel_id = vessel1.id
    track1.timestamp = datetime.now(UTC)
    track1.position = "position1"

    track2 = Mock()
    track2.vessel_id = vessel2.id
    track2.timestamp = datetime.now(UTC)
    track2.position = "position2"

    req = ScoreRequest(
        incident_id=incident_id,
        origin_point=GeoJSONPoint(
            coordinates=(75.98, 9.72)
        ),
        origin_time_start=datetime.now(UTC) - timedelta(hours=2),
        origin_time_end=datetime.now(UTC),
    )

    with patch(
        "app.services.attribution_service.query_ais_tracks",
        new=AsyncMock(return_value=[track1, track2])
    ), patch(
        "app.services.attribution_service.detect_ais_gaps",
        new=AsyncMock(return_value=[])
    ), patch(
        "app.services.attribution_service.to_shape",
        side_effect=[
            Point(75.99, 9.73),
            Point(76.00, 9.74),
        ]
    ):
        results = await calculate_attribution_scores(db, req)

    assert len(results) == 2
    assert all(
        isinstance(score, AttributionScore)
        for score in results
    )
    assert all(
        0 <= score.score <= 1
        for score in results
    )
    assert all(
        hasattr(score, "proximity_score")
        for score in results
    )
    assert all(
        hasattr(score, "temporality_score")
        for score in results
    )
    assert all(
        hasattr(score, "trajectory_score")
        for score in results
    )
    assert all(
        hasattr(score, "anomaly_score")
        for score in results
    )

    db.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_calculate_attribution_scores_with_aligned_trajectory():
    incident_id = uuid4()
    db = AsyncMock()

    vessel = Mock(spec=Vessel)
    vessel.id = uuid4()
    vessel.mmsi = "232003423"
    vessel.name = "MSC ELSA III"

    db.execute.side_effect = [
        make_db_result(vessel),
        make_db_result(None),
    ]

    now = datetime.now(UTC)

    track1 = Mock()
    track1.vessel_id = vessel.id
    track1.timestamp = now - timedelta(minutes=10)
    track1.position = "position1"

    track2 = Mock()
    track2.vessel_id = vessel.id
    track2.timestamp = now
    track2.position = "position2"

    req = ScoreRequest(
        incident_id=incident_id,
        origin_point=GeoJSONPoint(
            coordinates=(75.98, 9.72)
        ),
        origin_time_start=now - timedelta(hours=2),
        origin_time_end=now,
    )

    with patch(
        "app.services.attribution_service.query_ais_tracks",
        new=AsyncMock(return_value=[track1, track2])
    ), patch(
        "app.services.attribution_service.detect_ais_gaps",
        new=AsyncMock(return_value=[])
    ), patch(
        "app.services.attribution_service.to_shape",
        side_effect=[
            Point(75.98, 9.72),
            Point(76.08, 9.85),
        ]
    ):
        results = await calculate_attribution_scores(db, req)

    assert len(results) == 1

    score = results[0]

    assert isinstance(score, AttributionScore)
    assert score.trajectory_score > 0.5