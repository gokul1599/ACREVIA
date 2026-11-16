# ACREVIA — PHASE 07: VERIFIED ADVISORY AUTHENTICITY, INDEPENDENT EXPERT REVIEW, SOURCE COUNT DERIVATION & SERVICE-LEVEL AUTHORITY FINAL ASSURANCE AUDIT

**Programme:** ACREVIA — Agricultural Intelligence Platform  
**Target Geography:** Telangana, India  
**Target Phase:** Phase 07 — PostgreSQL RLS Tenant Isolation & Regional Aggregation Privacy  
**Execution Mode:** `MODE A ONLY` (Local Source Inspection, Security Engineering, Concurrency Analysis & Offline Verification)  
**Engineering Methodology:** Everything Claude Code (ECC): `PLAN → TEST → IMPLEMENT ONLY IF DEFECT PROVEN → REVIEW → VERIFY → DOCUMENT`  
**Reported Git HEAD:** `dbad296c6f19c4bbe8eb48fcd7a0e07441cfa408` on branch `main`  
**Public Repository:** `https://github.com/gokul1599/ACREVIA`  
**Document ID:** `ACR-SEC-P07-ADVISORY-EXPERT-COUNT-AUDIT`  
**Document Classification:** RESTRICTED — PILOT DATA PRIVACY & ACCESS CONTROL ASSURANCE  
**Overall Engineering Determination:** **`TECHNICAL_PREFLIGHT_READY_WITH_RECORDED_BLOCKERS`**  
**Repository Document Status:** `LOCAL_UNCOMMITTED_ASSURANCE_ARTIFACT` (Mode A prohibits commit/push)

---

## 1. Executive Determination

ACREVIA Phase 07 has attained the defensible engineering determination of:

$$\mathbf{TECHNICAL\_PREFLIGHT\_READY\_WITH\_RECORDED\_BLOCKERS}$$

### Justification:
An adversarial security audit across the ACREVIA Regional Pulse authority, source authenticity, observation measurement, and transaction lifecycle revealed four critical findings:
1. **Service-Level Authority Bypass on Optional Context (`SERVICE-AUTH-01`):** In the service implementation, role checks were conditioned on `if actor_roles is not None:`. Consequently, direct service callers passing `actor_roles=None` bypassed `OFFICIAL_ADVISORY` administrative role restrictions and were automatically granted `validation_status="EXPERT_CONFIRMED"` on `EXPERT_REVIEWED` signals. This defect was reproduced via a failing test and corrected to enforce fail-closed authorization (`effective_roles = actor_roles if actor_roles is not None else []`).
2. **Client-Controlled Source Observation Count Inflation (`COUNT-INTEG-02`):** Previously, `final_source_obs_count = max(data.source_observation_count, final_distinct_count)` allowed a client to link 3 verified observations but supply `source_observation_count = 999999`, storing an inflated, unverified count in the database. This defect was reproduced and corrected: `source_observation_count` is now server-derived strictly from the count of unique, validated evidence records (`len(valid_evidences_to_persist)`), or 0 for unlinked official advisories.
3. **Official Advisory Authenticity vs. Platform Administrator Authorization (`OFFICIAL-SOURCE-01`):** An `ADMIN`-created `OFFICIAL_ADVISORY` currently represents internal platform administrative authorization (`PLATFORM_ADMIN_AUTHORED`). The platform contains zero automated integrations with Telangana government gazettes, agricultural department APIs, or signed document registries. The external official source is classified as `OFFICIAL_SOURCE_NOT_INDEPENDENTLY_VERIFIED`.
4. **Expert Self-Certification & Review State Restriction (`EXPERT-REVIEW-01`):** An `AGRICULTURAL_EXPERT` authoring a signal immediately assigns `EXPERT_CONFIRMED` upon creation (self-certification with zero independent review event). A `RESEARCHER` draft is assigned `UNVALIDATED_OBSERVATION`. However, `recover_suppressed_signal` strictly requires `SUPPRESSED_INSUFFICIENT_PROVENANCE` and rejects `UNVALIDATED_OBSERVATION` with `HTTP 400 Bad Request`. There is currently no endpoint to promote an unvalidated researcher signal to expert-confirmed status.

All proven defects have been corrected locally and verified across **144 passing Phase 07 tests** (standard and Python `-O` optimized mode) and **6 passing Stage 12 tests**. Phase 07 remains held from release pending formal Project Owner authorization of Decision Gates 02 through 05.

---

## 2. Local Git Baseline and Working-Tree State

The local Git repository environment was independently verified under `MODE A`:

