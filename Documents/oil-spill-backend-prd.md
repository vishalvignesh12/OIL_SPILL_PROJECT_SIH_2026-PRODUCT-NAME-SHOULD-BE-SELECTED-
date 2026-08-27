# Backend Product Requirements Document (PRD)
## Oil Spill Detection & AIS-Based Vessel Attribution Platform

**Document Version:** 1.0  
**Date:** 27 August 2026  
**Status:** Implementation-ready MVP specification  
**Primary Backend Stack:** Python, FastAPI, PostgreSQL/PostGIS  
**Architecture:** Modular monolith with replaceable intelligence services  
**Primary Frontend Consumer:** React + TypeScript GIS investigation dashboard

---

# 1. Executive Summary

## 1.1 Product Overview

The backend is the data, geospatial, intelligence, and integration layer supporting an oil-spill investigation frontend.

The system receives or references satellite imagery, determines whether an oil slick is present, characterizes the slick, estimates its probable origin using drift hindcasting, correlates that origin/time window with AIS vessel traffic, and produces an explainable ranking of candidate vessels.

The core investigation chain is:

```text
Satellite imagery
      ↓
Oil slick detection
      ↓
Slick characterization
      ↓
Drift hindcast
      ↓
Probable origin + time window
      ↓
AIS reconstruction
      ↓
Spatial + temporal + trajectory correlation
      ↓
AIS anomaly detection
      ↓
Ranked candidate vessels
      ↓
Evidence summary
      ↓
Frontend investigation dashboard
```

The backend must support the frontend's central investigation workspace, including:

- Incident list and filtering.
- Satellite/slick visualization.
- Slick geometry and characteristics.
- Hindcast and forecast paths.
- Probable origin probability region.
- AIS vessel tracks.
- Vessel candidate ranking.
- Attribution score breakdown.
- AIS-gap alerts.
- Timeline events.
- Evidence summaries.
- Authentication and role-based access.
- CSV export.

## 1.2 Product Positioning

The system is an **AI-assisted maritime oil-spill investigation and attribution platform**, not an automated legal verdict system.

The backend must therefore expose confidence and evidence dimensions and avoid presenting an attribution score as proof that a vessel caused a spill.

## 1.3 MVP Objective

The MVP objective is to demonstrate a complete, coherent end-to-end investigation workflow using real or documented historical data where practical and precomputed/mock intelligence outputs where necessary.

The existing project analysis recommends selecting 2–3 historical spill cases, using Sentinel-1 imagery, applying segmentation, running GNOME/OpenDrift for drift analysis, correlating AIS traffic, and presenting confidence at each stage. fileciteturn1file8L331-L336

For the compressed MVP, the detection and drift components may initially be fixture/precomputed implementations behind real API contracts. The attribution pipeline should be functional.

---

# 2. Product Goals and Non-Goals

## 2.1 Goals

1. Provide a stable REST API for the frontend.
2. Store incident, slick, vessel, AIS, drift, and attribution data.
3. Perform geospatial queries using PostGIS.
4. Support satellite-derived slick detection results.
5. Support drift hindcast and forecast results.
6. Reconstruct relevant vessel traffic around a probable origin/time window.
7. Calculate explainable vessel attribution scores.
8. Detect AIS gaps/anomalies as investigation leads.
9. Maintain inference/audit records.
10. Provide secure analyst/admin access.
11. Support containerized local development and cloud deployment.
12. Keep intelligence modules replaceable without rewriting the frontend or core backend.

## 2.2 Non-Goals for MVP

- Building a custom ocean-physics engine.
- Guaranteeing real-time satellite imagery.
- Guaranteeing real-time AIS attribution.
- Establishing legal culpability.
- Building a full distributed microservice platform.
- Kubernetes orchestration.
- Kafka/RabbitMQ infrastructure unless later proven necessary.
- Advanced ML serving infrastructure.
- Fully automated legal evidence submission.

The project analysis specifically warns against claiming arbitrary real-time satellite detection because SAR revisit cycles impose structural limits. fileciteturn1file6L244-L250

---

# 3. Source-Derived Constraints and Assumptions

The following constraints are carried forward from the project analysis.

## 3.1 Data Constraints

- Sentinel-1 SAR imagery is a practical source for the MVP.
- Raw SAR scenes can be large and require preprocessing.
- Historical AIS is more practical than unrestricted live high-density AIS.
- Global Fishing Watch or simulated/dummy AIS can be used as fallbacks.
- CMEMS provides ocean-current data.
- ERA5 provides wind reanalysis.
- GNOME and OpenDrift are open-source drift-model options. fileciteturn1file5L210-L222
- Ground-truth oil-spill labels can be scarce and imbalanced.
- Slick age estimation does not have a mature off-the-shelf solution and should be treated as a low-confidence heuristic. fileciteturn1file5L218-L222

## 3.2 Scientific Constraints

- Drift uncertainty increases over time.
- Origin should be represented as a probability region/cone rather than a falsely precise coordinate.
- AIS correlation must account for spatial proximity, temporality, trajectory alignment, and anomalies.
- An AIS gap is an investigation lead, not proof of responsibility. fileciteturn1file6L244-L250

---

# 4. System Architecture

## 4.1 Architectural Style

### Decision: Modular Monolith

The MVP will use a **modular FastAPI monolith**, not independently deployed microservices.

```text
                    ┌─────────────────────┐
                    │ React Frontend      │
                    └──────────┬──────────┘
                               │ HTTPS / JSON
                               ▼
                    ┌─────────────────────┐
                    │ FastAPI Application │
                    │                     │
                    │ Auth                │
                    │ Incidents           │
                    │ Scenes              │
                    │ Detection            │
                    │ Drift                │
                    │ AIS                 │
                    │ Attribution         │
                    │ Evidence            │
                    │ Admin               │
                    └──────────┬──────────┘
                               │
             ┌─────────────────┼──────────────────┐
             ▼                 ▼                  ▼
       PostgreSQL          External APIs      Intelligence
       + PostGIS            / datasets         modules
             │                 │                  │
             └─────────────────┼──────────────────┘
                               ▼
                       Investigation Result
```

