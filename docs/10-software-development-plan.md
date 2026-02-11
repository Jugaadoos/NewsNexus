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
- Require PR descriptions to include: what, why, risk, rollback, docs updates.
- Keep docs updates in same PR as behavior changes.

## Coding standards
- Small, cohesive functions and modules.
- Prefer service-layer extensions over ad-hoc logic duplication.
- Keep secrets/configuration externalized via environment variables.

## Definition of done
- Implementation complete.
- Basic validation executed.
- Documentation and release notes updated.
- Security and data-contract implications reviewed.

## Change rationale
The plan creates predictable delivery and easier onboarding for both humans and AI agents by making execution standards explicit.
