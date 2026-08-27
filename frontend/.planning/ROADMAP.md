# Roadmap: National Marine Oil Spill Monitoring System

## Overview

Transform the static HTML prototypes into a production-grade React application with interactive geospatial forensics, algorithmic vessel attribution, and official evidence dossier generation across 5 progressive milestone phases.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

- [ ] **Phase 1: React Application Foundation & Design System Engine** - Initialize Vite React framework, shared theme tokens, component library, and mock API service layer.
- [ ] **Phase 2: Command Dashboard & Detection Registry** - Build core application shell, navigation routing, operational KPIs, alert feeds, and searchable oil spill detection registry.
- [ ] **Phase 3: Interactive GIS Investigation Workspace** - Build Leaflet-powered maritime forensics map with slick polygons, layer controls, and temporal scrubber playback.
- [ ] **Phase 4: AIS Vessel Attribution & Forensic Profiling** - Implement candidate vessel ranking, confidence factor breakdowns, trajectory analysis, and deep vessel profile views.
- [ ] **Phase 5: Legal Evidence Dossier, Alerts Portal & Export Engine** - Deliver official incident dossier (INC-2026-001), alert acknowledgement workflow, audit logging, and print/PDF export.

---

## Phase Details

### Phase 1: React Application Foundation & Design System Engine
**Goal**: Establish the modern React SPA architecture, port the Material Design 3 maritime design system (`DESIGN.md`), and scaffold reusable UI components with a typed mock API service layer.
**Mode:** mvp
**Depends on**: Nothing (first phase)
**Requirements**: ARCH-01, ARCH-02, ARCH-03, ARCH-04
**Success Criteria** (what must be TRUE):
  1. Vite + React application boots cleanly with hot module reloading and no CDN dependencies.
  2. Complete maritime color palette, typography scale, and layout tokens are implemented in reusable CSS/Tailwind configuration.
  3. Reusable components (Header, SideNavBar, StatusChip, MetricCard, DataTable, Modal, Button) render with authentic visual styling matching the prototypes.
  4. Mock API service provides structured, type-safe data for incidents, detections, vessels, and alerts.
**Plans**: 2 plans

Plans:
- [ ] 01-01: React project initialization, build configuration, and design system token setup.
- [ ] 01-02: Core reusable UI component library and mock data service layer.

---

### Phase 2: Command Dashboard & Detection Registry
**Goal**: Deliver the primary operational command center and oil spill detection catalog with active filtering, live status summaries, and incident navigation.
**Mode:** mvp
**Depends on**: Phase 1
**Requirements**: DASH-01, DASH-02, DASH-03, REG-01, REG-02, REG-03
**Success Criteria** (what must be TRUE):
  1. User can view the Command Dashboard with live KPI counters, regional overview, and priority alert ribbons.
  2. User can browse the Oil Spill Detection Registry table with pagination, column sorting, and multi-criteria filters (region, severity, status).
  3. User can click any detection or incident to navigate seamlessly into the investigation workspace.
**Plans**: 2 plans

Plans:
- [ ] 02-01: Application shell routing, Command Dashboard screen, and KPI metrics.
- [ ] 02-02: Oil Spill Detection Registry table, search/filter controls, and incident routing.

---

### Phase 3: Interactive GIS Investigation Workspace
**Goal**: Deliver the interactive geospatial forensics map for incident INC-2026-001 (Bay of Bengal) with oil slick geometry, bathymetric layers, coordinate inspection, and temporal timeline playback.
**Mode:** mvp
**Depends on**: Phase 2
**Requirements**: GIS-01, GIS-02, GIS-03, GIS-04
**Success Criteria** (what must be TRUE):
  1. Interactive Leaflet GIS map renders centered on the Bay of Bengal with responsive pan, zoom, and coordinate crosshairs.
  2. Oil slick polygons and AIS vessel track vectors display with accurate color-coded confidence levels and hover tooltips.
  3. User can toggle layers (SAR Slicks, Vessel Tracks, EEZ Boundaries, Nautical Grid) on and off dynamically.
  4. User can drag the temporal playback slider to see vessel positions animate across the timeline.
**Plans**: 2 plans

Plans:
- [ ] 03-01: Leaflet GIS map integration, custom dark maritime tiles, and layer toggle control panel.
- [ ] 03-02: Oil slick polygon rendering, vessel marker overlays, telemetry sidebar, and temporal playback scrubber.

---

### Phase 4: AIS Vessel Attribution & Forensic Profiling
**Goal**: Implement the probabilistic vessel attribution engine, factor-by-factor confidence scoring breakdown, and deep vessel forensic profile screen.
**Mode:** mvp
**Depends on**: Phase 3
**Requirements**: ATTR-01, ATTR-02, ATTR-03
**Success Criteria** (what must be TRUE):
  1. User can view ranked candidate vessels for INC-2026-001 with primary suspect (MSC Ocean Star - 94% confidence) prominently displayed.
  2. Factor breakdown visualizer details proximity distance, trajectory intersection, speed anomaly, and vessel type risk weights.
  3. User can navigate to the Vessel Forensic Profile view to inspect IMO/MMSI records, flag history, voyage track history, and photographic evidence.
**Plans**: 2 plans

Plans:
- [ ] 04-01: Vessel Attribution Ranking screen with confidence factor scoring visualizer.
- [ ] 04-02: Vessel Forensic Profile deep-dive screen with voyage history and AIS ping logs.

---

### Phase 5: Legal Evidence Dossier, Alerts Portal & Export Engine
**Goal**: Build the official Evidence Dossier report view, Security Alerts management center, System Configuration console, and printable report export engine.
**Mode:** mvp
**Depends on**: Phase 4
**Requirements**: EVID-01, EVID-02, EVID-03
**Success Criteria** (what must be TRUE):
  1. Official Evidence Dossier renders all incident telemetry, SAR satellite imagery snapshots, AIS attribution proofs, and chain-of-custody signatures.
  2. User can generate a clean, print-ready or exportable PDF-style government evidentiary report.
  3. Security Alerts portal and System Configuration console provide complete operational oversight with interactive alert acknowledgement.
**Plans**: 2 plans

Plans:
- [ ] 05-01: Evidence Dossier incident report screen with export/print layout optimization.
- [ ] 05-02: Security Alerts management portal, system settings console, and end-to-end integration polish.

---

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3 → 4 → 5

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. React Application Foundation & Design System Engine | 2/2 | Complete | 2026-08-27 |
| 2. Command Dashboard & Detection Registry | 2/2 | Complete | 2026-08-27 |
| 3. Interactive GIS Investigation Workspace | 1/1 | Complete | 2026-08-27 |
| 4. AIS Vessel Attribution & Forensic Profiling | 2/2 | Complete | 2026-08-27 |
| 5. Legal Evidence Dossier, Alerts Portal & Export Engine | 2/2 | Complete | 2026-08-27 |