### Rationale

A modular monolith provides:

- Fast development.
- Simple deployment.
- Low operational overhead.
- Clear separation of business domains.
- Easy debugging during a hackathon.
- A straightforward migration path to microservices later.

Kubernetes, Kafka, RabbitMQ, and a distributed service mesh are explicitly not required for the MVP.

---

# 5. Infrastructure

## 5.1 Environments

Three environments are recommended:

```text
Development
    ↓
Staging
    ↓
Production
```

### Development

- Local Docker Compose.
- Local PostgreSQL/PostGIS.
- Mock or fixture data.
- FastAPI hot reload.

### Staging

- Cloud-hosted API.
- Cloud PostgreSQL/PostGIS.
- Test data.
- Frontend integration testing.

### Production

- Cloud-hosted API.
- Managed PostgreSQL/PostGIS.
- HTTPS.
- Secrets stored through platform environment configuration.
- Logging and health monitoring.

The existing MVP plan recommends getting staging live early rather than waiting until the final day. fileciteturn1file6L262-L268

---

# 6. API Design

## 6.1 API Style

**RESTful HTTP/JSON**

Base path:

```text
/api/v1
```

Example:

```text
GET /api/v1/incidents
```

## 6.2 API Principles

- Resource-oriented URLs.
- JSON request/response bodies.
- Consistent error format.
- Pydantic validation.
- Explicit API versioning.
- OpenAPI documentation.
- Authentication via bearer JWT.
- Pagination for potentially large lists.
- ISO-8601 timestamps in UTC.
- GeoJSON for frontend geospatial payloads.
- Backend performs expensive geospatial filtering.

## 6.3 Content Types

Request:

```text
application/json
```

File upload where required:

```text
multipart/form-data
```

Response:

```text
application/json
```

Geospatial geometry:

```text
GeoJSON
```

---

# 7. Authentication and Authorization

## 7.1 Authentication

Use:

**JWT bearer authentication**

Flow:

```text
Register
   ↓
Password hashing
   ↓
PostgreSQL
   ↓
Login
   ↓
Credential verification
   ↓
JWT issued
   ↓
Authorization: Bearer <token>
```

## 7.2 Roles

Two MVP roles:

```text
analyst
admin
```

### Analyst

Can:

- View incidents.
- View investigations.
- View vessels.
- Query AIS.
- Run/inspect analysis where permitted.
- Export investigation data.

### Admin

All analyst permissions plus:

- View users.
- Manage basic vessel/user records.
- Access administrative endpoints.

## 7.3 Security Rule

Frontend role checks are UX controls only.

The backend must enforce authorization on every protected endpoint.

---

# 8. Rate Limiting

## MVP

A simple API rate limiter is recommended for public-facing endpoints.

Suggested starting limits:

| Endpoint Category | Suggested Limit |
|---|---:|
| Authentication | 10 requests/minute/IP |
| General GET APIs | 120 requests/minute/user |
| Analysis endpoints | 10 requests/minute/user |
| File upload endpoints | 5 requests/minute/user |
| Admin endpoints | 60 requests/minute/user |

These are initial engineering limits, not validated production capacity targets.

Redis may be used for distributed rate-limit state if the deployment requires it. For a single-instance MVP, a simpler implementation is acceptable.

---

# 9. Core API Endpoint Specification

## 9.1 Authentication

| Method | Endpoint | Purpose | Auth |
|---|---|---|---|
| POST | `/api/v1/auth/register` | Create user | Public |
| POST | `/api/v1/auth/login` | Authenticate user | Public |
| GET | `/api/v1/auth/me` | Current user | JWT |

### Register Request

```json
{
  "name": "Analyst",
  "email": "analyst@example.com",
  "password": "..."
}
```

### Login Request

```json
{
  "email": "analyst@example.com",
  "password": "..."
}
```

### Login Response

```json
{
  "access_token": "...",
  "token_type": "bearer"
}
```

### Acceptance Criteria

- Valid registration creates a hashed-password user.
- Duplicate email is rejected.
- Invalid login returns `401`.
- Valid login returns JWT.
- Protected routes reject missing/invalid JWT.
- Admin-only routes reject analyst users.

---

# 10. Incident APIs

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/v1/incidents` | List incidents |
| GET | `/api/v1/incidents/{id}` | Incident details |
| POST | `/api/v1/incidents` | Create incident |
| PUT | `/api/v1/incidents/{id}` | Update incident |

## Filters

```text
?start_date=
?end_date=
?min_confidence=
?status=
?region=
```

## Acceptance Criteria

- Incident list supports date filtering.
- Confidence filtering works.
- Invalid dates return validation errors.
- Nonexistent incident returns `404`.
- Authorized users can retrieve incident details.

---

# 11. Satellite Scene APIs

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/v1/scenes` | List scene metadata |
| GET | `/api/v1/scenes/{id}` | Scene details |
| POST | `/api/v1/scenes` | Register scene metadata |

## Stored Metadata

```json
{
  "satellite": "Sentinel-1",
  "product_type": "GRD",
  "polarization": "VV",
  "timestamp": "2026-08-27T14:20:00Z",
  "bbox": {},
  "image_url": "...",
  "thumbnail_url": "..."
}
```

Raw large imagery should be stored in object/file storage where appropriate, while PostgreSQL stores metadata and references.

---

# 12. Detection API

## Endpoint

```http
POST /api/v1/detections/analyze
```

## Purpose

Analyze a satellite scene or image reference and return oil-slick detection/characterization results.

## Request

```json
{
  "scene_id": "scene_001",
  "image_url": "...",
  "timestamp": "2026-08-27T14:20:00Z"
}
```

## Response

```json
{
  "detection_id": "det_001",
  "slick_polygon": {},
  "area_km2": 12.4,
  "length_km": 8.2,
  "width_km": 1.4,
  "orientation_deg": 73,
  "confidence": 0.94,
  "age_estimate_hours": 18,
  "age_confidence": 0.42
}
```

## MVP Implementation

The endpoint may initially call a fixture/precomputed detection result while preserving the final API contract.

Later:

