# QA / Testing Plan and Acceptance Criteria

## Document status
- Owner: QA + Engineering
- Last updated: 2026-02-11

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

## Quality gates for release
- No unresolved blocker defects for primary user paths.
- Legal/privacy-impacting changes reviewed.
- Release notes and troubleshooting docs updated.
