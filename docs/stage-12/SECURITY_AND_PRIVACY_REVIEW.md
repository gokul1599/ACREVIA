# ACREVIA — Security, Privacy and Governance Review
**Stage:** 12 — Collaborative Agricultural Intelligence  
**Focus:** Boundary Enforcement, Purpose Consent, Tenant Isolation, and Collective Anonymity

---

## 1. Access Control & Authorization Boundaries

1. **Expert Badge Security:**
   - Expert replies and review actions check that the user's role is `AGRICULTURAL_EXPERT` and that a corresponding active `ExpertProfile` exists.
   - Users cannot grant themselves expert badges or review knowledge contributions through simple profile edits.
2. **FPO & Collective Tenant Isolation:**
   - An organization administrator cannot access a member farmer's private plot boundaries, soil sensor streams, or financial ledgers without explicit, legally documented data sharing consents.
   - Cross-organization queries return HTTP 403 Forbidden.

---

## 2. Privacy-Preserving Regional Aggregation Safeguards

1. **Minimum Sample Size Gate:**
   - Aggregation algorithms suppress any regional signal or collective statistic if fewer than 3 independent farms (for regional pulse) or fewer than 5 farms (for collective analytics) are present.
2. **Zero Coordinate Exposure:**
   - Regional maps and public summaries render at the Mandal or District centroid level, completely omitting exact farm boundaries or farmer legal identities.

---

## 3. Purpose-Specific Research Consent Architecture

- Operational farm usage permissions **never** substitute for research consent.
- Farmers must explicitly sign a `ResearchConsent` granting rights to specific data categories (e.g. `ANNOTATED_IMAGES` or `SENSOR_DATA`).
- Revocation takes effect immediately for future dataset versions.
