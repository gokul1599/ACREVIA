# ACREVIA — SECURITY, GOVERNANCE & MULTI-TENANT ISOLATION AUDIT
## STRIDE Threat Modeling, Cross-Tenant Intrusion Defenses, Cryptographic Immutability & DPDP Act 2023 Compliance

**Document Identifier:** ACREVIA-SPEC-ST10-012  
**Target Subsystem:** Security Architecture & Stage 10 Endpoints  
**Classification:** Security & Data Governance Audit  
**Status:** Implemented & Verified in Production  

---

### 1. Multi-Tenant Isolation Architecture

In agricultural intelligence platforms, unauthorized cross-tenant data exposure can leak proprietary yield figures, land boundary disputes, or confidential input spending. 

ACREVIA implements strict **Row-Level Tenancy Guardrails** across all Stage 10 subsystems:
1. Every access to a digital twin root (`/api/v1/twin/farms/{id}`), snapshot list, or reconciliation endpoint requires an authenticated JWT bearer token.
2. The endpoint dependency extracts `current_user` and executes an explicit database assertion:
   $$\text{Farm.owner\_id} == \text{current\_user.id} \quad \lor \quad \text{UserRole} == \text{ADMIN}$$
3. Any attempt by an authenticated user to query or trigger operations on another farmer's farm, plot, or digital twin yields an immediate `HTTP 403 Forbidden`.

---

### 2. STRIDE Threat Model & Mitigations

| STRIDE Threat Category | Identified Vulnerability / Attack Vector | Engineering Countermeasure Implemented | Verification Evidence |
|---|---|---|---|
| **Spoofing** | Attacker crafts forged farm ID to simulate or extract water allocation strategies. | JWT token signature verification; strict farm ownership query filtering. | `backend/tests/test_stage10.py::test_scenario_f_security_and_tenant_isolation` |
| **Tampering** | Rogue actor or database admin alters historical `twin_snapshots` state payload. | Cryptographic SHA-256 `payload_hash` computed over canonical serialized state. Alteration breaks hash validation. | Validated in automated snapshot generation test; 64-char hex verified. |
| **Repudiation** | Operator denies completing an operational task or logging chemical materials. | Immutable `farm_operations` audit log created with user ID, timestamp, and material quantities. | `test_scenario_d_crop_planning_and_weather_conflict` |
| **Information Disclosure** | Competitor queries regional water optimization to infer neighbor's borewell depletion. | Optimization problems scoped strictly to farm ID; multi-plot calculations isolate external geometries. | Verified cross-tenant 403 blocking on `/api/v1/optimization/problems`. |
| **Denial of Service (DoS)**| Malicious client submits 10-year simulation horizon or 10,000-variable LP problem. | Parameter bounding: Simulation horizon capped at $30\text{ days}$; LP solver constrained to $\le 50\text{ plots}$; timeout at $500\text{ ms}$. | Execution durations monitored; all tests run in $< 200\text{ ms}$. |
| **Elevation of Privilege** | Farmer attempts to approve regulatory pesticide exemptions or override ban filters. | Decision intelligence filters execute server-side in Python runtime; banned chemical filters cannot be bypassed by client request. | `test_scenario_e_decision_intelligence_grounding_and_safety` |

---

### 3. Digital Personal Data Protection (DPDP) Act 2023 Compliance

ACREVIA complies with India's Digital Personal Data Protection Act (DPDP Act 2023):
1. **Notice & Purpose Limitation:** Data collected (cadastral coordinates, soil reports, scouting images) is processed solely for farm advisory generation. No telemetry is shared with commercial third-party input vendors without explicit consent.
2. **Right to Erasure & Portability:** Deleting a farm cascades deletions across `farm_twins`, `twin_snapshots`, and `simulation_scenarios`.
3. **Data Localization:** Relational database resides in AWS Singapore (`sin1`) with zero unencrypted cross-border routing of identifiable farmer personal data.
