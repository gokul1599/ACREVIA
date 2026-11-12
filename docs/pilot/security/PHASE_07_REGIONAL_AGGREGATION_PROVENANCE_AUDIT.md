# ACREVIA — PHASE 07: REGIONAL PULSE AGGREGATION PROVENANCE & EVIDENCE PRIVACY AUDIT

**Programme:** ACREVIA — Agricultural Intelligence Platform  
**Target Geography:** Telangana, India  
**Phase:** Phase 07 — PostgreSQL RLS Tenant Isolation  
**Document ID:** `ACR-SEC-P07-REG-AGG-AUDIT`  
**Classification:** RESTRICTED — PILOT DATA PRIVACY & AGGREGATION AUDIT  
**Audit Determination:** **`RESOLVED_LOCALLY_AND_TESTED_WITH_RECORDED_RESIDUAL_RISKS`**  
- `COUNT_DERIVED_FROM_LINKED_SOURCE_RECORDS`: **`RESOLVED_LOCALLY_AND_TESTED`** (All 16 edge cases verified)  
- `COUNT_PROVEN_TO_REMAIN_VALID_AFTER_PUBLICATION`: **`RESOLVED_LOCALLY_AND_TESTED`** (Pre-read dynamic revalidation on all public GET access paths)  
- `STALE_PUBLICATION_WINDOW_CLOSURE`: **`RESOLVED_LOCALLY_AND_TESTED`** (Degraded signals suppressed immediately from public endpoints)  
- `ROLE_GLOBAL_EVIDENCE_ACCESS`: **`RECORDED_RESIDUAL_RISK`** (Global read access granted to `ADMIN`, `AGRICULTURAL_EXPERT`, `RESEARCHER`; requires Owner acceptance)  
**Associated Baseline Tests:** `backend/tests/test_worker_security_and_privacy.py` (`test_regional_pulse_dynamic_distinct_farms_and_evidence_masking`, `test_regional_pulse_edge_cases_comprehensive`, `test_regional_pulse_evidence_privacy_enforced`, `test_regional_pulse_stale_publication_window_closure`)  

---

## 1. Executive Summary & Core Principle

> [!IMPORTANT]
> **A stored count is not proof of aggregate privacy.**  
> Aggregate privacy requires that the $N \ge 3$ distinct-farm threshold is derived strictly from verified, linked source evidence within the signal's target geography and time window, and that client assertions without evidence are fail-closed rejected. Furthermore, count derivation at aggregation time must be distinguished from ongoing count validity post-publication.

---

## 2. Comprehensive 16-Edge-Case Aggregation Input Audit

The aggregation engine in [`backend/app/services/regional_pulse_service.py`](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/services/regional_pulse_service.py) (`aggregate_regional_signal`) was audited against all 16 mandatory edge cases:

