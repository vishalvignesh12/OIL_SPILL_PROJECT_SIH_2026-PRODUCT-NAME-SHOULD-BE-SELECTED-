# Dashboard API PRD

## Oil Spill Detection & Vessel Attribution Platform

**Module:** Backend — Dashboard API  
**Priority:** High  
**Status:** Ready for Development

---

## 1. Executive Summary

The Dashboard API is a read-only aggregation layer between persisted backend data and the frontend dashboard.

```text
PostgreSQL / PostGIS
        ↓
Repositories / Queries
        ↓
Dashboard Service
        ↓
Response Schemas
        ↓
REST API
        ↓
Frontend Dashboard
```

It provides:
- System overview statistics
- Recent oil-spill incidents
- Spill regions as GeoJSON
- Vessel candidates and attribution scores
- Recent system activity
- Complete investigation summaries

The dashboard must consume existing backend data and must not duplicate scientific/business logic.

---

## 2. Scope

### In Scope

```text
Dashboard Router
Dashboard Service
Repository / Query layer
Pydantic response schemas
Dashboard endpoints
PostGIS → GeoJSON conversion
Pagination
Filtering
Error handling
Unit tests
Integration tests
OpenAPI documentation
```

### Out of Scope

```text
❌ ML model or training
❌ Satellite ingestion
❌ Drift model
❌ Environmental data ingestion
❌ AIS provider integration
❌ Attribution algorithm
❌ Frontend
❌ Notifications
❌ WebSockets
❌ Kubernetes
❌ New database technology
```

---

## 3. Architecture

```text
                    FRONTEND
                        │
                        ▼
              /api/v1/dashboard/*
                        │
                        ▼
                Dashboard Router
                        │
                        ▼
                Dashboard Service
                        │
                        ▼
              Repository / Queries
                        │
                        ▼
                 PostgreSQL/PostGIS
```

Keep route handlers thin. Do not place large SQL queries or business logic inside routers.

---

# 4. API Endpoints

| Priority | Method | Endpoint | Purpose |
|---|---|---|---|
| P0 | GET | `/api/v1/dashboard/overview` | Summary statistics |
| P1 | GET | `/api/v1/dashboard/incidents` | Recent incidents |
| P0 | GET | `/api/v1/dashboard/spills` | Spill map GeoJSON |
| P1 | GET | `/api/v1/dashboard/vessels` | Ranked vessel candidates |
| P2 | GET | `/api/v1/dashboard/activity` | Recent backend activity |
| P0 | GET | `/api/v1/dashboard/investigations/{investigation_id}` | Complete investigation |

---

# 5. Dashboard Overview

## Endpoint

```http
GET /api/v1/dashboard/overview
```

## Purpose

Provide high-level dashboard statistics.

## Response

```json
{
  "total_incidents": 12,
  "active_incidents": 3,
  "detected_spills": 8,
  "total_spill_area_km2": 143.7,
  "analyses_completed": 24,
  "analyses_processing": 2,
  "analyses_failed": 1,
  "high_confidence_spills": 6
}
```

## Requirements

- Use database aggregation.
- Do not load every record into Python for counting.
- Use `COUNT`, `SUM`, and appropriate filters.
- Return zero values when the database is empty.
- Do not hardcode production statistics.

---

# 6. Recent Incidents

## Endpoint

```http
GET /api/v1/dashboard/incidents
```

## Query Parameters

```text
page
page_size
status
min_confidence
```

Example:

```http
GET /api/v1/dashboard/incidents?page=1&page_size=20
```

## Response

```json
{
  "items": [
    {
      "incident_id": "INC-001",
      "status": "INVESTIGATION_READY",
      "detected_at": "2026-08-29T10:32:00Z",
      "confidence": 0.94,
      "area_km2": 12.4,
      "location": {
        "latitude": 9.72,
        "longitude": 75.98
      }
    }
  ],
  "page": 1,
  "page_size": 20,
  "total": 12
}
```

Default sorting:

```text
detected_at DESC
```

---

# 7. Spill Map

## Endpoint