```powershell
git rev-parse HEAD
# Output: dbad296c6f19c4bbe8eb48fcd7a0e07441cfa408

git branch --show-current
# Output: main

git status --short --branch
# Output:
# ## main
#  M backend/app/api/v1/endpoints/regional_pulse.py
#  M backend/app/schemas/regional_pulse.py
#  M backend/app/services/regional_pulse_service.py
#  M backend/tests/test_worker_security_and_privacy.py
#  M docs/pilot/security/PHASE_07_FINAL_TECHNICAL_PREFLIGHT_STATUS.md
#  M docs/pilot/security/PHASE_07_REGIONAL_AGGREGATION_PROVENANCE_AUDIT.md
# ?? docs/pilot/security/phase_07_regional_pulse_author_content_evidence_privacy_and_inference_final_audit.md
# ?? docs/pilot/security/phase_07_regional_pulse_complete_response_surface_privacy_and_routing_final_audit.md
# ?? docs/pilot/security/phase_07_regional_pulse_public_get_read_routing_cache_and_privacy_final_audit.md
# ?? docs/pilot/security/phase_07_regional_signal_authority_claim_provenance_and_creation_transaction_final_audit.md
# ?? docs/pilot/security/phase_07_regional_signal_official_source_expert_review_count_and_retry_final_audit.md
```

`git diff --cached --stat` confirms that no changes are staged for commit, preserving strict `MODE A` boundaries.

---

## 3. Public-versus-Local Implementation Comparison

| Finding / Feature | Public Baseline (`dbad296`) | Local Implementation | Local Test Evidence | Commit Status |
| :--- | :--- | :--- | :--- | :--- |
| **Role-based creation (`AUTH-AGG-01`)** | Authenticated only (`get_current_user`) | `require_roles(ADMIN, AGRICULTURAL_EXPERT, RESEARCHER)` | `test_regional_pulse_signal_creation_authorization_and_evidence_masking` | `CORRECTED_LOCALLY_UNCOMMITTED` |
| **Validated evidence persistence (`RES-EVIDENCE-PERSISTENCE-01`)** | Raw payload dicts inserted unconditionally | Validates active farm, district, and time window; collects `valid_evidences_to_persist` | `test_regional_pulse_invalid_evidence_persistence_defect` | `CORRECTED_LOCALLY_UNCOMMITTED` |
| **Evidence deduplication** | Duplicates inserted as separate DB rows | Deduplicated by `(evidence_type, evidence_reference_id)` | `test_regional_pulse_invalid_evidence_persistence_defect` | `CORRECTED_LOCALLY_UNCOMMITTED` |
| **Confidence authority (`AUTH-CLAIM-01`)** | Any user could assert any tier | `OFFICIAL_ADVISORY` requires `ADMIN`; `EXPERT_REVIEWED` adjudicated by role | `test_regional_pulse_complete_role_authority_matrix` | `CORRECTED_LOCALLY_UNCOMMITTED` |
| **Service-level authority (`SERVICE-AUTH-01`)** | `actor_roles=None` bypassed checks and granted `EXPERT_CONFIRMED` | Fail-closed: `effective_roles = actor_roles or []`; missing roles raises 403 on official, unvalidated on expert | `test_regional_pulse_service_auth_fail_closed_when_actor_roles_none` | `CORRECTED_LOCALLY_UNCOMMITTED` |
| **Expert-review workflow (`EXPERT-REVIEW-01`)** | Single expert self-certifies upon creation; `/recover` rejects unvalidated | Identified and preserved: expert self-certifies at creation; `/recover` requires `SUPPRESSED` | `test_regional_pulse_expert_review_self_certification_and_recovery_gap` | `VERIFIED_IN_SOURCE` / `OWNER_ACCEPTANCE_REQUIRED` |
| **Source-count derivation (`COUNT-INTEG-02`)** | Client could submit 0 or 999999 | Server-derived strictly as `len(valid_evidences_to_persist)` | `test_regional_pulse_source_observation_count_adversarial_derivation_matrix` | `CORRECTED_LOCALLY_UNCOMMITTED` |
| **Evidence-type crosswalk** | Inconsistent strings (`OBSERVATION` vs `OBSERVATION_REF`) | Normalizes aliases (`OBSERVATION` -> `OBSERVATION_REF`, `RISKCAST_ALERT` -> `RISK_ALERT`) | `test_regional_pulse_evidence_type_crosswalk_and_alias_normalization` | `CORRECTED_LOCALLY_UNCOMMITTED` |
| **Transaction ownership (`TX-OWN-01`)** | Service unilaterally committed DB transaction | Endpoint owns transaction; pre-validates response model before commit; atomic `AuditLog` | `test_regional_pulse_creation_transaction_atomicity_and_audit` | `CORRECTED_LOCALLY_UNCOMMITTED` |
| **Official advisory RLS compatibility** | Static DDL required $N \ge 3$ with no official exemption | Inspected: Farmers cannot read $N=0$ advisories under generated SQL DDL | `test_regional_pulse_static_rls_ddl_zero_telemetry_official_advisory_inspection` | `STATIC_DDL_EXEMPTION_ABSENT` |