```text
Sentinel-1
   ↓
Preprocessing
   ↓
Segmentation model
   ↓
Mask
   ↓
Polygonization
   ↓
Geometric characterization
```

## Acceptance Criteria

- Valid scene request returns detection result.
- GeoJSON polygon is valid.
- Confidence is normalized to `[0,1]`.
- Geometry properties are returned.
- Age uncertainty is represented explicitly.
- Detection request and response are logged.

---

# 13. Drift APIs

## Hindcast

```http
POST /api/v1/drift/hindcast
```

## Forecast

```http
POST /api/v1/drift/forecast
```

## Input

```json
{
  "incident_id": "INC-001",
  "slick_polygon": {},
  "timestamp": "2026-08-27T14:20:00Z"
}
```

## Response

```json
{
  "origin_point": {},
  "origin_probability_cone": {},
  "origin_time_estimate": "2026-08-27T02:10:00Z",
  "origin_confidence": 0.72,
  "hindcast_path": {},
  "forward_path": {}
}
```

## Architecture

```text
Slick
  ↓
Timestamp
  ↓
Wind + current forcing
  ↓
GNOME/OpenDrift
  ↓
Particle trajectories
  ↓
Probability region
  ↓
GeoJSON
```

The project analysis recommends using GNOME or OpenDrift rather than building an oil-transport physics engine from scratch. fileciteturn1file5L210-L222

## MVP

Precomputed drift results are acceptable if the API contract and frontend behavior are real.

## Acceptance Criteria

- Hindcast endpoint returns origin geometry.
- Origin uncertainty can be represented.
- Forecast endpoint returns forward trajectory where data exists.
- Missing forcing data returns a structured error.
- Results are stored/retrievable.
- Drift confidence is exposed.
- No response claims a scientifically exact origin when uncertainty exists.

---

# 14. AIS APIs

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/v1/vessels` | List/search vessels |
| GET | `/api/v1/vessels/{id}` | Vessel details |
| GET | `/api/v1/vessels/{id}/track` | Vessel track |
| GET | `/api/v1/ais` | Query AIS records |
| POST | `/api/v1/ais/upload` | Upload AIS fixture/data |

## AIS Query

Example:

```text
GET /api/v1/ais
    ?start_time=...
    &end_time=...
    &bbox=...
    &vessel_id=...
```

## Acceptance Criteria

- AIS records can be loaded from CSV/JSON fixture data.
- Spatial queries return only relevant records.
- Temporal filtering works.
- Vessel tracks can be returned as GeoJSON.
- Large unrestricted datasets are never sent to the browser by default.

---

# 15. AIS Spatial Query Architecture

The backend should use PostGIS rather than filtering the complete AIS dataset in the browser.

```text
Probable Origin
      ↓
Create search region
      ↓
PostGIS spatial query
      +
Temporal window
      ↓
Relevant AIS points
      ↓
Group by vessel
      ↓
Track reconstruction
```

This is a core backend responsibility.

---

# 16. Attribution API

## Endpoint

```http
POST /api/v1/attribution/score
```

## Input

```json
{
  "incident_id": "INC-001",
  "origin_point": {},
  "origin_time_start": "2026-08-27T01:00:00Z",
  "origin_time_end": "2026-08-27T04:00:00Z"
}
```

The backend may internally perform AIS discovery rather than requiring the frontend to provide all track IDs.

## Output

```json
{
  "ranked_vessels": [
    {
      "vessel_id": "v001",
      "score": 0.87,
      "proximity": 0.92,
      "temporality": 0.89,
      "trajectory_parity": 0.84,
      "anomaly_score": 0.76,
      "anomaly_flag": true
    }
  ]
}
```

## MVP Scoring

Initial heuristic:

```text
Score =
    0.30 × spatial proximity
  + 0.30 × temporal match
  + 0.25 × trajectory alignment
  + 0.15 × AIS anomaly
```

All components must be normalized to `[0,1]`.

These weights are an initial engineering heuristic and must not be represented as scientifically validated probabilities.

The project analysis identifies proximity, temporality, trajectory parity, and AIS anomaly as the important correlation dimensions. fileciteturn1file5L210-L214

## Acceptance Criteria

- Candidates are ranked descending by score.
- Score components are exposed.
- Spatial and temporal filters are applied.
- AIS anomalies are incorporated when present.
- Missing AIS data does not crash the analysis.
- Output is explainable.
- Attribution output is labeled as investigative correlation, not legal proof.

---

# 17. AIS Dark-Vessel / Gap Branch

## Requirement

The backend must explicitly handle incomplete AIS coverage.

```text
Origin window
     ↓
AIS query
     ↓
No complete match / gap found
     ↓
Check last known vessel positions
     ↓
Identify overlapping AIS gap
     ↓
