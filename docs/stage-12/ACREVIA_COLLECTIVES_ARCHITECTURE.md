# ACREVIA — Collectives Architecture (FPO & Cooperative Workspaces)
**Subsystem:** Pillar C — ACREVIA Collectives  
**Primary Objective:** Governed private workspaces for Farmer Producer Organizations (FPOs), primary cooperatives, and farmer groups.

---

## 1. Domain Purpose & Operational Scope

Farmer collectives in Telangana (e.g. Cotton & Chilli FPOs in Warangal, Khammam, and Nalgonda) require coordination tools for input procurement, collective training, shared crop calendar tracking, and aggregated production planning.

### Permitted Collective Activities:
- **Shared Crop Planning:** Aligning sowing windows and harvesting timelines across member plots.
- **Collective Training:** Organizing extension workshops, field demonstrations, and expert webinars.
- **Resource Coordination:** Coordinating machinery hire (tractors, mechanical sprayers, combined harvesters).
- **Aggregated Analytics:** Visualizing total acreage, crop distribution, and harvest projections across consenting members.

### Out of Scope (Stage 12 Boundary):
- Direct financial lending, money pooling, or peer-to-peer loan handling.
- Automated commercial purchase/sale agreements.

---

## 2. Organization Verification Lifecycle

```
[Application Submitted] ──> [Under Review (Govt/ROC Docs)] ──> [Approved (Verified FPO)]
                                  │
                                  ├──> [Rejected (Invalid Credentials)]
                                  └──> [Suspended (Governance Breach)]
```

Only verified organizations display the official `VERIFIED_ORGANIZATION` badge. Unverified groups operate in informal collaborative mode without institutional trust claims.

---

## 3. Privacy-Preserving Collective Farm Intelligence

Collectives operate under strict tenant isolation rules:

| Individual Farm Data | Default Group Visibility | Authorized Aggregated View |
| :--- | :---: | :---: |
| **Farmer Legal Name & Phone** | Restricted to Org Admins | Redacted in General Reports |
| **Private Financial Ledgers & Receipts** | **STRICTLY PRIVATE (HIDDEN)** | **NEVER EXPOSED TO COLLECTIVE** |
| **Exact Plot Geometry & Boundary GPS** | **STRICTLY PRIVATE (HIDDEN)** | Only Village / Mandal centroid |
| **Crop Diagnoses & Health Scans** | **STRICTLY PRIVATE (HIDDEN)** | Anonymized symptom counts |
| **Total Crop Acreage** | Hidden per farmer | **Aggregated Cohort Sum (Cohort $\ge 5$)** |
| **Harvest Yield Projections** | Hidden per farmer | **Aggregated Cohort Sum (Cohort $\ge 5$)** |

### Minimum Cohort Size Rule ($N \ge 5$):
To prevent reverse-identification of individual farmers in small communities, aggregate statistics (total acreage, projected harvest, input requirements) are suppressed unless at least 5 distinct member farms are represented.