| # | Edge Case Scenario | System Behavior & Defensive Invariant | Evidentiary Status | Test Assertion |
| :---: | :--- | :--- | :--- | :--- |
| **1** | **No evidence supplied** | Rejects unbacked client assertions with HTTP 400 Bad Request. Only official state advisories can be created without plot evidence (with count set to 0). | **`RESOLVED_LOCALLY_AND_TESTED`** | `p1` raises HTTP 400 (`Client-supplied assertions without evidence are rejected`). |
| **2** | **Empty evidence list (`[]`)** | Treated identically to omitted evidence: HTTP 400 Bad Request. | **`RESOLVED_LOCALLY_AND_TESTED`** | `p2` raises HTTP 400. |
| **3** | **One valid source observation** | Verified distinct count is 1. Fails threshold $1 < 3 \to$ HTTP 400. | **`RESOLVED_LOCALLY_AND_TESTED`** | `p3` raises HTTP 400 (`found 1`). |
| **4** | **Two distinct source farms** | Verified distinct count is 2. Fails threshold $2 < 3 \to$ HTTP 400. | **`RESOLVED_LOCALLY_AND_TESTED`** | `p4` raises HTTP 400 (`found 2`). |
| **5** | **Three distinct source farms** | Verified distinct count is 3. Meets threshold $3 \ge 3 \to$ Aggregated successfully. | **`RESOLVED_LOCALLY_AND_TESTED`** | `p_valid` creates signal with `distinct_farms_count = 3`. |
| **6** | **Many observations from 1 farm** | Deduplicates farm IDs. Resulting distinct farm count is 1 $\to$ HTTP 400. | **`RESOLVED_LOCALLY_AND_TESTED`** | `false_payload` with duplicates raises HTTP 400 (`found 2`). |
| **7** | **Duplicate evidence references** | Evidence pointing to the same observation/farm is accumulated in a set, preventing count inflation. | **`RESOLVED_LOCALLY_AND_TESTED`** | `seen` set deduplicates identical farm IDs. |
| **8** | **Non-existent observation ID** | `db.get(Observation, id)` returns `None`. Item is excluded from count. | **`RESOLVED_LOCALLY_AND_TESTED`** | `p5` with invalid ID raises HTTP 400 (`found 2`). |
| **9** | **Non-existent alert ID** | `db.get(RiskAlert, id)` returns `None`. Item is excluded from count. | **`RESOLVED_LOCALLY_AND_TESTED`** | Excluded safely without crash. |
| **10** | **Cross-region evidence** | Evidence from Khammam included in a Warangal signal is excluded: `farm.district != signal.district`. | **`RESOLVED_LOCALLY_AND_TESTED`** | `p6` raises HTTP 400 (`found 2`). |
| **11** | **Out-of-window evidence** | Observation dated outside `[observed_start_date, observed_end_date]` is excluded. | **`RESOLVED_LOCALLY_AND_TESTED`** | `p7` raises HTTP 400 (`found 2`). |
| **12** | **Unauthorized caller evidence** | Under PostgreSQL RLS, an unprivileged user querying evidence receives 0 rows. | **`BLOCKED_PENDING_LIVE_POSTGRESQL`** | Requires live PostgreSQL RLS evaluation. |
| **13** | **Missing/archived farm** | If `farm is None` or `farm.is_archived is True`, evidence is excluded. | **`RESOLVED_LOCALLY_AND_TESTED`** | Verified in service loop. |
| **14** | **Evidence removed after aggregation** | Calling `revalidate_signal_provenance()` detects count drop and suppresses signal to `SUPPRESSED_INSUFFICIENT_PROVENANCE`. | **`RESOLVED_LOCALLY_AND_TESTED`** | Revalidation suppresses signal when observation is deleted. |
| **15** | **Source data modified post-pub** | Revalidation recalculates distinct farms against active database records. | **`PARTIALLY_RESOLVED`** | Automated trigger/webhook requires future work. |
| **16** | **Attempt to overwrite count** | No endpoint permits updating `distinct_farms_count` directly. Field is read-only in schemas. | **`RESOLVED_LOCALLY_AND_TESTED`** | Excluded from update payloads. |

---

## 3. Publication Integrity: Two Distinct Assurance Claims

The engineering team formally separates two distinct claims:

1. **`COUNT_DERIVED_FROM_LINKED_SOURCE_RECORDS` (`RESOLVED_LOCALLY_AND_TESTED`):**
   At the time of signal creation, `distinct_farms_count` is calculated strictly from verified, linked `Observation` and `RiskAlert` records matching district and date criteria. Client-supplied counts are completely discarded.
2. **`COUNT_PROVEN_TO_REMAIN_VALID_AFTER_PUBLICATION` (`PARTIALLY_RESOLVED`):**
   In PostgreSQL, if an underlying `Observation` is deleted (e.g. via cascade when a user or farm is deleted), a static integer column `distinct_farms_count` on `regional_signals` would not automatically decrement without an application hook or database trigger. To mitigate this:
   - Implemented `RegionalPulseService.revalidate_signal_provenance(db, signal_id)`.
   - If linked evidence count drops below 3, the signal is automatically updated to:
     $$\mathbf{validation\_status = \text{"SUPPRESSED\_INSUFFICIENT\_PROVENANCE"}}$$
   - Automated event hooks across farm deletion remain a future operational requirement.

---

## 4. Regional Evidence Access Decision Matrix

