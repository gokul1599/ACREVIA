# ACREVIA — PHASE 07: TRUSTED PROVENANCE VERIFIER POLICY-COMPOSITION PROOF, RESTRICTIVE RLS COMPATIBILITY & SOURCE-MUTATION SERIALIZATION ASSURANCE

**Programme:** ACREVIA — Agricultural Intelligence Platform  
**Target Geography:** Telangana, India (33 Administrative Districts)  
**Target Phase:** Phase 07 — PostgreSQL RLS Tenant Isolation & Regional Aggregation Privacy  
**Execution Mode:** `MODE A ONLY` — Read-only Source Inspection, PostgreSQL Policy-Semantics Analysis, Threat Modelling, Concurrency Analysis & Governance Documentation  
**Methodology:** Everything Claude Code (ECC) — `PLAN → INSPECT → TRACE → ADVERSARIAL REVIEW → IMPLEMENT ONLY IF EXPLICITLY AUTHORIZED → REVIEW → VERIFY → DOCUMENT`  
**Public Repository:** `https://github.com/gokul1599/ACREVIA`  
**Pinned Baseline Commit:** `c9e334d14110e8a6e4c9b71b89cae3294288af0d` (`main`)  
**Deliverable Path:** `docs/pilot/security/PHASE_07_TRUSTED_PROVENANCE_VERIFIER_POLICY_COMPOSITION_AND_SERIALIZATION_PROOF.md`  

**`DESIGN_VERDICT: DESIGN_NOT_YET_PROVEN`**  
**`IMPLEMENTATION_STATUS: NOT_IMPLEMENTATION_AUTHORIZED`**  
**`PHASE_07_STATUS: NOT_RELEASED`**  
**`MODE_B_STATUS: NOT_AUTHORIZED`**  
**`LIVE_POSTGRESQL_VERIFICATION: NOT_PERFORMED`**  
**`CANONICAL_BLOCKER_CLOSURE: NONE_AUTHORIZED`**  

---

## 1. EXECUTIVE ASSURANCE VERDICT

This audit evaluates the policy-composition feasibility, identity trust boundary, district authorization contract, and source-mutation serialization properties of the proposed ACREVIA Regional Pulse trusted provenance verifier (`verify_regional_signal_provenance` owned by `acrevia_verifier`).

**Primary Audit Question:**  
*Can `acrevia_verifier` read exactly the authorized source records under the existing restrictive RLS policy composition, without acquiring an unrestricted cross-tenant data-access capability?*

**Assurance Answer (`STATIC_SQL_SEMANTICS` / `PUBLIC_SOURCE_VERIFIED`):**  
**NO — NOT UNDER THE PROPOSED ROLE-TARGETED PERMISSIVE POLICY.**

1. **Restrictive `TO PUBLIC` Override Failure (`STATIC_SQL_SEMANTICS`):**  
   In `backend/app/database/rls.py#L349-L361`, every `TENANT_DIRECT` source table (`farms`, `observations`, `risk_alerts`) has a **`RESTRICTIVE FOR ALL TO PUBLIC`** policy (`{table}_tenant_isolation_policy`). Under PostgreSQL RLS composition (`(OR of PERMISSIVE) AND (AND of RESTRICTIVE)`), every PostgreSQL role—including `acrevia_verifier`—is implicitly a member of `PUBLIC`. Adding a `PERMISSIVE FOR SELECT TO acrevia_verifier USING (true)` policy **does not bypass or relax the `RESTRICTIVE TO PUBLIC` policy**. When `acrevia_verifier` executes with `app.current_tenant_id = ''` and `SESSION_USER = acrevia_staging_app`, the restrictive policy evaluates `ADMIN_BYPASS_SQL (FALSE) OR tenant_col::text = '' (FALSE)`, returning **0 rows**. Enabling `acrevia_verifier` without `BYPASSRLS` or `SUPERUSER` requires modifying the `RESTRICTIVE` policy itself to include a narrowly scoped `CURRENT_USER::text = 'acrevia_verifier'` predicate bound to valid signal/district scope—an unimplemented schema/DDL change.
