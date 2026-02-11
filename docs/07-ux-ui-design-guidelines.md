# UX/UI Design Guidelines

## Document status
- Owner: UX + Frontend Engineering
- Last updated: 2026-02-11

## Core principles
1. Clarity over density.
2. Summary-first reading experience.
3. Accessible interactions and semantics.
4. Consistent role-aware navigation patterns.

## Visual and interaction guidance
- Keep typography readable and prioritize content hierarchy.
- Reuse existing card and layout patterns from `components/`.
- Use sentiment/theme indicators carefully; avoid manipulative color usage.
- Keep critical actions discoverable and consistent across pages.

## Accessibility baseline
- Sufficient color contrast.
- Keyboard navigability where Streamlit supports it.
- Clear labels for forms and actions.
- Avoid color-only meaning (pair with text/icon labels).

## UX consistency rules
- Similar data types should render with consistent components.
- Error states should explain what happened and what to do next.
- Empty states should guide users to meaningful actions.

## Documentation rationale
These guidelines reduce UI drift and help AI/human contributors make coherent front-end decisions in a fast-changing codebase.
