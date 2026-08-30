---
last_mapped: 2026-08-27
---

# CONCERNS.md — Technical Debt, Known Issues & Risks

## Critical Issues

### 1. Tailwind Config Block Duplicated Across All Pages
**Severity: HIGH**
- The full `tailwind.config` object (~90 lines of JSON) is copy-pasted verbatim into every `code.html`
- Any design token change (color, spacing, typography) must be manually updated in 9 files
- High risk of drift: pages may silently diverge from `DESIGN.md` spec
- **Fix:** Extract to a shared config file and import, or move to a build tool (Vite/Next.js)

### 2. CDN-Only Dependencies (No Local Fallback)
**Severity: HIGH**
- All CSS (Tailwind), fonts (Inter), and icons (Material Symbols) are loaded from external CDNs
- No network connectivity = broken UI (no graceful degradation)
- Tailwind CDN version is unpinned — auto-updates could break the UI silently
- **Fix:** Pin CDN versions, bundle assets locally for production, add font-display fallbacks

### 3. All Data is Hardcoded HTML (No Real Data Layer)
**Severity: HIGH** (blocker for production use)
- Every metric, table row, incident ID, vessel name, coordinate, confidence score is static HTML
- INC-2026-001 / MSC Ocean Star / 94% confidence are example fixtures, not live data
- No fetch calls, no state management, no pagination logic
- **Fix:** Major architectural work needed to connect to real SAR/AIS/detection APIs

### 4. No Authentication / Authorization Logic
**Severity: HIGH**
- The login page is purely decorative — no form submission handler, no session management, no JWT/cookie
- Any page is accessible directly by URL; there is no access control
- **Fix:** Implement auth flow (backend + frontend session management)

## Moderate Issues

### 5. Duplicate Font Imports
**Severity: MEDIUM**
- Several pages import Material Symbols Outlined twice in `<head>` (two identical `<link>` elements)
- Causes an unnecessary extra HTTP request on page load
- Files affected: `secure_login_.../code.html`, `gis_investigation_workspace_.../code.html`, `vessel_attribution_.../code.html`, `evidence_dossier_.../code.html`

### 6. No Navigation Wiring Between Pages
**Severity: MEDIUM**
- All sidebar nav links use `href="#"` — clicking navigates nowhere
- Pages are isolated; no way to flow from Login → Dashboard → GIS in the browser
- **Fix:** Wire up relative hrefs between `code.html` pages or implement a router

### 7. No Error States or Loading States in UI
**Severity: MEDIUM**
- No skeleton loaders, no empty states, no error messages for failed data loads
- Real users would see stale content while data loads — needs proper UX states
- **Fix:** Add loading/error/empty state variants per component

### 8. Map Layer is CSS-Simulated (Not a Real Map)
**Severity: MEDIUM**
- The GIS workspace map is implemented as a CSS grid pattern:
  ```css
  .map-layer { background-color: #0b1426; background-image: linear-gradient(...); background-size: 50px 50px; }
  ```
- No real geospatial library (Leaflet, MapboxGL, OpenLayers, Deck.gl, Google Maps)
- No coordinates, no zoom, no oil slick polygons, no AIS vessel trajectories
- **Fix:** Integrate a real mapping library (Leaflet.js or MapboxGL recommended per domain skills)

## Minor Issues

### 9. No `<meta>` Description or SEO Tags
**Severity: LOW**
- Pages lack `<meta name="description">` (not critical for internal government tool, but good practice)

### 10. Inconsistent `<html>` Class Usage
- Some pages use `<html class="light" lang="en">`, others use `<html lang="en">` without `class="light"`
- Minor inconsistency in dark mode toggle targeting (`darkMode: "class"` in Tailwind config)

### 11. No `package.json` at Root / No Build Pipeline
**Severity: LOW for now, HIGH if project grows**
- No scripts for dev server, build, or linting
- Developer must manually open `code.html` in a browser
- **Fix:** Add Vite (or simple `npx serve`) for local development; add scripts when needed

### 12. Long Directory Names
- Directory names like `a_sophisticated_professional_abstract_visualization_of_maritime_surveillance` are unwieldy
- File paths become very long on Windows; may cause issues with some tooling
- Consider renaming to shorter slugs: `login/`, `dashboard/`, `gis-workspace/`, etc.

## Security Observations

- No sensitive data in source (no API keys, tokens, credentials) — **SAFE** for current state
- No HTTPS enforcement needed for static files (CDN assets are HTTPS)
- XSS risk is minimal (no dynamic HTML injection in current static pages)
- Future risk: when real API integration begins, ensure credentials are never embedded in front-end code

## Prioritized Action List

1. **Wire up navigation** — connect pages with real hrefs (quick win)
2. **Add a local dev server** — `npx serve .` or Vite for hot reload
3. **Integrate real map library** — Leaflet.js or MapboxGL (highest value visual upgrade)
4. **Extract shared Tailwind config** — deduplicate across pages
5. **Add authentication** — when backend is available
6. **Connect to real data APIs** — AIS, SAR detection, incident store