2. **District Authority & Expert Status Disconnect (`PUBLIC_SOURCE_VERIFIED`):**  
   `app.current_user_districts` does not exist (`NOT_ESTABLISHED`). `ExpertProfile.districts_covered_json` ([expert_profile.py#L25](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/models/expert_profile.py#L25)) and `verification_status` (`APPROVED`, `SUSPENDED`, `REVOKED`) are **never** loaded in `get_current_user()` or checked in `recover_signal()` / `rls.py`.
3. **Source-Mutation Serialization Gap (`PUBLIC_SOURCE_VERIFIED`):**  
   Parent `RegionalSignal FOR UPDATE` does not serialize `FarmService.update_farm()` district edits or `RiskService` updates. No Regional Pulse provenance invalidation outbox exists (`WebhookService.publish_outbox_event` serves Stage 14 webhooks only).
4. **Open Credential Fallback (`PUBLIC_SOURCE_VERIFIED`):**  
   `frontend/lib/server/db.ts#L10` retains a hard-coded Neon URI fallback (`DB-CREDENTIAL-EXPOSURE-01 = OPEN`).

---

## 2. BASELINE VERIFICATION

- **Local Git Inspection (`LOCAL_SOURCE_VERIFIED`):**
  - `git log -1 --format="%H %s"` $\to$ `c9e334d14110e8a6e4c9b71b89cae3294288af0d` (`main`).
  - `git rev-parse HEAD origin/main` $\to$ both `c9e334d14110e8a6e4c9b71b89cae3294288af0d` (0 divergence against local `origin/main` ref; live GitHub network fetch was not executed in Mode A).
  - `git diff --name-only` $\to$ 7 tracked historical governance files in `docs/pilot/security/`. Zero application source, model, migration, or test modifications.
  - `git status --short` $\to$ 18 prior untracked Phase 07 assurance reports preserved non-destructively (including `PHASE_07_TRUSTED_PROVENANCE_FUNCTION_SECURITY_AND_MULTI_TENANT_CONCURRENCY_DESIGN_PROOF.md`).

---

## 3. EVIDENCE CLASSIFICATION

All findings in this proof use the following strict evidence labels:
- `PUBLIC_SOURCE_VERIFIED`: Directly observed in pinned commit `c9e334d14110e8a6e4c9b71b89cae3294288af0d` files.
- `LOCAL_SOURCE_VERIFIED`: Directly observed in the local workspace working tree.
- `STATIC_SQL_SEMANTICS`: Derived from PostgreSQL 16 engine rules (`rowsecurity.c`, `analyze.c`) applied to generated DDL.
- `STATIC_CODE_INFERENCE`: Derived from static control-flow/ORM analysis of Python/SQLAlchemy source.
- `DESIGN_PROPOSAL`: Proposed architecture, role, or DDL not present in pinned source.
- `USER_REPORTED`: Reported externally without independent verification.
- `LIVE_DATABASE_UNKNOWN`: Live Neon/PostgreSQL catalog, role attributes, and ACLs (`NOT_PERFORMED` in Mode A).
- `NOT_ESTABLISHED`: Unproven or absent from source and governance records.

---

## 4. CURRENT RLS ARCHITECTURE (`PUBLIC_SOURCE_VERIFIED`)

Inspecting `TABLE_CLASSIFICATION` and `generate_rls_ddl()` in [backend/app/database/rls.py](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/database/rls.py):

| Table | Category (`rls.py`) | RLS Enabled & Forced? | Permissive Policies | Restrictive Policies | Command & Roles |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `farms` | `TENANT_DIRECT` (`id`, L42) | `ENABLE` + `FORCE` (L338-339) | `farms_base_access_policy` (`USING (true)`) | `farms_tenant_isolation_policy` (`ADMIN_BYPASS_SQL OR id::text = current_setting('app.current_tenant_id', true)`) | `FOR ALL TO PUBLIC` |
| `observations` | `TENANT_DIRECT` (`farm_id`, L53) | `ENABLE` + `FORCE` (L338-339) | `observations_base_access_policy` (`USING (true)`) | `observations_tenant_isolation_policy` (`ADMIN_BYPASS_SQL OR farm_id::text = current_setting('app.current_tenant_id', true)`) | `FOR ALL TO PUBLIC` |
| `risk_alerts` | `TENANT_DIRECT` (`farm_id`, L57) | `ENABLE` + `FORCE` (L338-339) | `risk_alerts_base_access_policy` (`USING (true)`) | `risk_alerts_tenant_isolation_policy` (`ADMIN_BYPASS_SQL OR farm_id::text = current_setting('app.current_tenant_id', true)`) | `FOR ALL TO PUBLIC` |
| `regional_signals` | `COMMUNITY_COLLABORATIVE` (L242) | `ENABLE` + `FORCE` (L952-953) | `regional_signals_public_read_policy` (`FOR SELECT`); `regional_signals_author_write_policy` (`FOR ALL`) | None | `TO PUBLIC` |
| `regional_signal_evidences` | `COMMUNITY_COLLABORATIVE` (L246) | `ENABLE` + `FORCE` (L952-953) | `regional_signal_evidences_public_read_policy` (`FOR SELECT`); `regional_signal_evidences_author_write_policy` (`FOR ALL`) | None | `TO PUBLIC` |

*Note: `regional_signals_public_read_policy` (L901-907) uses `ADMIN_BYPASS_SQL OR (distinct_farms_count >= 3 AND validation_status != 'SUSPENDED')`, whereas `regional_signals_author_write_policy` (L921-931) uses `ADMIN_BYPASS_SQL OR (app.current_user_id != '' AND EXISTS user_roles IN ('ADMIN', 'AGRICULTURAL_EXPERT', 'RESEARCHER'))`.*

---

## 5. COMPLETE POLICY-COMPOSITION ANALYSIS (`STATIC_SQL_SEMANTICS`)

Under PostgreSQL RLS evaluation (`src/backend/rewrite/rowsecurity.c`):
$$\text{Row Permitted} \iff \left(\bigvee_{p \in \text{PERMISSIVE}} P_p(\text{row})\right) \land \left(\bigwedge_{r \in \text{RESTRICTIVE}} R_r(\text{row})\right)$$

### 5.1 Why `PERMISSIVE FOR SELECT TO acrevia_verifier` Fails Against `RESTRICTIVE TO PUBLIC`
Suppose we add:
```sql
-- HYPOTHETICAL DESIGN PROPOSAL (FAILS UNDER EXISTING RESTRICTIVE POLICY)
CREATE POLICY farms_verifier_read_policy ON farms
    AS PERMISSIVE FOR SELECT TO acrevia_verifier USING (true);
```
Because `acrevia_verifier` is implicitly a member of `PUBLIC`, PostgreSQL evaluates **both**:
1. **Permissive (`OR`):** `farms_base_access_policy (true) OR farms_verifier_read_policy (true)` $\implies$ `TRUE`.
2. **Restrictive (`AND`):** `farms_tenant_isolation_policy` (`TO PUBLIC`) $\implies$ `ADMIN_BYPASS_SQL OR id::text = current_setting('app.current_tenant_id', true)`.
   - When `app.current_tenant_id = ''` and `SESSION_USER = acrevia_staging_app`, `ADMIN_BYPASS_SQL` is `FALSE` and `id::text = ''` is `FALSE`.
   - Restrictive result = **`FALSE`**.
3. **Combined Effective Predicate:** `TRUE AND FALSE` = **`FALSE`** (0 rows returned).

**Architectural Blocker (`DESIGN_PROPOSAL` Gap):** A permissive policy **cannot** overcome a restrictive policy applied `TO PUBLIC`. For `acrevia_verifier` to read cross-tenant source rows without `BYPASSRLS` or `SUPERUSER`, the `RESTRICTIVE` policy on `farms`, `observations`, and `risk_alerts` must itself be updated to incorporate a tightly constrained `CURRENT_USER::text = 'acrevia_verifier'` clause (e.g., scoped to active signal evidence references and district match), **and** `acrevia_verifier` must remain `NOLOGIN` and non-inheritable by `acrevia_staging_app`.

---

## 6. IDENTITY AND ROLE TRUTH TABLES

### 6.1 Policy Evaluation Truth Table (Source Tables: `farms`, `observations`, `risk_alerts`)
| Identity | Tenant GUC | Admin GUC | Expected Investigation (`STATIC_SQL_SEMANTICS` / `LIVE_DATABASE_UNKNOWN`) |
| :--- | :--- | :--- | :--- |
| `acrevia_staging_app` | Empty (`''`) | `false` | Restricted application: `ADMIN_BYPASS_SQL` = `FALSE`, `tenant_col = ''` = `FALSE` $\implies$ **0 rows**. |
| `acrevia_staging_app` | Empty (`''`) | `true` | Application `ADMIN`: `SESSION_USER` (`acrevia_staging_app`) fails `ADMIN_BYPASS_SQL` $\implies$ **0 rows**. |
| `acrevia_verifier` | Empty (`''`) | `false` | Proposed verifier owner with permissive-only policy: blocked by `RESTRICTIVE TO PUBLIC` $\implies$ **0 rows**. |
| `acrevia_verifier` | Authorized tenant (`<farm_id>`) | `false` | Tenant-scoped verifier: sees **1 farm's rows only** (cannot aggregate `>= 3` distinct farms in one query). |
| `acrevia_verifier` | Untrusted tenant (`<spoofed_id>`) | `false` | Spoofed/unauthorized context: if `app.current_tenant_id` is mutable in session, restrictive predicate matches `<spoofed_id>` unless verifier avoids GUC reliance. |
| `neondb_owner` | Empty (`''`) | `true` | Administrative identity (`LIVE_DATABASE_UNKNOWN` runtime attributes): satisfies `ADMIN_BYPASS_SQL` if `SESSION_USER` & `CURRENT_USER` = `neondb_owner` (or if superuser/`BYPASSRLS`). |
| `acrevia_admin` | Empty (`''`) | `true` | Administrative identity (`LIVE_DATABASE_UNKNOWN` runtime attributes): satisfies `ADMIN_BYPASS_SQL` when `SESSION_USER` & `CURRENT_USER` = `acrevia_admin`. |


---

## 7. `SECURITY DEFINER` THREAT MODEL (`STATIC_SQL_SEMANTICS` / `DESIGN_PROPOSAL`)

When `acrevia_staging_app` invokes a `SECURITY DEFINER` function owned by `acrevia_verifier`:
- `CURRENT_USER` changes to `acrevia_verifier`; **`SESSION_USER` remains `acrevia_staging_app`**.
- `ADMIN_BYPASS_SQL` (`SESSION_USER::text IN ('neondb_owner', 'acrevia_admin') AND CURRENT_USER::text IN (...)`) evaluates to **`FALSE`**.
- `FORCE ROW LEVEL SECURITY` remains enforced against `acrevia_verifier` (even if `acrevia_verifier` owned the tables) unless `BYPASSRLS` or `SUPERUSER` is granted.

### 7.1 Hardening Controls Classification
| Proposed Control | Classification | Technical Assessment |
| :--- | :---: | :--- |
| Dedicated `NOLOGIN` owner (`acrevia_verifier`) | **`REQUIRED`** | Prevents direct login under verifier identity. |
| `NOSUPERUSER` & `NOBYPASSRLS` | **`REQUIRED`** | Prevents global RLS bypass if function has a flaw. |
| No unnecessary role memberships / `SET ROLE` | **`REQUIRED`** | Prevents `acrevia_staging_app` from assuming `acrevia_verifier` directly. |
| Explicit schema-qualified object references (`public.*`) | **`REQUIRED`** | Prevents object shadowing across schemas. |
| `SET search_path = public, pg_temp` (`pg_temp` last) | **`REQUIRED`** | Insufficient alone if untrusted roles hold `CREATE` on `public`; must pair with `REVOKE CREATE ON SCHEMA public FROM PUBLIC`. |
| No dynamic SQL (`EXECUTE`) | **`REQUIRED`** | Eliminates SQL injection inside elevated context. |
| Explicit input validation (`p_signal_id` non-null/format) | **`REQUIRED`** | Prevents malformed parameter errors. |
| Explicit caller authorization & district scope validation | **`REQUIRED`** | Prevents unauthorized callers or cross-district probing. |
| `REVOKE ALL FROM PUBLIC` + narrow `GRANT EXECUTE` | **`REQUIRED`** | Blocks default `PUBLIC` execution. |
| Aggregate-only output & zero raw source PII | **`REQUIRED`** | Preserves DPDPA 2023 / $k \ge 3$ privacy. |

### 7.2 GUC Trust Boundary
`app.current_user_id`, `app.current_tenant_id`, and `app.is_admin` are set via `set_config(..., true)` ([rls.py#L280-L291](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/database/rls.py#L280-L291)). Any arbitrary SQL executed in the `acrevia_staging_app` session can overwrite these GUCs. Therefore, a mutable GUC **cannot** serve as independent cryptographic proof of caller identity or district scope inside a `SECURITY DEFINER` function without server-side session binding or authenticated gateway/worker separation.

---

## 8. VERIFIER-OWNER PRIVILEGE ANALYSIS

1. `acrevia_verifier` requires `USAGE ON SCHEMA public` and `SELECT` on `regional_signals`, `regional_signal_evidences`, `observations`, `risk_alerts`, `farms`, and (once normalized) `expert_district_assignments`.
2. `acrevia_verifier` requires **zero** `INSERT`, `UPDATE`, `DELETE`, `TRUNCATE`, `REFERENCES`, or `TRIGGER` privileges.
3. Under existing `RESTRICTIVE TO PUBLIC` policies, `acrevia_verifier` cannot read source rows unless `{table}_tenant_isolation_policy` is amended to permit `CURRENT_USER::text = 'acrevia_verifier'` (scoped strictly to evidence-linked rows for the target signal).

---

## 9. DISTRICT AUTHORIZATION ANALYSIS (`PUBLIC_SOURCE_VERIFIED`)

Inspecting [expert_profile.py#L15-L40](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/models/expert_profile.py#L15-L40), [dependencies.py](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/security/dependencies.py), and [regional_pulse_service.py](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/services/regional_pulse_service.py):
- `ExpertProfile.districts_covered_json` is used **only** in `expertconnect.py` and `expert_service.py`.
- It is **not** loaded in `get_current_user()`, **not** validated against Telangana's 33 districts, **not** checked before `recover_suppressed_signal()`, and **not** referenced in `rls.py`.
- `recover_signal()` ([regional_pulse.py#L156](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/api/v1/endpoints/regional_pulse.py#L156)) checks `require_roles(ADMIN, AGRICULTURAL_EXPERT)` via `user_roles` only—it does **not** verify `ExpertProfile.verification_status == 'APPROVED'`. Thus, `SUSPENDED`, `REVOKED`, or `APPLICATION_SUBMITTED` experts who still hold the `AGRICULTURAL_EXPERT` row in `user_roles` are not blocked.

### 9.1 Actor Authority Matrix
| Actor | Role Check (`user_roles`) | `ExpertProfile.verification_status` Checked? | District Scope Enforced? | Recovery Access (`PUBLIC_SOURCE_VERIFIED`) |
| :--- | :--- | :---: | :---: | :--- |
| Application `ADMIN` | `ADMIN` | N/A | No (statewide) | Passes route check; fails source RLS (`0` rows). |
| Approved Agricultural Expert | `AGRICULTURAL_EXPERT` | **NO** | **NO** | Passes route check; fails source RLS (`0` rows). |
| Unverified / Suspended Expert | `AGRICULTURAL_EXPERT` (if retained) | **NO** | **NO** | **Not blocked by route/service**; fails source RLS (`0` rows). |
| Researcher / Farmer | `RESEARCHER` / `FARMER` | N/A | No | Rejected `HTTP 403` by `require_roles`. |
| Verifier Owner (`acrevia_verifier`) | `NOLOGIN` (`DESIGN_PROPOSAL`) | N/A | Must check in DB | Cannot read source rows until `RESTRICTIVE` policy amended. |
| Worker (`acrevia_worker`) | `NOLOGIN` (`DESIGN_PROPOSAL`) | N/A | Must check in DB | `NOT_ESTABLISHED` (`WRK-DISP-01`). |

`EXP-AUTH-01` remains **OPEN**.

---

## 10. RECOVERY SOURCE-QUERY TRACE (`PUBLIC_SOURCE_VERIFIED` / `STATIC_SQL_SEMANTICS`)

Tracing `recover_signal()` $\to$ `recover_suppressed_signal()` ([regional_pulse_service.py#L430-L512](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/services/regional_pulse_service.py#L430-L512)) under `acrevia_staging_app` with `app.current_tenant_id = ''`:

| Query Target | Lookup Key | Tenant Col | District Source | RLS Category | Applicable Policies | Lock Clause & Privileges Needed | Expected Result Under Static Design |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `regional_signals` (L430-437) | `id == signal_id` | None | `signal.district` | `COMMUNITY_COLLABORATIVE` | `public_read_policy` (`FOR SELECT`) + `author_write_policy` (`FOR ALL`) | `FOR UPDATE` (`SELECT` + `UPDATE` on 1+ col) | **0 rows** if `distinct_farms_count < 3` (hidden by `public_read_policy`); visible if `>= 3` & `status != 'SUSPENDED'`. |
| `regional_signal_evidences` (L459-466) | `signal_id == signal_id` | None | Via parent/farm | `COMMUNITY_COLLABORATIVE` | `public_read_policy` + `author_write_policy` | `FOR SHARE` (`SELECT` + `UPDATE` on 1+ col) | **Rows visible** if `user_roles` matches, OR **SQLSTATE `42501`** if `UPDATE` revoked! |
| `observations` (L476-483) | `id.in_(obs_ids)` | `farm_id` | Via `farms.district` | `TENANT_DIRECT` | `base_access` + `tenant_isolation` (`RESTRICTIVE`) | `FOR SHARE` (`SELECT` + `UPDATE` on 1+ col) | **0 rows** (filtered by `tenant_isolation_policy` — not permission error if `UPDATE` granted). |
| `risk_alerts` (L487-494) | `id.in_(alert_ids)` | `farm_id` | Via `farms.district` | `TENANT_DIRECT` | `base_access` + `tenant_isolation` (`RESTRICTIVE`) | `FOR SHARE` (`SELECT` + `UPDATE` on 1+ col) | **0 rows** (filtered by `tenant_isolation_policy`). |
| `farms` (L505-512) | `id.in_(farm_ids)` | `id` | `farms.district` | `TENANT_DIRECT` | `base_access` + `tenant_isolation` (`RESTRICTIVE`) | `FOR SHARE` (`SELECT` + `UPDATE` on 1+ col) | **0 rows** (filtered by `tenant_isolation_policy`). |

---

## 11. SOURCE-MUTATION INVENTORY (`PUBLIC_SOURCE_VERIFIED`)

| Mutation Path | Service / Endpoint | Rows Modified | Locks Source Row? | Locks `RegionalSignal`? | Emits Provenance Outbox Event? | Independent Commit? |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: |
| Farm update / district reassignment | `FarmService.update_farm()` ([farm_service.py#L84-L103](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/services/farm_service.py#L84-L103)) | `farms` (`district`, `mandal`, `village`, `name`, `total_acreage`) | Yes (`UPDATE`) | **NO** | **NO** | **YES** (`db.commit()`) |
| Farm archival | `Farm.is_archived` (no dedicated archive endpoint; `UPDATE` in `PRIVILEGE_CROSSWALK`) | `farms` (`is_archived`) | Yes (DML) | **NO** | **NO** | **YES** |
| Observation creation | `ObservationService.create_observation()` | `observations` | Yes (`INSERT`) | **NO** | **NO** | **YES** |
| Observation update / delete | No update/delete service method; permitted by `PRIVILEGE_CROSSWALK` (`TENANT_DIRECT_DML`) | `observations` | Yes (DML) | **NO** | **NO** | **YES** |
| Risk alert creation | `RiskService` (`backend/app/services/riskcast/risk_service.py#L117`) | `risk_alerts` | Yes (`INSERT`) | **NO** | **NO** | **YES** |
| Risk alert ack / dismiss | `RiskService.acknowledge_alert()` / `dismiss_alert()` ([risk_service.py#L266-L290](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/services/riskcast/risk_service.py#L266-L290)) | `risk_alerts` (`is_acknowledged`, `is_dismissed`) | Yes (`UPDATE`) | **NO** | **NO** | **YES** |
| Evidence insertion | `RegionalPulseService.aggregate_regional_signal()` | `regional_signal_evidences` | Yes (`INSERT`) | Only if parent locked | **NO** | Caller-owned |
| Evidence update / removal | `PRIVILEGE_CROSSWALK` permits `UPDATE` on `COMMUNITY_COLLABORATIVE` (`rls.py#L1002`) | `regional_signal_evidences` | Yes (DML) | **NO** | **NO** | **YES** |

---

## 12. LOCKING AND SERIALIZATION ANALYSIS (`STATIC_SQL_SEMANTICS`)

1. **Parent-Lock Limitation:** Locking `RegionalSignal` (`FOR UPDATE`) serializes only concurrent `recover_suppressed_signal()` calls on the same `signal_id` (and blocks child `INSERT` FK checks `FOR KEY SHARE`). It **does not** lock `Farm`, `Observation`, or `RiskAlert`, nor does it block `FarmService.update_farm()`.
2. **Phantom & Membership Races:**
   - Because `evidence_reference_id` is a `VARCHAR(100)` string (no FK), deleting an `Observation` or `RiskAlert` is not blocked by `RegionalSignalEvidence`.
   - Under `READ COMMITTED`, `Farm.district` reassignment or `Farm.is_archived = True` can commit between verification and `COMMIT`, leaving a falsely confirmed signal visible.
   - New `Observation` / `RiskAlert` rows can be created concurrently (harmless unless linked by a new `RegionalSignalEvidence` row, which parent `FOR UPDATE` blocks via FK `FOR KEY SHARE` contention).


---

## 13. ISOLATION-LEVEL COMPARISON (`STATIC_SQL_SEMANTICS`)

| Protocol | Guarantees | Does Not Guarantee | Detects Concurrent Changes? | Phantom Rows | Retry Needed? | Deadlock Risk | Complexity | Privacy Invariant |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **1. `READ COMMITTED` + Explicit Row Locks** | Per-statement snapshot; locks current rows | Snapshot consistency across statements | Only on locked rows | Possible between statements | No | Moderate | Moderate | Preserved if source locks succeed |
| **2. `REPEATABLE READ`** | Transaction-wide snapshot (`T1`) | Cross-table write-skew serialization | Only same-row write-write conflicts | Prevented within snapshot | On `40001` write conflict | Low | Low | Preserved within snapshot, stale at commit |
| **3. `SERIALIZABLE` (SSI + Bounded Retry)** | Full serializability; detects read-write anti-dependencies | Immediate lock blocking | **Yes** (`40001` abort on skew) | Prevented | **Yes** (bounded retry) | Low (SSI aborts) | Moderate | **Strongest** consistency |
| **4. Common Advisory-Lock Protocol** | Mutual exclusion on `(signal_id)` or `(farm_id)` key | Protection if any writer skips lock | Only if all writers participate | Not prevented | No | Low if ordered | High (every writer must opt in) | Fragile |
| **5. Common Parent/Source Lock Protocol** | Locks parent + source rows (`FOR SHARE`) | Protection if `UPDATE` revoked on evidence/source | Yes on locked rows | Prevented for locked IDs | No | High | High + privilege conflict | Conflicts with append-only `UPDATE` revoke |
| **6. Optimistic Version Checking** | Detects stale `updated_at`/version at commit | Prevention of read skew prior to check | Yes on versioned rows | Not prevented | Yes | None | Moderate | Safe if all source tables versioned |
| **7. Transactional Outbox Invalidation** | Atomic event staging with source mutation | **Immediate** consistency (eventual only) | Asynchronously via worker | Reconciled async | Worker retry | None | Moderate | Stale window until worker runs |
| **8. Hybrid Verifier + `SERIALIZABLE`/Outbox** | Verifier snapshot + async outbox catch-up | Zero-lag if `READ COMMITTED` used | Yes (SSI) or async (Outbox) | Handled | Bounded if SSI | Low | Moderate-High | **Recommended candidate** |

---

## 14. OUTBOX COMPLETENESS ANALYSIS (`PUBLIC_SOURCE_VERIFIED` / `DESIGN_PROPOSAL`)

- **Current State (`PUBLIC_SOURCE_VERIFIED`):** `WebhookService.publish_outbox_event()` ([webhook_service.py#L132](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/services/webhook_service.py#L132)) writes to Stage 14 `webhook_events` only. **Zero** Regional Pulse provenance-invalidation outbox writers exist in `FarmService`, `ObservationService`, `RiskService`, or `RegionalPulseService`.
- **Missing Writers:** Every source mutation in Section 11 (`update_farm`, `is_archived`, observation/alert DML, evidence DML) lacks an outbox emitter. Even if added to FastAPI services, direct SQL edits outside the service layer would bypass application-only outbox calls unless enforced via database triggers or restricted write functions.
- **Required Outbox Properties (`DESIGN_PROPOSAL`):** Unique `idempotency_key`, per-`signal_id` monotonic ordering, `FOR UPDATE SKIP LOCKED` claim locks, bounded `retry_count` + `DEAD_LETTER` state, lease-expiry recovery on worker crash, dedicated `acrevia_worker` `SELECT`/`UPDATE` privileges on `outbox_events` only, and **reader fail-closed / revalidation behavior while invalidation is pending** (acknowledging eventual-consistency windows). Because the outbox is absent from Regional Pulse, the outbox design is **INCOMPLETE**.

---

## 15. AGGREGATE-OUTPUT PRIVACY ASSESSMENT (`DESIGN_PROPOSAL`)

The proposed verifier returns `meets_threshold BOOLEAN` and `verified_distinct_farms_count INT` (`DESIGN_PROPOSAL` only — does not exist in code).
- **Inference & Differencing Risks:** Even a boolean or integer can leak small-sample farm presence (`1` or `2` farms) via repeated queries, overlapping date windows (`observed_start_date`/`observed_end_date`), narrow district/crop filters, or timing/error differences (`HTTP 400` with `current_count` in error detail at [regional_pulse_service.py#L550](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/services/regional_pulse_service.py#L550)).
- **Required Mitigations:** Restrict execution strictly to `ADMIN` / approved `AGRICULTURAL_EXPERT` / `acrevia_worker` (never farmers/public), enforce stable signal aggregation windows, suppress exact counts `< 3` from unprivileged/error responses, rate-limit recovery attempts, and audit-log every invocation.

---

## 16. PRIVILEGE AND MIGRATION CROSSWALK (`PUBLIC_SOURCE_VERIFIED`)

1. **Five-Layer Separation:**
   - *Python Specification (`rls.py#L977-L1037`):* `PRIVILEGE_CROSSWALK` assigns `UPDATE=True` to `COMMUNITY_COLLABORATIVE` (`regional_signals`, `regional_signal_evidences`) and `INSERT/UPDATE/DELETE=True` to `TENANT_DIRECT` (`farms`, `observations`, `risk_alerts`). Only `audit_logs` has `UPDATE=False, DELETE=False`.
   - *Generated DDL:* `generate_privilege_grants_ddl()` ([rls.py#L1040](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/database/rls.py#L1040)) produces `GRANT`/`REVOKE` strings.
   - *Migration Call Sites:* `a1089411c87d_enable_postgresql_rls_tenant_isolation.py` calls `generate_rls_ddl()`, **NOT** `generate_privilege_grants_ddl()`.
   - *Executed DDL / Live ACLs:* `LIVE_DATABASE_UNKNOWN` (`NOT_PERFORMED` in Mode A).
2. **Recovery Mutated Columns (`PUBLIC_SOURCE_VERIFIED`):**
   `recover_suppressed_signal()` mutates `distinct_farms_count` (L545), `validation_status` (L562), `is_outbreak_claim_suppressed` (L563), and `updated_at` via Python `TimestampMixin` (`onupdate=lambda: datetime.now(timezone.utc)`, [base.py#L28](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/database/base.py#L28)) — **not** PostgreSQL `clock_timestamp()`.
3. **Locking Privileges:** Any `SELECT ... FOR UPDATE` or `FOR SHARE` requires `SELECT` + `UPDATE` on at least one column of the locked table plus `SELECT` and `UPDATE` RLS `USING` qualification.

---

## 17. WORKER IDENTITY ANALYSIS (`DESIGN_PROPOSAL` / `OWNER_DECISION_REQUIRED`)

- A `NOLOGIN` role (`acrevia_worker`) **cannot** open a PostgreSQL connection. It requires an authenticating login principal (`acrevia_worker_login WITH LOGIN NOSUPERUSER NOBYPASSRLS NOCREATEDB NOCREATEROLE`) granted membership in `acrevia_worker`, executing `SET ROLE acrevia_worker;` per transaction and `RESET ROLE;` on pool return.
- `acrevia_worker` must **not** receive global `SELECT` on `farms`, `observations`, or `risk_alerts`; it should invoke `verify_regional_signal_provenance()` and hold narrow `SELECT`/`UPDATE` on `outbox_events` and status/count columns on `regional_signals`.
- Neither `acrevia_worker` nor `acrevia_verifier` is authorized in the current Owner Register; both require an explicit extension to **`DB-AUTH-01`**.

---

## 18. APPEND-ONLY EVIDENCE RETENTION ANALYSIS (`PUBLIC_SOURCE_VERIFIED` / `STATIC_CODE_INFERENCE`)

- **Current Code (`PUBLIC_SOURCE_VERIFIED`):** `RegionalSignal.evidences` uses `cascade="all, delete-orphan"` ([regional_pulse.py#L36](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/models/regional_pulse.py#L36)), FK `signal_id` uses `ondelete="CASCADE"` (L47), and `PRIVILEGE_CROSSWALK` grants `UPDATE=True` on `regional_signal_evidences`.
- **Required Design (`DESIGN_PROPOSAL`):** Pair `cascade="save-update, merge", passive_deletes="all"` in ORM with `ON DELETE RESTRICT` on FK `signal_id`, revoke `UPDATE` and `DELETE` from runtime roles (`acrevia_staging_app`, `acrevia_worker`), and remove client-side `FOR SHARE` on `regional_signal_evidences` (which otherwise conflicts with revoking `UPDATE`). Runtime role revocation prevents application-level tampering; table owners/`neondb_owner` remain able to alter data unless restricted by database triggers.


---

## 19. ARCHITECTURE COMPARISON MATRIX

| Architecture Option | Security Feasibility | Tenant Isolation | District Authorization | Source-Data Minimization | Concurrency Correctness | Operational Complexity | Owner Decisions Required | Unresolved Proof Obligations |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- | :--- |
| **1. Current app-role recovery** | **Infeasible** | Breaks (0 rows) or requires global bypass | Unenforced (`EXP-AUTH-01`) | Poor (reads raw rows) | Vulnerable to `update_farm` if `FOR SHARE` removed | Low | N/A (broken) | Fails under `FORCE RLS` |
| **2. `SECURITY DEFINER` verifier (`acrevia_verifier`)** | **Conditionally Feasible** (only if `RESTRICTIVE` policy amended) | Preserved if scoped inside `RESTRICTIVE` policy | Requires normalized table + DB check | **High** (aggregate output only) | Needs `SERIALIZABLE` or outbox | Moderate | `DB-AUTH-01` extension, `D-01`..`D-03` | `RESTRICTIVE TO PUBLIC` blocks permissive-only policy; live PG test unrun |
| **3. Dedicated worker (`acrevia_worker`)** | **Conditionally Feasible** | Fails if granted global `SELECT` | Needs DB district contract | Low if direct `SELECT`; High if calls verifier | Async lag unless paired with sync check | Moderate-High | `DB-AUTH-01` extension | Login/group role unprovisioned; `WRK-DISP-01` open |
| **4. `SECURITY INVOKER` view/function** | **Infeasible** | Blocked identically to Option 1 | Unenforced | N/A | N/A | Low | N/A | Returns 0 rows under `app.current_tenant_id=''` |
| **5. Common source-mutation lock protocol** | **Fragile** | Requires `UPDATE` on source tables | Unenforced | Poor | Strong if universal, high deadlock risk | High | Schema/service refactor | Conflicts with append-only `UPDATE` revocation |
| **6. `SERIALIZABLE` with bounded retry** | **Feasible (Concurrency only)** | Does not solve RLS visibility alone | Orthogonal | Orthogonal | **Strongest** (catches skew via `40001`) | Moderate (retry loop) | App retry policy | Must pair with verifier & district check |
| **7. Hybrid verifier + `SERIALIZABLE`/Outbox** | **Target Candidate** | Preserved via amended `RESTRICTIVE` policy | Enforced via normalized `expert_district_assignments` | **High** (aggregate-only) | **Strong** (SSI + async outbox catch-up) | Moderate-High | `DB-AUTH-01`, `D-01`..`D-03`, `GATE-02`..`05` | All 7 obligations in Section 25 (`DESIGN_NOT_YET_PROVEN`) |

---

## 20. CANONICAL BLOCKER RECONCILIATION

All 15 canonical blocker IDs are preserved with zero closures or downgrades:

| Blocker ID | Canonical Severity / State | Audit Finding (`PUBLIC_SOURCE_VERIFIED` / `LIVE_DATABASE_UNKNOWN`) |
| :--- | :--- | :--- |
| **`RLS-WRITE-AUTH-01`** | `ACTIVE_BLOCKER` (HIGH) | `regional_signals_author_write_policy` uses broad `FOR ALL` without status `WITH CHECK`. |
| **`RLS-ROLE-ASSIGNMENT-01`** | `ACTIVE_BLOCKER` (HIGH) | `app.current_user_id` mutable via `set_config` in shared session. |
| **`DB-AUTH-01`** | `OWNER_DECISION_REQUIRED` | `acrevia_staging_app`, `acrevia_verifier`, `acrevia_worker_login`, `acrevia_worker` unprovisioned. |
| **`DB-CREDENTIAL-EXPOSURE-01`** | **`OPEN`** (CRITICAL) | `frontend/lib/server/db.ts#L10` still contains hard-coded Neon URI fallback; rotation unproven. |
| **`APP-ROLE-SELF-SELECT-01`** | `ACTIVE_BLOCKER` | Coupled to mutable `app.current_user_id` GUC on `user_roles`. |
| **`EXP-AUTH-01`** | `ACTIVE_BLOCKER` | `districts_covered_json` & `verification_status` unenforced in auth/recovery/RLS; `app.current_user_districts` absent. |
| **`CASCADE-ROLE-DEL-01`** | `ACTIVE_BLOCKER` | Role lifecycle DDL unapplied in live DB (`LIVE_DATABASE_UNKNOWN`). |
| **`TENANT-MEMBERSHIP-01`** | `ACTIVE_BLOCKER` | Recovery leaves `app.current_tenant_id=''`, filtering source rows to 0. |
| **`OWNER-AUTH-01`** | `ACTIVE_BLOCKER` (CRITICAL) | `GATE-02` through `GATE-05` unchecked. |
| **`DB-RLS-01`** | `ACTIVE_BLOCKER` (HIGH) | `a1089411c87d` not executed on live PostgreSQL (`LIVE_DATABASE_UNKNOWN`). |
| **`WRK-DISP-01`** | `ACTIVE_BLOCKER` (HIGH) | No Regional Pulse outbox worker implemented (`backend/app/workers/` absent). |
| **`RES-PULSE-01`** | `ACTIVE_BLOCKER` | Provenance recalculation returns 0 under `FORCE RLS` (`TENANT_DIRECT`). |
| **`RES-PULSE-02`** | `ACTIVE_BLOCKER` | Parent `FOR UPDATE` does not serialize `FarmService.update_farm()`. |
| **`GATE01-PROV-01`** | `ACTIVE_BLOCKER` | `staging-rls-phase07` vs `staging-rls-phase05` discrepancy + physical branch unverified in Mode A. |
| **`RES-PULSE-READ-01`** | `ACTIVE_BLOCKER` | Farmer read boundary unverified under live `FORCE RLS`. |

---

## 21. RESIDUAL-RISK RECONCILIATION

- **`RES-PULSE-01` — MEDIUM:** Global expert/researcher evidence access without district scoping (`rls.py#L910-L920`).
- **`RES-PULSE-02` — MEDIUM:** Snapshot/concurrency skew across multi-query provenance verification under `READ COMMITTED`.
- **`RES-PRIMARY-ROUTING-01` — MEDIUM:** Write-on-read GET routes failing on read replicas (`25006`).
- **`RES-REPLICA-LAG-01` — LOW:** Read-replica lag serving stale signal states.
- **`RES-FREE-TEXT-01` — LOW:** Unredacted PII risk in free-text fields.
- **`DB-GRANT-APPLY-01`:** Retained as **`PROPOSED — OWNER APPROVAL REQUIRED`**.
- **`FARMER_READ_BLOCKED_BY_EVIDENCE_ASSOCIATION_RLS`:** Retained as a descriptive finding only.

---

## 22. OWNER DECISION RECONCILIATION

- **D-01** (Official Advisory Public Visibility vs $N \ge 3$), **D-02** (Source Authenticity & Terminology), **D-03** (Agronomic Peer-Review Workflow), and **DB-AUTH-01** (Trusted Writer Architecture) remain distinct, unapproved `OWNER_DECISION_REQUIRED` items.

---

## 23. GATE STATUS RECONCILIATION (`PUBLIC_SOURCE_VERIFIED`)

From [PHASE_07_OWNER_AUTHORIZATION_AND_EXECUTION_REGISTER.md](file:///c:/Users/gokul/OneDrive/Documents/projects/docs/pilot/security/PHASE_07_OWNER_AUTHORIZATION_AND_EXECUTION_REGISTER.md):
- **GATE-01:** `[x] APPROVED BY OWNER (2026-11-10)` (`staging-rls-phase07`); physical provisioning `LIVE_DATABASE_UNKNOWN`.
- **GATE-02 through GATE-05:** `[ ] UNCHECKED (AWAITING SIGN-OFF)`.
- **Branch Discrepancy:** `staging-rls-phase07` (GATE-01) vs `staging-rls-phase05` (Section 1 & GATE-05).
- **MODE B:** **`NOT_AUTHORIZED`**.

---

## 24. ADVERSARIAL REVIEW (17 EXPLICIT QUESTIONS)

1. **Does a permissive verifier policy overcome the existing restrictive tenant policy?**  
   **No (`STATIC_SQL_SEMANTICS`).** `acrevia_verifier` is in `PUBLIC`, so `{table}_tenant_isolation_policy` (`AS RESTRICTIVE ... TO PUBLIC`, `rls.py#L349-L361`) still applies via `AND`.
2. **If not, what exact policy expression blocks it?**  
   `(ADMIN_BYPASS_SQL OR {column_name}::text = current_setting('app.current_tenant_id', true))` in `{table}_tenant_isolation_policy`.
3. **Can the function owner read records from multiple farms without bypassing RLS?**  
   Only if the `RESTRICTIVE` policy itself is amended to permit `CURRENT_USER::text = 'acrevia_verifier'` scoped to valid signal evidence links.
4. **Where does the function obtain independently trusted district authorization?**  
   Currently **nowhere** (`NOT_ESTABLISHED`). Must use a normalized `expert_district_assignments` table joined with `ExpertProfile.verification_status = 'APPROVED'`.
5. **Can a caller spoof the identity or district context through a mutable GUC?**  
   **Yes (`PUBLIC_SOURCE_VERIFIED`).** Any SQL in the `acrevia_staging_app` session can call `set_config('app.current_user_id', ...)` (`rls.py#L285`).
6. **Does `SECURITY DEFINER` accidentally introduce a new privileged execution boundary?**  
   **Yes** if owned by `SUPERUSER`/`BYPASSRLS`, if `PUBLIC` retains `EXECUTE`, or if `pg_temp` shadows objects.
7. **Does the function owner have more privileges than its intended output requires?**  
   It must read `farms`, `observations`, and `risk_alerts` internally to compute the aggregate, making strict `PUBLIC` revocation, non-`LOGIN`, and `NOBYPASSRLS` mandatory.
8. **Can source mutations occur without invalidating the signal?**  
   **Yes (`PUBLIC_SOURCE_VERIFIED`).** `FarmService.update_farm()` (`farm_service.py#L84-L103`) commits district edits with zero signal lock or outbox event.
9. **Can a new source row appear during the aggregation window?**  
   **Yes** under `READ COMMITTED`; prevented within a snapshot by `REPEATABLE READ` and across concurrent commits by `SERIALIZABLE` (`40001`).
10. **Can evidence be deleted or reassigned while verification is in progress?**  
    **Yes** under current `PRIVILEGE_CROSSWALK` (`UPDATE=True` on `regional_signal_evidences`, `rls.py#L1002`) and missing FK on `evidence_reference_id` (`regional_pulse.py#L50`).
11. **Does the outbox cover every source writer?**  
    **No (`PUBLIC_SOURCE_VERIFIED`).** Zero Regional Pulse outbox writers exist (`webhook_events` is Stage 14 only).
12. **Can asynchronous invalidation leave stale information visible?**  
    **Yes** during the worker processing lag window (eventual consistency).
13. **Can repeated aggregate queries reveal information about individual farms?**  
    **Yes** via differencing or below-threshold counts (`< 3`) if rate limits and threshold masking are absent.
14. **Does the selected lock protocol create deadlock cycles?**  
    Client-side multi-table `FOR SHARE` risks deadlocks with `FarmService`; encapsulating reads inside `verify_regional_signal_provenance()` + `SERIALIZABLE`/Outbox avoids multi-table lock cycles.
15. **Are retries bounded and safe?**  
    Currently **no** `SERIALIZABLE` (`40001`) retry loop or outbox `retry_count` cap exists in Regional Pulse (`NOT_ESTABLISHED`).
16. **Does the proposed architecture preserve append-only evidence?**  
    Only if `passive_deletes="all"`, `ON DELETE RESTRICT`, `REVOKE UPDATE/DELETE`, and removal of `FOR SHARE` on `regional_signal_evidences` are all implemented together.
17. **Which conclusions require live PostgreSQL catalog evidence?**  
    Live `pg_roles` attributes, active `pg_policies`, `relrowsecurity`/`relforcerowsecurity`, `pg_proc` `prosecdef`/`proconfig`, active ACLs (`generate_privilege_grants_ddl()`), and runtime `SERIALIZABLE`/lock behavior (`LIVE_DATABASE_UNKNOWN`).


---

## 25. UNRESOLVED PROOF OBLIGATIONS

Before any implementation or Mode B authorization can be granted, seven proof obligations remain unresolved:
1. **Restrictive Policy Amendment (`RLS`):** Amend `{table}_tenant_isolation_policy` on `farms`, `observations`, and `risk_alerts` so `acrevia_verifier` can read evidence-linked rows without `BYPASSRLS` or `SUPERUSER`.
2. **District & Expert Status Enforcement (`EXP-AUTH-01`):** Replace unverified `districts_covered_json` with normalized `expert_district_assignments` and enforce `ExpertProfile.verification_status == 'APPROVED'`.
3. **Source-Mutation Outbox & Concurrency Protocol (`RES-PULSE-02`):** Implement `SERIALIZABLE`/retry or transactional outbox invalidation across all source writers (`FarmService`, `ObservationService`, `RiskService`).
4. **Role & Privilege Provisioning (`DB-AUTH-01` / `DB-GRANT-APPLY-01`):** Obtain Owner approval for `acrevia_staging_app`, `acrevia_verifier`, `acrevia_worker_login`, and `acrevia_worker`, and invoke `generate_privilege_grants_ddl()` in migration.
5. **Append-Only Evidence Alignment:** Implement `passive_deletes="all"`, `ON DELETE RESTRICT`, and revoke `UPDATE`/`DELETE` on `regional_signal_evidences` while removing client-side `FOR SHARE`.
6. **Credential Containment (`DB-CREDENTIAL-EXPOSURE-01`):** Rotate exposed `neondb_owner` credential in Neon Console and remove hard-coded fallback in `frontend/lib/server/db.ts#L10`.
7. **Live PostgreSQL Catalog Verification (`DB-RLS-01`):** Execute `verify_staging_rls.py` and verifier/concurrency tests in Mode B staging.

---

## 26. CORRECTIVE RECOMMENDATIONS

1. **Amend `RESTRICTIVE` Policies Safely:** Add `OR (CURRENT_USER::text = 'acrevia_verifier' AND EXISTS (...))` inside `farms_tenant_isolation_policy`, `observations_tenant_isolation_policy`, and `risk_alerts_tenant_isolation_policy` rather than relying on a standalone `PERMISSIVE` policy.
2. **Harden `verify_regional_signal_provenance(p_signal_id VARCHAR(36))`:** Own by `acrevia_verifier` (`NOLOGIN NOSUPERUSER NOBYPASSRLS`), `SET search_path = public, pg_temp`, `REVOKE CREATE ON SCHEMA public FROM PUBLIC`, `REVOKE ALL ON FUNCTION ... FROM PUBLIC`, schema-qualify all `public.*` tables, and enforce `SERIALIZABLE` + bounded retry in recovery transactions.
3. **Normalize Expert District Authorization:** Enforce `ExpertProfile.verification_status = 'APPROVED'` and district membership before allowing recovery.
4. **Eliminate Hard-Coded Credential Fallback:** Remove `frontend/lib/server/db.ts#L10` fallback and fail closed when `DATABASE_URL` is absent.

---

## 27. EVIDENCE AND CITATION REGISTER

- **RLS & Privileges:** [backend/app/database/rls.py](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/database/rls.py) (`ADMIN_BYPASS_SQL` L23-27, `TABLE_CLASSIFICATION` L40-250, `set_tenant_context` L253-303, `generate_rls_ddl` L325-970, `PRIVILEGE_CROSSWALK` L977-1037).
- **Session & Config:** [backend/app/database/session.py](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/database/session.py), [backend/app/database/base.py#L28](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/database/base.py#L28).
- **Authentication & Expert Profile:** [backend/app/security/dependencies.py](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/security/dependencies.py), [backend/app/models/expert_profile.py#L25-L32](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/models/expert_profile.py#L25-L32), [backend/app/services/expertconnect/expert_service.py](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/services/expertconnect/expert_service.py).
- **Regional Pulse & Source Services:** [backend/app/api/v1/endpoints/regional_pulse.py#L152-L185](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/api/v1/endpoints/regional_pulse.py#L152-L185), [backend/app/services/regional_pulse_service.py#L395-L570](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/services/regional_pulse_service.py#L395-L570), [backend/app/models/regional_pulse.py#L15-L55](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/models/regional_pulse.py#L15-L55), [backend/app/services/farm_service.py#L84-L113](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/services/farm_service.py#L84-L113), [backend/app/services/riskcast/risk_service.py#L266-L290](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/services/riskcast/risk_service.py#L266-L290), [backend/app/services/webhook_service.py#L132](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/services/webhook_service.py#L132).
- **Migration & Governance:** [a1089411c87d_enable_postgresql_rls_tenant_isolation.py](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/database/migrations/versions/a1089411c87d_enable_postgresql_rls_tenant_isolation.py), [PHASE_07_OWNER_AUTHORIZATION_AND_EXECUTION_REGISTER.md](file:///c:/Users/gokul/OneDrive/Documents/projects/docs/pilot/security/PHASE_07_OWNER_AUTHORIZATION_AND_EXECUTION_REGISTER.md).
- **Credential Exposure (`PUBLIC_SOURCE_VERIFIED`):** [frontend/lib/server/db.ts#L8-L10](file:///c:/Users/gokul/OneDrive/Documents/projects/frontend/lib/server/db.ts#L8-L10) — retains hard-coded Neon URI fallback containing administrative role name and embedded password-like credential (secret value deliberately omitted; `DB-CREDENTIAL-EXPOSURE-01 = OPEN`).
- **PostgreSQL 16 Reference:** `src/backend/rewrite/rowsecurity.c` (permissive `OR` + restrictive `AND`, `SELECT`/`UPDATE` `USING` on locking `SELECT`, `FORCE ROW LEVEL SECURITY`) and `src/backend/parser/analyze.c` (`SELECT` + `UPDATE` 1+ col for `FOR UPDATE`/`FOR SHARE`).

---

## 28. FINAL RELEASE-READINESS VERDICT

`DESIGN_VERDICT: DESIGN_NOT_YET_PROVEN`

`IMPLEMENTATION_STATUS: NOT_IMPLEMENTATION_AUTHORIZED`

`PHASE_07_STATUS: NOT_RELEASED`

`MODE_B_STATUS: NOT_AUTHORIZED`

`LIVE_POSTGRESQL_VERIFICATION: NOT_PERFORMED`

`CANONICAL_BLOCKER_CLOSURE: NONE_AUTHORIZED`
