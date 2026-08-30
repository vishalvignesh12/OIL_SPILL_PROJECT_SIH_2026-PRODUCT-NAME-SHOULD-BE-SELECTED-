# Frontend PRD --- Oil Spill Detection & AIS Attribution Platform

## 1. Document Information

  -----------------------------------------------------------------------
  Field                               Value
  ----------------------------------- -----------------------------------
  Product                             Oil Spill Detection & AIS
                                      Attribution Platform

  Module                              Frontend / Analyst Dashboard

  Version                             1.0

  Date                                27 August 2026

  Target MVP                          29 August 2026

  Primary Users                       Maritime/environmental analysts,
                                      investigators, administrators

  Primary Goal                        Visualize the complete spill
                                      investigation workflow from
                                      satellite detection through drift
                                      analysis and vessel attribution
  -----------------------------------------------------------------------

------------------------------------------------------------------------

# 2. Product Context

The frontend is the visual investigation layer for the SIH problem:

> Leveraging satellite imagery to determine oil spills at sea along with
> AIS data correlations to identify the vessel responsible for the
> spill.

The broader system has three linked technical stages:

1.  Detect and characterize an oil slick from SAR/EO imagery.
2.  Hindcast its movement to estimate a probable origin and forecast
    future drift using oceanographic and meteorological data.
3.  Correlate the origin/time window with AIS traffic and rank candidate
    vessels using explainable evidence.

The frontend must make this chain understandable to an analyst and to a
hackathon evaluator.

The core product flow is:

**Incident → Satellite/Slick → Drift → Origin → AIS → Attribution →
Evidence**

The frontend should therefore be designed as an investigation and
evidence-analysis tool rather than a conventional CRUD dashboard.

------------------------------------------------------------------------

# 3. Product Goals

## 3.1 Primary Goals

-   Provide a single GIS-centric investigation workspace.
-   Display detected oil slick geometry and characteristics.
-   Visualize AIS vessel tracks around the relevant time and location.
-   Visualize drift hindcast and forecast outputs.
-   Show probable origin regions with uncertainty.
-   Rank candidate vessels using attribution scores.
-   Explain why each vessel received its score.
-   Highlight suspicious AIS gaps as investigation leads.
-   Allow analysts to filter incidents and evidence by time and
    confidence.
-   Provide a clear, professional interface suitable for an SIH
    demonstration.
-   Keep the frontend independent from the implementation of the ML
    models through stable API contracts.

## 3.2 Secondary Goals

-   Provide an overview dashboard for incidents and system status.
-   Provide a vessel explorer.
-   Provide a minimal administrative interface.
-   Support CSV export of filtered investigation data.
-   Establish a reusable frontend component system for future production
    expansion.

## 3.3 Non-Goals for the Aug 29 MVP

The following are explicitly outside the critical MVP path:

-   Real-time WebSocket infrastructure.
-   Full mobile-first application.
-   Advanced notification delivery.
-   Sophisticated password-reset email delivery.
-   Full-featured CMS.
-   Advanced analytics suite.
-   Production-grade ML inference implementation.
-   Live satellite tasking.
-   Legal certification of attribution.
-   Automated legal evidence submission.

------------------------------------------------------------------------

# 4. Target Users

## 4.1 Analyst / Investigator

Primary user.

Needs to:

-   Find an incident.
-   Inspect the slick.
-   Understand when and where it was detected.
-   Inspect estimated origin.
-   Review hindcast and forecast.
-   See vessels present around the origin window.
-   Compare candidate vessels.
-   Investigate AIS anomalies.
-   Understand confidence and uncertainty.

## 4.2 Administrator

Needs to:

-   View users.
-   View vessels.
-   View datasets/incidents.
-   Manage or verify basic records.

## 4.3 Hackathon Evaluator

Not a production user, but a critical audience.

The UI must allow an evaluator to understand the entire system in
approximately 2--5 minutes without requiring technical explanation of
every backend component.

------------------------------------------------------------------------

# 5. UX Principles

## 5.1 Map First

The GIS map is the primary product surface.

The map should visually communicate:

-   Where the slick is.
-   Where it probably originated.
-   Where it may move.
-   Where vessels were.
-   Which vessel is currently selected.
-   Where AIS gaps occurred.

## 5.2 Evidence Over Decoration

Every visual element should help answer:

> Why does the system believe this vessel is relevant?

Avoid decorative dashboards that consume development time without
improving the investigation workflow.

## 5.3 Explainable Attribution

Never present:

> "Vessel X caused the spill."

Instead present:

> "Vessel X --- 87% attribution score"

with the evidence contributing to the score.

## 5.4 Uncertainty Is a Feature

The UI must distinguish:

-   Detection confidence.
-   Age-estimation confidence.
-   Origin confidence.
-   Attribution score.

A probability cone should be used where the backend provides uncertain
origin/drift output instead of displaying a false exact coordinate.

## 5.5 Failure States Are Visible

The application should explicitly communicate:

-   No AIS match.
-   AIS gap.
-   Missing drift data.
-   Low detection confidence.
-   No vessels in selected time window.
-   API failure.

------------------------------------------------------------------------

# 6. Information Architecture

``` text
Application
│
├── Authentication
│   ├── Login
│   └── Register
│
├── Overview
│   └── Dashboard
│
├── Analysis
│   ├── Incidents
│   └── Investigation
│
├── Maritime Data
│   └── Vessels
│
└── System
    └── Admin
```

Primary navigation:

``` text
Dashboard
Incidents
Investigations
Vessels
Admin
```

The Investigation page is the centerpiece.

------------------------------------------------------------------------

# 7. Page Specifications

# 7.1 Login

## Purpose

Authenticate an analyst or administrator.

## Components

-   Logo/product identity
-   Email/username input
-   Password input
-   Login button
-   Loading state
-   Validation messages
-   API error state
-   Optional "Forgot password" link

## Functional Requirements

-   Submit credentials to backend.
-   Store authentication token securely according to the selected
    frontend architecture.
-   Redirect authenticated users to Dashboard.
-   Display backend authentication errors.
-   Prevent submission with invalid required fields.

------------------------------------------------------------------------

# 7.2 Register

## Purpose

Allow creation of an analyst account.

## Components

-   Name
-   Email/username
-   Password
-   Confirm password
-   Register button
-   Validation messages

## Functional Requirements

-   Submit registration to backend.
-   Display duplicate-user and validation errors.
-   Redirect to login or dashboard according to backend contract.

------------------------------------------------------------------------

# 7.3 Dashboard

## Purpose

Provide a high-level operational overview.

## Layout

``` text
┌─────────────────────────────────────────────────────────┐
│ Page Header                                             │
├─────────────┬─────────────┬─────────────┬──────────────┤
│ Total Spills│ High Risk   │ Vessels     │ AIS Gaps    │
├─────────────┴─────────────┴─────────────┴──────────────┤
│                                                         │
│ Recent Incidents                                       │
│                                                         │
├──────────────────────────────┬──────────────────────────┤
│ Incidents Over Time           │ Top Scored Vessels      │
│                              │                          │
└──────────────────────────────┴──────────────────────────┘
```

## Components

-   `StatCard`
-   `RecentIncidents`
-   `IncidentChart`
-   `TopVesselsChart`
-   `QuickInvestigationLink`

## Required Metrics

At minimum:

-   Total incidents.
-   High-confidence/high-priority incidents.
-   Number of vessels associated with incidents.
-   Number of AIS-gap alerts.

Metrics may be driven by backend aggregates or derived from loaded data.

## Charts

At least:

1.  Incidents over time.
2.  Top-scored candidate vessels.

------------------------------------------------------------------------

# 7.4 Incidents Page

## Purpose

Provide a searchable/filterable list of detected incidents.

## Layout

``` text
┌─────────────────────────────────────────────────────────┐
│ Incidents                              [Filters]        │
├─────────────────────────────────────────────────────────┤
│ Date Range | Region | Confidence | Status              │
├─────────────────────────────────────────────────────────┤
│ Incident Card                                           │
│ Incident Card                                           │
│ Incident Card                                           │
└─────────────────────────────────────────────────────────┘
```

## Incident Card

Must show:

-   Incident ID.
-   Date/time.
-   Location/region.
-   Detection confidence.
-   Status.
-   Candidate vessel count.
-   Investigation button.

## Filters

Required:

-   Date range.
-   Confidence threshold.

Recommended:

-   Region.
-   Status.

## Interaction

Clicking an incident opens:

`/investigations/:incidentId`

------------------------------------------------------------------------

# 7.5 Investigation Page

## Priority

**P0 --- highest-priority frontend feature.**

This page must demonstrate the complete SIH workflow.

## Primary Layout

``` text
┌─────────────────────────────────────────────────────────────┐
│ Investigation Header                                        │
├──────────────────────────────────────┬───────────────────────┤
│                                      │ Slick Analysis        │
│                                      ├───────────────────────┤
│                                      │ Drift Analysis        │
│              GIS MAP                  ├───────────────────────┤
│                                      │ Attribution           │
│                                      │                       │
├──────────────────────────────────────┴───────────────────────┤
│ Timeline                                                    │
├─────────────────────────────────────────────────────────────┤
│ AIS / Evidence Alert                                       │
└─────────────────────────────────────────────────────────────┘
```