Generate anomaly alert
```

Example:

```json
{
  "anomaly_flag": true,
  "gap_start": "2026-08-27T11:00:00Z",
  "gap_end": "2026-08-27T12:00:00Z",
  "priority": "HIGH",
  "explanation": "AIS gap overlaps inferred investigation window."
}
```

The analysis explicitly recommends a branch for cases where the responsible vessel may have gone dark on AIS. fileciteturn1file7L395-L397

## Acceptance Criteria

- AIS gaps are detected from timestamp discontinuities or source-provided gaps.
- Gaps overlapping the investigation window are flagged.
- The API distinguishes an anomaly from confirmed responsibility.
- No-AIS cases return an actionable investigation state rather than an empty/error screen.

---

# 18. Investigation Aggregation API

## Endpoint

```http
GET /api/v1/investigations/{incident_id}
```

## Purpose

Provide the frontend with one consolidated investigation payload.

## Response Structure

```json
{
  "incident": {},
  "slick": {},
  "drift": {},
  "vessels": [],
  "attribution": [],
  "ais_alerts": [],
  "evidence": {}
}
```

## Rationale

The frontend's main investigation page should not need to understand the internal orchestration of detection, drift, AIS, and attribution.

The backend acts as the orchestration layer.

---

# 19. Evidence API

## Endpoint

```http
GET /api/v1/investigations/{incident_id}/evidence
```

## Response

```json
{
  "incident_id": "INC-001",
  "detection": {
    "confidence": 0.94
  },
  "origin": {
    "confidence": 0.72
  },
  "top_candidate": {
    "vessel_id": "v001",
    "score": 0.87
  },
  "evidence": [
    {
      "type": "spatial",
      "description": "Candidate was within the inferred origin region."
    },
    {
      "type": "temporal",
      "description": "Candidate was present during the inferred origin window."
    },
    {
      "type": "trajectory",
      "description": "Candidate trajectory aligned with inferred drift."
    },
    {
      "type": "ais_anomaly",
      "description": "AIS gap overlaps the investigation window."
    }
  ]
}
```

## Acceptance Criteria

- Evidence is derived from stored analysis results.
- Each evidence item identifies its category.
- Evidence does not overstate certainty.
- Frontend can render the result without additional interpretation.

---

# 20. CSV Export

## Endpoint

```http
GET /api/v1/investigations/{incident_id}/export
```

MVP format:

```text
text/csv
```

Fields:

```text
incident_id
incident_timestamp
vessel_id
vessel_name
mmsi
attribution_score
proximity
temporality
trajectory_parity
anomaly_flag
```

---

# 21. Admin APIs

| Method | Endpoint | Role |
|---|---|---|
| GET | `/api/v1/admin/users` | Admin |
| GET | `/api/v1/admin/vessels` | Admin |
| GET | `/api/v1/admin/incidents` | Admin |

MVP administration is intentionally minimal.

The frontend requires administrators to be able to view users and vessels; advanced administrative workflows are not required for the compressed MVP.

---

# 22. Data Model

## 22.1 Entity Overview

```text
User
 │
 └── authentication/authorization

Incident
 ├── SatelliteScene
 ├── SlickDetection
 ├── DriftResult
 └── AttributionScore
              │
              └── Vessel
                    │
                    └── AISTrack
```

---

# 23. Database Schema

## 23.1 users

```text
users
-------------------------
id UUID PK
name
email UNIQUE
password_hash
role
created_at
updated_at
```

## 23.2 incidents

```text
incidents
-------------------------
id UUID PK
name
description
timestamp
location GEOMETRY(Point, 4326)
status
created_at
updated_at
```

## 23.3 satellite_scenes

```text
satellite_scenes
-------------------------
id UUID PK
satellite
product_type
polarization
timestamp
bbox GEOMETRY(Polygon, 4326)
image_url
thumbnail_url
created_at
```

## 23.4 slick_detections

```text
slick_detections
-------------------------
id UUID PK
incident_id FK
scene_id FK
geometry GEOMETRY(Polygon, 4326)
area_km2
length_km
width_km
orientation_deg
confidence
age_estimate_hours
age_confidence
created_at
```

## 23.5 drift_results

```text
drift_results
-------------------------
id UUID PK
incident_id FK
origin_point GEOMETRY(Point, 4326)
origin_probability_cone GEOMETRY
origin_time_estimate
origin_confidence
hindcast_path GEOMETRY
forecast_path GEOMETRY
model_name
model_version
created_at
```

## 23.6 vessels

```text
vessels
-------------------------
id UUID PK
mmsi
imo
name
type
flag
length
created_at
updated_at
```

## 23.7 ais_tracks

```text
ais_tracks
-------------------------
id UUID PK
vessel_id FK
timestamp
position GEOMETRY(Point, 4326)
speed
course
heading
source
created_at
```

## 23.8 attribution_scores

```text
attribution_scores
-------------------------
id UUID PK
incident_id FK
vessel_id FK
score
proximity_score
temporality_score
trajectory_score
anomaly_score
anomaly_flag
explanation
created_at
```

## 23.9 ml_inference_log

```text
ml_inference_log
-------------------------
id UUID PK
service_name
request_payload JSONB
response_payload JSONB
model_name
model_version
latency_ms
status
timestamp
```

---

# 24. Database Relationships

```text
incidents
   │
   ├───────────────┐
   │               │
   ▼               ▼
scenes        slick_detections
                   │
                   ▼
              drift_results
                   │
                   ▼
             attribution_scores
                   │
                   ▼
                vessels
                   │
                   ▼
               ais_tracks
```

Foreign keys must enforce referential integrity.

---

# 25. Geospatial Requirements

## Mandatory

Use SRID `4326` for stored geographic coordinates unless a specialized projected CRS is required for a particular calculation.

Use PostGIS for:

- Distance calculations.
- Spatial intersections.
- Bounding-box searches.
- Buffer generation.
- Track filtering.
- Slick geometry storage.
- Origin probability regions.

## Example Operations

```text
ST_DWithin
ST_Distance
ST_Intersects
ST_Contains
ST_Buffer
```

Exact functions may vary depending on geometry/geography representation.

---

# 26. Indexing Strategy

Mandatory indexes:

```text
users.email
vessels.mmsi
incidents.timestamp
ais_tracks.timestamp
```

Spatial indexes:

```text
incidents.location
slick_detections.geometry
drift_results.origin_point
ais_tracks.position
```

Use PostgreSQL/PostGIS spatial indexes appropriate to the chosen geometry/geography types.

---

# 27. Data Flow

## 27.1 Complete Investigation Flow

```text
1. Satellite scene registered
        ↓
2. Detection API
        ↓
3. Slick geometry stored
        ↓
4. Drift API
        ↓
5. Origin + uncertainty stored
        ↓
6. AIS query
        ↓
7. Relevant tracks selected
        ↓
8. Attribution engine
        ↓
9. Candidate ranking stored
        ↓
10. AIS anomaly detection
        ↓
11. Evidence generated
        ↓
12. Investigation API
        ↓
13. React frontend
```

---

# 28. External Integrations

## 28.1 Satellite Data

Potential sources include Sentinel-1 public/accessible archives.

The backend should use an adapter:

```text
SatelliteProvider
      ↓
fetch scene metadata
      ↓
normalize
      ↓
