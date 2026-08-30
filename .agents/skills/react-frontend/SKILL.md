---
name: react-frontend
description: Build and maintain the React JavaScript frontend for the oil spill detection and AIS vessel attribution application.
---

# React Frontend Skill

You are working on a React + JavaScript frontend.

## Core rules

- Inspect the existing project before modifying it.
- Preserve the existing architecture unless there is a strong technical reason to change it.
- Use functional React components.
- Use reusable components.
- Keep components small and maintainable.
- Use React hooks appropriately.
- Do not put the entire application inside App.jsx.
- Separate pages, components, services, hooks, utilities and assets.
- Keep API logic separate from UI components where practical.
- Do not hardcode production data.
- Do not use fake API responses when real APIs exist.

## Recommended structure

Use an architecture similar to:

src/
  components/
  pages/
  layouts/
  maps/
  charts/
  services/
  hooks/
  utils/
  assets/

Adapt this structure to the existing project instead of blindly replacing it.

## UI requirements

Create a professional technical dashboard.

Use:

- reusable buttons
- cards
- tables
- forms
- modals
- dropdowns
- tabs
- alerts
- badges
- tooltips
- loading states
- error states
- empty states

Avoid:

- excessive gradients
- unnecessary animations
- giant cards
- clutter
- fake statistics
- generic AI-generated dashboard layouts

## Responsive design

The frontend must work on:

- desktop
- laptop
- tablet
- mobile

Pay special attention to the map, tables and dashboard layout.

## State management

Use appropriate React state patterns.

Do not create unnecessary global state.

Keep loading, error and data states explicit.

## Routing

Use the project's existing routing solution if present.

Protect authenticated pages when authentication exists.

## Code quality

Use clean JavaScript.

Avoid duplicated code.

Use meaningful variable and component names.

Do not modify unrelated backend code unless explicitly requested.