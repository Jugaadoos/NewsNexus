# Software Development Plan

## Document status
- Owner: Engineering Management
- Last updated: 2026-02-11

## Delivery model
- Agile iteration with backlog hierarchy (theme → epic → feature → story → task).
- SAFe-aligned planning cadence for larger increments.

## Sprint/iteration practices
- Planning: define acceptance criteria and instrumentation needs up front.
- Daily sync: track blockers, quality risks, and dependency issues.
- Review/demo: show user-visible outcomes and operational impact.
- Retrospective: identify reliability, quality, and velocity improvements.

## Branching and code review
- Use feature branches with focused, atomic commits.
- Require `.github/pull_request_template.md` for PR descriptions so every review includes summary, why, risk, rollback, docs changed, test evidence, and deployment impact.
- Keep docs updates in the same PR as behavior changes and record merged outcomes in `docs/pr-history.md`.

## Coding standards
- Small, cohesive functions and modules.
- Prefer service-layer extensions over ad-hoc logic duplication.
- Keep secrets/configuration externalized via environment variables.

## Definition of done
- Implementation complete.
- Basic validation executed.
- Documentation and release notes updated.
- A new merged-PR row is appended to `docs/pr-history.md` (date, PR link/ID, scope, impacted docs, migration/deploy notes, rollback note).
- Security and data-contract implications reviewed.

## Change rationale
The plan creates predictable delivery and easier onboarding for both humans and AI agents by making execution standards explicit.