## Header

Display:

-   Incident ID.
-   Location.
-   Incident timestamp.
-   Detection confidence.
-   Investigation status.
-   Overall attribution status.

Example:

``` text
Investigation #INC-001
Kerala Coast
27 Aug 2026 · 14:20 UTC

Detection 94%
Attribution: Candidate identified
```

------------------------------------------------------------------------

# 8. Investigation Map

## Priority

**P0**

## Technology

Leaflet + React-Leaflet.

## Map Responsibilities

The map must support the following layers:

### 8.1 Slick Layer

Display:

-   Slick polygon.
-   Slick centroid.
-   Optional confidence visualization.

Data source:

`GeoJSON Polygon`

### 8.2 AIS Layer

Display:

-   Vessel markers.
-   Historical vessel tracks.
-   Direction/course where available.
-   Selected-vessel highlight.

Data source:

`GeoJSON LineString / Point`

### 8.3 Origin Layer

Display:

-   Estimated origin point.
-   Origin probability region/cone.

### 8.4 Hindcast Layer

Display:

-   Backward trajectory.
-   Origin movement path.

### 8.5 Forecast Layer

Display:

-   Predicted forward path.
-   Forecast uncertainty region where available.

### 8.6 Investigation Layer

Display:

-   Ranked candidate vessels.
-   AIS-gap markers.
-   Selected evidence points.

------------------------------------------------------------------------

# 9. Map Controls

## P1

Controls:

-   Zoom in/out.
-   Reset view.
-   Fit incident.
-   Layer visibility toggles.
-   Optional base-map switch.
-   Timeline synchronization.

## Layer Toggle

``` text
MAP LAYERS

☑ Slick
☑ AIS Tracks
☑ Vessels
☑ Origin
☑ Hindcast
☑ Forecast
☑ AIS Gaps
```

------------------------------------------------------------------------

# 10. Map Legend

## P0

The legend must explain map semantics.

Example:

``` text
Slick
Origin
Hindcast
Forecast
Vessel
Selected vessel
AIS gap
Probability region
```

The exact visual encoding should remain consistent throughout the
application.

------------------------------------------------------------------------

# 11. Slick Analysis Panel

## P0

Display:

``` text
SLICK ANALYSIS

Detection Confidence       94%

Area                       12.42 km²
Length                      8.21 km
Width                       1.42 km
Orientation                   73°

Estimated Age               ~18 hrs
Age Confidence               LOW
```

## Requirements

-   Numeric values must come from the backend.
-   Nullable age values must render safely.
-   Low-confidence age estimates must not appear as authoritative facts.
-   Include a visual confidence badge.

------------------------------------------------------------------------

# 12. Drift Analysis Panel

## P0

Display:

``` text
DRIFT ANALYSIS

Estimated Origin
27 Aug 2026 · 01:30 UTC

Origin Confidence
72%

[HINDCAST] [FORECAST]
```

## Hindcast View

Show:

-   Current slick.
-   Backward path.
-   Estimated origin.
-   Origin uncertainty.

## Forecast View

Show:

-   Current slick.
-   Forward trajectory.
-   Forecast time horizon.
-   Forecast uncertainty.

## Time Controls

Recommended options:

``` text
-12h
-8h
-4h
NOW
+6h
+12h
+24h
```

Exact available horizons must be driven by backend data.

------------------------------------------------------------------------

# 13. Attribution Panel

## P0

The attribution panel is the second-most important investigation
component after the map.

Display:

``` text
VESSEL ATTRIBUTION

3 candidates identified

#1 Vessel A                  87%
#2 Vessel B                  71%
#3 Vessel C                  43%
```

Each candidate must include:

-   Vessel name.
-   Vessel ID/MMSI where available.
-   Attribution score.
-   Spatial proximity.
-   Temporal match.
-   Trajectory parity.
-   AIS anomaly state.

------------------------------------------------------------------------

# 14. Vessel Candidate Card

## P0

Example:

``` text
┌──────────────────────────────────────────┐
│ MSC EXAMPLE                              │
│                                          │
│ Attribution Score                 87%    │
│                                          │
│ Spatial Proximity                 92%    │
│ Temporal Match                    89%    │
│ Trajectory Alignment              84%    │
│ AIS Anomaly                        YES    │
│                                          │
│ [VIEW ON MAP] [VIEW EVIDENCE]            │
└──────────────────────────────────────────┘
```

## Interactions

### View on Map

-   Center map on vessel.
-   Highlight vessel track.
-   Show related AIS data.

### View Evidence

-   Open evidence drawer/panel.
-   Show score breakdown.
-   Show relevant timestamps.
-   Show AIS-gap information if present.

