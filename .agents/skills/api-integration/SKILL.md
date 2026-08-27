---
name: api-integration
description: Connect the React frontend safely and reliably to the existing backend APIs for oil spill detection and AIS attribution.
---

# API Integration Skill

The React frontend communicates with the existing backend.

Architecture:

React frontend
    ↓
Backend REST API
    ↓
ML/GIS/AIS services
    ↓
Database or processing pipeline

## First rule

Before creating API calls:

1. Inspect the backend.
2. Inspect existing routes.
3. Inspect controllers/services.
4. Inspect response formats.
5. Inspect authentication requirements.

Do not invent API endpoints if equivalent endpoints already exist.

## API service layer

Centralize API communication.

Prefer a structure such as:

src/services/

Do not scatter raw fetch calls throughout every component.

## Handle

Every API request must support:

- loading
- success
- error
- empty response
- timeout where appropriate

## Data integrity

Never fabricate:

- vessel coordinates
- oil spill coordinates
- confidence scores
- vessel names
- MMSI numbers
- detection dates
- attribution results

Use backend-provided data.

## Authentication

Follow the existing backend authentication mechanism.

Do not expose secrets in React code.

Do not store backend secrets in frontend source.

## Environment variables

API base URLs should use environment configuration where appropriate.

Never hardcode production secrets.

## Error handling

Show useful user-facing errors.

Examples:

"Unable to load spill data."

"Unable to retrieve vessel information."

"Backend service unavailable."

Provide retry functionality where appropriate.

## API changes

If a required endpoint does not exist:

1. Identify the missing endpoint.
2. Do not silently create fake data.
3. Report the frontend dependency clearly.
4. Suggest the expected request/response structure if useful.

## Backend ownership

Do not modify backend code unless explicitly requested.

The frontend consumes backend functionality.