```http
GET /api/v1/dashboard/spills
```

## Purpose

Return detected spill regions directly consumable by a map.

Preferred format:

```text
GeoJSON FeatureCollection
```

## Response

```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": {
        "type": "Polygon",
        "coordinates": [
          [
            [75.97, 9.71],
            [75.99, 9.71],
            [75.99, 9.73],
            [75.97, 9.73],
            [75.97, 9.71]
          ]
        ]
      },
      "properties": {
        "incident_id": "INC-001",
        "detection_id": "DET-001",
        "confidence": 0.94,
        "area_km2": 12.4,
        "status": "ACTIVE"
      }
    }
  ]
}
```

### Critical

GeoJSON coordinates must be:

```text
[longitude, latitude]
```

not:

```text
[latitude, longitude]
```

Optional filters:

```text
status
min_confidence
bbox
```

Use existing PostGIS infrastructure.

---

# 8. Vessel Candidates

## Endpoint

```http
GET /api/v1/dashboard/vessels
```

## Query Parameters

```text
page
page_size
incident_id
min_score
```

## Response

```json
{
  "items": [
    {
      "vessel_id": "123456789",
      "name": "MSC ELSA III",
      "rank": 1,
      "attribution_score": 0.87,
      "confidence": "HIGH",
      "distance_to_origin_km": 4.2,
      "temporal_match": 0.92
    }
  ],
  "page": 1,
  "page_size": 20,
  "total": 3
}
```

The dashboard must return the ranking produced by the attribution layer.

**Do not recalculate attribution inside the dashboard service.**

---

# 9. Activity Feed

## Endpoint

```http
GET /api/v1/dashboard/activity
```

## Response

```json
{
  "items": [
    {
      "event": "OIL_SPILL_DETECTED",
      "incident_id": "INC-001",
      "timestamp": "2026-08-29T10:32:00Z"
    },
    {
      "event": "HINDCAST_COMPLETED",
      "incident_id": "INC-001",
      "timestamp": "2026-08-29T10:34:12Z"
    },
    {
      "event": "ATTRIBUTION_COMPLETED",
      "incident_id": "INC-001",
      "timestamp": "2026-08-29T10:35:41Z"
    }
  ]
}
```

Possible events:

```text
SCENE_INGESTED
ANALYSIS_STARTED
ANALYSIS_COMPLETED
ANALYSIS_FAILED
OIL_SPILL_DETECTED
HINDCAST_COMPLETED
FORECAST_COMPLETED
AIS_CORRELATION_COMPLETED
ATTRIBUTION_COMPLETED
INVESTIGATION_CREATED
```

Reuse existing project terminology where available.

---

# 10. Investigation Details

## Endpoint

```http
GET /api/v1/dashboard/investigations/{investigation_id}
```

## Purpose

Return one aggregated response for the investigation screen.

The frontend should not need to call multiple domain endpoints just to render an investigation.

## Response

```json
{
  "investigation": {
    "id": "INV-001",
    "status": "READY"
  },
  "detection": {
    "detected": true,
    "confidence": 0.94,
    "area_km2": 12.4
  },
  "spill_regions": [],
  "hindcast": {},
  "forecast": {},
  "ais_tracks": [],
  "candidate_vessels": [],
  "attribution": {},
  "evidence": []
}
```

Reuse existing backend response models wherever possible.

Return:

```http
404 Not Found
```

if the investigation does not exist.

---

# 11. Data Sources

The dashboard should consume existing domain models.

Conceptually:

```text
SatelliteScene
      ↓
Analysis
      ↓
Detection
      ↓
SpillRegion
      ↓
Drift
      ↓
AISTrack
      ↓
Vessel
      ↓
Attribution
      ↓
Investigation
```

**The coding agent must inspect the current repository before implementing database queries.**

Do not invent duplicate database models if equivalent models already exist.

---

# 12. Suggested Project Structure

Adapt this to the existing repository rather than blindly creating new directories.