------------------------------------------------------------------------

# 15. Attribution Score Breakdown

## P0

The frontend must not only show a single score.

Display:

``` text
ATTRIBUTION SCORE

Overall                  87%

Spatial proximity       92%
Temporal match          89%
Trajectory alignment    84%
AIS anomaly             76%
```

The UI should make clear that these are evidence dimensions, not
independent probabilities unless the backend explicitly defines them
that way.

------------------------------------------------------------------------

# 16. AIS Gap Alert

## P0

A dedicated alert must appear when `anomaly_flag = true`.

Example:

``` text
AIS GAP DETECTED

Vessel: MSC EXAMPLE

Last seen:       11:32 UTC
AIS resumed:     13:14 UTC

The AIS gap overlaps the
inferred spill investigation window.

Investigation Priority: HIGH
```

The frontend must use investigation-oriented language.

It must not state that an AIS gap proves illegal discharge.

------------------------------------------------------------------------

# 17. Timeline

## P0

The timeline is critical because the attribution problem is
spatio-temporal.

Example:

``` text
08:00       10:00       12:00       14:00       16:00
 |-----------|-----------|-----------|-----------|
             Vessel A
             ────────────X
                         AIS gap
                                     ● Spill
```

## Requirements

-   Display event timestamps.
-   Allow scrubbing through available time.
-   Synchronize map state with selected timestamp where data supports
    it.
-   Display vessel positions at the selected time.
-   Show spill detection time.
-   Show AIS gaps.
-   Show origin estimate.

## MVP Implementation

A simple slider is sufficient.

True real-time streaming is not required.

------------------------------------------------------------------------

# 18. Evidence Panel

## P1 --- Strong Differentiator

The evidence panel should summarize the investigation.

``` text
EVIDENCE SUMMARY

INCIDENT
INC-001

SLICK
Area: 12.4 km²
Detection confidence: 94%

ORIGIN
Estimated: 01:30 UTC
Confidence: 72%

TOP CANDIDATE
MSC EXAMPLE
Attribution: 87%

EVIDENCE
✓ Spatial proximity
✓ Temporal overlap
✓ Trajectory alignment
⚠ AIS gap detected

[EXPORT CSV]
```

Future versions can generate a complete evidence dossier.

------------------------------------------------------------------------

# 19. Vessel Explorer

## P1

Purpose:

Allow analysts to inspect vessel records independently from an incident.

## Components

-   Search box.
-   Vessel list.
-   Vessel details.
-   AIS track viewer.
-   Related incidents.
-   Attribution history.

Example:

``` text
VESSELS

Search: [MSC........]

MMSI        Name          Type       Risk
123456      Vessel A      Tanker     HIGH
456789      Vessel B      Cargo      MEDIUM
987654      Vessel C      Cargo      LOW
```

------------------------------------------------------------------------

# 20. Admin Page

## P1

Keep minimal for the MVP.

### Users

-   List users.
-   Role.
-   Basic account status.

### Vessels

-   List vessels.
-   Basic metadata.

### Incidents/Datasets

-   View available records.
-   Optional verification flag.

The MVP does not require a sophisticated administration system.

------------------------------------------------------------------------

# 21. Shared Components

Create these as reusable components.

## P0

### `StatCard`

Displays a metric and label.

### `ConfidenceBadge`

Examples:

``` text
94% HIGH
72% MEDIUM
41% LOW
```

### `StatusBadge`

Examples:

``` text
DETECTED
INVESTIGATING
VERIFIED
```

### `LoadingState`

Examples:

``` text
Loading satellite data...
Loading AIS tracks...
Calculating attribution...
```

### `ErrorState`

Must include a useful recovery action where possible.

### `EmptyState`

Examples:

``` text
No vessels found in selected time window.
```

### `DateRangePicker`

Used by incident filtering.

### `FilterBar`

Shared across list/analysis screens.

### `Modal / Drawer`

Used for:

-   Vessel details.
-   Evidence.
-   Incident details.

------------------------------------------------------------------------

# 22. Frontend Routes

Recommended routing:

``` text
/login
/register

/dashboard

/incidents
/incidents/:incidentId

/investigations
/investigations/:incidentId

/vessels
/vessels/:vesselId

/admin
```

The MVP can omit separate investigation listing if the incidents page
directly opens the investigation workspace.

------------------------------------------------------------------------

# 23. Frontend API Requirements

The frontend should consume versioned REST APIs.

Expected contracts:

``` text
GET  /api/v1/incidents
GET  /api/v1/incidents/{id}

GET  /api/v1/detections/{incident_id}

POST /api/v1/detections/analyze

POST /api/v1/drift/hindcast
POST /api/v1/drift/forecast

POST /api/v1/attribution/score

GET  /api/v1/vessels
GET  /api/v1/vessels/{id}

POST /api/v1/auth/register
POST /api/v1/auth/login
GET  /api/v1/auth/me
```