store scene metadata
```

The project analysis identifies Sentinel-1 as a practical public SAR source while noting that raw scenes can be large and computationally expensive to preprocess. fileciteturn1file5L216-L220

## 28.2 AIS

Preferred integration:

```text
Global Fishing Watch
```

Fallback:

```text
CSV/JSON fixture
```

Real-time commercial AIS sources may be unavailable or rate-limited for an MVP.

## 28.3 Ocean Currents

```text
Copernicus Marine Service / CMEMS
```

## 28.4 Wind

```text
ECMWF ERA5
```

## 28.5 Drift Model

```text
OpenDrift
or
NOAA GNOME
```

These data/software options are identified as available resources in the project analysis. fileciteturn1file7L293-L299

---

# 29. Integration Adapter Pattern

External services should not be called directly from route handlers.

Use:

```text
API Route
   ↓
Service
   ↓
Integration Adapter
   ↓
External Provider
```

Example:

```text
drift.py
   ↓
drift_service.py
   ↓
opendrift_adapter.py
   ↓
OpenDrift
```

This allows the team to replace:

```text
OpenDrift
```

with:

```text
GNOME
```

without rewriting the API.

---

# 30. Message Queue Strategy

## MVP

**No message queue required.**

Use synchronous API calls or lightweight background processing.

## Future

If processing becomes long-running:

```text
API
 ↓
Job
 ↓
Queue
 ↓
Worker
 ↓
Detection/Drift/Attribution
 ↓
Database
```

Possible future choices:

- Celery + Redis.
- RabbitMQ.
- AWS SQS.

Kafka is not justified for the MVP.

---

# 31. Background Jobs

Use background jobs for:

- Large file ingestion.
- Long-running ML inference.
- Drift simulations.
- Large AIS imports.

MVP implementation:

```text
FastAPI BackgroundTasks
```

Future:

```text
Celery/RQ
+
Redis/RabbitMQ
```

---

# 32. Caching

## MVP

Caching is optional.

Potential cache targets:

- Dashboard aggregates.
- Frequently viewed investigation results.
- Vessel metadata.
- Repeated AIS queries.

## Future

```text
FastAPI
   ↓
Redis
   ↓
PostgreSQL/PostGIS
```

Redis is not a dependency for the critical MVP path.

---

# 33. Data Retention

The MVP should retain:

- Incident metadata.
- Detection results.
- Drift results.
- Attribution results.
- Relevant AIS records.
- Model inference logs.

Raw satellite imagery should not automatically be duplicated into PostgreSQL.

Recommended policy:

```text
Metadata/results:
retain for project lifetime

Raw source data:
retain according to storage capacity,
licensing, and source terms

Logs:
retain at least 30 days for MVP
```

Exact legal retention requirements require confirmation from the eventual deployment organization and jurisdiction.

---

# 34. Security Requirements

## 34.1 Transport

Production APIs must use:

```text
HTTPS / TLS 1.2+
```

TLS 1.3 is preferred where supported.

## 34.2 At Rest

Managed cloud databases should use provider-supported encryption at rest.

Sensitive secrets must not be stored in source code.

## 34.3 Passwords

Never store plaintext passwords.

Use:

```text
Argon2id
```

or an appropriately configured bcrypt implementation.

## 34.4 Input Validation

Validate:

- JSON fields.
- UUIDs.
- Dates.
- Coordinates.
- GeoJSON.
- Numeric ranges.
- File types.
- Upload sizes.
- Pagination parameters.

## 34.5 SQL Injection

Use SQLAlchemy parameterized queries/ORM operations.

Never construct SQL by concatenating untrusted request strings.

## 34.6 CORS

Development:

```text
localhost frontend origin
```

Production:

```text
specific deployed frontend origin
```

Do not use unrestricted:

```text
allow_origins=["*"]
```

for authenticated production APIs.

## 34.7 Secrets

Store through environment variables or a managed secret store:

```text
DATABASE_URL
JWT_SECRET
GFW_API_KEY
CMEMS credentials
ERA5 credentials
```

Never commit secrets.

---

# 35. Compliance Considerations

The MVP does not process medical or payment data and does not inherently require HIPAA compliance.

Potential future considerations include:

- GDPR if personal data from identifiable users or vessel operators is processed in applicable jurisdictions.
- Data licensing restrictions for satellite/AIS sources.
- Maritime data usage restrictions.
- Evidence-chain requirements if outputs are later used in enforcement/legal proceedings.

This PRD does not claim legal compliance certification.

---

# 36. Error Handling

## Standard Format

```json
{
  "error": {
    "code": "AIS_DATA_UNAVAILABLE",
    "message": "AIS data is unavailable for the requested time window."
  }
}
```

## Required Error Codes

```text
AUTHENTICATION_REQUIRED
INVALID_CREDENTIALS
FORBIDDEN
RESOURCE_NOT_FOUND
VALIDATION_ERROR
INVALID_GEOJSON
INVALID_TIME_WINDOW
AIS_DATA_UNAVAILABLE
DRIFT_DATA_UNAVAILABLE
DETECTION_FAILED
ATTRIBUTION_FAILED
EXTERNAL_SERVICE_ERROR
RATE_LIMITED
INTERNAL_ERROR
```

---

# 37. HTTP Status Codes

| Status | Meaning |
|---:|---|
| 200 | Successful request |
| 201 | Resource created |
| 202 | Accepted/background job |
| 400 | Invalid request |
| 401 | Authentication required/invalid |
| 403 | Insufficient permissions |
| 404 | Resource not found |
| 409 | Conflict |
| 422 | Validation error |
| 429 | Rate limited |
| 500 | Internal error |
| 502 | External dependency failure |
| 503 | Service unavailable |

---

# 38. Logging and Observability

## Structured Logging

Every request should ideally include:

```text
timestamp
level
request_id
user_id
endpoint
method
status_code
latency_ms
```

For intelligence services also include:

```text
incident_id
service_name
model_name
model_version
```

## Example

```json
{
  "level": "INFO",
  "request_id": "req_123",
  "endpoint": "/api/v1/attribution/score",
  "incident_id": "INC-001",
  "latency_ms": 842,
  "status_code": 200
}
```

---

# 39. Monitoring

## MVP

At minimum monitor:

- API availability.
- HTTP error rate.
- Request latency.
- Database connectivity.
- External API failures.
- Background job failures.

## Recommended Future Stack

```text
Prometheus
   ↓
