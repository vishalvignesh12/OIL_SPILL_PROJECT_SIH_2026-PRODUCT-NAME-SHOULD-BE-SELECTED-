---
last_mapped: 2026-08-27
---

# TESTING.md — Test Structure & Practices

## Current State

**No tests exist.** This is a static HTML prototype codebase with no test framework, no test files, no CI/CD configuration, and no linting setup.

- No `jest.config.*`, `vitest.config.*`, `playwright.config.*`, or `cypress.config.*` found
- No `.eslintrc`, `.prettierrc`, or style linting config
- No `package.json` at the project root (only inside `.agent/`)
- No GitHub Actions workflows, no CI pipeline

## Testing Approach for Future Development

Given the static HTML + Tailwind architecture, the appropriate testing strategy when the project evolves would be:

### Visual / UI Testing
- **Recommended:** Playwright or Cypress for end-to-end page-level tests
- Screenshot regression testing to catch visual regressions in the design system
- Test each page renders correctly in desktop (1440px) and mobile (≤600px) breakpoints

### Unit / Component Testing
- Not applicable currently (no JavaScript components or functions)
- When JS logic is added (filtering, calculations, API calls), use Vitest or Jest

### Manual Testing Protocol (Current)
Given no automated tests, manual verification should cover:
1. Each `code.html` opens correctly in browser (no console errors)
2. CDN assets load (Tailwind, Google Fonts, Material Symbols)
3. Responsive breakpoints render correctly (mobile `<600px`, tablet `600-1024px`, desktop `>1024px`)
4. Interactive elements (buttons, inputs, toggles) have correct focus/hover states
5. Navigation active states highlight correctly per page

### Accessibility
- No automated a11y testing present
- Manual check: each form field has a visible `<label>` with `for` attribute
- Icons used decoratively include `aria-label` on interactive buttons (e.g., password toggle)
- Color contrast target: 4.5:1 minimum (specified in DESIGN.md for status colors)

## Testing Notes for GSD Phases

When adding test coverage:
- Target each `code.html` as a separate test fixture
- Use the `screen.png` files as visual baseline references
- The `data-icon` attributes on nav items can serve as test selectors
- Form IDs (`id="email"`, `id="password"`) are stable selectors for Playwright tests
