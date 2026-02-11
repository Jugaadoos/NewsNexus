# AI News Hub (NewsNexus)

AI News Hub is a Streamlit-based product that brings together news aggregation, AI-powered summarization, geographic personalization, subscriptions, advertising, affiliate commerce, and analytics in one platform.

This repository now includes a stronger documentation foundation for both humans and AI agents:

- `docs/product-foundation.md` → the main product, architecture, and operating model reference.
- `docs/ai-agent-context.md` → practical implementation context for coding and operations agents.
- `docs/child-friendly-architecture.md` → a kid-friendly explanation of the code and architecture.

## Why this README update

The old repository had no top-level README, which made onboarding difficult. This README provides a clear entry point, links to detailed docs, and aligns the project with product-management and SAFe 6.0 style documentation expectations.

## Product at a glance

- **Core UI:** Streamlit app (`app.py`) with modular pages and reusable components.
- **Data layer:** PostgreSQL access through SQL queries (`database.py`) plus SQLAlchemy models (`database/models.py`) used by service modules.
- **AI layer:** OpenAI-assisted summarization, sentiment, and theme generation.
- **Agent layer:** Specialized agents (`news`, `review`, `content`) coordinated by an orchestrator.
- **Business layer:** subscriptions, ads, affiliate commerce, partner portal, and analytics.

## Architecture quick map

```text
User → Streamlit UI (app.py + pages/) → Domain modules
    → services/* (AI, auth, news, analytics, payment, geo, blockchain)
    → database.py + database/models.py
    → External APIs (OpenAI, Stripe, RSS feeds, geolocation)
```

## Setup

### 1) Install dependencies

```bash
pip install -e .
```

### 2) Configure environment variables

At minimum:

- `OPENAI_API_KEY`
- PostgreSQL variables (`PGHOST`, `PGPORT`, `PGDATABASE`, `PGUSER`, `PGPASSWORD`) or `DATABASE_URL`
- Optional integrations: Stripe, Zoho, Google Maps, PayPal

See `config.py` for complete variable usage.

### 3) Run the app

```bash
streamlit run app.py
```

## Documentation index

- **Product foundation (primary):** `docs/product-foundation.md`
- **AI/codex operating context:** `docs/ai-agent-context.md`
- **Kid-friendly architecture:** `docs/child-friendly-architecture.md`
- **Historical architecture notes:** `replit.md`

## Recommended workflow for maintainers

1. Read `docs/product-foundation.md` before changing architecture-level behavior.
2. Read `docs/ai-agent-context.md` before implementing multi-module changes.
3. Update both docs + README links whenever scope, architecture, or data contracts change.
4. Keep acceptance criteria and NFR notes aligned with SAFe 6.0 sections in the foundation doc.

## Current repository structure

- `app.py` – primary app entry point and top-level rendering orchestration.
- `pages/` – role-driven product surfaces (dashboard, admin, profile, analytics, partner portal, etc.).
- `components/` – reusable UI elements (news card, map interface, themes, ad manager).
- `services/` – service classes for AI, auth, analytics, blockchain, payments, geo, news.
- `agents/` – asynchronous AI workers and orchestration logic.
- `database.py` and `database/` – SQL-based persistence and SQLAlchemy model definitions.
- `utils.py` and `utils/` – helper functions and utilities.

## Contribution expectations

- Keep business logic out of UI where possible.
- Add or update docs for all significant behavior changes.
- Maintain traceability from feature → data model → service → UI.
- Document tradeoffs and known limitations explicitly.

---

For deep product context, start with `docs/product-foundation.md`.
