# Satellite Ingestion Module — Backend PRD / Implementation Specification

> **Purpose:** Implementation specification for an AI coding agent. Defines the Satellite Ingestion feature for the existing backend without redesigning the rest of the system.
>
> **Scope:** Ingest Sentinel-1 satellite scenes from the project's replay/data-source pipeline, validate and normalize their metadata, persist scene information, register the image artifact, and trigger downstream analysis asynchronously.
>
> **Important:** The ingestion module must **not implement the oil-spill AI model, drift model, AIS correlation, or vessel attribution**. It only prepares and dispatches satellite scenes to downstream components.

---

## 1. Objective

Implement a robust **Satellite Ingestion Service** that accepts a satellite scene produced by the project's satellite-data replay mechanism and converts it into a validated, persistent backend entity.

```text
Historical Sentinel-1 Dataset
          │
          ▼
    Replay Script
          │
          ▼
   Satellite Ingestion API
          │
          ├── Validate metadata
          ├── Validate image reference
          ├── Normalize metadata
          ├── Check duplicate
          ├── Store scene metadata
          └── Create analysis job
                    │
                    ▼
             Message / Job Queue
                    │
                    ▼
               AI Service
```

The system should behave as though satellite acquisitions are arriving sequentially.

The current source may be a historical Sentinel-1 dataset replay, but the ingestion interface must remain source-agnostic so a genuine satellite provider can be connected later.

---

## 2. Existing Backend Context

The existing backend already has a satellite scene domain and API/service architecture.

Relevant concepts:

```text
app/
├── api/v1/
│   └── scenes.py
├── models/
│   └── satellite_scene.py
├── schemas/
├── services/
└── ...
```

### Do NOT

- create a second `SatelliteScene` model
- create duplicate scene endpoints
- create another database layer
- replace the existing FastAPI architecture
- introduce a new framework
- rewrite existing services unnecessarily

### Instead

Extend the existing architecture.

---

## 3. Mandatory Goals

1. Accept satellite-scene metadata.
2. Validate the incoming request.
3. Validate the referenced image/file.
4. Normalize satellite metadata.
5. Detect duplicate scenes.
6. Persist the scene in PostgreSQL/PostGIS.
7. Assign or preserve a unique scene identifier.
8. Record ingestion status.
9. Create an analysis job/event.
10. Return a useful API response.
11. Handle malformed data safely.
12. Provide structured logging.
13. Be testable without the complete 40 GB dataset.
14. Support replayed historical Sentinel-1 acquisitions.

---

## 4. Non-Goals

The Satellite Ingestion module must **not**:

- detect oil spills
- run DeepLabv3/U-Net/etc.
- calculate spill confidence
- calculate spill area from pixels
- calculate vessel responsibility
- query AIS
- calculate drift
- forecast ocean movement
- perform image segmentation
- train ML models
- perform satellite image enhancement unless explicitly required elsewhere

Those belong to downstream services.

---

## 5. Functional Architecture

```text
                    ┌──────────────────────┐
                    │ Sentinel-1 Dataset   │
                    │ / Replay Script      │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │ Satellite API        │
                    │ /scenes/ingest       │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │ Request Validation   │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │ Ingestion Service    │
                    └──────────┬───────────┘
                               │
              ┌────────────────┼────────────────┐
              ▼                ▼                ▼
        Duplicate Check   File Check      Metadata
                                             Normalize
              │                │                │
              └────────────────┼────────────────┘
                               ▼
                    ┌──────────────────────┐
                    │ PostgreSQL/PostGIS   │
                    │ satellite_scenes     │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │ Analysis Job/Event   │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │ AI/ML Processing     │
                    └──────────────────────┘
```

---

## 6. API Design

Use the existing `/api/v1/scenes` router.

### Endpoint

```http
POST /api/v1/scenes/ingest
```

Do not create `/api/v1/satellite/ingest` if the existing API architecture already uses `scenes.py`.

---

## 7. Request Schema

Recommended request:

```json
{
  "source": "sentinel-1-replay",
  "scene_id": "S1A_20250615_001",
  "satellite": "Sentinel-1A",
  "sensor": "SAR",
  "product_type": "GRD",
  "acquisition_time": "2025-06-15T05:12:00Z",
  "processing_time": null,
  "polarization": ["VV", "VH"],
  "orbit": "ASCENDING",
  "image_uri": "storage://satellite-scenes/S1A_20250615_001.tif",
  "bbox": {
    "min_lat": 12.0,
    "min_lon": 68.0,
    "max_lat": 12.5,
    "max_lon": 68.5
  },
  "metadata": {}
}
```

The exact fields must be reconciled with the **existing `SatelliteScene` schema/model** rather than blindly replacing it.

---

## 8. Required vs Optional Fields

| Field | Required | Purpose |
|---|---:|---|
| `scene_id` | YES | Source scene identifier |
| `source` | YES | Identifies data source/replay |
| `satellite` | YES | Satellite platform |
| `acquisition_time` | YES | Critical for temporal analysis |
| `image_uri` | YES | Location of image artifact |
| `bbox` | YES | Geographic coverage |
| `sensor` | Recommended | Sensor information |
| `product_type` | Recommended | Sentinel product |
| `polarization` | Optional | SAR polarization |
| `orbit` | Optional | Orbit direction |
| `processing_time` | Optional | Processing timestamp |
| `metadata` | Optional | Additional provider metadata |

---

## 9. Acquisition Time

Treat `acquisition_time` as a first-class field.

It will later be used for:

```text
Satellite Scene
      │
      ├── AI detection
      ├── Drift analysis
      └── AIS correlation
              │
              ▼
       Vessel positions
       around spill time
```

Do not silently replace acquisition time with ingestion time.

Example:

```text
acquisition_time = 2025-06-15T05:12:00Z
ingestion_time   = 2026-08-28T07:30:00Z
```

The first represents when the satellite captured the scene. The second represents when the system received it.

---

## 10. Replay Compatibility

The ingestion API must support the project's replay architecture.

```text
Replay Engine
     │
     ├── Scene 001
     ├── Scene 002
     ├── Scene 003
     └── Scene 004
```

Each scene should pass through the same ingestion endpoint.

The replay system must not use a special shortcut around the backend.

---

## 11. Idempotency

The same scene may accidentally be submitted more than once.

Use a uniqueness strategy based on source scene identity, for example:

```text
(source, scene_id)
```

First request:

```http
201 Created
```

For duplicates, choose one consistent policy:

```http
200 OK
```

returning the existing scene, or:

```http
409 Conflict
```

if that matches existing API conventions.

---

## 12. File/Image Handling

Do **not** store large Sentinel-1 images directly inside PostgreSQL.

Use object/file storage:

```text
PostgreSQL
    │
    └── image_uri
             │
             ▼
       Object Storage
             │
             ├── TIFF
             ├── GeoTIFF
             └── processed artifacts
```

For development, local filesystem or MinIO can be used.

For production, use S3-compatible object storage.

The database stores the `image_uri`, not the binary image.

---

## 13. Local Replay Mode

For development, support local files where appropriate:

```json
{
  "image_uri": "file:///data/sentinel-1/S1_scene_001.tif"
}
```

Restrict local file access to a configured dataset directory:

```env
SATELLITE_DATA_ROOT=/data/satellite
```

Never allow arbitrary filesystem access such as `/etc/passwd`.

---

## 14. Metadata Normalization

Normalize provider-specific metadata into the internal representation.

Example:

```text
External:
"satelliteName": "S1A"

Internal:
satellite = "Sentinel-1A"
```

and:

```text
"acqTime"
      ↓
"acquisition_time"
```

Downstream services consume the normalized representation.

---

## 15. Geographic Validation

Validate bounding-box coordinates.

```text
-90 ≤ latitude ≤ 90
-180 ≤ longitude ≤ 180
```

and:

```text
min_lat < max_lat
min_lon < max_lon
```

Invalid geographic data must be rejected.

---

## 16. PostGIS Geometry

If the existing model supports geographic geometry, use PostGIS.

