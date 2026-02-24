# AI News Hub (NewsNexus)

AI News Hub is a Streamlit-based platform that combines news aggregation, AI-powered summarization, geographic personalization, subscriptions, advertising, affiliate commerce, and analytics.

## Documentation-first update

This repository now includes a full documentation suite covering strategic, design, technical, legal, and launch/user documentation to support long-term maintainability for humans and AI agents.

## Product at a glance

- **Core UI:** Streamlit app (`app.py`) with modular pages and reusable components.
- **Data layer:** PostgreSQL access through SQL helpers (`database.py`) plus SQLAlchemy models (`database/models.py`).
- **AI layer:** OpenAI-assisted summarization and sentiment/theme logic.
- **Agent layer:** Specialized agents coordinated by an orchestrator.
- **Business layer:** subscriptions, ads, affiliate commerce, partner portal, and analytics.

## Setup

### 1) Install dependencies

```bash
pip install -e .
```

### 2) Configure environment variables

At minimum:
- `OPENAI_API_KEY`
- PostgreSQL variables (`PGHOST`, `PGPORT`, `PGDATABASE`, `PGUSER`, `PGPASSWORD`) or `DATABASE_URL`
- Optional: Stripe, Zoho, Google Maps, PayPal

### Database mode selection (canonical policy)

Use the same runtime policy across all environments to avoid configuration drift:
- **preprod/prod:** `DATABASE_URL` must be set to a PostgreSQL connection string.
- **local/dev fallback:** if `DATABASE_URL` is unset, the app defaults to SQLite (`sqlite:///newsnexus.db`) via `database/connection.py`.
- **expected environment variables:** keep `DATABASE_URL` as the primary selector; keep `PGHOST`, `PGPORT`, `PGDATABASE`, `PGUSER`, and `PGPASSWORD` populated for platform/tooling compatibility through `config.py`.

Rationale: one explicit policy reduces ambiguity, keeps local onboarding simple, and prevents environment-specific behavior mismatches during deployment.

### 3) Run the app

```bash
streamlit run app.py
```

## Documentation index

### Core documentation hub
- `docs/README.md`

### Strategic and planning
- `docs/product-foundation.md`
- `docs/01-product-vision-strategy.md`
- `docs/02-product-requirements-document-prd.md`
- `docs/03-market-requirements-document-mrd.md`
- `docs/04-product-roadmap.md`
- `docs/05-user-personas-journey-maps.md`

### Design and UX
- `docs/06-wireframes-and-mockups.md`
- `docs/07-ux-ui-design-guidelines.md`

### Technical documentation
- `docs/08-technical-design-document-tdd.md`
- `docs/09-api-documentation.md`
- `docs/10-software-development-plan.md`
- `docs/11-qa-testing-plan-and-acceptance-criteria.md`
- `docs/12-infrastructure-and-security-documentation.md`
- `docs/ai-agent-context.md`
- `docs/child-friendly-architecture.md`

### Launch and user documentation
- `docs/release-notes.md`
- `docs/user-manual-help-center-faq.md`
- `docs/troubleshooting-guide.md`

### Legal and compliance documentation (drafts)
- `legal/terms-of-service.md`
- `legal/terms-of-purchase.md`
- `legal/privacy-policy-and-gdpr.md`
- `legal/eula.md`
- `legal/data-processing-agreement-dpa.md`

## Contribution expectations

- Keep business logic out of UI where practical.
- Update relevant docs for all significant behavior changes.
- Maintain traceability from feature → data model → service → UI.
- Document rationale, risks, and known limitations.

---
For deep context, start with `docs/README.md` and `docs/product-foundation.md`.
