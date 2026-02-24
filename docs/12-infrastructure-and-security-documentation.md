# Infrastructure & Security Documentation

## Document status
- Owner: Engineering + Operations
- Last updated: 2026-02-11

## Infrastructure overview
- Runtime: Streamlit application process.
- Database: PostgreSQL.
- External services: OpenAI, Stripe, RSS providers, optional maps/geo APIs.
- Configuration: environment variables through `config.py` pathways.

## Security posture (current)
- Password hashing exists in auth paths.
- Role-based authorization checks exist.
- Some demo-level behaviors remain and require production hardening.

## Security controls baseline
- Keep secrets out of code and in environment variables.
- Limit privileged roles and review role assignment pathways.
- Log operational events and monitor unusual usage patterns.
- Ensure fallback behavior does not leak sensitive internal data.

## Data protection principles
- Collect only required user and analytics data.
- Define retention windows for event-level telemetry.
- Provide legal policy links and update when processing changes.

## Incident response basics
1. Detect via app errors, analytics anomalies, or provider failures.
2. Triage by severity and user impact.
3. Mitigate via rollback/fallback.
4. Publish issue summary and follow-up tasks.

## Hardening backlog
- Remove demo OTP assumptions.
- Expand auth/session auditability.
- Add dependency scanning and secrets scanning to CI.

## Release governance links
- Release planning, rollout windows, validation evidence, and rollback procedures are maintained in [`docs/release-notes.md`](./release-notes.md).
- Incident triage/escalation workflow details are maintained in [`docs/troubleshooting-guide.md`](./troubleshooting-guide.md).
- During active incidents, use all three documents together:
  1. `troubleshooting-guide` to classify/triage the issue.
  2. `release-notes` to identify recent changes and rollback options.
  3. `infrastructure-and-security-documentation` (this file) to apply security-aware mitigation.