Recommended SRID:

```text
4326
```

Represent the scene footprint as a polygon or multipolygon where appropriate.

If only a bounding box is available, generate a bounding-box polygon.

Do not invent detailed geometry from incomplete metadata.

---

## 17. Scene Lifecycle

Use the existing status model if one already exists.

Conceptually:

```text
RECEIVED
    ↓
VALIDATING
    ↓
INGESTED
    ↓
QUEUED
    ↓
PROCESSING
    ↓
COMPLETED
```

Errors should transition to:

```text
FAILED
```

Do not duplicate existing status definitions.

---

## 18. Analysis Job Creation

After successful ingestion:

```text
SatelliteScene
      │
      ▼
Create Analysis Job
      │
      ▼
PENDING
```

The ingestion endpoint must **not wait for AI inference**.

### Incorrect

```text
POST /ingest
      ↓
run AI
      ↓
run drift
      ↓
query AIS
      ↓
return
```

### Correct

```text
POST /ingest
      ↓
validate
      ↓
save
      ↓
create job
      ↓
queue
      ↓
return
```

Example response:

```json
{
  "scene_id": "S1A_20250615_001",
  "status": "QUEUED",
  "analysis_id": "ANL_001"
}
```

---

## 19. Event Contract

Recommended event:

```json
{
  "event_type": "SATELLITE_SCENE_INGESTED",
  "event_id": "evt_001",
  "scene_id": "S1A_20250615_001",
  "analysis_id": "ANL_001",
  "source": "sentinel-1-replay",
  "acquisition_time": "2025-06-15T05:12:00Z",
  "image_uri": "storage://satellite-scenes/S1A_20250615_001.tif",
  "created_at": "2026-08-28T07:30:00Z"
}
```

The event is what the AI worker should consume.

---

## 20. API Response

Successful ingestion:

```json
{
  "success": true,
  "scene_id": "S1A_20250615_001",
  "analysis_id": "ANL_001",
  "status": "QUEUED",
  "message": "Satellite scene successfully ingested."
}
```

Do not return the AI result from this endpoint.

---

## 21. Error Handling

### Invalid metadata

```http
400 Bad Request
```

```json
{
  "error": {
    "code": "INVALID_SCENE_METADATA",
    "message": "Invalid satellite scene metadata."
  }
}
```

### Duplicate scene

```http
409 Conflict
```

or the selected idempotent behavior.

### Image unavailable

```http
422 Unprocessable Entity
```

```json
{
  "error": {
    "code": "IMAGE_NOT_ACCESSIBLE",
    "message": "The referenced satellite image could not be accessed."
  }
}
```

### Internal failure

```http
500 Internal Server Error
```

Never expose stack traces, credentials, or internal filesystem details.

---

## 22. Authentication and Authorization

Use the backend's existing authentication mechanism.

Do not introduce a separate authentication system.

Example policy:

```text
ADMIN
  ✓ ingest

ANALYST
  ✓ ingest

VIEWER
  ✗ ingest
```

If the existing authorization model differs, follow it.

---

## 23. Rate Limiting

The replay engine may send scenes rapidly during demonstrations.

Do not impose an artificially low limit that prevents replay.

Reuse the project's existing rate-limiting mechanism where possible.

---

## 24. Security Requirements

### Path traversal

Reject paths such as:

```text
../../etc/passwd
```

### SSRF

If HTTP URLs are supported, do not blindly fetch arbitrary URLs. Restrict allowed domains or use an approved storage service.

### File size

Make maximum image size configurable:

```env
MAX_SATELLITE_IMAGE_SIZE_MB=2048
```

### File type

Validate the actual file format rather than trusting the filename extension.

---

## 25. Structured Logging

Example:

```json
{
  "event": "satellite_scene_ingested",
  "scene_id": "S1A_20250615_001",
  "source": "sentinel-1-replay",
  "acquisition_time": "2025-06-15T05:12:00Z",
  "status": "QUEUED"
}
```

Failure:

```json
{
  "event": "satellite_ingestion_failed",
  "scene_id": "S1A_20250615_001",
  "reason": "IMAGE_NOT_ACCESSIBLE"
}
```