The exact backend contract must be treated as the source of truth.

The existing MVP architecture defines the AI boundary around:

-   Detection analysis.
-   Drift hindcast/forecast.
-   Attribution scoring.

The frontend should therefore never depend on the internal
implementation of those services.

------------------------------------------------------------------------

# 24. Core TypeScript Data Contracts

## Incident

``` typescript
interface Incident {
  id: string;
  timestamp: string;
  location: GeoJSON.Point;
  status: string;
}
```

## Slick Detection

``` typescript
interface SlickDetection {
  id: string;
  incident_id: string;
  polygon: GeoJSON.Polygon;
  area_km2: number;
  length_km?: number;
  width_km?: number;
  orientation_deg?: number;
  confidence: number;
  age_estimate_hours?: number | null;
}
```

## Drift Result

``` typescript
interface DriftResult {
  origin_point?: GeoJSON.Point;
  origin_probability_cone?: GeoJSON.Geometry;
  origin_time_estimate?: string;
  origin_confidence?: number;
  forward_path?: GeoJSON.Geometry;
  hindcast_path?: GeoJSON.Geometry;
}
```

## Vessel

``` typescript
interface Vessel {
  id: string;
  mmsi?: string;
  name: string;
  type?: string;
}
```

## Attribution

``` typescript
interface Attribution {
  vessel_id: string;
  score: number;
  proximity: number;
  temporality: number;
  trajectory_parity: number;
  anomaly_flag: boolean;
}
```

These interfaces are intentionally aligned with the proposed backend
AI-service contracts.

------------------------------------------------------------------------

# 25. State Management

## P0

Use a lightweight approach.

Recommended:

-   React local state for isolated component state.
-   TanStack Query for server state.
-   URL query parameters for filters where practical.
-   Context only for truly global application state such as
    authentication/theme.

Avoid introducing Redux unless the application actually requires it.

## Server State

TanStack Query should handle:

-   Incident fetching.
-   Detection fetching.
-   Vessel fetching.
-   Attribution results.
-   Drift results.
-   Loading states.
-   Error states.
-   Cache invalidation.

------------------------------------------------------------------------

# 26. Map State

Map state should include:

``` typescript
interface MapState {
  center: [number, number];
  zoom: number;
  visibleLayers: {
    slick: boolean;
    ais: boolean;
    origin: boolean;
    hindcast: boolean;
    forecast: boolean;
    gaps: boolean;
  };
  selectedVesselId?: string;
  selectedTimestamp?: string;
}
```

------------------------------------------------------------------------

# 27. Loading, Error and Empty States

Every API-driven component must have all three.

## Loading

``` text
Loading incident...
```

## Error

``` text
Unable to load AIS data.

[Retry]
```

## Empty

``` text
No AIS vessels were found
in the selected investigation window.
```

The application should never render a blank map or empty panel without
explaining why.

------------------------------------------------------------------------

# 28. Authentication and RBAC

## P0

Frontend route protection:

``` text
Unauthenticated
      ↓
     Login
      ↓
Authenticated
      ↓
Analyst / Admin
```

Role-based navigation:

### Analyst

-   Dashboard.
-   Incidents.
-   Investigations.
-   Vessels.

### Admin

All analyst capabilities plus:

-   Admin.

Important:

**Frontend route hiding is not security.**

The backend must enforce authorization. The frontend only improves UX.

------------------------------------------------------------------------

# 29. Responsive Design

## Priority

P1.

Primary target:

**Desktop analyst workstation.**

Breakpoints:

-   Mobile: view-only/basic access.
-   Tablet: reduced layout.
-   Desktop: full investigation experience.

The MVP should optimize for desktop because the system is primarily an
analyst tool.

------------------------------------------------------------------------

# 30. Accessibility

## P1

Target:

WCAG AA principles where practical.

Requirements:

-   Keyboard-accessible buttons and controls.
-   Semantic HTML.
-   Visible focus states.
-   Sufficient contrast.
-   Tooltips/labels for map controls.
-   Do not rely solely on color to communicate severity.
-   Accessible form validation messages.

------------------------------------------------------------------------

# 31. Performance Requirements

## P0

The MVP should remain responsive with:

-   At least one incident.
-   Multiple AIS tracks.
-   Slick polygons.
-   Drift paths.
-   Candidate vessels.

## Performance Rules

-   Avoid rendering unnecessary map layers.
-   Use memoization for expensive derived UI state.
-   Paginate large vessel/incident lists.
-   Fetch investigation-specific data only when needed.
-   Avoid loading all historical AIS data into the browser.
-   Let backend perform heavy geospatial filtering.