Grafana
```

or a managed platform such as Datadog/New Relic.

ELK/OpenSearch is optional and unnecessary for the initial hackathon deployment.

---

# 40. Health Checks

## Liveness

```http
GET /health
```

Response:

```json
{
  "status": "ok"
}
```

## Readiness

Recommended:

```http
GET /health/ready
```

Response:

```json
{
  "status": "ready",
  "database": "connected"
}
```

External dependency health should not necessarily make the core API appear completely dead unless that dependency is required for startup.

---

# 41. Performance Requirements

The MVP is expected to serve a small analyst/demo workload rather than Internet-scale traffic.

Initial targets:

| Operation | Target |
|---|---:|
| Health check | <100 ms |
| Normal CRUD API | <500 ms |
| Incident list | <500 ms |
| Investigation retrieval | <1.5 s |
| AIS spatial query | <2 s for bounded queries |
| Attribution calculation | <5 s |
| Heavy detection/drift job | Asynchronous if >5–10 s |

These are initial engineering targets, not production SLAs.

---

# 42. Scalability Strategy

## Vertical Scaling

First scale:

- CPU.
- RAM.
- Database resources.

## Horizontal Scaling

When required:

```text
             Load Balancer
                  │
       ┌──────────┼──────────┐
       ▼          ▼          ▼
    FastAPI    FastAPI    FastAPI
       │          │          │
       └──────────┼──────────┘
                  ▼
          PostgreSQL/PostGIS
```

FastAPI application instances should remain stateless except for temporary request state.

JWT authentication supports stateless API scaling.

---

# 43. CDN

The backend does not need to serve static frontend assets.

Recommended architecture:

```text
Frontend static assets
       ↓
CDN / frontend host

API requests
       ↓
FastAPI
```

Large imagery should preferably be served from object storage/CDN rather than through FastAPI itself.

---

# 44. Containerization

## Docker Services

MVP:

```text
backend
postgres-postgis
```

Optional:

```text
redis
```

Example:

```text
docker compose up -d
```

Every developer should be able to reproduce the database environment locally.

---

# 45. CI/CD

## Pipeline

```text
Git push
   ↓
GitHub Actions
   ↓
Lint
   ↓
Unit tests
   ↓
Integration tests
   ↓
Docker build
   ↓
Deploy staging
   ↓
Smoke tests
   ↓
Production deployment
```

## Required Checks

- Python formatting/linting.
- Type/static checks where configured.
- Unit tests.
- API tests.
- Docker build.
- Migration validation.

---

# 46. Testing Strategy

## Unit Tests

Test:

- Attribution scoring.
- Distance normalization.
- Temporal scoring.
- Trajectory scoring.
- AIS gap detection.
- Input validation.

## Integration Tests

Test:

```text
FastAPI
   ↓
PostgreSQL/PostGIS
```

including:

- CRUD.
- Spatial queries.
- Authentication.
- RBAC.

## End-to-End Tests

Critical flow:

```text
Login
 ↓
Incident
 ↓
Investigation
 ↓
Slick
 ↓
Drift
 ↓
AIS
 ↓
Attribution
 ↓