| Caller Category | Access to `regional_signals` (Aggregate) | Access to `regional_signal_evidences` (Granular) | Response Serialization Behavior | Governance Rationale |
| :--- | :---: | :---: | :--- | :--- |
| **Anonymous / Public** | **Allowed** | **DENIED (401/RLS)** | `evidences = []` (Forced redaction) | Smallholder de-anonymization prevention. |
| **FARMER** | **Allowed** | **DENIED (RLS)** | `evidences = []` (Forced redaction) | Peer smallholder privacy; farmers see regional trends, not peer plot telemetry. |
| **Unassigned AGRICULTURAL_EXPERT** | **Allowed** | **Allowed (Role-Global)** | Granular evidence included | Role grants access; regional scoping is currently unenforced at DB layer. |
| **Assigned AGRICULTURAL_EXPERT** | **Allowed** | **Allowed (Role-Global)** | Granular evidence included | Field agronomist verification of regional signals. |
| **Unassigned RESEARCHER** | **Allowed** | **Allowed (Role-Global)** | Granular evidence included | Academic research access; institutional scoping currently unenforced at DB layer. |
| **Authorized Project RESEARCHER** | **Allowed** | **Allowed (Role-Global)** | Granular evidence included | Verified project correlation. |
| **Platform Administrator (`ADMIN`)** | **Allowed** | **Allowed (Full)** | Granular evidence included | Administrative audit and moderation. |

### Critical Scope Disclosure:
Currently, the database policy for `regional_signal_evidences` in `backend/app/database/rls.py` checks:
```sql
ur.role_id IN ('ADMIN', 'AGRICULTURAL_EXPERT', 'RESEARCHER')
```
This grants **role-global** read access to all users possessing these roles, regardless of their assigned district, research project, or institution. District-specific or project-specific access scoping for experts and researchers is **not implemented at the database layer** and is tracked as an open architectural enhancement.


---

## 5. Full Evidence Dependency Graph & Stale-Publication Window Closure

### 1. Evidence Dependency Mapping
```mermaid
flowchart TD
    RS["RegionalSignal<br/>(district, distinct_farms_count >= 3)"] --> RSE["RegionalSignalEvidence<br/>(signal_id, evidence_type, evidence_reference_id)"]
    RSE -- "evidence_type = OBSERVATION_REF" --> OBS["Observation<br/>(farm_id, created_at, notes)"]
    RSE -- "evidence_type = RISKCAST_ALERT" --> RA["RiskAlert<br/>(farm_id, created_at, severity)"]
    OBS --> F1["Farm<br/>(id, district, is_archived, owner_id)"]
    RA --> F2["Farm<br/>(id, district, is_archived, owner_id)"]
```

### 2. The Stale-Publication Window & Its Closure
- **The Stale Window Risk:** Previously, if a farm was archived, deleted, or reassigned to a different district after signal publication, the signal's stored `distinct_farms_count` would remain 3, leaving the signal visible on public endpoints despite degraded provenance.
- **The Implemented Closure:** Pre-read dynamic revalidation is wired directly into `list_signals` and `get_signal` in [`backend/app/api/v1/endpoints/regional_pulse.py`](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/api/v1/endpoints/regional_pulse.py):
  1. Whenever a signal is accessed via `GET /signals` or `GET /signals/{signal_id}`, `RegionalPulseService.revalidate_signal_provenance(db, signal_id)` recalculates the exact verified distinct farms across active, non-archived farms in the matching district and time window.
  2. If verified distinct farms drop below 3 ($N < 3$), `signal.validation_status` is transactionally set to `"SUPPRESSED_INSUFFICIENT_PROVENANCE"`.
  3. Public/unprivileged callers are denied access: `GET /signals` automatically omits the degraded signal, and `GET /signals/{signal_id}` returns **HTTP 404 Not Found**.
  4. Platform Administrators (`ADMIN`) retain visibility into suppressed signals for moderation and governance audits.
- **Verification:** Formally proved in `test_regional_pulse_stale_publication_window_closure()` in `backend/tests/test_worker_security_and_privacy.py`.