------------------------------------------------------------------------

# 32. Security Requirements

## P0

Frontend must:

-   Use HTTPS in deployment.
-   Avoid hardcoding secrets.
-   Never expose backend credentials/API keys.
-   Handle expired authentication tokens.
-   Avoid trusting role information from UI alone.
-   Avoid rendering unsanitized HTML from backend data.
-   Use environment variables for public configuration.

------------------------------------------------------------------------

# 33. Export

## P1

MVP export:

**CSV**

Potential fields:

``` text
incident_id
timestamp
vessel_id
vessel_name
mmsi
attribution_score
proximity
temporality
trajectory_parity
anomaly_flag
```

GeoJSON export is optional for the compressed MVP.

------------------------------------------------------------------------

# 34. Visual Design Direction

## Product Character

The interface should feel like:

**Maritime intelligence / geospatial investigation software**

rather than:

-   consumer SaaS;
-   generic admin template;
-   flashy AI landing page.

## Recommended Visual Language

-   Dark or neutral analyst-console aesthetic.
-   High information density without clutter.
-   Clear typography.
-   Strong hierarchy.
-   Map as the visual centerpiece.
-   Consistent severity/confidence indicators.
-   Minimal animation.

Dark/light mode is optional and should be cut before core investigation
functionality if time is limited.

------------------------------------------------------------------------

# 35. Component Priority Matrix

  Component              Priority                MVP
  -------------------- ---------- ------------------
  App Shell                    P0                Yes
  Sidebar                      P0                Yes
  Login                        P0                Yes
  Register                     P0                Yes
  Dashboard                    P1                Yes
  Incident List                P0                Yes
  Incident Filters             P0                Yes
  Investigation Map            P0                Yes
  Slick Layer                  P0                Yes
  AIS Layer                    P0                Yes
  Origin Layer                 P0                Yes
  Hindcast Layer               P0                Yes
  Forecast Layer               P0                Yes
  Map Legend                   P0                Yes
  Slick Analysis               P0                Yes
  Drift Panel                  P0                Yes
  Attribution Panel            P0                Yes
  Vessel Cards                 P0                Yes
  Score Breakdown              P0                Yes
  AIS Gap Alert                P0                Yes
  Timeline                     P0                Yes
  Evidence Panel               P1        Recommended
  Vessel Explorer              P1        Recommended
  Admin                        P1            Minimal
  CSV Export                   P1        Recommended
  Dark Mode                    P2          Cut first
  Advanced Analytics           P2                Cut
  Notifications                P2                Cut
  GeoJSON Export               P2   Cut if necessary

------------------------------------------------------------------------

# 36. Recommended Frontend Tech Stack

## Core

  Layer          Technology        Purpose
  -------------- ----------------- --------------------------------
  Language       TypeScript        Type-safe frontend development
  Framework      React             Component-based UI
  Build Tool     Vite              Fast development/build
  Styling        Tailwind CSS      Rapid UI styling
  Components     shadcn/ui         Reusable accessible components
  Routing        React Router      Application routing
  Server State   TanStack Query    API/server-state management
  Maps           Leaflet           GIS map rendering
  React Maps     React-Leaflet     Leaflet integration with React
  Charts         Recharts          Dashboard analytics
  Forms          React Hook Form   Form state/validation
  Validation     Zod               Runtime/type-safe validation
  HTTP           fetch or Axios    API communication

## Geospatial

  -----------------------------------------------------------------------
  Technology                          Purpose
  ----------------------------------- -----------------------------------
  Leaflet                             Interactive map

  React-Leaflet                       React map integration

  GeoJSON                             Data interchange

  Turf.js                             Client-side lightweight geospatial
                                      calculations when required
  -----------------------------------------------------------------------

Heavy geospatial operations should remain on the backend/PostGIS side.

## Authentication

Recommended:

``` text
JWT
+
HTTP API
+
Protected React routes
```

The frontend should consume the backend's authentication contract rather
than implementing authentication logic independently.

## Testing

Recommended:

``` text
Vitest
React Testing Library
Playwright
```

For the Aug 29 MVP, prioritize smoke/integration coverage of:

-   Login.
-   Incident loading.
-   Investigation loading.
-   Map rendering.
-   Attribution rendering.

## Code Quality

Recommended:

``` text
ESLint
Prettier
TypeScript strict mode
```

------------------------------------------------------------------------

# 37. Recommended Frontend Project Structure