Evidence
```

The project execution plan emphasizes an actual end-to-end flow without manually editing the database for the demo. fileciteturn1file6L262-L268

---

# 47. Repository Structure

```text
backend/
│
├── app/
│   ├── main.py
│   │
│   ├── api/
│   │   └── v1/
│   │       ├── router.py
│   │       ├── auth.py
│   │       ├── incidents.py
│   │       ├── scenes.py
│   │       ├── detections.py
│   │       ├── drift.py
│   │       ├── ais.py
│   │       ├── vessels.py
│   │       ├── attribution.py
│   │       ├── investigations.py
│   │       └── admin.py
│   │
│   ├── models/
│   │   ├── user.py
│   │   ├── incident.py
│   │   ├── satellite_scene.py
│   │   ├── slick_detection.py
│   │   ├── drift_result.py
│   │   ├── vessel.py
│   │   ├── ais_track.py
│   │   ├── attribution.py
│   │   └── inference_log.py
│   │
│   ├── schemas/
│   │   ├── auth.py
│   │   ├── incident.py
│   │   ├── scene.py
│   │   ├── detection.py
│   │   ├── drift.py
│   │   ├── ais.py
│   │   ├── vessel.py
│   │   └── attribution.py
│   │
│   ├── services/
│   │   ├── detection_service.py
│   │   ├── drift_service.py
│   │   ├── ais_service.py
│   │   ├── attribution_service.py
│   │   ├── evidence_service.py
│   │   └── investigation_service.py
│   │
│   ├── integrations/
│   │   ├── satellite.py
│   │   ├── global_fishing_watch.py
│   │   ├── opendrift.py
│   │   └── weather.py
│   │
│   └── core/
│       ├── config.py
│       ├── database.py
│       ├── security.py
│       └── logging.py
│
├── migrations/
├── tests/
├── scripts/
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
├── .env.example
└── README.md
```

---

# 48. Recommended Technology Stack

## Core Backend

| Technology | Role | Priority |
|---|---|---:|
| Python 3.12+ | Backend language | P0 |
| FastAPI | REST API | P0 |
| Pydantic v2 | Validation/schema | P0 |
| SQLAlchemy 2 / SQLModel | ORM/data access | P0 |
| PostgreSQL | Relational database | P0 |
| PostGIS | Geospatial storage/querying | P0 |
| Alembic | Database migrations | P0 |
| psycopg | PostgreSQL driver | P0 |

## Geospatial / Scientific

| Technology | Role | Priority |
|---|---|---:|
| Shapely | Geometry operations | P0 |
| GeoPandas | Geospatial processing | P0 |
| PyProj | Coordinate systems | P1 |
| Rasterio | Raster/SAR processing | P1 |
| GDAL | Raster/geospatial tooling | P1 |
| OpenDrift | Drift simulation | P1 |
| NOAA GNOME | Alternative drift model | P1 |
| Pandas | AIS/data processing | P0 |

## Infrastructure

| Technology | Role | Priority |
|---|---|---:|
| Docker | Containers | P0 |
| Docker Compose | Local environment | P0 |
| GitHub Actions | CI/CD | P1 |
| Redis | Cache/rate limiting/jobs | P1 |
| Prometheus | Metrics | P1 |
| Grafana | Dashboards | P1 |

## Testing

| Technology | Role |
|---|---|
| Pytest | Unit/integration testing |
| HTTPX | API testing |
| Testcontainers or Docker | Database integration testing |

---

# 49. Critical Dependency Matrix

| Dependency | Required Before | Owner |
|---|---|---|
| API contracts | Frontend integration | Backend lead |
| DB schema | Core APIs | Backend data developer |
| AIS schema | Attribution | Geospatial developer |
| Origin output | AIS attribution | Drift/ML developer |
| Slick polygon | Drift | Detection/ML developer |
| Historical incident | End-to-end demo | Research/data |
| AIS dataset | Attribution demo | Geospatial/backend |
| Deployment environment | Full integration | DevOps |

---

# 50. Development Roadmap

## Phase 1 — Foundation

**Deliverables**

- Repository.
- Python environment.
- FastAPI.
- Docker.
- PostgreSQL/PostGIS.
- Environment configuration.
- Health endpoint.
- OpenAPI docs.

**Acceptance**

```text
FastAPI → PostgreSQL/PostGIS
```

works locally.

---

## Phase 2 — Database + Core APIs

**Deliverables**

- All MVP database models.
- Alembic migrations.
- Incident CRUD.
- Vessel CRUD/read APIs.
- Scene metadata APIs.
- AIS fixture ingestion.

**Acceptance**

Core data can be created, queried, filtered, and persisted.

---

## Phase 3 — Authentication

**Deliverables**

- Registration.
- Login.
- JWT.
- Current-user endpoint.
- Analyst/admin RBAC.

**Acceptance**

Unauthorized and unauthorized-role requests are correctly rejected.

---

## Phase 4 — Intelligence Contracts

**Deliverables**

```text
/detections/analyze
/drift/hindcast
/drift/forecast
/attribution/score
```

**Acceptance**

All endpoints have stable request/response schemas documented in Swagger.

The existing project plan explicitly calls for freezing these intelligence boundaries early so frontend/backend work can proceed in parallel. fileciteturn1file6L262-L268

---

## Phase 5 — Functional AIS Attribution

**Deliverables**

- PostGIS spatial filtering.
- Temporal filtering.
- Track reconstruction.
- Proximity score.
- Temporal score.
- Trajectory score.
- AIS gap detection.
- Candidate ranking.

**Acceptance**

Given a known historical incident and AIS dataset, the system produces ranked candidate vessels.

---

## Phase 6 — Drift Integration

**Deliverables**

- OpenDrift/GNOME adapter.
- Wind/current inputs.
- Hindcast.
- Forecast.
- Origin probability region.
- Persistence of drift results.

**Acceptance**

A slick can be converted into a reproducible drift result.

---

## Phase 7 — Investigation Orchestration

**Deliverables**

```text
GET /investigations/{id}
GET /investigations/{id}/evidence
```

**Acceptance**

The frontend can load the majority of an investigation through a coherent backend contract.

---

## Phase 8 — Frontend Integration

**Deliverables**

- Authentication integration.
- Incident list.
- Investigation map.
- Slick.
- Drift.
- AIS.
- Attribution.
- Timeline.
- Evidence.

**Acceptance**

Complete demo flow works without manual database editing.

---

## Phase 9 — Deployment

**Deliverables**

- Docker production build.
- Staging deployment.
- Production deployment.
- HTTPS.
- Environment secrets.
- Health checks.
- Logs.

**Acceptance**

Frontend can communicate with the deployed backend over HTTPS.

---

# 51. Timeline for Current Hackathon Sprint

## 27 Aug — Foundation + API Contracts

```text
Morning/Afternoon
├── Repository
├── FastAPI
├── PostgreSQL/PostGIS
├── Schema
├── Alembic
└── API contracts

Evening
├── Auth
├── Incident APIs
├── Vessel APIs
└── AIS fixture loading
```

## 28 Aug — Intelligence + Integration

```text
Morning
├── AIS spatial queries
├── AIS temporal filtering
├── Attribution engine
└── AIS gap detection

Afternoon
├── Detection API
├── Drift API
├── Investigation aggregation
└── Evidence API

Evening
├── Frontend integration
├── End-to-end test
└── Staging deployment
```

## 29 Aug — Stabilization

```text
Morning
├── Integration bugs
├── API failures
├── Data validation
├── Demo dataset
└── Security checks

