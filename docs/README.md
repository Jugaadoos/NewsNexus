# Documentation Hub

This folder is the central documentation hub for NewsNexus.

## Canonical architecture source of truth

To avoid architecture drift between audience-specific summaries and implementation-facing documentation, the **canonical technical truth** for architecture decisions lives in:

1. `product-foundation.md` (business + product context that informs architecture constraints)
2. `08-technical-design-document-tdd.md` (technical architecture, component boundaries, and implementation details)

When architecture statements appear elsewhere (for example in onboarding summaries, AI-agent context docs, or child-friendly explainers), those documents must be treated as derivatives and periodically reconciled against the canonical sources above.

## Why this hub exists

The project now includes a complete documentation set that maps to common product, design, engineering, legal, and launch requirements. The goal is to make code and business intent understandable for:

- New engineers and maintainers.
- Product and operations stakeholders.
- AI coding agents that need high-context references.

## Document map

### Strategic and planning
- `product-foundation.md` (legacy + SAFe aligned master context)
- `01-product-vision-strategy.md`
- `02-product-requirements-document-prd.md`
- `03-market-requirements-document-mrd.md`
- `04-product-roadmap.md`
- `05-user-personas-journey-maps.md`

### Design and UX
- `06-wireframes-and-mockups.md`
- `07-ux-ui-design-guidelines.md`

### Technical
- `08-technical-design-document-tdd.md`
- `09-api-documentation.md`
- `10-software-development-plan.md`
- `11-qa-testing-plan-and-acceptance-criteria.md`
- `12-infrastructure-and-security-documentation.md`
- `deployment-runbook.md` (manual release and rollback procedure for preprod/prod)
- `pr-history.md` (required merged PR ledger)
- `ai-agent-context.md`
- `child-friendly-architecture.md`

### Launch and user docs
- `release-notes.md`
- `user-manual-help-center-faq.md`
- `troubleshooting-guide.md`

### Legal and compliance
See `../legal/`:
- `terms-of-service.md`
- `terms-of-purchase.md`
- `privacy-policy-and-gdpr.md`
- `eula.md`
- `data-processing-agreement-dpa.md`

## Maintenance policy

When product behavior changes, update:
1. Relevant technical docs in this folder.
2. Relevant legal docs if data usage or transaction flows changed.
3. `release-notes.md` with a dated entry.
4. README links if document names or scope changed.
5. `pr-history.md` by appending one row for each merged PR.

Every documentation update should explicitly include:
- What changed.
- Why the change was made.
- Operational impact.
- Follow-up tasks and known gaps.

## Pull request governance artifacts

- PR authoring template: `../.github/pull_request_template.md`
- Merged PR ledger: `pr-history.md`

These artifacts are mandatory process controls for keeping decision context durable over time. Together they ensure each PR captures intent during review and then records final merge outcomes for future audits, onboarding, and AI-assisted maintenance.