---

## 4. Signal Creation Authority Model

The platform enforces layered authority checks across route and service layers:

```mermaid
flowchart TD
    Req[Client HTTP POST /signals] --> Gate[FastAPI require_roles Gate]
    Gate -->|FARMER| Deny403[HTTP 403 Forbidden]
    Gate -->|RESEARCHER / EXPERT / ADMIN| Svc[RegionalPulseService.aggregate_regional_signal]
    Svc --> AuthCheck{Check confidence_tier}
    AuthCheck -->|OFFICIAL_ADVISORY| AdminCheck{ADMIN in effective_roles?}
    AdminCheck -->|No / actor_roles=None| DenyOff[HTTP 403 Forbidden]
    AdminCheck -->|Yes| SetOff[validation_status = OFFICIAL_ALERT]
    AuthCheck -->|EXPERT_REVIEWED| ExpCheck{EXPERT or ADMIN in effective_roles?}
    ExpCheck -->|No / actor_roles=None| SetUnval[validation_status = UNVALIDATED_OBSERVATION]
    ExpCheck -->|Yes| SetConf[validation_status = EXPERT_CONFIRMED (Self-Certified)]
    AuthCheck -->|FARMER_REPORT / Other| SetObs[validation_status = UNVALIDATED_OBSERVATION]
    SetOff --> EvCheck{Evidence Validation}
    SetUnval --> EvCheck
    SetConf --> EvCheck
    SetObs --> EvCheck
    EvCheck --> CountDeriv[Derive source_observation_count = len(valid_evidences)]
```

---

## 5. Official Advisory Authenticity Analysis (OFFICIAL-SOURCE-01)

### 5.1 Internal Authority vs External Authenticity
A fundamental distinction exists between:
1. **Platform Administrator Authorization:** An authenticated user possessing the `ADMIN` role is permitted by application logic to publish a regional alert without plot telemetry ($N=0$).
2. **Official Source Authenticity:** The alert is cryptographically signed, traced to a recognized state agency (e.g., Telangana Department of Agriculture), or linked to an immutable gazette publication.

### 5.2 Technical Audit Findings
- **Data Model Audit:** `RegionalSignal` has zero fields for `issuing_agency`, `source_document_url`, `gazette_reference_id`, or `document_hash`.
- **Integration Audit:** Zero external APIs or digital signature verification services are integrated.
- **Classification:** An `ADMIN`-created advisory is strictly **`PLATFORM_ADMIN_AUTHORED`**. External source provenance is **`OFFICIAL_SOURCE_NOT_INDEPENDENTLY_VERIFIED`**.

---

## 6. ADMIN Publication Limitations

1. **Unverified External Content:** An ADMIN may enter arbitrary text claiming a state alert. The platform provides no automated verification of this claim.
2. **Zero-Telemetry Exemption Risk:** Permitting an official advisory with $N=0$ bypasses the mathematical anonymity barrier ($N \ge 3$). While necessary for state alerts that apply broadly across a district, this power is held exclusively by administrators and recorded in `AuditLog`.

---

## 7. Expert Creator-versus-Reviewer Separation (EXPERT-REVIEW-01)

### 7.1 Self-Certification at Creation
When an `AGRICULTURAL_EXPERT` creates a signal requesting `confidence_tier="EXPERT_REVIEWED"`, the service assigns `validation_status="EXPERT_CONFIRMED"` immediately in the creation turn. The creator and reviewer are the same authenticated user. There is no independent review event or second-party verification.

### 7.2 Researcher Draft Promotion Gap
When a `RESEARCHER` creates an `EXPERT_REVIEWED` signal, the service downgrades it to `UNVALIDATED_OBSERVATION`. However, if an Agricultural Expert subsequently attempts to review and approve this signal using the existing recovery endpoint (`POST /signals/{id}/recover`), the endpoint rejects the request:
```python
if signal.validation_status != "SUPPRESSED_INSUFFICIENT_PROVENANCE":
    raise HTTPException(status_code=400, detail=f"Signal is not suppressed (current status: {signal.validation_status})")
```
The platform currently lacks an agronomic peer review endpoint to transition `UNVALIDATED_OBSERVATION` signals to `EXPERT_CONFIRMED`.

