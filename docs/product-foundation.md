# AI News Hub Product Foundation (SAFe 6.0 Aligned)

## 1) Document purpose

This document is the foundation context for:

- Product managers and engineering leaders.
- Human maintainers and new team members.
- AI coding/operations agents (Codex-style agents).

It defines product intent, architecture boundaries, operational model, and SAFe 6.0-aligned governance so the platform can evolve safely.

---

## 2) Product mission and value proposition

### Mission
Deliver personalized, trustworthy, and explainable news experiences with AI augmentation while balancing engagement, editorial quality, and monetization.

### Primary value streams
1. **Reader value stream:** discover and consume relevant news quickly.
2. **Creator/publisher value stream:** distribute content with review and analytics visibility.
3. **Business value stream:** monetize through subscriptions, ads, and affiliate channels.
4. **Operational value stream:** continuously improve content quality with AI and analytics feedback loops.

### Differentiators
- AI summaries and sentiment-aware theming.
- Location-aware content hierarchy (local → international).
- Multi-role access model (reader, reviewer, editor, affiliate, admin).
- Blockchain-style review traceability pathways.

---

## 3) Scope and personas

### Core personas
- **Reader:** consumes/saves content; can subscribe.
- **Reviewer/Editor:** quality controls content, approves/rejects.
- **Creator/Journalist:** contributes content.
- **Publishing Partner:** manages submissions and revenue view.
- **Affiliate:** promotes products and tracks commissions.
- **Admin:** platform-wide operations and governance.

### Product boundaries
- In scope: aggregation, summarization, personalization, subscription/ads/affiliate monetization, analytics dashboards.
- Out of scope (currently): advanced rights-management workflows, fully decentralized blockchain network, event-stream microservices.

---

## 4) Functional architecture

## 4.1 Presentation layer
- `app.py`: root app lifecycle (session, header, nav, content, footer).
- `pages/`: feature surfaces (dashboard, analytics, profile, admin, partner portal, settings, etc.).
- `components/`: reusable building blocks:
  - `news_card.py` for rich article rendering.
  - `map_interface.py` for geospatial views.
  - `theme_manager.py` for personalization.
  - `ad_manager.py` for ad placements.

## 4.2 Domain/application layer
- **News ingestion and enrichment:** `news_aggregator.py`
- **Auth/session behavior:** `auth.py`
- **Monetization:** `subscription.py`, `advertisement.py`, `affiliate.py`
- **Insights:** `analytics.py`
- **Geo intelligence:** `geo_services.py`
- **AI augmentation:** `ai_services.py`, `color_psychology.py`
- **Agent automation:** `agents/*.py`

## 4.3 Service layer
`services/` provides class-based implementations for:
- AI (`ai_service.py`)
- Auth (`auth_service.py`)
- News (`news_service.py`)
- Geo (`geo_service.py`)
- Payment (`payment_service.py`)
- Blockchain (`blockchain_service.py`)
- Analytics (`analytics_service.py`)

This gives a path toward cleaner dependency injection and modular scaling.

## 4.4 Data layer
Two persistence approaches coexist:
1. **Direct SQL path:** `database.py` (psycopg2 queries and schema bootstrapping).
2. **ORM path:** `database/models.py` with SQLAlchemy models used by some service/agent logic.

This mixed approach works but should be converged over time to reduce contract drift.

---

## 5) Technical architecture

## 5.1 Runtime architecture
- Single Streamlit runtime for UI + business logic.
- PostgreSQL as system of record.
- External APIs:
  - OpenAI (LLM features)
  - Stripe (payments)
  - RSS feed providers (content source)
  - Optional geo/maps/providers

## 5.2 Integration architecture
- Pull-based ingestion from RSS.
- Synchronous request-response for most user interactions.
- Async orchestration for AI agents (`agents/orchestrator.py`) with workflow loops.

## 5.3 Reliability and quality constraints
- Soft-fail pattern in many modules (catch exceptions and continue).
- Content fallback behavior when APIs fail.
- Session-state-driven UX resilience in Streamlit.

## 5.4 Security and compliance posture (current)
- Password hashing exists (PBKDF2 + salt) in app-layer auth flow.
- Role-based checks available by permission mapping.
- Several areas are demo-level and require hardening for production:
  - OTP stub values.
  - Password hash persistence currently tied to session memory helper paths.

---

## 6) Information architecture and data model

## 6.1 Core domain entities

### Users and identity
- `users` table / `User` model stores identity, role, tier, and preferences.
- Supports role-based capabilities and personalization settings.

### Content
- `news_articles` table and `Article` model represent canonical content objects.
- Fields support source metadata, summaries, category, sentiment, and geo relevance.

### Reviews and trust
- `reviews` and `Review` include status/comments and optional blockchain hash.
- Enables moderation workflows and audit-style traces.

### Monetization
- `subscriptions` / `Subscription` for paid tiers.
- `advertisements` and affiliate entities for ad + partner revenue.

### Analytics
- `user_analytics` and `Analytics` capture behavior events and usage trends.

### Agent operations
- `ai_agents` tracks managed AI workers and run status.
- `blockchain_records` stores chain-related records.

## 6.2 Data model notes
- JSON columns are used heavily for flexible attributes (preferences, geo data, configs).
- Multiple naming patterns exist across SQL vs ORM schemas (example: `news_articles` vs `articles`).
- A future schema convergence RFC is recommended to avoid semantic mismatch.

