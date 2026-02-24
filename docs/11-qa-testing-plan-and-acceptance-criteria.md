# QA / Testing Plan and Acceptance Criteria

## Document status
- Owner: QA + Engineering
- Last updated: 2026-02-24

## Testing strategy
1. Smoke tests for critical user journeys.
2. Module-level functional verification for changed areas.
3. Regression checklist for auth, feed rendering, subscriptions, and analytics events.
4. Documentation verification (links and consistency) as a release gate.

## Critical scenarios
- User signup/login/session behavior.
- Feed ingestion and article rendering.
- Summary/sentiment generation fallback behavior.
- Subscription status and entitlement enforcement.
- Ad and affiliate interaction logging.
- Admin and partner page access by role.

## Acceptance criteria template
Every feature/change should define:
- Functional expected behavior.
- Negative/error case behavior.
- Data updates expected.
- Analytics events expected.
- UX copy and feedback expectations.

## Bug tracking guidance
- Include reproducible steps, observed/expected behavior, environment, severity, and impacted roles.
- Link bug to release-note and remediation PR when resolved.

## Quarterly documentation consistency checklist

Run this checklist once per quarter (and additionally before major releases) to prevent architecture drift across docs:

- [ ] Confirm the documented **database mode** is consistent across canonical and derivative docs (for example SQLAlchemy + PostgreSQL references, persistence boundaries, and any fallback/offline modes).
- [ ] Confirm the documented **authentication/authorization model** is consistent (session model, role model, OTP/MFA expectations, and entitlement behavior).
- [ ] Confirm the documented **AI agent workflow** is consistent (agent responsibilities, orchestrator sequence, async execution assumptions, and human override points).
- [ ] Confirm the documented **external dependencies** list is consistent (OpenAI, payments, geolocation/maps, RSS/content providers, and operationally critical third-party services).
- [ ] Cross-check the assertions above against canonical architecture sources: `docs/product-foundation.md` and `docs/08-technical-design-document-tdd.md`.
- [ ] Log any mismatches as documentation debt items with owner + due date, then update release notes if behavior expectations changed.

## Quality gates for release
- No unresolved blocker defects for primary user paths.
- Legal/privacy-impacting changes reviewed.
- Release notes and troubleshooting docs updated.
