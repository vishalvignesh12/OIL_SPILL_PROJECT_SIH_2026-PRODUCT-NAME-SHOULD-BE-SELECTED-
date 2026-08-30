# PRD — ML Inference Integration & Oil-Spill Detection Persistence

**Project:** AI-Based Satellite Oil Spill Detection & Vessel Attribution Platform  
**Feature:** ML Detection Integration  
**Priority:** P0 — MVP Critical  
**Status:** Ready for Development

## 1. Executive Summary

Connect the existing backend analysis pipeline to the ML oil-spill detection model.

Target vertical slice:

```text
Satellite Scene
      ↓
Satellite Ingestion       [Existing]
      ↓
Analysis Orchestration    [Existing]
      ↓
ML Inference              [THIS FEATURE]
      ↓
Prediction Validation
      ↓
Detection Persistence
      ↓
PostGIS Spill Geometry
      ↓
Dashboard APIs            [Existing]
```

The backend must submit an ingested scene to ML inference, receive a structured prediction, validate it, persist the result, and expose it through the existing dashboard.

**ML training is out of scope.** The ML engineer owns the model; the backend owns the inference contract, invocation, validation, persistence, errors, and integration.

## 2. MVP Objective

Given a valid satellite scene, the backend must produce and persist a usable oil-spill detection.

Example:

```json
{
  "detected": true,
  "confidence": 0.94,
  "area_km2": 12.43,
  "geometry": {
    "type": "Polygon",
    "coordinates": []
  },
  "model_name": "oilspill-detector",
  "model_version": "v1"
}
```

## 3. Scope

### Mandatory

- ML input/output contract
- ML integration service/provider
- Model invocation
- Timeout/error handling
- Response validation
- Detection persistence
- PostGIS spill geometry
- Analysis → detection relationship
- Detection status
- Model/version tracking
- Unit and integration tests
- Dashboard compatibility

### Out of Scope

```text
❌ ML training
❌ Dataset preparation
❌ Model architecture
❌ Hyperparameter tuning
❌ AIS integration
❌ Drift/hindcast
❌ Vessel attribution
❌ Frontend
❌ Kubernetes
❌ Advanced model serving
```

## 4. Mandatory Pre-Implementation Inspection

The coding agent must inspect and reuse:

```text
satellite ingestion
analysis orchestration
database models
database session
PostgreSQL/PostGIS
service/repository patterns
Pydantic schemas
configuration
error handling
tests
dashboard spill endpoint
```

Do not create duplicate models or infrastructure.

## 5. Architecture

```text
Satellite Scene
      ↓
Analysis Orchestrator
      ↓
ML Integration Service
      ↓
ML Provider
      ↓
Prediction
      ↓
Validation
      ↓
Detection Repository
      ↓
PostgreSQL + PostGIS
      ↓
Dashboard API
```

Recommended abstraction:

```python
class MLInferenceProvider:
    async def predict(scene) -> MLPrediction:
        ...
```

The exact implementation must follow the existing backend architecture.

## 6. ML Input Contract

Conceptual request:

```json
{
  "scene_id": "SCENE-001",
  "image_uri": "/data/scenes/scene-001.tif",
  "acquisition_time": "2026-08-29T10:30:00Z",
  "sensor": "Sentinel-1",
  "latitude": 9.72,
  "longitude": 75.98,
  "bounding_box": {
    "min_lat": 9.70,
    "min_lon": 75.95,
    "max_lat": 9.75,
    "max_lon": 76.02
  }
}
```

Adapt this to the existing satellite-scene model.

Do not transfer large images through JSON unnecessarily. Prefer an existing file path, object URI, mounted volume, or internal image reference.

## 7. ML Output Contract

Minimum result:

```json
{
  "detected": true,
  "confidence": 0.94,
  "area_km2": 12.43,
  "geometry": {
    "type": "Polygon",
    "coordinates": []
  },
  "model_name": "oilspill-detector",
  "model_version": "v1"
}
```