``` text
frontend/
│
├── src/
│   ├── app/
│   │   ├── router.tsx
│   │   ├── providers.tsx
│   │   └── query-client.ts
│   │
│   ├── components/
│   │   ├── layout/
│   │   ├── map/
│   │   ├── incidents/
│   │   ├── investigation/
│   │   ├── attribution/
│   │   ├── drift/
│   │   ├── analytics/
│   │   └── common/
│   │
│   ├── pages/
│   │   ├── Login/
│   │   ├── Register/
│   │   ├── Dashboard/
│   │   ├── Incidents/
│   │   ├── Investigation/
│   │   ├── Vessels/
│   │   └── Admin/
│   │
│   ├── api/
│   │   ├── auth.ts
│   │   ├── incidents.ts
│   │   ├── detections.ts
│   │   ├── drift.ts
│   │   ├── attribution.ts
│   │   └── vessels.ts
│   │
│   ├── hooks/
│   │   ├── useIncidents.ts
│   │   ├── useInvestigation.ts
│   │   ├── useVessels.ts
│   │   └── useAttribution.ts
│   │
│   ├── types/
│   │   ├── incident.ts
│   │   ├── slick.ts
│   │   ├── vessel.ts
│   │   ├── drift.ts
│   │   └── attribution.ts
│   │
│   ├── lib/
│   │   ├── api-client.ts
│   │   ├── auth.ts
│   │   └── utils.ts
│   │
│   └── styles/
│       └── globals.css
│
├── public/
├── .env.example
├── package.json
├── tsconfig.json
├── vite.config.ts
└── README.md
```

------------------------------------------------------------------------

# 38. Frontend-to-Backend Dependency Contract

The frontend team requires the backend team to freeze these before
parallel development:

## P0

### Authentication

``` text
POST /auth/register
POST /auth/login
GET  /auth/me
```

### Incidents

``` text
GET /incidents
GET /incidents/:id
```

### Detection

``` text
POST /detections/analyze
```

Expected output:

``` json
{
  "slick_polygon": {},
  "area_km2": 12.4,
  "confidence": 0.94,
  "age_estimate_hours": 18
}
```

### Drift

``` text
POST /drift/hindcast
POST /drift/forecast
```

### Attribution

``` text
POST /attribution/score
```

Expected output:

``` json
{
  "ranked_vessels": [
    {
      "vessel_id": "v001",
      "score": 0.87,
      "proximity": 0.92,
      "temporality": 0.89,
      "trajectory_parity": 0.84,
      "anomaly_flag": true
    }
  ]
}
```

The actual backend schema is authoritative; these examples define the
frontend expectations and should be reconciled with the frozen OpenAPI
contract before implementation.

------------------------------------------------------------------------

# 39. MVP Development Sequence

## Phase 1 --- Foundation

**Target: Aug 27**

-   [ ] Create React + Vite + TypeScript project.
-   [ ] Configure Tailwind.
-   [ ] Configure shadcn/ui.
-   [ ] Configure routing.
-   [ ] Configure API client.
-   [ ] Configure TanStack Query.
-   [ ] Create app shell.
-   [ ] Create design tokens.
-   [ ] Agree on API types with backend.

## Phase 2 --- Map

**Target: Aug 28 morning**

-   [ ] Build Leaflet map.
-   [ ] Add base map.
-   [ ] Add slick GeoJSON.
-   [ ] Add AIS tracks.
-   [ ] Add vessel markers.
-   [ ] Add origin marker.
-   [ ] Add drift paths.
-   [ ] Add legend.
-   [ ] Add layer controls.

## Phase 3 --- Investigation UI

**Target: Aug 28 afternoon**

-   [ ] Slick Analysis panel.
-   [ ] Drift panel.
-   [ ] Attribution panel.
-   [ ] Candidate cards.
-   [ ] Score breakdown.
-   [ ] AIS-gap alert.
-   [ ] Timeline.

## Phase 4 --- API Integration

**Target: Aug 28 evening**

-   [ ] Replace mock incident data with API data.
-   [ ] Connect detection endpoint.
-   [ ] Connect drift endpoints.
-   [ ] Connect attribution endpoint.
-   [ ] Connect vessel data.
-   [ ] Handle loading/error/empty states.

## Phase 5 --- Stabilization

**Target: Aug 29 morning**

-   [ ] Fix integration bugs.
-   [ ] Test complete investigation flow.
-   [ ] Test filters.
-   [ ] Test authentication.
-   [ ] Test role restrictions.
-   [ ] Test API failures.
-   [ ] Test no-AIS case.
-   [ ] Test AIS-gap case.
-   [ ] Test low-confidence case.

## Phase 6 --- Demo Polish

**Target: Aug 29 afternoon**

