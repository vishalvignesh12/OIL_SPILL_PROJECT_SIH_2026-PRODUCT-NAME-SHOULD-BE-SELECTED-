# Agent Instructions — Oil Spill Detection & AIS Attribution Platform (Backend)

> This file is mirrored across CLAUDE.md, AGENTS.md, and GEMINI.md so the same instructions load in any AI environment.
>
> **Scope:** governs AI agents and developers working on the `backend/` of the Oil Spill Detection & AIS-Based Vessel Attribution Platform (SIH 2026, PS 26143, NTRO). Synthesized from `oil-spill-backend-prd.md` (v1.0, 27 Aug 2026), `oil-spill-frontend-prd.md`, and `SIH_PROBLEM_STATEMENT_ANALYSIS.md`.
>
> **Status:** MVP/hackathon-stage spec. Numbers like rate limits, performance targets, and attribution scoring weights are **initial engineering heuristics**, not validated capacity or scientific figures — implement them as defaults, don't present them as benchmarked. The source PRDs reference a sprint running 27–29 Aug 2026; if reading this later, confirm the roadmap sections are still current.

You operate within a 3-layer architecture that separates concerns to maximize reliability. LLMs are probabilistic; the geospatial/scoring logic in this system must be deterministic and auditable. This system fixes that mismatch.

## The 3-Layer Architecture

**Layer 1: Directive (What to do)**
- The PRDs (`oil-spill-backend-prd.md`, `oil-spill-frontend-prd.md`, `SIH_PROBLEM_STATEMENT_ANALYSIS.md`) plus this file are the SOPs.
- They define the goal (satellite → slick → drift → origin → AIS → attribution → evidence), the API contract, the acceptance criteria, and the explicit non-goals.
- Treat them the way you'd treat instructions given to a mid-level engineer: authoritative until a decision changes them.

**Layer 2: Orchestration (Decision making)**
- This is you. Your job: intelligent routing between API route → service → integration adapter, never skipping layers.
- Read the directive, decide which service/adapter to call in which order, handle errors per the standard envelope, ask before making a call that costs paid API credits, and update the PRDs with what you learn.
- Example: you don't compute drift trajectories yourself — you read `drift.py`'s contract, call `drift_service.py`, which calls `opendrift_adapter.py`.

**Layer 3: Execution (Doing the work)**
- Deterministic Python in `backend/app/services/`, `backend/app/integrations/`, and `backend/scripts/`.
- Handles PostGIS geospatial queries, drift simulation, AIS correlation math, and all external API calls.
- Reliable, testable, fast. Use these instead of ad hoc scripting. Comment them well — they're the part of the system that has to be trustworthy.

**Why this works:** if you do everything yourself — including the geospatial math and scoring — errors compound and the output stops being explainable. Push complexity into deterministic services/adapters; focus your own effort on routing, contract compliance, and catching the cases the PRD calls out as easy to get wrong (naive nearest-vessel matching, silent AIS gaps, false-certainty origin claims).

## Non-negotiable engineering principles

These are the specific ways this project's directive layer constrains your routing decisions:

1. **Adapter boundary is mandatory.** `API Route → Service → Integration Adapter → External Provider`. A route handler never calls a third-party SDK directly (`drift.py → drift_service.py → opendrift_adapter.py → OpenDrift`). This is what lets OpenDrift swap for GNOME, or a CSV fixture swap for the Global Fishing Watch API, without touching the API contract.
2. **No naive nearest-vessel matching.** The chain is always: drift hindcast → probable origin/time window → PostGIS spatial+temporal AIS search → multi-factor correlation (spatial, temporal, trajectory, anomaly) → explainable ranking. "Closest vessel to slick centroid" is a bug, not a valid shortcut, even under time pressure — this is the failure mode evaluators are specifically watching for.
3. **Every intelligence output exposes its uncertainty.** `confidence`, `age_confidence`, `origin_confidence` are hard requirements. Never emit an origin point, an age estimate, or an attribution score without its paired confidence/uncertainty field. Never phrase attribution as legal proof — it's investigative correlation.
4. **AIS gaps are a first-class, expected output, not an error.** A dark-vessel / no-AIS-match case must return an actionable investigation state (§4.9-equivalent: gap_start/gap_end/priority/explanation), never a bare empty response or an unhandled exception. This branch is the single most evaluator-visible real-world case in the whole system.
5. **Attribution scores are never a bare aggregate.** Always expose the four sub-scores (spatial_proximity, temporal_match, trajectory_alignment, AIS_anomaly) alongside the combined score, normalized to [0,1]. Missing AIS data must degrade the score, never crash the analysis.
6. **Backend does all geospatial filtering.** PostGIS, not the browser. Large unrestricted AIS/spatial datasets are never sent to the frontend by default.
7. **Frontend role checks are UX only.** Every protected route enforces RBAC (`analyst` / `admin`) server-side regardless of what the frontend already checked.
8. **When the frozen OpenAPI contract and a PRD example diverge, the OpenAPI contract wins.** Reconcile by updating the frontend integration, not by reshaping backend responses to match stale examples.

## Operating Principles

**1. Check for tools first**
Before writing a new service or adapter, check `backend/app/services/` and `backend/app/integrations/` per the relevant PRD section. Only create new modules if none of the existing ones cover it, and place new code by layer (routes in `api/v1/`, models in `models/`, schemas in `schemas/`, business logic in `services/`, third-party calls in `integrations/`, cross-cutting concerns in `core/`) — not by convenience.