| Field | Type | Required | Description |
|---|---|---:|---|
| `detected` | boolean | Yes | Oil spill detected |
| `confidence` | float | Yes | 0–1 confidence |
| `area_km2` | float | Recommended | Estimated area |
| `geometry` | GeoJSON | When detected | Spill region |
| `model_name` | string | Yes | Model identifier |
| `model_version` | string | Yes | Model version |

## 8. Validation

Validate before persistence.

```text
0 <= confidence <= 1
area_km2 >= 0
geometry is structurally valid
geometry coordinates are valid
correct spatial reference
model_name present
model_version present
```

When `detected=true`, a valid spill geometry should normally be present.

Invalid predictions must not be silently stored.

## 9. Detection Persistence

Conceptual entity:

```text
Detection
├── id
├── analysis_id
├── scene_id
├── detected
├── confidence
├── area_km2
├── geometry
├── model_name
├── model_version
├── status
├── created_at
└── updated_at
```

Do not blindly create these exact fields if equivalent models already exist.

The detection must be traceable to:

```text
scene
analysis
model
model version
timestamp
```

## 10. Detection Lifecycle

Recommended MVP states:

```text
PENDING
   ↓
PROCESSING
   ↓
COMPLETED
```

Failure:

```text
PROCESSING
   ↓
FAILED
```

Keep the state machine simple.

## 11. Orchestration Integration

The existing orchestrator should invoke ML:

```text
Analysis Job
     ↓
Validate scene
     ↓
PROCESSING
     ↓
ML inference
     ↓
Validate prediction
     ↓
Persist detection
     ↓
COMPLETED
```

On failure:

```text
ML error/timeout
      ↓
Record error
      ↓
FAILED
```

Do not duplicate existing orchestration lifecycle logic.

## 12. Idempotency

Prevent accidental duplicate detections for the same logical analysis.

The implementation must follow existing uniqueness/retry conventions.

If retries exist, use a clearly defined policy rather than creating uncontrolled duplicate results.

## 13. Error Handling

Handle:

```text
ML unavailable
ML timeout
ML execution failure
invalid ML response
missing fields
invalid confidence
invalid geometry
database failure
```

Never expose:

```text
stack traces
database credentials
ML credentials
internal filesystem paths
```

## 14. Timeout & Retry

External ML calls must have configurable timeouts.

Example:

```text
ML_INFERENCE_TIMEOUT_SECONDS
```

Retries must be limited. For MVP, at most one controlled retry where safe; otherwise mark the operation failed.

Do not retry indefinitely.

## 15. Configuration

Do not hardcode service configuration.

Potential variables:

```text
ML_PROVIDER
ML_SERVICE_URL
ML_INFERENCE_TIMEOUT_SECONDS
ML_MODEL_NAME
ML_MODEL_VERSION
```

Only add variables actually required by the selected ML implementation.

Never commit secrets.

## 16. PostGIS

Persist detected spill geometry using the existing PostGIS infrastructure.

Ensure:

```text
valid geometry
correct SRID
correct coordinate order
```

For GeoJSON, coordinates are:

```text
[longitude, latitude]
```

not `[latitude, longitude]`.

The geometry must remain compatible with:

```http
GET /api/v1/dashboard/spills
```

## 17. Dashboard Integration

No ML-specific dashboard implementation should be necessary if the dashboard already reads persisted spill data.

Expected flow:

```text
ML Prediction
     ↓
Detection
     ↓
PostGIS
     ↓
GET /api/v1/dashboard/spills
     ↓
GeoJSON
     ↓
Frontend map
```

## 18. Logging

Use existing structured logging.

Record useful lifecycle events:

```text
ML inference started
ML inference completed
ML inference failed
Detection persisted
```

Include:

```text
scene_id
analysis_id
detection_id
model_name
model_version
duration_ms
```

Do not log sensitive information.

## 19. Testing

### Unit Tests

Test:

```text
valid prediction accepted
invalid confidence rejected
invalid area rejected
invalid geometry rejected
missing model version rejected
timeout handled
ML exception handled
successful persistence
failed inference status
```

### Integration Tests

Verify:

```text
Analysis
  ↓
ML provider
  ↓
Prediction
  ↓
Detection
  ↓
Database
```

