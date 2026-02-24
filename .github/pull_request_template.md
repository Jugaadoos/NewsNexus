# Pull Request Template

## Summary (required)
Describe **what changed** in this PR at a high level. Include the primary files, modules, or flows that were modified so reviewers can quickly orient themselves.

## Why (required)
Explain the rationale behind these changes:
- What problem is being solved?
- Why this approach over alternatives?
- What user, product, operational, or engineering outcome is expected?

## Risk (required)
Document potential risk areas introduced by this PR:
- Functional risk (behavior regressions, edge cases)
- Data risk (schema, migration, integrity, privacy)
- Operational risk (performance, alerting, deploy complexity)

## Rollback (required)
Provide a rollback plan that can be executed quickly if needed:
- Safe revert procedure
- Data rollback/forward-only caveats
- Feature flags, toggles, or compensating controls

## Docs changed (required)
List all documentation updates in this PR and what each update explains.

Required checks:
- [ ] I updated all relevant docs for this change.
- [ ] I reviewed `docs/pr-history.md` and prepared a row to append after merge.

## Test evidence (required)
List test and validation evidence that supports correctness.

Use command + result format:
- `command`: pass/fail + key output
- Manual validation steps (if applicable)
- Known limitations or untested paths

## Deployment impact (required)
Describe release implications:
- Deployment order/dependencies
- Migration requirements
- Runtime config or secret changes
- Monitoring/alert expectations after deploy