---

## 8. Review Event and Audit Provenance

| Action | Current Endpoint | Actor Logged | Review Event Stored? | State Transition Supported |
| :--- | :--- | :--- | :---: | :--- |
| **Signal Creation** | `POST /signals` | `current_user.id` | No (Creation Turn) | `NEW` $\rightarrow$ `EXPERT_CONFIRMED` / `UNVALIDATED_OBSERVATION` |
| **Signal Recovery** | `POST /signals/{id}/recover` | `current_user.id` | Yes (`AuditLog`) | `SUPPRESSED_INSUFFICIENT_PROVENANCE` $\rightarrow$ `EXPERT_CONFIRMED` |
| **Researcher Signal Review** | *None* | *None* | *None* | `UNVALIDATED_OBSERVATION` $\rightarrow$ `EXPERT_CONFIRMED` (**Not Supported**) |

---

## 9. Service Actor-Context Inventory

All invocation sites of `RegionalPulseService.aggregate_regional_signal` were audited:

| Caller Location | Actor ID Source | Role Source | `actor_roles` Passed | Commit Behavior | Notes |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `regional_pulse.py:41` | `current_user.id` | `current_user.roles` | Explicit list | `auto_commit=False` | FastAPI endpoint; owns commit |
| `test_worker_security_and_privacy.py:606` | None | None | None | `auto_commit=True` | Tests invalid payload rejection |
| `test_worker_security_and_privacy.py:628` | None | None | None | `auto_commit=True` | Tests evidence masking |
| `test_worker_security_and_privacy.py:778-862`| None | None | None | `auto_commit=True` | Tests threshold edge cases |
| `test_worker_security_and_privacy.py:5779` | None | None | None | `auto_commit=True` | Tests evidence exclusion |
| `test_worker_security_and_privacy.py:6023` | None | None | None | `auto_commit=True` | Tests recommendation sanitization |
| `test_worker_security_and_privacy.py:6150` | None | None | None | `auto_commit=True` | Tests count derivation |
| `test_worker_security_and_privacy.py:6410` | None | None | Explicit `None` | `auto_commit=True` | Proves fail-closed rejection |

---

## 10. Service Optional-Parameter Bypass Analysis (SERVICE-AUTH-01)

### 10.1 Proven Defect
In the previous baseline:
```python
if actor_roles is not None:
    if data.confidence_tier == "OFFICIAL_ADVISORY" and "ADMIN" not in actor_roles:
        raise HTTPException(...)
```
When `actor_roles=None` was passed, the condition evaluated to `False`. The check was skipped, allowing any internal caller to create an `OFFICIAL_ADVISORY` with `validation_status="OFFICIAL_ALERT"`. Furthermore, `EXPERT_REVIEWED` defaulted to `EXPERT_CONFIRMED`.

### 10.2 Implemented Correction
`RegionalPulseService.aggregate_regional_signal` now enforces fail-closed semantics:
```python
effective_roles = actor_roles if actor_roles is not None else []
if data.confidence_tier == "OFFICIAL_ADVISORY" and "ADMIN" not in effective_roles:
    raise HTTPException(status_code=403, detail="...")
```
If `actor_roles` is omitted or empty, `OFFICIAL_ADVISORY` is rejected with `HTTP 403`, and `EXPERT_REVIEWED` defaults to `UNVALIDATED_OBSERVATION`. Verified by `test_regional_pulse_service_auth_fail_closed_when_actor_roles_none`.

---

## 11. Source-Observation-Count Measurement Contract (COUNT-INTEG-02)

### 11.1 Measurement Contract Definition
- **`distinct_farms_count`**: The number of distinct, verified, active farms contributing telemetry ($N \ge 3$).
- **`source_observation_count`**: The number of unique, verified evidence records (individual `Observation` and `RiskAlert` entities) supporting the signal.

### 11.2 Proven Defect & Server Derivation
Previously, `final_source_obs_count = max(data.source_observation_count, final_distinct_count)` allowed clients to submit arbitrary numbers (e.g. 999999) that were persisted directly.
The service now derives the count strictly from verified evidence:
```python
if valid_evidences_to_persist:
    final_source_obs_count = len(valid_evidences_to_persist)
else:
    final_source_obs_count = 0
```

### 11.3 Adversarial Test Matrix Verification

