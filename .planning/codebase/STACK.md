---
last_mapped: 2026-08-27
---

# STACK.md — Technology Stack

## Language & Runtime

- **Primary Language:** HTML5 + vanilla JavaScript (ES6+)
- **Styling Framework:** Tailwind CSS v3 (loaded via CDN: `https://cdn.tailwindcss.com?plugins=forms,container-queries`)
- **No build tool / bundler** — all pages are standalone self-contained `.html` files
- **No package manager artifacts** (no `package.json`, `node_modules` in source; only in `.agent/`)
- **Runtime:** Browser-only (client-side rendering, no server-side)

## Frontend Frameworks & Libraries

| Library | Source | Purpose |
|---|---|---|
| Tailwind CSS | CDN (tailwindcss.com) | Utility-first CSS, configured per-page |
| Tailwind Forms Plugin | CDN `?plugins=forms` | Form styling normalization |
| Tailwind Container Queries | CDN `?plugins=container-queries` | Responsive container queries |
| Google Fonts — Inter | fonts.googleapis.com | Primary typeface (400, 500, 600, 700 weights) |
| Google Material Symbols Outlined | fonts.googleapis.com | Icon system (variable font, FILL & wght axes) |

## Design System

- **Source of truth:** `maritime_oversight_response/DESIGN.md`
- **Theme:** Material Design 3 color token naming (`primary`, `on-primary`, `surface`, `on-surface-variant`, etc.)
- **Colors:** Deep Navy `#002147` primary, Muted Teal `#096969` secondary, white surfaces
- **Typography scale:** Inter at `display-lg` → `label-sm` with defined sizes, weights, line-heights
- **Spacing:** 4px base unit, 24px gutter, 16px mobile margin, 40px desktop margin, 1440px max-width
- **Border-radius:** 2px default, 4px lg, 8px xl, 12px full
- **Tailwind theme extension:** every page duplicates the same `tailwind.config` block inline

## External Services / CDNs

| Service | URL | Role |
|---|---|---|
| Tailwind CSS | cdn.tailwindcss.com | CSS framework (no local copy) |
| Google Fonts | fonts.googleapis.com | Inter font + Material Symbols |
| Google Static Fonts | fonts.gstatic.com | Font file hosting |
| Google AI image proxy | lh3.googleusercontent.com/aida-public/... | Hero images (login page) |

## No Backend / API

- The current codebase has **no backend, no API client, no auth logic, no HTTP requests** (beyond CDN assets)
- All data displayed is **static/hardcoded HTML** (no fetch, no XHR)
- No state management library (no React, Vue, Angular, etc.)
- No database client or ORM
