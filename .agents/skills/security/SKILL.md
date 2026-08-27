---
name: security
description: Apply security practices to the React frontend and prevent exposure of backend credentials, API keys and sensitive configuration.
---

# Frontend Security Skill

## Never expose secrets

Never place these in frontend source:

- database passwords
- PostgreSQL credentials
- JWT signing secrets
- private API keys
- backend service credentials
- private access tokens
- cloud provider secrets

## Environment variables

Frontend environment variables must only contain values safe to expose to the browser.

Anything secret must remain on the backend.

## API architecture

Use:

React
 ↓
Backend API
 ↓
External services

Do not bypass the backend to access protected services directly.

## Authentication

Follow the existing authentication implementation.

Do not invent a new authentication mechanism without reviewing the backend.

## Input handling

Validate user input.

Do not dangerously inject untrusted HTML.

Avoid unsafe use of:

dangerouslySetInnerHTML

unless explicitly required and sanitized.

## External data

Treat backend/API data as untrusted input.

Handle missing and malformed fields gracefully.

## Sensitive information

Do not unnecessarily display:

- private credentials
- internal server information
- database errors
- access tokens
- secret configuration

## Git security

Before committing:

Check that secrets are not being added.

Do not commit:

.env

private keys

credentials

access tokens

secret configuration files

Use .gitignore where appropriate.