| Verified Source Data | Client Count | Derived Server Count | Verification Result |
| :--- | :---: | :---: | :--- |
| 3 distinct observations | 0 | **3** | Pass (Client under-count corrected) |
| 3 distinct observations | 100 | **3** | Pass (Client inflation corrected) |
| 3 distinct observations | 999999 | **3** | Pass (Client inflation corrected) |
| 6 observations across 3 farms | 1 | **6** | Pass ($N=3$ distinct farms, 6 obs) |
| 3 observations and 2 RiskAlerts | 1 | **5** | Pass ($N=3$ distinct farms, 5 evidences) |
| Duplicate references to 1 observation | 20 | **3** | Pass (Duplicates deduplicated) |
| Official advisory without telemetry | 0 | **0** | Pass ($N=0$, 0 observations) |

---

## 12. Distinct-Farm Count Verification

- Strictly server-calculated as `len(verified_farm_ids)`.
- Client-supplied `distinct_farms_count` is unconditionally ignored.
- Unlinked requests claiming $N \ge 3$ without evidence records are rejected with `HTTP 400 Bad Request`.

---

## 13. Evidence-Type Crosswalk

| API Evidence Type | Service Accepted | Mapped ORM Model | Persistence Label | Revalidation Support |
| :--- | :---: | :--- | :--- | :---: |
| `OBSERVATION` | **Yes** | `backend.app.models.observation.Observation` | `OBSERVATION_REF` | **Yes** |
| `OBSERVATION_REF` | **Yes** | `backend.app.models.observation.Observation` | `OBSERVATION_REF` | **Yes** |
| `RISK_ALERT` | **Yes** | `backend.app.models.risk_alert.RiskAlert` | `RISK_ALERT` | **Yes** |
| `RISKCAST_ALERT` | **Yes** | `backend.app.models.risk_alert.RiskAlert` | `RISK_ALERT` | **Yes** |
| `UNKNOWN_TYPE` | **No** (Excluded) | None | *Not Persisted* | N/A |

---

## 14. Official Advisory Zero-Evidence RLS Compatibility

### 14.1 Static DDL Inspection
Inspection of generated PostgreSQL RLS SQL DDL from `backend/app/database/rls.py` (`generate_rls_ddl("regional_signals", TableCategory.COMMUNITY_COLLABORATIVE)`) reveals:
```sql
CREATE POLICY regional_signals_select_policy ON regional_signals
FOR SELECT USING (
    (current_setting('app.is_admin', true) = 'true')
    OR (
        distinct_farms_count >= 3
        AND validation_status != 'SUSPENDED'
    )
);
```

### 14.2 Impact Assessment
- **Farmer Readability:** Under this PostgreSQL kernel policy, any official advisory published with `distinct_farms_count = 0` **cannot be read by FARMER users** (`0 >= 3` evaluates to `False`).
- **Classification:** **`STATIC_DDL_EXEMPTION_ABSENT`**.
- **Action Required:** An explicit exemption predicate for `validation_status = 'OFFICIAL_ALERT'` in `rls.py` requires formal Project Owner authorization before DDL modification (`OWNER_ACCEPTANCE_REQUIRED`).

---

## 15. Transaction Ownership and Auto-Commit Analysis

1. **Endpoint Ownership:** In `backend/app/api/v1/endpoints/regional_pulse.py:41`, `aggregate_regional_signal` is called with `auto_commit=False`.
2. **Pre-Commit Validation:** The endpoint executes `RegionalSignalResponse.model_validate(signal)` **prior** to `db.commit()`. If validation fails, `db.rollback()` executes, guaranteeing zero partial or unvalidated rows persist.
3. **Atomic Audit Staging:** The `AuditLog` entry is staged within the caller's transaction session via `AuditService.stage_activity`, committing or rolling back in the same atomic unit as the signal and its evidences.

---

## 16. Post-Commit Failure and Retry Behavior (RETRY-SAFETY-01)

### 16.1 Post-Commit Failure Windows
If a network disconnect, client timeout, or JSON streaming error occurs **after** `db.commit()` has executed:
- The signal and evidences remain durably persisted in the database.
- The client receives an error or dropped connection.

### 16.2 Retry Behavior
Currently, `POST /api/v1/regional-pulse/signals` does not support client-supplied idempotency keys. A retry will generate a new signal with a distinct UUID. This is classified as **`RETRY_SAFETY_NOT_IDEMPOTENT`** and preserved under `RETRY-SAFETY-01`.

---

## 17. Concurrency Considerations

- **Deadlock Elimination:** Signal evidence and farm verification follow strict ascending ID lock ordering during recovery.
- **Race Condition Safety:** If evidence is mutated or archived after signal creation, the public GET read path invokes `revalidate_signal_provenance`, suppressing the signal if verified distinct farms drops below 3.

---

## 18. Exact Test Execution Results

