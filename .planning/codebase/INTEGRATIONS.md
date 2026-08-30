---
last_mapped: 2026-08-27
---

# INTEGRATIONS.md — External Services & APIs

## Current Integrations (Static Mockup Phase)

The application is currently a **static HTML prototype**. No backend integrations exist yet. All data is hardcoded in markup.

### External CDN Dependencies

| Service | URL | Type | Required |
|---|---|---|---|
| Tailwind CSS | `https://cdn.tailwindcss.com?plugins=forms,container-queries` | CSS framework | YES — breaks styling if unavailable |
| Google Fonts (Inter) | `https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700` | Typeface | Soft — falls back to system sans-serif |
| Material Symbols | `https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:...` | Icon font | Soft — icons disappear as text fallback |
| Google AI public images | `https://lh3.googleusercontent.com/aida-public/...` | Hero images | Soft — used on login page hero |

### Data Sources (Planned / Not Yet Integrated)

Based on page content and domain, these are the expected backend integrations when moving from mockup to production:

| Integration | Purpose | Pages Affected |
|---|---|---|
| Satellite SAR/optical imagery API | Oil slick detection imagery | `gis_investigation_workspace`, `command_dashboard` |
| AIS (Automatic Identification System) API | Vessel position and trajectory data | `vessel_attribution_ranking`, `gis_investigation_workspace` |
| Detection ML model API | Oil spill confidence scoring, area estimation | `oil_spill_detection_registry`, `command_dashboard` |
| Auth / Identity provider (SSO/OAuth) | Government secure login | `secure_login` |
| Incident management backend | INC-2026-xxx record store | `evidence_dossier`, `vessel_forensic_profile` |
| Alert notification service | Real-time security alerts | `security_alerts_maritime_surveillance_portal` |
| Report generation service | PDF/export of evidence dossiers | `system_reports_configuration_console` |

### Domains Referenced in Source

- `cdn.tailwindcss.com` — CSS styles
- `fonts.googleapis.com` — fonts & icons (2 separate link elements per page, minor duplicate)
- `fonts.gstatic.com` — font file serving (referenced in GIS and Evidence Dossier pages)
- `lh3.googleusercontent.com` — Google AI-generated hero image proxy

## Security Notes

- No API keys, tokens, or credentials are present in source (all pages are purely static)
- No CORS policies needed currently (no fetch/XHR calls)
- CDN dependency is a future production risk — consider self-hosting Tailwind in production build
