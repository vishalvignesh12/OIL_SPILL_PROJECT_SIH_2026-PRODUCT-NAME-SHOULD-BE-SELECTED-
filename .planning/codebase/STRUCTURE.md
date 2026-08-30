---
last_mapped: 2026-08-27
---

# STRUCTURE.md — Directory Layout

## Root Directory

```
stitch_national_marine_oil_spill_system/
│
├── .agent/                          # GSD tooling (not source code)
│   ├── get-shit-done/               # GSD workflow engine
│   ├── skills/                      # Project-specific GSD skills
│   ├── agents/                      # GSD agent definitions
│   ├── gsd-file-manifest.json       # File tracking
│   └── gsd-install-state.json       # Migration state
│
├── .agents/                         # Additional agents / skills
│   └── skills/                      # Domain skills (api-integration, gis-mapping, etc.)
│
├── .planning/                       # GSD project planning (just initialized)
│   └── codebase/                    # Codebase map (this directory)
│
├── maritime_oversight_response/     # Design system specification
│   └── DESIGN.md                    # Master color tokens, typography, spacing, components
│
│── [PAGE DIRECTORIES] (9 screen directories):
│
├── secure_login_.../
│   ├── code.html                    # Login page (204 lines)
│   └── screen.png                   # Screenshot
│
├── command_dashboard_.../
│   ├── code.html                    # Dashboard page (496 lines)
│   └── screen.png
│
├── oil_spill_detection_registry_.../
│   ├── code.html                    # Detection registry (429 lines)
│   └── screen.png
│
├── gis_investigation_workspace_.../
│   ├── code.html                    # GIS/Map workspace (488 lines)
│   └── screen.png
│
├── vessel_attribution_ranking_.../
│   ├── code.html                    # Vessel ranking (363 lines)
│   └── screen.png
│
├── vessel_forensic_profile_.../
│   ├── code.html                    # Vessel profile deep-dive
│   └── screen.png
│
├── evidence_dossier_.../
│   ├── code.html                    # Evidence report (623 lines)
│   └── screen.png
│
├── security_alerts_.../
│   ├── code.html                    # Alerts management
│   └── screen.png
│
└── system_reports_configuration_.../
    ├── code.html                    # Reports/admin config
    └── screen.png
```

## Naming Conventions

- **Page directories:** Long descriptive slugs matching the screen/view name (no kebab/camel case — uses underscores and full words)
- **Source files:** Always `code.html` inside each directory
- **Screenshots:** Always `screen.png` paired with `code.html`
- **Design docs:** `DESIGN.md` (uppercase) in `maritime_oversight_response/`

## Key File Locations

| What | Where |
|---|---|
| Design system tokens | `maritime_oversight_response/DESIGN.md` |
| Login / Auth entry | `secure_login_.../code.html` |
| Primary dashboard | `command_dashboard_.../code.html` |
| Map / GIS workspace | `gis_investigation_workspace_.../code.html` |
| Detection registry | `oil_spill_detection_registry_.../code.html` |
| Vessel attribution | `vessel_attribution_ranking_.../code.html` |
| Vessel detail | `vessel_forensic_profile_.../code.html` |
| Evidence dossier | `evidence_dossier_.../code.html` |
| Alerts | `security_alerts_.../code.html` |
| Reports/Config | `system_reports_configuration_.../code.html` |
| GSD project planning | `.planning/` |
| GSD tooling | `.agent/` |
| Project custom skills | `.agents/skills/` |

## Observations

- No shared CSS file, shared JS module, or common HTML template/include — each page is fully self-contained
- The Tailwind config block (~100 lines) is duplicated verbatim in every `code.html`
- Screenshots (`screen.png`) suggest pages were generated from a design tool and captured
- One directory (`a_sophisticated_professional_abstract_visualization_of_maritime_surveillance/`) contains only `screen.png` — no `code.html` — likely a design reference image
