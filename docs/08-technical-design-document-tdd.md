# Technical Design Document (TDD)

## Document status
- Owner: Engineering
- Last updated: 2026-02-11

## Architecture summary
- UI and orchestration: `app.py` + `pages/` + `components/`.
- Domain logic: top-level modules (`news_aggregator.py`, `auth.py`, `subscription.py`, etc.).
- Service layer: `services/` class-based wrappers.
- Persistence: `database.py` (SQL) and `database/models.py` (ORM).
- Agent automation: `agents/` worker modules and orchestrator.

## Data model overview
Core entities include users, articles, reviews, subscriptions, ads, affiliate objects, analytics events, and blockchain records.

## API and integration model
- External inputs: RSS feeds, AI APIs, payment providers, geolocation services.
- Internal interfaces: function-based module APIs and service class methods.

## Design constraints
- Current runtime is single Streamlit app process.
- External API response times and failures directly affect UX unless fallback is present.
- Dual persistence patterns increase model drift risk.

## Key technical decisions
1. Keep Streamlit for rapid UI delivery.
2. Use modular services for gradual architectural cleanup.
3. Maintain graceful degradation when APIs are unavailable.
4. Preserve observability through analytics event capture.

## Open technical debt
- Standardize schema naming and contracts.
- Expand automated tests.
- Harden auth/session security flows.

## Change rationale
This TDD centralizes architectural intent so contributors can align implementation decisions with known constraints and future migration paths.