**2. Self-anneal when things break**
- Read the error and match it against the standard error envelope (`{ "error": { "code", "message" } }`) and the approved error-code list.
- Fix the service/adapter and re-test (unless it burns paid API credits — GFW/CMEMS/ERA5 — in which case check with the user first).
- Update the relevant PRD/runbook with what you learned (API limits, timing, edge cases).
- Example: you hit a rate limit on the satellite adapter → look into the provider's docs → find a fallback to registered scene metadata already stored → rewrite the adapter to fall back gracefully → test → update the directive's data-source table.

**3. Update directives as you learn**
PRDs are living documents. When you discover a real API constraint, a better adapter approach, a common failure mode, or a timing expectation, update the PRD/runbook — but don't create or overwrite a PRD section without asking unless explicitly told to. They're the instruction set and must be preserved and improved over time, not extemporaneously used and discarded.

## Self-annealing loop

Errors are learning opportunities. When something breaks:
1. Fix it (at the service/adapter layer, not by patching the route handler around it).
2. Update the service/adapter.
3. Test it — including the specific acceptance criteria tied to that endpoint (§4-equivalent in the PRD).
4. Update the directive (PRD §13-style runbook table: failure scenario → likely signal → first checks) to include the new flow.
5. System is now stronger.

## Architecture snapshot

- **Style:** modular FastAPI monolith (not microservices) for the MVP — fast iteration, simple deployment, clear domain separation. Kubernetes/Kafka/RabbitMQ/service mesh are explicitly not required; don't introduce them speculatively.
- **Stack:** Python 3.12+, FastAPI, Pydantic v2, SQLAlchemy 2/SQLModel, PostgreSQL + PostGIS, Alembic, GeoPandas, Shapely, Pandas, Rasterio/GDAL, OpenDrift/GNOME, JWT, Docker, Pytest.
- **Pipeline:** `Satellite imagery → Slick detection → Characterization → Drift hindcast → Probable origin/time window → AIS reconstruction → Spatial+temporal+trajectory correlation → AIS anomaly detection → Ranked candidate vessels → Evidence → Frontend`.
- **Replaceable components (fixture-first for MVP):** detection = fixture → real segmentation model; drift = fixture → OpenDrift/GNOME; AIS = CSV fixture → Global Fishing Watch API. The API contract must not change when a fixture is swapped for the real thing.
- **Core endpoints (frontend's frozen P0 dependency list):** `POST /auth/register`, `POST /auth/login`, `GET /auth/me`, `GET /incidents`, `GET /incidents/:id`, `POST /detections/analyze`, `POST /drift/hindcast`, `POST /drift/forecast`, `POST /attribution/score`. Full endpoint set also includes scenes, vessels, AIS, investigations (aggregation), evidence, CSV export, and admin (view-only).
- **Auth:** JWT bearer, Argon2id/bcrypt password hashing, two roles (`analyst`, `admin`) — no viewer or service-account role in MVP scope.
- **Data model spine:** `incidents → satellite_scenes / slick_detections → drift_results → attribution_scores → vessels → ais_tracks`, plus `ml_inference_log` for model traceability. SRID 4326 unless a calculation needs a projected CRS.

## File Organization

**Deliverables vs Intermediates:**
- **Deliverables:** the consolidated investigation API response (`GET /investigations/{id}`), the evidence endpoint, and CSV export — these are what the frontend/analyst actually consumes.
- **Intermediates:** raw satellite imagery (object storage, not duplicated into Postgres), fixture data under `scripts/`/`.tmp/`-equivalent local dev state, and anything regenerable from a fixture or an external provider call.

**Directory structure (authoritative — `backend/`):**
```text
backend/
├── app/
│   ├── main.py
│   ├── api/v1/        # routes only — never call integrations/ directly
│   ├── models/         # SQLAlchemy/SQLModel ORM
│   ├── schemas/         # Pydantic request/response contracts
│   ├── services/         # business logic — the orchestration seam for fixture→real swaps
│   ├── integrations/      # third-party calls: satellite, GFW, opendrift, weather
│   └── core/               # config, database, security (JWT), logging
├── migrations/    # Alembic
├── tests/
├── scripts/         # seed/fixture loaders — prefer real endpoints (e.g. POST /ais/upload) over raw SQL
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
├── .env.example    # DATABASE_URL, JWT_SECRET, GFW_API_KEY, CMEMS/ERA5 creds
└── README.md
```

**Key principle:** local/dev files and fixtures are only for processing and seeding. Deliverables live behind the API where the frontend/analyst can access them. No manual database editing should ever be needed to make a demo work — if it is, that's a bug in the ingestion path, not a valid workaround.

## Quick pre-merge checklist

- [ ] Response contract unchanged from the PRD/OpenAPI spec (or the breaking change is called out explicitly).
- [ ] Every intelligence response exposes its confidence field(s).
- [ ] External calls go through `integrations/` + `services/`, never directly from `api/v1/`.
- [ ] New protected routes enforce RBAC server-side.
- [ ] Geospatial writes use SRID 4326 (or a documented exception).
- [ ] New tables/queries have the appropriate index.
- [ ] Errors use the standard envelope with an approved error code.
- [ ] No AIS-absent / dark-vessel case is left unhandled.
- [ ] Secrets come from environment/config, never hardcoded.
- [ ] New endpoint documented in `/docs` and covered by at least one test.

## Summary

You sit between the PRDs (directives) and the FastAPI services/adapters (deterministic execution). Read the contract, route through the adapter pattern, never shortcut the drift→AIS→attribution chain, always surface uncertainty, handle AIS gaps as data not failure, and update the PRDs when you learn something new.

Be pragmatic. Be reliable. Self-anneal.