```text
app/
├── api/
│   └── v1/
│       └── dashboard.py
├── schemas/
│   └── dashboard.py
├── services/
│   └── dashboard_service.py
├── repositories/
│   └── dashboard_repository.py
└── tests/
    ├── unit/
    │   └── test_dashboard_service.py
    └── integration/
        └── test_dashboard_api.py
```

---

# 13. Pagination

Collection endpoints should support:

```text
page = 1
page_size = 20
```

Maximum:

```text
page_size <= 100
```

Response:

```json
{
  "items": [],
  "page": 1,
  "page_size": 20,
  "total": 100
}
```

---

# 14. Filtering

Implement only the required MVP filters.

### Incidents

```text
status
min_confidence
```

### Spills

```text
status
min_confidence
bbox
```

### Vessels

```text
incident_id
min_score
```

---

# 15. Error Handling

Follow the existing backend error-handling conventions.

### Not Found

```http
404 Not Found
```

### Invalid parameters

```http
400 Bad Request
```

### Server/database failure

```http
500 Internal Server Error
```

Never expose:

```text
SQL queries
database credentials
stack traces
internal filesystem paths
```

---

# 16. Performance

MVP targets:

| Endpoint | Target |
|---|---:|
| `/overview` | < 500 ms |
| `/incidents` | < 500 ms |
| `/spills` | < 1 s |
| `/vessels` | < 500 ms |
| `/activity` | < 500 ms |
| `/investigations/{id}` | < 1 s |

Use:

```text
database indexes
spatial indexes
pagination
aggregation queries
select only required columns
```

Avoid:

```text
N+1 queries
loading entire tables
large Python-side aggregations
```

---

# 17. Caching

Caching is **optional for MVP**.

Do not introduce Redis solely for these endpoints if the project does not already use it.

Possible future cache targets:

```text
overview statistics
activity feed
frequently accessed investigations
```

---

# 18. Security

Use the project's existing authentication and authorization mechanisms.

Requirements:

```text
authentication
authorization
input validation
parameter validation
rate limiting
existing CORS policy
```

Do not introduce a second authentication system.

---

# 19. Testing

## Unit Tests

Test:

```text
overview aggregation
incident filtering
pagination
spill serialization
GeoJSON conversion
vessel result serialization
investigation aggregation
empty database
missing records
invalid parameters
```

## Integration Tests

Test:

```text
GET /dashboard/overview
GET /dashboard/incidents
GET /dashboard/spills
GET /dashboard/vessels
GET /dashboard/activity
GET /dashboard/investigations/{id}
```

Verify:

```text
HTTP status
response schema
database values
pagination
filters
GeoJSON structure
404 behavior
```

---

# 20. Acceptance Criteria

## Overview

- [ ] Endpoint exists.
- [ ] Statistics come from the database.
- [ ] Empty database returns zero values.
- [ ] No hardcoded production values.
- [ ] Tests pass.

## Incidents

- [ ] Recent incidents returned.
- [ ] Newest-first ordering.
- [ ] Pagination works.
- [ ] Filtering works.
- [ ] Location returned correctly.
- [ ] Tests pass.

## Spill Map

- [ ] Valid GeoJSON FeatureCollection.
- [ ] Valid polygon geometry.
- [ ] Correct `[longitude, latitude]` ordering.
- [ ] Spill properties included.
- [ ] Filtering works.
- [ ] Tests pass.

## Vessels

- [ ] Candidate vessels returned.
- [ ] Attribution ranking preserved.
- [ ] Attribution score returned.
- [ ] Incident filtering works.
- [ ] Pagination works.
- [ ] Tests pass.

## Activity

- [ ] Recent events returned.
- [ ] Newest-first ordering.
- [ ] Related incident IDs included where available.
- [ ] Tests pass.

## Investigation

- [ ] Complete investigation summary returned.
- [ ] Detection included.
- [ ] Spill regions included.
- [ ] Drift included when available.
- [ ] AIS tracks included when available.
- [ ] Candidate vessels included.
- [ ] Attribution included.
- [ ] Evidence included when available.
- [ ] Unknown investigation returns 404.
- [ ] Tests pass.

---

# 21. MVP Demo Requirement

