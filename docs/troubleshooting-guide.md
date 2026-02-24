# Troubleshooting Guide

## Purpose
Help operators and users quickly diagnose common issues.

## 1) App does not start
### Symptoms
- Streamlit fails to run.
### Checks
- Verify dependencies installed.
- Confirm required environment variables are set.
- Confirm database connectivity.

## 2) No news or stale content
### Symptoms
- Feed appears empty or old.
### Checks
- Validate external RSS source availability.
- Check ingestion logs and fallback behavior.
- Confirm database write/read health.

## 3) AI summaries missing
### Symptoms
- Articles appear without generated summaries.
### Checks
- Verify AI provider key and service availability.
- Inspect error paths and fallback outputs.

## 4) Login/session issues
### Symptoms
- Users cannot log in or get logged out unexpectedly.
### Checks
- Validate auth config and session state handling.
- Confirm database user records.
- Review role assignment and permission checks.

## 5) Subscription/payment issues
### Symptoms
- Upgrade/checkout fails.
### Checks
- Verify payment provider credentials.
- Check callback/webhook handling if configured.
- Confirm entitlement update logic.

## 6) Geolocation or map issues
### Symptoms
- Incorrect location or empty map.
### Checks
- Confirm geo provider availability and API keys.
- Check user preference overrides.

## 7) Escalation template
When escalating, include:
- Environment and timestamp.
- User role and impacted flow.
- Reproduction steps.
- Expected vs observed behavior.
- Relevant logs/screenshots.

## 8) Release and rollback context
- Release-specific risk, rollout windows, and rollback runbooks are tracked in [`docs/release-notes.md`](./release-notes.md).
- Infrastructure and security baseline expectations during incidents are tracked in [`docs/12-infrastructure-and-security-documentation.md`](./12-infrastructure-and-security-documentation.md).
- When escalating incidents, include the relevant release entry ID/date from release notes so responders can correlate behavior changes to shipped documentation/process updates.
