# API Documentation

## Document status
- Owner: Engineering
- Last updated: 2026-02-11

## Scope note
NewsNexus is currently implemented primarily as an internal-module architecture rather than a public REST API. This document describes callable interfaces and integration touchpoints used by the product.

## Internal module interfaces (representative)

### `database.py`
- `init_database()`
- CRUD helpers for users, articles, analytics, subscriptions, ads, affiliate tracking

### `news_aggregator.py`
- Feed fetch and parse operations
- Summary/sentiment/category enrichment

### `ai_services.py` and `services/ai_service.py`
- Text summarization and sentiment evaluation pathways

### `geo_services.py` and `services/geo_service.py`
- Location detection and geographic filtering utilities

### `auth.py` and `services/auth_service.py`
- Login/signup/session and permission checks

## Environment-specific data backend
To keep internal API assumptions aligned with runtime behavior, treat `database/connection.py` and `config.py` as normative references for backend selection and environment contracts.

- `database/connection.py` governs live database binding (`DATABASE_URL` first, SQLite fallback when unset).
- `config.py` defines expected environment variables and remains the shared contract surface for deployment and local setup (`DATABASE_URL`, `PGHOST`, `PGPORT`, `PGDATABASE`, `PGUSER`, `PGPASSWORD`).
- Environment policy: preprod/prod integrations must target PostgreSQL via `DATABASE_URL`; local/dev integrations can rely on SQLite fallback when that variable is absent.

## External service contracts
- OpenAI API: model-based text generation and analysis.
- Stripe: subscription/payment operations.
- RSS feeds: source ingestion.
- Optional geo/map providers.

## Error and fallback behavior
- If AI service fails, content should still render with baseline metadata.
- If payment service fails, user should receive clear retry/support guidance.
- If feed source fails, fallback sources/cached content should be preferred.

## Versioning approach (current)
- No explicit semantic API versioning yet.
- Contract changes must be documented in release notes and technical docs.

## Recommended future direction
Expose stable HTTP APIs for selected domains (news feed, analytics, partner operations) with explicit schema and versioning policies.
