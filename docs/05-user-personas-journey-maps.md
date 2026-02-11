# User Personas & Journey Maps

## Document status
- Owner: Product + UX
- Last updated: 2026-02-11

## Personas

### 1) Reader (primary)
- Goal: understand important news quickly.
- Pain points: information overload, poor source trust, noisy feeds.
- Key flows: onboarding → browse feed → read summary → save/share/subscribe.

### 2) Reviewer/Editor
- Goal: keep quality high and reduce misinformation risk.
- Pain points: large content queues, unclear priority.
- Key flows: review queue → approve/reject/comment → audit trail check.

### 3) Publishing Partner
- Goal: distribute content and monitor performance.
- Pain points: fragmented analytics and unclear attribution.
- Key flows: submit/manage content → view engagement/revenue metrics.

### 4) Affiliate
- Goal: promote relevant products and track commission.
- Pain points: limited performance transparency.
- Key flows: manage products → track clicks/conversions → optimize campaigns.

### 5) Admin
- Goal: ensure platform reliability, security, and policy compliance.
- Pain points: broad surface area and mixed module maturity.
- Key flows: monitor system usage → manage users/roles → enforce controls.

## Journey maps (condensed)

### Reader journey
Discover -> evaluate source/title -> open AI summary -> decide deep read -> interact (save/share/subscribe).

### Reviewer journey
Receive queue -> inspect article + metadata -> publish moderation decision -> log rationale.

### Partner journey
Onboard -> configure content/revenue settings -> monitor dashboards -> iterate distribution strategy.

## Design and implementation implications
- Prioritize clear summary-first reading surfaces.
- Keep moderation actions low-friction with explicit status labels.
- Preserve analytics traceability across monetization paths.
