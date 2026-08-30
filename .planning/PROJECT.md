# National Marine Oil Spill Monitoring System

## What This Is

A mission-critical maritime surveillance and forensic intelligence web application designed for national environmental oversight, oil spill detection, and vessel attribution. The platform transforms satellite SAR observations and AIS tracking data into actionable geospatial investigations and evidentiary dossiers for maritime authorities.

## Core Value

Enable maritime surveillance officers to rapidly detect satellite-observed oil slicks, pinpoint candidate polluting vessels via spatial-temporal AIS attribution with confidence scoring, and compile legally defensible incident dossiers.

## Requirements

### Validated

- ✓ [High-fidelity UI prototype across 9 core operational screens] — existing (static HTML mockups)
- ✓ [Standardized maritime oversight design system & design tokens] — existing (`maritime_oversight_response/DESIGN.md`)
- ✓ [Visual layout and styling for incident INC-2026-001 (Bay of Bengal)] — existing

### Active

- [ ] **Modern React Architecture**: Convert static HTML mockups into a clean, modular React application (SPA) with shared layouts, design tokens, and components.
- [ ] **Interactive GIS Forensics Workspace**: Real interactive mapping engine (Leaflet/Mapbox) rendering satellite detection overlays, oil slick polygons, coordinate grids, and interactive layer toggles.
- [ ] **AIS Vessel Attribution & Trajectory Engine**: Visual spatial-temporal vessel tracks, nearest-approach calculations, drift modeling, and probabilistic suspect ranking with confidence breakdown.
- [ ] **Live Operations Dashboard & Detection Registry**: Dynamic operational metrics, filterable oil spill registry, severity categorization, and status workflows (New, Investigating, Attributed, Closed).
- [ ] **Forensic Profiling & Legal Evidence Dossier**: Deep vessel dossier inspection (MMSI, IMO, flag history, voyage logs), verifiable audit trails, and official PDF/report export capabilities.
- [ ] **Mock & Extensible API Integration Layer**: Safe, typed service layer connecting components to mock backend data, ready for seamless switchover to live backend endpoints.

### Out of Scope

- Direct satellite downlink processing in frontend — processed downstream by backend services
- Full real-time radar hardware interfacing — ingested via standard AIS/SAR APIs
- Mobile native application — web-first responsive design targeting desktop operations centers

## Context

- Existing prototype consists of 9 isolated HTML files utilizing Tailwind CDN and Google Fonts.
- Design system follows **Corporate Modernism / Information Density** with deep navy (`#002147`), muted teal (`#096969`), and semantic alert colors.
- The project is equipped with domain skills for React frontend engineering, GIS mapping, technical data visualization, API integration, and security.

## Constraints

- **Tech Stack**: React + Vanilla CSS / Tailwind (consistent design system), HTML5, JavaScript
- **Performance**: Instantaneous client-side filtering and smooth pan/zoom on GIS map layers
- **Security**: Strict isolation of mock credentials, sanitized inputs, and defensible audit log trails

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| React SPA Architecture | Replaces duplicated HTML files and shared config drift with reusable component tree | — Pending |
| Leaflet.js for GIS Mapping | Lightweight, highly extensible, excellent polygon & GeoJSON support for maritime overlays | — Pending |
| Vertical MVP Phased Delivery | Fast operational capability at each increment (Setup → Core Layout → GIS → Attribution → Dossier) | — Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-08-27 after initialization*