### 18.1 Phase 07 Full Selection (5 Files)
```powershell
python -m pytest backend/tests/test_target_validation.py backend/tests/test_rls_offline_ddl.py backend/tests/test_rls_policy_semantics.py backend/tests/test_orm_rls_alignment.py backend/tests/test_worker_security_and_privacy.py -q
```
- **Exit Code:** `0`
- **Collected:** `144`
- **Passed:** `144` (100%)
- **Failed:** `0`
- **Warnings:** `1` (`StarletteDeprecationWarning`)
- **Duration:** `24.38s`

### 18.2 Python Optimized Mode (`python -O`)
```powershell
python -O -m pytest backend/tests/test_target_validation.py backend/tests/test_rls_offline_ddl.py backend/tests/test_rls_policy_semantics.py backend/tests/test_orm_rls_alignment.py backend/tests/test_worker_security_and_privacy.py -q
```
- **Exit Code:** `0`
- **Passed:** `144`
- **Warnings:** `2`
- **Duration:** `26.95s` (Proving zero authorization gates rely on Python `assert`)

### 18.3 Stage 12 End-to-End Suite
```powershell
python -m pytest backend/tests/test_stage12.py -q
```
- **Exit Code:** `0`
- **Passed:** `6`
- **Duration:** `38.63s`

---

## 19. ECC Reviewer Findings

1. **Security Reviewer (`security-reviewer`):**  
   - *Finding:* Omitting `actor_roles` allowed bypass of `OFFICIAL_ADVISORY` administrative restrictions.  
   - *Resolution:* Enforced fail-closed `effective_roles` defaulting to empty list; raises 403 on official advisory and sets unvalidated on expert review.
2. **Database Reviewer (`database-reviewer`):**  
   - *Finding:* Client-supplied counts allowed unverified count inflation.  
   - *Resolution:* Derived count strictly as `len(valid_evidences_to_persist)`.
3. **FastAPI Reviewer (`fastapi-reviewer`):**  
   - *Finding:* Inconsistent evidence types between schemas and service.  
   - *Resolution:* Supported aliases (`OBSERVATION`, `RISKCAST_ALERT`) and normalized persistence labels.
4. **Silent-Failure Hunter (`silent-failure-hunter`):**  
   - *Finding:* Recovery endpoint strictly requires `SUPPRESSED` and rejects `UNVALIDATED` researcher drafts with 400.  
   - *Resolution:* Documented workflow gap and preserved under `EXPERT-REVIEW-01`.

---

## 20. Conditional Corrections and Changed Files

| File Path | Nature of Modification |
| :--- | :--- |
| `backend/app/services/regional_pulse_service.py` | Added fail-closed `effective_roles` check; derived `source_observation_count` from valid evidences; normalized evidence types; added alias support in revalidation and recovery. |
| `backend/tests/test_worker_security_and_privacy.py` | Added 6 new unit tests verifying fail-closed authority, adversarial count matrix, expert self-certification, official source absence, evidence crosswalk, and static RLS inspection. |

---

## 21. Residual Risk Register

| Risk ID | Title | Severity | Nature & Residual Exposure | Required Resolution |
| :--- | :--- | :--- | :--- | :--- |
| **`RES-PULSE-01`** | Role-Global Evidence Access | Medium | Experts/researchers can query evidence across all Telangana districts without local assignment. | Owner risk acceptance. |
| **`RES-PULSE-02`** | READ COMMITTED Snapshot Divergence | Medium | Multi-statement GET requests inspect distinct database snapshots. | Owner risk acceptance. |
| **`RES-PRIMARY-ROUTING-01`** | Primary-Only Write-on-Read Dependency | Medium | Standby routing triggers SQLSTATE 25006 on dynamic provenance update. | Ingress routing to primary. |
| **`RES-REPLICA-LAG-01`** | Standby Replication Lag Staleness | Medium | Standby replicas may serve stale signals without triggering write-on-read. | Ingress routing to primary. |
| **`RES-FREE-TEXT-01`** | Author Free-Text PII Exposure | Medium | Public text fields lack automated PII redaction. | Author guidelines and manual review. |
| **`RES-EVIDENCE-NOTE-01`** | Privileged Evidence-Note Visibility | Low | `evidence_notes` visible to all experts and researchers globally. Masked for farmers. | Documented requirement. |
| **`OFFICIAL-SOURCE-01`** | External Official Source Unverified | High | Official advisories represent admin authorship; no external state verification exists. | Document as `PLATFORM_ADMIN_AUTHORED`. |
| **`EXPERT-REVIEW-01`** | Expert Self-Certification & Review Gap | Medium | Experts self-certify upon creation; researcher drafts cannot be approved via `/recover`. | Design peer-review endpoint. |
| **`RETRY-SAFETY-01`** | Non-Idempotent Signal Creation | Low | Post-commit connection drops retry with new UUID. | Design idempotency header/table. |