Use a fake/mock ML provider for normal tests.

### API Test

Verify:

```text
analysis completes
      ↓
detection persisted
      ↓
GET /dashboard/spills
      ↓
valid GeoJSON returned
```

## 20. Acceptance Criteria

- [ ] Existing analysis orchestration invokes ML.
- [ ] Input contract documented.
- [ ] Output contract documented.
- [ ] Prediction validated before persistence.
- [ ] Confidence constrained to 0–1.
- [ ] Geometry validated.
- [ ] Detection persisted.
- [ ] Detection linked to scene/analysis.
- [ ] Model name/version stored.
- [ ] Detection status maintained.
- [ ] Timeout handled.
- [ ] ML failures handled.
- [ ] Duplicate results controlled.
- [ ] PostGIS geometry correct.
- [ ] Dashboard can expose persisted spill.
- [ ] Unit tests pass.
- [ ] Integration tests pass.
- [ ] No secrets committed.
- [ ] Existing ingestion/orchestration remains functional.

## 21. Implementation Sequence

### Step 1 — Inspect
Inspect ingestion, orchestration, models, PostGIS, services, repositories, config, tests, and dashboard APIs.

### Step 2 — Map
Map:

```text
Satellite Scene → existing model
Analysis → existing model
Detection → existing/equivalent model
Geometry → existing PostGIS utilities
```

### Step 3 — Contract
Create typed ML request/response schemas.

### Step 4 — Provider
Implement an ML provider abstraction.

### Step 5 — Service
Implement inference, timeout handling, response validation, and normalization.

### Step 6 — Persistence
Persist validated detections and geometry.

### Step 7 — Integration
Connect the service to analysis orchestration.

### Step 8 — Testing
Run unit, integration, and existing backend tests.

### Step 9 — Dashboard Verification
Verify detection → database → `/dashboard/spills` → GeoJSON.

## 22. MVP Demo

The feature should enable:

```text
SATELLITE IMAGE
      ↓
INGESTION
      ↓
ANALYSIS JOB
      ↓
ML MODEL
      ↓
Oil Spill Detected — 94%
      ↓
Spill Polygon
      ↓
Database
      ↓
Dashboard Map
```

Example displayed result:

```text
Oil Spill Detected
Confidence: 94%
Estimated Area: 12.43 km²
Model: oilspill-detector
Version: v1
```

## 23. ML Engineer Handoff

Backend and ML engineer must agree on:

```text
1. Input format
2. Output format
3. Confidence semantics
4. Geometry format
5. CRS/SRID
6. Model name
7. Model version
8. Expected inference time
9. Error format
10. Image/file access method
```

Do not integrate undocumented assumptions.

## 24. Final AI Coding-Agent Instruction

> Inspect the existing backend repository first. Implement ML inference integration as a clean service/provider layer connected to the existing analysis orchestration. Reuse existing models, repository patterns, database session, PostGIS utilities, configuration, error handling, and testing conventions. Do not implement or modify the ML model itself. Define a typed input/output contract, invoke the configured ML provider, validate the prediction, persist the detection and spill geometry, track model name/version, handle timeout and inference failures, and make the persisted result compatible with the existing dashboard spill endpoint. Add unit and integration tests. Do not rewrite satellite ingestion, analysis orchestration, dashboard APIs, drift, AIS, attribution, or frontend code except where a minimal integration change is strictly necessary.

## 25. What to Build Next

After ML integration works, build in this order:

```text
1. ML Detection Integration       ← NOW
2. Investigation/Incident Model
3. Drift/Hindcast Integration
4. AIS Data Integration
5. AIS-Spill Correlation
6. Vessel Attribution/Ranking
7. Evidence + Investigation Timeline
```

If the existing backend already has a complete Investigation/Incident model, skip #2 and move directly to Drift/Hindcast.

## MVP Success Condition

The immediate feature is successful when:

```text
Satellite Scene
      ↓
Analysis Orchestrator
      ↓
ML Inference
      ↓
Oil-Spill Detection
      ↓
PostGIS Polygon
      ↓
Database
      ↓
Dashboard API
      ↓
Spill visible on map
```
