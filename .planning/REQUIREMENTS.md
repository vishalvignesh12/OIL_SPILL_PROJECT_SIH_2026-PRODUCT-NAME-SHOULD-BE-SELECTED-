# Requirements: National Marine Oil Spill Monitoring System

**Defined:** 2026-08-27
**Core Value:** Enable maritime surveillance officers to rapidly detect satellite-observed oil slicks, pinpoint candidate polluting vessels via spatial-temporal AIS attribution with confidence scoring, and compile legally defensible incident dossiers.

## v1 Requirements

### Foundation & Architecture (ARCH)

- [ ] **ARCH-01**: User can run and navigate a unified React SPA without full page reloads.
- [ ] **ARCH-02**: Application applies unified design system tokens (Deep Navy, Muted Teal, Typography scales) consistently across all screens.
- [ ] **ARCH-03**: User can navigate between all views (Dashboard, Detection Registry, GIS Workspace, Attribution, Vessel Profile, Dossier, Alerts, Settings) via persistent sidebar and breadcrumb routing.
- [ ] **ARCH-04**: System includes a clean, modular API service layer with structured mock data models for incidents, vessels, slicks, and alerts.

### Command Dashboard & Operations (DASH)

- [ ] **DASH-01**: User can view live operational KPI metric cards (Active Incidents, Monitored Vessels, Verified Slicks, Attribution Rate) with trend indicators.
- [ ] **DASH-02**: User can view recent high-priority alert cards with severity tags and direct jump to incident forensics.
- [ ] **DASH-03**: User can inspect regional surveillance status and quick-access active hot zones (e.g. Bay of Bengal).

### Detection Registry (REG)

- [ ] **REG-01**: User can view a comprehensive, tabular registry of all detected oil slicks with timestamps, coordinates, sensor type, and confidence levels.
- [ ] **REG-02**: User can filter and search detections by date range, geographical region, severity, and investigation status.
- [ ] **REG-03**: User can initiate a new forensic investigation directly from any detection row.

### Geospatial Investigation Workspace (GIS)

- [ ] **GIS-01**: User can interact with a responsive GIS map displaying oil slick polygons, coordinate grids, and bathymetric/satellite basemaps.
- [ ] **GIS-02**: User can toggle map layers (SAR slick outlines, AIS vessel trajectories, maritime zones/EEZ, satellite imagery).
- [ ] **GIS-03**: User can select an oil slick or vessel marker to inspect telemetry, area calculations, and timestamped proximity data in the inspection sidebar.
- [ ] **GIS-04**: User can scrub an interactive temporal playback slider to observe historical vessel movements relative to slick formation time.

### Vessel Attribution & Forensic Profiling (ATTR)

- [ ] **ATTR-01**: User can view ranked candidate polluting vessels with composite confidence percentages, proximity distances, and temporal alignment scores.
- [ ] **ATTR-02**: User can inspect factor-by-factor attribution breakdowns (temporal intersection, trajectory overlap, course change anomalies, vessel type risk).
- [ ] **ATTR-03**: User can view deep forensic profile details for suspect vessels (MMSI, IMO, flag history, voyage route, AIS ping timeline).

### Evidence Dossier & Reporting (EVID)

- [ ] **EVID-01**: User can view a structured, official incident report dossier (INC-2026-001) aggregating satellite evidence, vessel ranking, chain of custody, and forensic findings.
- [ ] **EVID-02**: User can export/print the evidence dossier in an official governmental report layout.
- [ ] **EVID-03**: User can acknowledge, classify, and update incident investigation status with immutable audit logging.

## v2 Requirements

### Real-Time & Integrations

- **REAL-01**: Live WebSocket stream integration for real-time AIS feed ingestion.
- **REAL-02**: Direct Copernicus / Sentinel-1 SAR imagery catalog query integration.
- **REAL-03**: Automated drift modeling simulation engine incorporating wind and ocean current vector datasets.
- **REAL-04**: Multi-user collaboration with incident tagging and assignment workflows.

## Out of Scope

| Feature | Reason |
|---------|--------|
| Native Mobile App | Specialized surveillance displays require desktop multi-monitor operational environments |
| Raw SAR ML Training in Browser | Model training executes server-side; frontend displays inferenced polygons & confidence scores |
| Third-party commercial AIS subscriptions | Frontend uses decoupled API abstraction layer agnostic to data provider |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| ARCH-01 | Phase 1 | Complete |
| ARCH-02 | Phase 1 | Complete |
| ARCH-03 | Phase 1 | Complete |
| ARCH-04 | Phase 1 | Complete |
| DASH-01 | Phase 2 | Complete |
| DASH-02 | Phase 2 | Complete |
| DASH-03 | Phase 2 | Complete |
| REG-01 | Phase 2 | Complete |
| REG-02 | Phase 2 | Complete |
| REG-03 | Phase 2 | Complete |
| GIS-01 | Phase 3 | Complete |
| GIS-02 | Phase 3 | Complete |
| GIS-03 | Phase 3 | Complete |
| GIS-04 | Phase 3 | Complete |
| ATTR-01 | Phase 4 | Complete |
| ATTR-02 | Phase 4 | Complete |
| ATTR-03 | Phase 4 | Complete |
| EVID-01 | Phase 5 | Complete |
| EVID-02 | Phase 5 | Complete |
| EVID-03 | Phase 5 | Complete |

**Coverage:**
- v1 requirements: 19 total
- Mapped to phases: 19
- Unmapped: 0 ✓

---
*Requirements defined: 2026-08-27*
*Last updated: 2026-08-27 after initial definition*