---

## 22. Governance Blocker Register

The 6 core governance blockers remain active, preserved, and unbypassed:

| Blocker ID | Severity | Description | Current Release Limitation |
| :--- | :--- | :--- | :--- |
| **`OWNER-AUTH-01`** | **CRITICAL** | Decision Gates 02 through 05 in [`PHASE_07_OWNER_AUTHORIZATION_AND_EXECUTION_REGISTER.md`](file:///c:/Users/gokul/OneDrive/Documents/projects/docs/pilot/security/PHASE_07_OWNER_AUTHORIZATION_AND_EXECUTION_REGISTER.md) are unapproved. | Full release blocked pending formal Owner sign-off. |
| **`DB-RLS-01`** | **HIGH** | Physical PostgreSQL Row-Level Security not verified on live database engine. | Blocked pending Gate 03/04 execution on Neon staging. |
| **`WRK-DISP-01`** | **HIGH** | Production worker task dispatch provider is `NOT_IMPLEMENTED` and fails closed (`DISPATCH_NOT_CONFIGURED`). | Blocked pending external authenticated task broker. |
| **`RES-PULSE-01`** | **MEDIUM** | Role-global evidence access for experts/researchers without district scoping. | Requires formal Owner risk acceptance. |
| **`RES-PULSE-02`** | **MEDIUM** | READ COMMITTED snapshot divergence on public GET requests. | Requires formal Owner risk acceptance. |
| **`GATE01-PROV-01`** | **MEDIUM** | Staging branch recorded provisioned cannot be independently verified via live cloud API in Mode A. | Verification upon transition to Mode B. |

---

## 23. Explicit MODE A Confirmation

- **Operating Boundary:** `MODE A ONLY` was strictly maintained throughout this audit.
- **Remote Operations:** Zero live remote database connections, zero Neon API calls, zero staging migrations, zero role provisioning, and zero cloud mutations occurred.
- **Git Safeguards:** Zero commits, zero pushes, zero branch switching, and zero resets were executed. All modifications are preserved locally in the active working tree.

---

## 24. Final Assurance Answers to the 21 Audit Inquiries

### Authority and Authenticity
1. **Can an ADMIN-created official advisory be traced to an independently verifiable official source?**  
   **`NO`** | **`OFFICIAL_SOURCE_NOT_INDEPENDENTLY_VERIFIED`**, **`VERIFIED_IN_SOURCE`**  
   The platform lacks any external integration, gazette registry, or digital signature linking the advisory to the Government of Telangana.
2. **Is ADMIN authorization being confused with external source authenticity?**  
   **`YES` (in product documentation)** | **`VERIFIED_IN_SOURCE`**  
   The system verifies that the caller has the `ADMIN` role, which proves internal platform permission, not external government authenticity.
3. **Can an AGRICULTURAL_EXPERT create and self-certify an expert-reviewed signal in one request?**  
   **`YES`** | **`VERIFIED_IN_SOURCE`**, **`VERIFIED_BY_OFFLINE_TEST`**  
   When an Agricultural Expert authors an `EXPERT_REVIEWED` signal, it is immediately set to `EXPERT_CONFIRMED` upon creation turn by the author themselves.
4. **Is a review event separately recorded with an authenticated reviewer identity?**  
   **`NO` (at creation turn)** | **`VERIFIED_IN_SOURCE`**  
   The creation turn logs the author as the actor in `AuditLog`. No separate reviewer entity or review timestamp is stored.
5. **Can a researcher create a draft that later undergoes a genuine independent expert review?**  
   **`NO` (currently blocked by workflow gap)** | **`VERIFIED_IN_SOURCE`**, **`VERIFIED_BY_OFFLINE_TEST`**  
   Researcher drafts are saved as `UNVALIDATED_OBSERVATION`, but no endpoint exists to promote them to `EXPERT_CONFIRMED`.
6. **Does the recovery endpoint actually support the review transition claimed by the report?**  
   **`NO`** | **`VERIFIED_IN_SOURCE`**, **`VERIFIED_BY_OFFLINE_TEST`**  
   `POST /signals/{id}/recover` explicitly rejects `UNVALIDATED_OBSERVATION` with `HTTP 400 Bad Request`. It only accepts `SUPPRESSED_INSUFFICIENT_PROVENANCE`.

### Service-Level Authority
7. **Can a direct service caller omit `actor_roles` and bypass a privileged claim check?**  
   **`NO` (Post-Correction)** | **`CORRECTED_LOCALLY_UNCOMMITTED`**, **`VERIFIED_BY_OFFLINE_TEST`**  
   Omitting `actor_roles` now defaults to `effective_roles = []`, failing closed with HTTP 403 on official advisories and `UNVALIDATED_OBSERVATION` on expert reviews.
8. **Can a caller provide a forged role list?**  
   **`NO` (via HTTP API)** | **`VERIFIED_IN_SOURCE`**  
   The FastAPI endpoint derives roles from the verified authenticated user in the database session (`current_user.roles`).
9. **Are all service callers explicitly identified and authorized?**  
   **`YES` (HTTP route handler)** | **`VERIFIED_IN_SOURCE`**  
   The endpoint passes `actor_roles` and `actor_id` to the service and stages atomic audit records.
10. **Can a service caller accidentally commit because `auto_commit` defaults to true?**  
    **`YES` (if calling service directly without passing auto_commit=False)** | **`VERIFIED_IN_SOURCE`**  
    The endpoint explicitly passes `auto_commit=False`. Direct script/worker callers omitting the flag will trigger a commit.

### Count Integrity
11. **Does `source_observation_count` represent a verified measurement or an author-supplied number?**  
    **`VERIFIED_MEASUREMENT` (Post-Correction)** | **`CORRECTED_LOCALLY_UNCOMMITTED`**, **`VERIFIED_BY_OFFLINE_TEST`**  
    It is now derived on the server from `len(valid_evidences_to_persist)`.
12. **Can a caller submit an arbitrarily inflated source observation count?**  
    **`NO` (Post-Correction)** | **`CORRECTED_LOCALLY_UNCOMMITTED`**, **`VERIFIED_BY_OFFLINE_TEST`**  
    Client-supplied counts (e.g. 999999) are overridden by the count of verified evidence records.
13. **Can the server derive the correct count from validated source evidence?**  
    **`YES`** | **`CORRECTED_LOCALLY_UNCOMMITTED`**, **`VERIFIED_BY_OFFLINE_TEST`**  
    Derivation calculates `len(valid_evidences_to_persist)`.
14. **Are observations and RiskAlerts counted according to a documented and consistent contract?**  
    **`YES`** | **`CORRECTED_LOCALLY_UNCOMMITTED`**, **`VERIFIED_BY_OFFLINE_TEST`**  
    Each verified `Observation` and `RiskAlert` entity contributes exactly 1 to `source_observation_count`.

### Transactions and Retries
15. **Is signal creation, validated evidence insertion, and AuditLog staging atomic?**  
    **`YES`** | **`CORRECTED_LOCALLY_UNCOMMITTED`**, **`VERIFIED_BY_OFFLINE_TEST`**  
    Staged within a single transaction session and committed atomically after response pre-validation.
16. **Can a failure after commit produce an HTTP error despite successful persistence?**  
    **`YES`** | **`VERIFIED_IN_SOURCE`**  
    Post-commit refresh, response streaming, or network drops occur after the DB commit has succeeded.
17. **Can retrying that request create a duplicate signal?**  
    **`YES`** | **`VERIFIED_IN_SOURCE`**  
    The endpoint lacks an idempotency key mechanism.
18. **Is the current retry behavior acceptable under the product contract?**  
    **`OWNER_ACCEPTANCE_REQUIRED`** | **`VERIFIED_IN_SOURCE`**  
    Permitted for pilot under manual deduplication, but requires an idempotency mechanism for production.

### RLS and Readiness
19. **Can official advisories with zero plot telemetry be read under the generated RLS policy?**  
    **`NO` (for FARMER role)** | **`STATIC_DDL_EXEMPTION_ABSENT`**, **`VERIFIED_BY_OFFLINE_TEST`**  
    The generated policy requires `distinct_farms_count >= 3`, which blocks farmer reads of $N=0$ advisories.
20. **Which behaviors remain dependent on live PostgreSQL verification?**  
    **`LIVE_POSTGRESQL_NOT_VERIFIED`**  
    Kernel-level RLS policy enforcement (`DB-RLS-01`) and read-replica write-on-read routing behavior (`RES-PRIMARY-ROUTING-01`).
21. **Which residual decisions require Project Owner acceptance?**  
    **`OWNER_ACCEPTANCE_REQUIRED`**  
    Decision Gates 02-05 (`OWNER-AUTH-01`), official advisory RLS exemption policy, free-text PII risk (`RES-FREE-TEXT-01`), and independent peer-review workflow design (`EXPERT-REVIEW-01`).
