---
last_mapped: 2026-08-27
---

# ARCHITECTURE.md — System Architecture

## Pattern

**Multi-page static HTML application** — a collection of individual standalone HTML pages representing different screens of the National Marine Oil Spill Monitoring System. There is no router, no shared JS module system, and no component framework.

Each page is a **self-contained document** that includes:
1. Tailwind CSS via CDN + inline `tailwind.config` (duplicated in every page)
2. Google Fonts links
3. Semantic HTML body
4. Minimal inline `<script>` for trivial DOM interactions (e.g., setting current date)

## Application Layers

```
┌─────────────────────────────────────────────────────────┐
│                  Browser (Client only)                   │
│                                                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ...        │
│  │ Login    │  │Dashboard │  │ GIS Map  │              │
│  │ page     │  │  page    │  │  page    │              │
│  └──────────┘  └──────────┘  └──────────┘              │
│                                                         │
│  Each page = standalone .html (HTML + Tailwind + JS)    │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │ Shared Design System (maritime_oversight_response│   │
│  │ DESIGN.md) — applied via per-page tailwind.config│   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

## Page Inventory & Purposes

| Directory | Title | Role |
|---|---|---|
| `secure_login_national_marine_oil_spill_monitoring_system/` | Login – National Marine Oil Spill Monitoring | Authentication entry point |
| `command_dashboard_national_marine_oil_spill_monitoring_system/` | Maritime Intel - Command Dashboard | Top-level operations overview (KPIs, active incidents, system health) |
| `oil_spill_detection_registry_maritime_intelligence_console/` | Oil Spill Detection – Maritime Intel | Tabular registry of all detection events with filtering |
| `gis_investigation_workspace_inc_2026_001_forensics/` | Main Investigation GIS Workspace | Map-first investigation UI for INC-2026-001 (Bay of Bengal) |
| `vessel_attribution_ranking_incident_inc_2026_001/` | Vessel Attribution – Maritime Intel | Ranked candidate vessel list with confidence scores |
| `vessel_forensic_profile_msc_ocean_star/` | Vessel Forensic Profile (MSC Ocean Star) | Deep-dive vessel investigation page |
| `evidence_dossier_incident_inc_2026_001_official_report/` | Evidence Dossier – INC-2026-001 | Legal/official compiled evidence report |
| `security_alerts_maritime_surveillance_portal/` | Security Alerts – Maritime Surveillance | Alert management and acknowledgement |
| `system_reports_configuration_console/` | System Reports Configuration Console | Admin/reporting configuration |
| `maritime_oversight_response/` | (Design system spec only — `DESIGN.md`) | Design tokens, typography, color specification |
| `a_sophisticated_professional_abstract_visualization_of_maritime_surveillance/` | (Visual asset only — `screen.png`) | Decorative/splash image |

## Navigation Model (as implemented in pages)

A **fixed sidebar nav** is used on interior pages (`gis_investigation_workspace`, etc.):
- Width: `w-[260px]`, fixed left, full height
- Nav items: Dashboard, Detection, Investigation Map, Vessel Attribution, Vessel Details, Evidence Dossier, Alerts, Reports, Settings
- Active state: `text-primary font-bold border-r-4 border-primary bg-surface-container-high`
- Inactive state: `text-on-surface-variant hover:bg-surface-container-highest`

The **Login page** has no sidebar — it uses a split-panel layout (hero left, form right).

## Layout Patterns

| Pattern | Usage |
|---|---|
| Split panel (50/50) | Login page (`lg:block w-1/2`) |
| Sidebar + main canvas | All interior pages (fixed `ml-[260px]`) |
| Top app bar | Interior pages — `h-16`, `border-b border-outline-variant`, incident badge, search, icon buttons |
| Content grid inside main canvas | Dashboard uses metric cards, tables; GIS uses resizable left panel + map canvas |

## Data Model (As Displayed in Static HTML)

Key data entities visible in the UI:
- **Incident**: `INC-2026-001`, location `Bay of Bengal`, confidence `94%`
- **Vessel**: `MSC Ocean Star`, with MMSI, IMO, flag, AIS trajectory
- **Oil Slick**: coordinates, area (km²), detection confidence, SAR imagery timestamp
- **Alert**: severity level (Critical/High/Medium), status (active/acknowledged/cleared)
- **Detection Event**: timestamp, satellite pass, detection confidence, area