Afternoon
├── Production deployment
├── Demo rehearsal
└── Code freeze
```

---

# 52. Team Allocation

For a six-person team, the recommended split is:

## Backend/Geospatial Developer 1

Own:

- PostgreSQL/PostGIS.
- Database schema.
- Alembic.
- Incident APIs.
- AIS ingestion.
- Spatial queries.

## Backend/Intelligence Developer 2

Own:

- JWT.
- RBAC.
- Attribution engine.
- AIS anomaly logic.
- Drift adapter.
- Investigation orchestration.

## ML/CV Developers

Own:

- Satellite preprocessing.
- Segmentation.
- Slick polygon generation.
- Detection service implementation.
- Model evaluation.

## Frontend Developer

Own:

- Investigation dashboard.
- GIS map.
- Timeline.
- Attribution UI.
- API integration.

## Research/Data/Pitch

Own:

- Historical incidents.
- Dataset preparation.
- Scientific references.
- Demo narrative.
- Evidence interpretation.

The project analysis recommends a six-person allocation of approximately two ML/CV, two backend/geospatial, one frontend, and one research/design/pitch role. fileciteturn1file6L252-L260

---

# 53. MVP Acceptance Criteria

The backend is considered complete when all of the following are true:

## Infrastructure

- [ ] FastAPI starts successfully.
- [ ] PostgreSQL/PostGIS is reachable.
- [ ] Docker Compose works.
- [ ] Environment variables are configured.
- [ ] `/health` works.
- [ ] `/docs` works.

## Authentication

- [ ] Registration works.
- [ ] Login works.
- [ ] JWT validation works.
- [ ] Analyst/admin authorization works.

## Data

- [ ] Incidents can be stored.
- [ ] Satellite scene metadata can be stored.
- [ ] Slick detections can be stored.
- [ ] Vessels can be stored.
- [ ] AIS records can be stored.
- [ ] Drift results can be stored.
- [ ] Attribution results can be stored.

## Intelligence

- [ ] Detection endpoint works.
- [ ] Hindcast endpoint works.
- [ ] Forecast endpoint works.
- [ ] AIS spatial filtering works.
- [ ] AIS temporal filtering works.
- [ ] Attribution scoring works.
- [ ] AIS gap detection works.
- [ ] Evidence generation works.

## Integration

- [ ] Investigation endpoint returns coherent data.
- [ ] Frontend loads an actual investigation.
- [ ] No manual database editing is needed during demo.
- [ ] Failure states are handled.

## Deployment

- [ ] Staging backend deployed.
- [ ] Production backend deployed.
- [ ] HTTPS enabled.
- [ ] Secrets excluded from source control.
- [ ] Health endpoint accessible.
- [ ] Logs available.

---

# 54. Final Architecture Decision

The backend should be treated as a **modular geospatial investigation engine**.

The most important architectural boundary is:

```text
                     INVESTIGATION
                           │
       ┌───────────────────┼───────────────────┐
       ▼                   ▼                   ▼
   DETECTION             DRIFT                AIS
       │                   │                   │
       ▼                   ▼                   ▼
     SLICK               ORIGIN             VESSELS
       │                   │                   │
       └───────────────────┼───────────────────┘
                           ▼
                    ATTRIBUTION
                           │
                           ▼
                       EVIDENCE
                           │
                           ▼
                      FRONTEND
```

The three intelligence components should be replaceable:

```text
Detection:
fixture → real segmentation model

Drift:
fixture → OpenDrift/GNOME

AIS:
CSV fixture → external AIS provider
```

The frontend and core backend should not need to change when those replacements happen.

---

# 55. Critical Engineering Principle

The backend must **not** be designed as a simple:

```text
Satellite → nearest vessel
```

system.

The project analysis explicitly identifies that as a red flag. A credible system needs time-windowing, trajectory logic, uncertainty handling, and an explicit dark-AIS branch. fileciteturn1file6L244-L250

The intended backend logic is:

```text
Satellite
    ↓
Slick detected
    ↓
Slick geometry + timestamp
    ↓
Drift hindcast
    ↓
Probable origin + time window
    ↓
PostGIS AIS search
    ↓
Candidate vessels
    ↓
Spatial correlation
    +
Temporal correlation
    +
Trajectory alignment
    +
AIS anomaly
    ↓
Explainable attribution ranking
    ↓
Evidence summary
```

That is the backend contract the frontend should be built against.

---

# 56. Appendix — Glossary

| Term | Meaning |
|---|---|
| AIS | Automatic Identification System used for vessel tracking |
| SAR | Synthetic Aperture Radar |
| Slick | Surface feature interpreted as a possible oil spill |
| Hindcast | Modeling movement backward from an observed state |
| Forecast | Modeling expected future movement |
| Origin | Estimated source region/time of the observed slick |
| Probability Cone | Spatial representation of origin/drift uncertainty |
| PostGIS | PostgreSQL extension for geospatial data |
| GeoJSON | JSON format for geographic objects |
| MMSI | Maritime Mobile Service Identity |
| GNOME | NOAA oil-spill trajectory modeling system |
| OpenDrift | Open-source particle drift modeling framework |
| CMEMS | Copernicus Marine Service |
| ERA5 | ECMWF atmospheric reanalysis dataset |
| Attribution Score | Explainable ranking score for candidate vessels |
| AIS Gap | Period during which expected AIS data is absent |
| Dark Vessel | Vessel whose AIS visibility is absent/incomplete during a relevant period |
| RBAC | Role-Based Access Control |
| JWT | JSON Web Token |

---

# 57. Appendix — Assumptions

1. The primary frontend is a React/TypeScript GIS dashboard.
2. The primary backend API is FastAPI.
3. PostgreSQL/PostGIS is the authoritative operational database.
4. Historical data is acceptable for the MVP.
5. Detection and drift may use precomputed results during the initial sprint.
6. Attribution must be explainable.
7. AIS gaps are investigative indicators rather than proof of responsibility.
8. Satellite detection and drift uncertainty must be exposed.
9. The MVP is optimized for a small analyst workload rather than Internet-scale traffic.
10. Production legal/compliance requirements will depend on the eventual deployment organization, data providers, and jurisdiction.
11. External provider availability and API limits may require CSV or precomputed fallbacks.
12. The system should be extensible toward Indian coastal surveillance infrastructure; the project analysis identifies ISRO EOS-4 and INCOIS as potential future integration paths. fileciteturn1file8L349-L353

---

# 58. Final Technology Lock

```text
                 ┌─────────────────────────────┐
                 │ React + TypeScript Frontend │
                 └──────────────┬──────────────┘
                                │
                         HTTPS / REST
                                │
                                ▼
                 ┌─────────────────────────────┐
                 │          FastAPI            │
                 │       Python 3.12+          │
                 └──────────────┬──────────────┘
                                │
               ┌────────────────┼─────────────────┐
               ▼                ▼                 ▼
          SQLAlchemy         Services        Integrations
               │                │                 │
               ▼                ▼                 ▼
        PostgreSQL +       Attribution      AIS / Satellite
           PostGIS         Detection        CMEMS / ERA5
                           Drift/OpenDrift
                                │
                                ▼
                         Investigation
                                │
                                ▼
                           Evidence
```

## Final Stack

**Python + FastAPI + Pydantic + SQLAlchemy/SQLModel + PostgreSQL + PostGIS + Alembic + GeoPandas + Shapely + Pandas + Rasterio/GDAL + OpenDrift/GNOME + JWT + Docker + Pytest**

**Redis, Celery/RQ, Prometheus/Grafana, and distributed messaging remain optional until the core investigation pipeline is stable.**
