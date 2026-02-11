# AI Agent Context Guide for NewsNexus

This document is designed for Codex-like agents and human maintainers who need implementation-level context quickly.

## 1) Fast orientation

- **Main entry point:** `app.py`
- **Main persistence API used by app-level modules:** `database.py`
- **Alternate ORM models:** `database/models.py`
- **Agent automation:** `agents/`
- **Service abstractions:** `services/`
- **Product pages:** `pages/`
- **Reusable UI blocks:** `components/`

## 2) Execution flow map

1. `app.py` initializes database schema via `init_database()`.
2. Session state is prepared (`user`, `location`, preferences, theme).
3. Authentication state is resolved (`get_current_user()`).
4. Geo location and user preferences are loaded.
5. UI sections render in sequence: header → navigation → content → footer.
6. Main content requests hierarchical news from `geo_services.py` and renders cards/maps.
7. Ads and subscription gating are applied based on user tier.

## 3) Module-level intent and contracts

## 3.1 `app.py`
- Coordinates page-level UX and system calls.
- Should remain orchestration-heavy but logic-light.
- If adding features, prefer extracting logic to services/modules and calling from here.

## 3.2 `database.py`
- Contains schema creation and SQL helper methods.
- Current schema includes users, articles, interactions, subscriptions, reviews, affiliate, analytics, ads, and themes.
- If changing table contracts, update all calling modules and docs in same change.

## 3.3 `database/models.py`
- ORM definitions for key entities and relationships.
- Used by service/agent code paths.
- Keep naming consistency with SQL schema migration strategy to avoid semantic mismatch.

## 3.4 `news_aggregator.py`
- Pulls RSS feeds.
- Extracts article content using trafilatura.
- Enriches with AI summary + sentiment + category.
- Saves/retrieves cache via `database.py` functions.

## 3.5 `auth.py`
- Streamlit-native login/signup components.
- Includes session timeout and role permission checks.
- Contains demo-level password/OTP flows; production hardening should replace session-only hash helpers.

## 3.6 `geo_services.py`
- User location inference and hierarchical filtering.
- Supports local/regional/national/international pathways.

## 3.7 `subscription.py`, `advertisement.py`, `affiliate.py`
- Monetization stack.
- Subscription status controls ad frequency and paywall behavior.
- Affiliate paths include product listing, click tracking, and analytics.

## 3.8 `analytics.py` + `services/analytics_service.py`
- Event capture and dashboard-level insight generation.
- Ensure every new user action has analytics event mapping where business-relevant.

## 3.9 `agents/`
- `news_agent.py`, `review_agent.py`, `content_agent.py`: specialized workers.
- `orchestrator.py`: asynchronous coordinator for standard and custom workflows.
- Known partial implementations use placeholders (`pass`) for some workflow operations.

## 3.10 `services/`
- Contains class-based service interfaces that can become core dependency injection points.
- Prefer extending these classes for new business capabilities before adding ad-hoc module-level functions.

## 4) Data contract hotspots (edit carefully)

1. `users` / `User` fields: role, subscription_tier, preferences.
2. Article fields: summary, sentiment score/category, location relevance.
3. Subscription and billing fields: tier, amount, expiry.
4. Analytics event structure: event type/action, metadata payload.
5. Review and blockchain linkage fields.

When editing any of these, verify:
- all write paths
- all read/display paths
- analytics pipelines
- docs references

## 5) Recommended engineering workflow for AI agents

1. **Read before edit:** open touched module + direct dependencies.
2. **Plan changes:** keep patch focused and reversible.
3. **Implement safely:** preserve backward compatibility unless migration is included.
4. **Validate quickly:** run syntax/compile checks and focused tests.
5. **Update docs:** explain what changed and why.
6. **Commit atomically:** one coherent story per commit.

## 6) SAFe-aware delivery checklist for each change

- [ ] Feature/story linked to measurable outcome.
- [ ] Enabler implications identified (architecture, security, testability).
- [ ] Acceptance criteria and NFRs documented.
- [ ] Operational impact understood (monitoring, support).
- [ ] Documentation updated (README + docs).

## 7) Non-functional expectations

- **Reliability:** fail gracefully when external services are down.
- **Security:** avoid storing secrets in code; use environment variables.
- **Performance:** avoid expensive per-article operations in render loops where possible.
- **Maintainability:** isolate UI code from business logic and persistence logic.
- **Observability:** ensure key user/business actions are tracked.

## 8) Known gaps for future backlog

1. Formal automated tests are sparse.
2. Persistence strategy should converge (SQL vs ORM).
3. Security hardening for auth and OTP flows.
4. Some orchestration workflow sections are stubs.
5. Potential schema inconsistencies should be standardized with migrations.

## 9) Definition of Done template (recommended)

A change is complete when:
- code compiles/runs,
- acceptance checks pass,
- analytics impact is addressed,
- docs are updated,
- rollout/rollback notes are known,
- PR includes rationale and risk notes.