The dashboard should support this flow:

```text
                 DASHBOARD
                     │
       ┌─────────────┼─────────────┐
       ▼             ▼             ▼
   Statistics     Spill Map     Activity
                     │
                     ▼
                Spill Polygon
                     │
                     ▼
                Investigation
                     │
              ┌──────┴──────┐
              ▼             ▼
            Drift          AIS
                             │
                             ▼
                         Candidates
                             │
                             ▼
                         Attribution
```

The frontend must be able to show:

```text
Oil spill detected
       ↓
Spill location
       ↓
Spill polygon
       ↓
Drift trajectory
       ↓
Vessel tracks
       ↓
Candidate ranking
```

---

# 22. Fixture Compatibility

During MVP development, upstream systems may still use fixtures.

For example:

```text
Fixture ML
Fixture Drift
Fixture AIS
```

can populate normal backend domain models.

The dashboard itself must remain fixture-agnostic.

### Bad

```python
if DEMO_MODE:
    return fake_vessels
```

### Good

```text
Fixture Adapter
      ↓
Normal Domain Models
      ↓
Dashboard Repository
      ↓
Dashboard API
```

This allows fixture implementations to later be replaced by real providers without rewriting the dashboard.

---

# 23. Implementation Sequence

## Step 1 — Inspect Repository

Identify:

```text
existing routers
existing models
existing schemas
existing services
existing repositories
database session
PostGIS utilities
authentication
error handling
testing conventions
```

Do this before writing code.

## Step 2 — Map Existing Models

Map:

```text
Dashboard requirement
        ↓
Existing model/table
```

Do not invent duplicate models.

## Step 3 — Create Response Schemas

Create typed Pydantic DTOs.

## Step 4 — Implement Repository Queries

Keep database access in the repository/query layer.

## Step 5 — Implement DashboardService

Aggregate and transform repository results.

## Step 6 — Implement Router

Keep route handlers thin.

## Step 7 — Register Router

Register:

```text
/api/v1/dashboard
```

without breaking existing APIs.

## Step 8 — Add Tests

Implement unit tests followed by integration tests.

## Step 9 — Validate OpenAPI

All endpoints must appear correctly in FastAPI's generated OpenAPI documentation.

## Step 10 — Frontend Integration

Verify the frontend can consume:

```text
overview
incidents
spills
vessels
activity
investigation
```

---

# 24. Definition of Done

```text
[ ] Dashboard router implemented
[ ] Dashboard schemas implemented
[ ] Repository queries implemented
[ ] Dashboard service implemented
[ ] Overview endpoint working
[ ] Incidents endpoint working
[ ] Spill GeoJSON endpoint working
[ ] Vessel endpoint working
[ ] Activity endpoint working
[ ] Investigation endpoint working
[ ] Pagination implemented
[ ] Required filtering implemented
[ ] PostGIS handled correctly
[ ] Existing authentication followed
[ ] Existing error handling followed
[ ] Unit tests passing
[ ] Integration tests passing
[ ] OpenAPI documentation available
[ ] No hardcoded production data
[ ] No unrelated modules rewritten
```

---

# 25. Final AI Coding Agent Instruction

> **Inspect the existing backend repository first. Implement the Dashboard API as a read-only aggregation layer using the project's existing models, services, database session, authentication, error handling, and PostGIS utilities. Do not rewrite existing domain logic and do not create duplicate models. Implement the six specified dashboard endpoints, keeping routers thin and placing database access in a repository/query layer and aggregation logic in a dashboard service. Use real persisted data where available and allow existing fixture adapters to populate that data during MVP development. Add complete unit and integration tests. Do not modify ML, satellite ingestion, drift, AIS, attribution, or frontend functionality unless a minimal integration change is strictly required to expose existing data to the dashboard.**

---

## Priority

```text
P0  /dashboard/overview
P0  /dashboard/spills
P0  /dashboard/investigations/{id}

P1  /dashboard/incidents
P1  /dashboard/vessels

P2  /dashboard/activity
```

The three P0 endpoints are sufficient to get the first dashboard MVP running.