Never log JWT tokens, passwords, or credentials.

---

## 26. Database Requirements

Conceptually:

```text
satellite_scenes
────────────────────────
id
scene_id
source
satellite
sensor
product_type
acquisition_time
ingestion_time
image_uri
footprint
bbox
metadata
status
created_at
updated_at
```

The exact schema must follow the existing model.

---

## 27. Database Indexing

Ensure efficient lookup by:

```text
scene_id
acquisition_time
status
```

Use a spatial index for the footprint where appropriate.

Important future query:

```text
Find satellite scenes
within geographic region
during a time period.
```

---

## 28. Replay Ordering

The replay engine should normally process scenes by:

```text
acquisition_time ASC
```

The backend must not assume requests always arrive chronologically.

The authoritative timestamp remains `acquisition_time`.

---

## 29. Replay Speed

The replay engine controls simulation speed.

Example:

```text
Real:
24 hours

Demo:
2 minutes
```

The backend should not contain replay timing logic.

It only processes events as they arrive.

---

## 30. Testing Strategy

The feature must be testable without downloading the 40 GB dataset.

Use small fixtures:

```text
tests/
└── fixtures/
    └── satellite/
        ├── valid_scene.json
        ├── invalid_scene.json
        └── sample_scene.tif
```

The image can be a tiny synthetic/test raster.

---

## 31. Mandatory Unit Tests

Test:

```text
test_valid_scene_metadata()
test_invalid_coordinates()
test_invalid_timestamp()
test_missing_image_uri()
test_invalid_source()
test_duplicate_scene()
test_metadata_normalization()
test_scene_id_generation()
```

---

## 32. Mandatory Integration Tests

Test:

```text
POST /api/v1/scenes/ingest
        ↓
FastAPI
        ↓
Database
        ↓
SatelliteScene
```

Verify both the HTTP response and database record.

---

## 33. Queue Integration Test

Mock the message broker.

Verify:

```text
POST /ingest
      ↓
scene created
      ↓
event generated
```

The event must contain:

```text
event_type
scene_id
analysis_id
image_uri
acquisition_time
```

---

## 34. End-to-End Test

Eventually:

```text
Test Satellite Scene
       ↓
POST ingestion
       ↓
Scene stored
       ↓
Analysis created
       ↓
Event emitted
       ↓
Mock AI worker
       ↓
Detection result
```

The real ML model must not be required for ingestion tests.

---

# 35. Implementation Sequence for the AI Coding Agent

## Step 1 — Inspect Existing Code

Before changing anything, inspect:

```text
app/api/v1/scenes.py
app/models/satellite_scene.py
app/schemas/
app/services/
app/core/
alembic/
tests/
```

Determine:

- existing fields
- existing endpoints
- existing database conventions
- dependency injection
- authentication
- error handling
- service patterns

Do not rewrite working components.

## Step 2 — Identify Gaps

Produce a short plan:

```text
Existing:
✓ API
✓ Model
✓ Schema

Missing:
? validation
? duplicate protection
? image validation
? job creation
? event emission
? tests
```

## Step 3 — Implement Validation

Implement:

```text
metadata validation
timestamp validation
geographic validation
image reference validation
```

## Step 4 — Implement Ingestion Service

Conceptually:

```python
ingest_scene(scene_request)
```

Responsibilities:

```text
validate
    ↓
check duplicate
    ↓
normalize
    ↓
persist
    ↓
create analysis
    ↓
emit event
    ↓
return result
```

Keep business logic outside the router.

## Step 5 — Implement API Endpoint

Keep the router thin:

```text
HTTP request
    ↓
Pydantic schema
    ↓
Service
    ↓
Response
```

## Step 6 — Implement Analysis Job Creation

```text
scene
 ↓
analysis job
```

## Step 7 — Implement Event Publishing

Use the project's selected queue/broker abstraction.

If a broker is not implemented yet, create an interface/adapter rather than a hard dependency that prevents local development.

Conceptually:

