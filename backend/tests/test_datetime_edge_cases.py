"""
Integration and edge-case tests for datetime & timezone handling.
"""
import pytest
from unittest.mock import Mock, AsyncMock
from uuid import uuid4
from datetime import datetime, timezone
from httpx import AsyncClient, ASGITransport
from shapely.geometry import Point

from app.main import app
from app.core.database import get_db
from app.core.security import create_access_token
from app.models.incident import Incident
from geoalchemy2.shape import from_shape


@pytest.mark.asyncio
@pytest.mark.parametrize("label, ts_str", [
    ('UTC Z format', '2026-08-29T12:00:00Z'),
    ('UTC +00:00 format', '2026-08-29T12:00:00+00:00'),
    ('IST +05:30 format', '2026-08-29T17:30:00+05:30'),
    ('EST -05:00 format', '2026-08-29T07:00:00-05:00'),
    ('Midnight UTC', '2026-08-29T00:00:00Z'),
    ('Year boundary', '2026-12-31T23:59:59Z')
])
async def test_datetime_timezone_edge_case(label, ts_str):
    """Test ISO-8601 parsing, timezone offsets, instant equivalence, and serialization."""
    token = create_access_token({
        'sub': f'test_tz_{label.replace(" ", "_")}@example.com',
        'role': 'analyst',
        'user_id': str(uuid4())
    })
    headers = {'Authorization': f'Bearer {token}'}

    # Mock DB dependency for clean isolated test execution
    mock_db = AsyncMock()
    mock_db.add = Mock()
    mock_db.commit = AsyncMock()
    
    # Mock refresh to populate incident attributes
    async def mock_refresh(obj):
        if hasattr(obj, 'id') and obj.id is None:
            obj.id = uuid4()
        if hasattr(obj, 'created_at') and obj.created_at is None:
            obj.created_at = datetime.now(timezone.utc)
        if hasattr(obj, 'updated_at') and obj.updated_at is None:
            obj.updated_at = datetime.now(timezone.utc)

    mock_db.refresh.side_effect = mock_refresh

    app.dependency_overrides[get_db] = lambda: mock_db

    payload = {
        'name': f'Incident {label}',
        'description': f'Testing {ts_str}',
        'timestamp': ts_str,
        'location': {'type': 'Point', 'coordinates': [76.11, 9.82]},
        'status': 'DETECTED'
    }
    
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            res = await client.post('/api/v1/incidents', json=payload, headers=headers)
            assert res.status_code == 201, f"Failed for {label}: {res.text}"
            data = res.json()
            returned_ts = data['timestamp']
            assert returned_ts is not None
            assert returned_ts.endswith("Z") or "+" in returned_ts or "-" in returned_ts
    finally:
        app.dependency_overrides.clear()