## 6.3 Information model (business meaning)
- **Article lifecycle:** ingest → enrich → store → render → track interaction.
- **User lifecycle:** register/login → personalize → consume → convert/retain.
- **Revenue lifecycle:** impression/click/subscription → analytics attribution.
- **Trust lifecycle:** AI review → human queue → blockchain recording.

---

## 7) Service model

## 7.1 Internal service responsibilities
- **News Service:** fetch, parse, classify, and cache external news.
- **AI Service:** summarize/analyze/generate contextual enhancements.
- **Geo Service:** location inference and geographic filtering.
- **Auth Service:** user verification and permission checks.
- **Payment Service:** subscription payment orchestration.
- **Analytics Service:** event collection and KPI calculations.
- **Blockchain Service:** integrity logging for review/content events.

## 7.2 External service dependencies
- OpenAI API availability directly impacts summary/sentiment/theme quality.
- RSS feed reliability affects freshness.
- Stripe availability affects paid conversions.

## 7.3 SLO-aligned service goals (recommended)
- **Content freshness SLO:** >95% category refresh jobs complete within planned cadence.
- **App availability SLO:** 99.0% monthly for reader views.
- **AI fallback success:** 100% requests return a graceful non-blocking response.

---

## 8) SAFe 6.0 alignment framework

The following sections map repository operations to SAFe 6 concepts so product delivery remains scalable.

## 8.1 Strategic themes and Lean Portfolio Management
Recommended strategic themes:
1. Trustworthy AI-enhanced journalism.
2. Monetization maturity (subscription + affiliate + ad mix).
3. Geo-personalized global relevance.
4. Operational excellence via observability and automation.

Portfolio governance artifacts to maintain:
- Epic hypothesis statements.
- Lean business cases.
- Epic Kanban with WIP limits.
- Benefit realization review every PI.

## 8.2 Agile Product Delivery (Customer Centricity)
- Maintain persona-specific journeys for reader, partner, affiliate, and admin.
- Connect each backlog item to measurable user outcome (e.g., CTR, retention, conversion).
- Use outcome hypotheses, not only output tasks.

## 8.3 Team and Technical Agility
- Keep modules cohesive (UI, services, data) with explicit ownership.
- Standardize code review checklists including architecture + security + docs deltas.
- Shift-left quality with lightweight checks before merge.

## 8.4 ART and PI Planning guidance
Use a single ART-style cadence for major enhancements:
- PI duration recommendation: 8–12 weeks.
- PI events:
  - Planning
  - Scrum of Scrums / PO sync
  - System demo
  - Inspect & Adapt workshop

PI objectives should include:
- Business objective (metric impact).
- Enabler objective (architecture/test/security improvements).
- Risks with ROAM status.

## 8.5 Built-In Quality and DevSecOps
Built-In Quality checklist for this repository:
- Functional acceptance criteria defined before implementation.
- NFRs captured (performance, security, reliability, maintainability).
- Documentation updated in same PR.
- Runtime error paths validated for graceful degradation.

DevSecOps pipeline target stages:
1. Code + docs lint.
2. Unit/integration tests (incremental addition recommended).
3. Security scan and dependency checks.
4. Deploy and smoke test Streamlit app.

## 8.6 Measure and Grow
Adopt metrics across 3 lenses:
- **Flow:** lead time, throughput, WIP age, blocked time.
- **Quality:** escaped defects, incident frequency, MTTR.
- **Outcome:** active users, retention, subscription conversion, partner revenue.

Run a Measure and Grow self-assessment at least once per PI.

---

## 9) Product management best-practice baseline

## 9.1 Backlog structure
Use hierarchy:
- Theme → Epic → Capability → Feature → Story → Task

All items should include:
- Problem statement.
- Hypothesis/outcome metric.
- Acceptance criteria.
- Instrumentation plan.
- Rollback strategy (where applicable).

## 9.2 Release governance
Each release candidate should have:
- Scope summary.
- Data migration notes.
- Config/environment changes.
- Known issues and mitigations.
- Observability dashboard links.

## 9.3 RACI clarity
Define owners for each domain:
- Product: value prioritization.
- Engineering: implementation and technical integrity.
- Operations: runtime health and incident response.
- Analytics: KPI definition and experimentation quality.

---

## 10) AI-agent operational guidance (high level)

1. Read architecture and module boundaries before editing.
2. Prefer small, reversible changes with explicit rationale.
3. Keep docs synchronized with behavior changes.
4. Avoid introducing new persistence patterns without migration plan.
5. If adding APIs, define data contracts and failure modes.

(See `docs/ai-agent-context.md` for detailed execution guidance.)

---

## 11) Risks and technical debt

1. **Dual data-access approach** (raw SQL + ORM) can diverge.
2. **Mixed maturity across modules** (some production-ready, some placeholders).
3. **Limited formal tests** increase regression risk.
4. **Security hardening gaps** in demo auth paths.
5. **Potential data contract drift** between tables and models.

### Mitigation roadmap
- Phase 1: Add contract tests for critical entities.
- Phase 2: Choose canonical persistence layer and migrate incrementally.
- Phase 3: Harden auth/payment pathways with secure storage and audits.

---

## 12) Documentation maintenance policy

When changing product behavior, update:
1. `README.md` for entry-level orientation.
2. `docs/product-foundation.md` for architecture/product implications.
3. `docs/ai-agent-context.md` for implementation and operational instructions.
4. `docs/child-friendly-architecture.md` if conceptual explanation is impacted.

Every meaningful PR should include:
- What changed.
- Why it changed.
- How to operate/verify the change.
- Which user/agent workflows are impacted.