```text
EventPublisher
    │
    ├── InMemoryPublisher
    └── RabbitMQPublisher
```

Follow existing messaging infrastructure if one exists.

## Step 8 — Add Tests

Run:

```bash
pytest tests/ -v
```

All existing tests must continue passing.

## Step 9 — Add Documentation

Document:

```text
endpoint
request
response
errors
replay usage
environment variables
```

---

# 36. Environment Variables

Add only variables not already present.

Potential configuration:

```env
SATELLITE_DATA_ROOT=/data/satellite
SATELLITE_MAX_IMAGE_SIZE_MB=2048
SATELLITE_ALLOWED_SCHEMES=file,storage
SATELLITE_DEFAULT_SRID=4326
```

For object storage:

```env
OBJECT_STORAGE_ENDPOINT=
OBJECT_STORAGE_BUCKET=
OBJECT_STORAGE_ACCESS_KEY=
OBJECT_STORAGE_SECRET_KEY=
```

Never commit credentials.

---

# 37. Acceptance Criteria

### AC-01 — Valid ingestion

Given valid satellite metadata and an accessible image, `POST /api/v1/scenes/ingest` returns success and persists the scene.

### AC-02 — Invalid metadata

Malformed metadata is rejected with a meaningful validation error.

### AC-03 — Geographic validation

Invalid coordinates or bounding boxes are rejected.

### AC-04 — Duplicate protection

Submitting the same source scene twice does not create duplicate records.

### AC-05 — Image validation

The referenced image is verified as accessible and acceptable.

### AC-06 — Persistence

The successfully ingested scene appears in the satellite-scene database model.

### AC-07 — Analysis creation

Successful ingestion creates an analysis job or equivalent processing record.

### AC-08 — Event emission

Successful ingestion produces `SATELLITE_SCENE_INGESTED` for downstream processing.

### AC-09 — Asynchronous behavior

The ingestion API does not wait for AI inference.

### AC-10 — Replay compatibility

A replay script can submit multiple historical Sentinel-1 scenes sequentially.

### AC-11 — Chronological metadata

Original satellite acquisition timestamps are preserved exactly.

### AC-12 — Security

Path traversal, unauthorized access, unsafe URLs, and excessive file sizes are rejected.

### AC-13 — Tests

Unit and integration tests pass without requiring the complete 40 GB dataset.

---

# 38. Future Live Satellite Extension

The ingestion contract should eventually support multiple sources:

```text
                  Satellite Sources
                         │
             ┌───────────┴───────────┐
             ▼                       ▼
       Historical Replay        Live Provider
             │                       │
             └───────────┬───────────┘
                         ▼
                  Ingestion API
                         │
                         ▼
                   Same Pipeline
```

This allows the current demo to use historical Sentinel-1 data while leaving the architecture ready for a future live provider.

---

# 39. Final Pipeline

```text
SATELLITE
    │
    ▼
INGESTION
    │
    ▼
AI DETECTION
    │
    ▼
OIL SLICK
    │
    ▼
DRIFT ENGINE
    │
    ├── HINDCAST
    └── FORECAST
    │
    ▼
AIS CORRELATION
    │
    ▼
VESSEL RANKING
    │
    ▼
INVESTIGATION
    │
    ▼
FRONTEND MAP
```

## Definition of Done

The Satellite Ingestion feature is complete when:

```text
SATELLITE REPLAY
       │
       ▼
POST /scenes/ingest
       │
       ▼
VALIDATION
       │
       ▼
DUPLICATE CHECK
       │
       ▼
METADATA NORMALIZATION
       │
       ▼
PostgreSQL/PostGIS
       │
       ▼
ANALYSIS JOB
       │
       ▼
EVENT PUBLISHED
       │
       ▼
AI/ML
```

works end-to-end using **one small Sentinel-1 scene fixture**, without requiring the complete 40 GB dataset.

---

## Core Implementation Principle

> **Receive a satellite acquisition → validate it → preserve its metadata → register its image → create an analysis job → emit an event.**

The ingestion layer should remain simple and reliable. Oil-spill intelligence belongs downstream.