-   [ ] Visual cleanup.
-   [ ] Improve map presentation.
-   [ ] Verify production deployment.
-   [ ] Add evidence summary if stable.
-   [ ] Rehearse complete demo.
-   [ ] Freeze code.

------------------------------------------------------------------------

# 40. Critical Frontend Demo Scenario

The frontend must be capable of executing this exact sequence:

``` text
1. Login
       ↓
2. Dashboard
       ↓
3. Open incident
       ↓
4. Investigation workspace
       ↓
5. Show SAR-derived slick
       ↓
6. Show slick characteristics
       ↓
7. Show estimated age + confidence
       ↓
8. Run/show hindcast
       ↓
9. Show probable origin region
       ↓
10. Show forecast
       ↓
11. Show AIS vessels around origin window
       ↓
12. Select candidate vessel
       ↓
13. Show attribution score
       ↓
14. Expand score breakdown
       ↓
15. Show AIS gap/anomaly if present
       ↓
16. Show evidence summary
       ↓
17. Explain uncertainty
```

This should be rehearsed against the deployed application before
submission.

------------------------------------------------------------------------

# 41. Definition of Done

The frontend is MVP-complete when:

-   [ ] Production URL loads successfully.
-   [ ] User can log in.
-   [ ] Dashboard renders.
-   [ ] Incident list loads from API.
-   [ ] Date/confidence filtering works.
-   [ ] Investigation page loads from an actual incident.
-   [ ] Map renders correct incident geography.
-   [ ] Slick polygon renders from API data.
-   [ ] AIS tracks render from API data.
-   [ ] Vessel markers render.
-   [ ] Origin/hindcast/forecast data renders.
-   [ ] Slick analysis values render.
-   [ ] Attribution candidates render.
-   [ ] Attribution score breakdown renders.
-   [ ] AIS-gap alert renders when applicable.
-   [ ] Timeline renders relevant events.
-   [ ] Loading/error/empty states exist.
-   [ ] Analyst/admin navigation is role-aware.
-   [ ] Backend authorization remains responsible for actual security.
-   [ ] No critical console errors exist during the demo.
-   [ ] Complete investigation can be demonstrated without manually
    editing the database.

------------------------------------------------------------------------

# 42. Scope-Cut Rules

If the team falls behind, cut in this order:

1.  Dark/light mode.
2.  Advanced analytics.
3.  Notifications.
4.  GeoJSON export.
5.  Vessel Explorer enhancements.
6.  Admin richness.
7.  Evidence dossier export.

Do **not** cut:

1.  Investigation map.
2.  Slick polygon.
3.  AIS tracks.
4.  Drift visualization.
5.  Attribution ranking.
6.  Score breakdown.
7.  AIS-gap handling.
8.  Timeline.
9.  API-driven data flow.
10. Authentication.
11. Core filtering.

The project should have a strong investigation workflow before adding
peripheral functionality.

------------------------------------------------------------------------

# 43. Final Frontend Product Definition

The frontend should ultimately feel like a **maritime intelligence
investigation console**.

The central screen should allow an analyst to answer five questions
without leaving the page:

### 1. What happened?

**Detected oil slick**

### 2. Where is it?

**Slick geometry on the map**

### 3. Where did it probably come from?

**Hindcast + origin probability region**

### 4. Which vessels were relevant?

**AIS tracks around the origin/time window**

### 5. Why is a vessel suspicious?

**Explainable attribution score + AIS anomaly evidence**

That is the frontend's core value proposition.

------------------------------------------------------------------------

# 44. Recommended Stack --- Final Lock

``` text
Frontend
│
├── React
├── TypeScript
├── Vite
│
├── UI
│   ├── Tailwind CSS
│   └── shadcn/ui
│
├── Routing
│   └── React Router
│
├── Server State
│   └── TanStack Query
│
├── Forms
│   ├── React Hook Form
│   └── Zod
│
├── GIS
│   ├── Leaflet
│   ├── React-Leaflet
│   ├── GeoJSON
│   └── Turf.js (lightweight calculations only)
│
├── Charts
│   └── Recharts
│
├── Testing
│   ├── Vitest
│   ├── React Testing Library
│   └── Playwright
│
└── Quality
    ├── ESLint
    ├── Prettier
    └── TypeScript strict mode
```

## Backend dependency

``` text
Frontend
    ↓ REST / JSON
FastAPI
    ↓
PostgreSQL + PostGIS
    ↓
Detection / Drift / AIS / Attribution services
```

This stack is deliberately aligned with the existing MVP execution plan:
React + Vite, Tailwind/shadcn, Leaflet, Recharts, and a
FastAPI/PostgreSQL/PostGIS backend. The existing plan also explicitly
recommends Leaflet to avoid map API-key friction and defines the AI
endpoints as stable integration boundaries.
