# ACREVIA — PHASE 07: PUBLIC REGIONAL PULSE READ-ROUTING, CACHE CONSISTENCY & PRIVACY-BOUNDARY FINAL ADVERSARIAL ASSURANCE REPORT

**Programme:** ACREVIA — Agricultural Intelligence Platform  
**Target Geography:** Telangana, India  
**Phase:** Phase 07 — PostgreSQL RLS Tenant Isolation & Regional Aggregation Privacy  
**Document ID:** `ACR-SEC-P07-READ-ROUTING-CACHE-PRIVACY-AUDIT`  
**Classification:** RESTRICTED — PILOT DATA PRIVACY & CONCURRENCY AUDIT  
**Operating Mode:** **`MODE A ONLY`** (Local Source Inspection, Concurrency Analysis & Offline Verification)  
**Engineering Methodology:** Everything Claude Code (ECC) — `PLAN → TEST → IMPLEMENT ONLY IF DEFECT PROVEN → REVIEW → VERIFY → DOCUMENT`  
**Git HEAD:** `dbad296c6f19c4bbe8eb48fcd7a0e07441cfa408` on branch `main`  
**Overall Determination:** **`TECHNICAL_PREFLIGHT_READY_WITH_RECORDED_BLOCKERS`**  
**Audit Scope:** Public GET consistency, write-on-read mechanics, primary-only read routing, caching layers, empirical privacy window, and field-level zero-PII validation.

---

## 1. Executive Summary

This assurance dossier represents the definitive adversarial evaluation of the ACREVIA Regional Pulse public read subsystem. The investigation rigorously examined the operational realities of dynamic provenance revalidation during public `GET` requests (`/api/v1/regional-pulse/signals` and `/api/v1/regional-pulse/signals/{id}`), inspecting database session routing, application and HTTP cache tiers, service worker behavior, frontend caching, empirical privacy latency, and public payload data privacy.

### Primary Audit Verdicts
1. **Database Routing Architecture:** Defensively classified as **`PRIMARY_ONLY_WRITE_ON_READ`**. The regional pulse public GET endpoints execute write-on-read database mutations when signal provenance falls below threshold ($N < 3$), committing the updated suppression status to the database. The application configures a single SQLAlchemy engine connected directly to the primary database. If misrouted to a PostgreSQL read-replica standby, the transaction fails closed with `SQLSTATE 25006: cannot execute UPDATE in a read-only transaction`, returning HTTP 500 and preventing any unauthorized publication.
2. **Cache Consistency Architecture:** Zero application-level in-memory cache exists on regional pulse endpoints. The FastAPI middleware stack enforces origin anti-caching headers (`Cache-Control: no-cache, no-store, must-revalidate` and `Pragma: no-cache`). The PWA Service Worker explicitly ignores `/api/` network requests. Client web requests execute un-cached `fetch()` operations. Multi-instance API nodes observe committed suppressions immediately upon the subsequent database query under PostgreSQL `READ COMMITTED` isolation. External CDN edge caching behavior is recorded as `DEPLOYMENT_CONFIGURATION_NOT_VERIFIED`.
3. **In-Process Privacy Window:** Defensively classified as **`MEASURED_BUT_NOT_HARD_BOUNDED`**. Empirical micro-benchmarking over 50 consecutive execution cycles demonstrates that in-process provenance revalidation and serialization executes with a median latency of **4.94 ms** (min: 4.47 ms, max: 26.25 ms). However, because operating system thread scheduling, garbage collection, and network transit cannot be hard-bounded by a static constant in multi-tenant cloud environments, hard mathematical latency bounding is rejected.
4. **Field-Level Public Response Privacy:** 100% compliant with zero PII exposure. All 17 fields in `RegionalSignalResponse` were audited. Granular evidence associations (`evidences`) are strictly stripped to `[]` for non-privileged callers (`FARMER`). Zero farmer names, phone numbers, email addresses, plot IDs, or GPS coordinates are exposed. Unauthenticated access is denied at the API boundary with HTTP 401.
5. **Phase 07 Test Suite Status:** **127 passed, 1 warning** in standard mode (17.94s); **127 passed, 2 warnings** in Python optimized mode (`python -O`, 17.65s); **80 passed** in worker security suite; **6 passed** in Stage 12.

---

## 2. Read-Replica Routing Reality & Write-on-Read Mechanics

### 2.1 The Write-on-Read Dynamic Revalidation Architecture
In [`backend/app/services/regional_pulse_service.py`](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/services/regional_pulse_service.py), `revalidate_signal_provenance()` re-evaluates the active distinct farm count supporting a regional signal:

```python
if distinct_farms < 3:
    signal.validation_status = "SUPPRESSED_INSUFFICIENT_PROVENANCE"
    signal.distinct_farms_count = distinct_farms
    return False
```

When an unsuppressed signal loses evidence (e.g. farm archived or observation removed), public GET endpoints (`list_signals` and `get_signal` in [`backend/app/api/v1/endpoints/regional_pulse.py`](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/api/v1/endpoints/regional_pulse.py)) detect the insufficiency and commit the updated suppression status to the database:

```python
is_valid = RegionalPulseService.revalidate_signal_provenance(db, signal.id)
if not is_valid:
    db.commit()  # Commits SUPPRESSED_INSUFFICIENT_PROVENANCE to database
    # Non-privileged caller receives HTTP 404 or filtered list
```

### 2.2 Routing Reality: Single Engine Primary Connection
Inspection of [`backend/app/database/session.py`](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/database/session.py) confirms:
- A single SQLAlchemy `engine` is instantiated using `settings.SQLALCHEMY_DATABASE_URI`.
- `SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)` provides the database session for all API dependencies (`get_db`).
- There is **no read-replica connection pool**, no secondary engine, and no read-write routing middleware in the application codebase.
- Therefore, all read requests (`GET`) execute against the primary read-write database connection.

### 2.3 Standby Read-Replica Failure Mode: SQLSTATE 25006 Fail-Closed
If an external infrastructure load balancer (e.g., PgBouncer pool or cloud proxy) routed `GET /api/v1/regional-pulse/signals` to a PostgreSQL read-replica standby (`default_transaction_read_only = on`):
1. A valid signal ($N \ge 3$) executes read-only SELECT queries and returns HTTP 200.
2. An invalidated signal ($N < 3$) triggers `revalidate_signal_provenance()`, attempting an `UPDATE` on `regional_signals`.
3. PostgreSQL read replica immediately aborts the statement with error:
   $$\mathbf{SQLSTATE\ 25006:\ cannot\ execute\ UPDATE\ in\ a\ read-only\ transaction}$$
4. The endpoint's outer exception handler catches the database error, executes `db.rollback()`, and raises:
   $$\mathbf{HTTPException(status\_code=500,\ detail="Internal\ server\ error")}$$
5. **Security Consequence:** The system **fails closed**. An invalidated signal is NEVER returned to a smallholder farmer as a valid outbreak claim.

Verified via test:
- [`test_regional_pulse_read_replica_sqlstate_25006_fail_closed`](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/tests/test_worker_security_and_privacy.py).

---

## 3. Cache Consistency & Multi-Instance Synchronization

A comprehensive audit was performed across all four potential caching tiers:

| Cache Layer | Architectural Location | Configured Status | Invalidation & Consistency Mechanism |
| :--- | :--- | :--- | :--- |
| **Application In-Memory** | API Process Memory / Redis | **NONE** | No in-memory cache or Redis key-value store is configured for regional pulse queries. All queries hit the database engine directly. |
| **Reverse Proxy / CDN** | Cloudflare / Nginx / ALB | **PREVENTED VIA ORIGIN HEADERS** | `backend/app/main.py` attaches `Cache-Control: no-cache, no-store, must-revalidate` and `Pragma: no-cache`. Origin instructs all intermediaries not to store responses. (`DEPLOYMENT_CONFIGURATION_NOT_VERIFIED` for external edge overrides). |
| **PWA Service Worker** | Browser Client Service Worker | **EXPLICITLY BYPASSED** | `frontend/public/sw.js` lines 39-45 explicitly filters out `/api/` network requests (`if (url.pathname.startsWith('/api/')) return fetch(event.request)`). Signal responses are never cached in browser cache storage. |
| **Frontend Client Application** | React Query / Client State | **NATIVE FETCH** | `frontend/lib/api/client.ts` uses native HTTP `fetch()` with standard request headers. No local client-side persistence or stale cache is maintained. |
| **Multi-Instance API Tier** | Horizontal API Pods / Nodes | **SYNCHRONIZED VIA DB** | In multi-instance deployments, once Node A commits signal suppression to the primary DB, Node B observes the suppression immediately on its next query under PostgreSQL `READ COMMITTED`. No distributed message bus invalidation is required. |

Verified via tests:
- [`test_regional_pulse_anti_caching_and_auth_headers_enforced`](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/tests/test_worker_security_and_privacy.py).

---

## 4. In-Process Privacy Window & Empirical Micro-Benchmark

### 4.1 Threat Model: The In-Process Window
When an evidence record is archived or removed, there is a theoretical duration between the evidence removal and the completion of the dynamic revalidation query on the next public read request.

### 4.2 Empirical Micro-Benchmark Execution
To establish empirical facts under Mode A, a controlled 50-cycle micro-benchmark was executed across provenance revalidation, model serialization, evidence stripping, and database commit.

**Execution Results ($N=50$ Samples):**
- **Provenance Query & Revalidation:**
  - Minimum: `4.246 ms`
  - Median: `4.685 ms`
  - Maximum: `13.989 ms`
- **Pydantic Model Validation & Evidence Stripping:**
  - Minimum: `0.084 ms`
  - Median: `0.093 ms`
  - Maximum: `11.998 ms`
- **Total In-Process Revalidation & Serialization Cycle:**
  - Minimum: `4.471 ms`
  - Median: `4.940 ms`
  - 95th Percentile: `8.512 ms`
  - Maximum: `26.251 ms`

### 4.3 Defensible Engineering Determination: `MEASURED_BUT_NOT_HARD_BOUNDED`
While the in-process execution is consistently fast (~5 ms), the following external variables in live cloud deployments prevent claiming a hard real-time latency guarantee (e.g. "$<50\text{ ms}$"):
1. Operating system kernel process scheduling and thread preemption.
2. PostgreSQL connection pool acquisition queuing under high concurrency.
3. TCP network transmission latencies, packet retransmissions, and TLS termination.
4. Client device browser DOM parsing and rendering performance.

Therefore, the architectural classification is formally recorded as:
$$\mathbf{MEASURED\_BUT\_NOT\_HARD\_BOUNDED}$$

Verified via test:
- [`test_regional_pulse_privacy_window_latency_benchmark`](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/tests/test_worker_security_and_privacy.py).

---

## 5. Field-Level Public Response Privacy Inventory

An exhaustive field-by-field audit of `RegionalSignalResponse` ([`backend/app/schemas/regional_pulse.py`](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/schemas/regional_pulse.py)) was conducted to verify compliance with smallholder data sovereignty:

| # | Field Name | Type | Public Visibility (`FARMER`) | Privileged Visibility (`ADMIN`, `EXPERT`) | PII / Granular Location Exposure |
| :-: | :--- | :--- | :--- | :--- | :--- |
| 1 | `id` | UUID | Visible | Visible | None (Synthetic UUID) |
| 2 | `district` | String | Visible | Visible | Coarse District (e.g., "Warangal") |
| 3 | `state` | String | Visible | Visible | Coarse State ("Telangana") |
| 4 | `crop_id` | String | Visible | Visible | Agronomic Crop Identifier |
| 5 | `signal_category` | String | Visible | Visible | Agronomic Category |
| 6 | `signal_title` | String | Visible | Visible | Non-identifying Summary Title |
| 7 | `signal_summary` | String | Visible | Visible | Non-identifying Agronomic Text |
| 8 | `confidence_tier` | String | Visible | Visible | Platform Confidence Level |
| 9 | `source_observation_count`| Integer| Visible | Visible | Aggregated Count ($\ge 3$) |
| 10 | `distinct_farms_count` | Integer| Visible | Visible | Aggregated Count ($\ge 3$) |
| 11 | `observed_start_date` | Date | Visible | Visible | Coarse Temporal Window |
| 12 | `observed_end_date` | Date | Visible | Visible | Coarse Temporal Window |
| 13 | `validation_status` | String | Visible | Visible | Lifecycle State |
| 14 | `recommended_action` | String | Visible | Visible | Advisory Guidance |
| 15 | `is_outbreak_claim_suppressed`| Boolean | Visible | Visible | Operational Suppression Flag |
| 16 | `evidences` | List | **MASKED TO `[]`** | Populated (`RegionalSignalEvidenceItem`)| **Zero granular evidence exposed to farmers** |
| 17 | `created_at` | Datetime | Visible | Visible | Audit Timestamp |

### Explicit Zero-PII Guarantees
- **Zero Identity Leakage:** The response contains NO `farmer_name`, `phone`, `email`, `owner_id`, or `user_id`.
- **Zero Cadastral Leakage:** The response contains NO `farm_id`, `plot_id`, `survey_number`, or village boundary data.
- **Zero Geographic Coordinates:** The response contains NO `latitude`, `longitude`, GPS bounding boxes, or geo-points.
- **Strict Role Masking:** The `evidences` list is unconditionally set to empty list `[]` for all non-privileged roles.
- **Authentication Wall:** All endpoints require authenticated access via `get_current_user`. Unauthenticated requests receive HTTP 401 Unauthorized.

Verified via test:
- [`test_regional_pulse_field_level_privacy_and_zero_pii`](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/tests/test_worker_security_and_privacy.py).

---

## 6. Risk Alert Status Independence

In [`backend/app/services/regional_pulse_service.py`](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/services/regional_pulse_service.py), signal evidence linked to a `RiskAlert` is evaluated for active provenance:

```python
active_alerts = (
    db.query(RiskAlert.farm_id)
    .filter(
        RiskAlert.id.in_(alert_ids),
        RiskAlert.farm_id.isnot(None),
    )
    .distinct()
    .all()
)
```

### Agronomic & Operational Rationale
1. **Alert Lifecycle vs Evidence Validity:** A smallholder farmer acknowledging (`is_acknowledged = True`) or dismissing (`is_dismissed = True`) an alert on their mobile interface represents personal task tracking, NOT an invalidation of the underlying agronomic threat.
2. **Anti-Tampering & Anti-Suppression:** Allowing an individual dismissal to invalidate a regional signal would permit coordinated dismissal attacks where malicious or uninformed users suppress legitimate disease surge warnings across a district.
3. **Audit Verdict:** Risk alert operational statuses (`is_acknowledged`, `is_dismissed`) correctly do NOT invalidate evidence supporting regional signals.

---

## 7. Comprehensive Offline Test Suite Verification

Full test execution was conducted across all 5 Phase 07 security test files and Stage 12:

```
Test Execution Summary:
- backend/tests/test_target_validation.py: 1 passed
- backend/tests/test_rls_offline_ddl.py: 4 passed
- backend/tests/test_rls_policy_semantics.py: 22 passed
- backend/tests/test_orm_rls_alignment.py: 20 passed
- backend/tests/test_worker_security_and_privacy.py: 80 passed
- Total Phase 07 Test Suite: 127 PASSED (0 failed, 0 skipped, 1 warning)
- Stage 12 Test Suite (test_stage12.py): 6 PASSED
- Python Optimized Mode (python -O -m pytest ...): 127 PASSED (0 failed, 0 skipped, 2 warnings)
```

---

## 8. Preserved Governance Blockers Register

In accordance with strict MODE A governance rules, the following 6 core blockers remain active and unapproved until formal Project Owner sign-off:

| Blocker ID | Severity | Status | Technical Description |
| :--- | :--- | :---: | :--- |
| **`OWNER-AUTH-01`** | **CRITICAL** | **BLOCKING** | Decision Gates 02, 03, 04, and 05 in the Owner Authorization Register remain unapproved. Live infrastructure execution is prohibited. |
| **`DB-RLS-01`** | **HIGH** | **BLOCKING** | Physical PostgreSQL Row-Level Security, `FORCE RLS`, and catalog reflection have not been executed on live PostgreSQL engine in Mode A. |
| **`WRK-DISP-01`** | **HIGH** | **BLOCKING** | Worker dispatch provider remains `NOT_IMPLEMENTED` and fails closed (`DISPATCH_NOT_CONFIGURED`). Requires production scheduler provisioning. |
| **`RES-PULSE-01`** | **MEDIUM** | **RECORDED RISK** | Policy on `regional_signal_evidences` grants role-global access to `AGRICULTURAL_EXPERT` and `RESEARCHER` without district-level scoping. Requires Owner acceptance. |
| **`RES-PULSE-02`** | **MEDIUM** | **RECORDED RISK** | Standard PostgreSQL `READ COMMITTED` multi-statement snapshot divergence during public GET revalidation loop. Requires Owner acceptance. |
| **`GATE01-PROV-01`**| **MEDIUM** | **RECORDED RISK** | Neon staging branch `staging-rls-phase07` recorded as provisioned in local artifacts, but unvalidated via live cloud API in Mode A. |

---

## 9. Final Assurance Determination

$$\mathbf{TECHNICAL\_PREFLIGHT\_READY\_WITH\_RECORDED\_BLOCKERS}$$

The ACREVIA Regional Pulse public GET read architecture, write-on-read suppression mechanics, primary-only routing classification, cache headers, service worker bypass, empirical in-process latency, and field-level zero-PII privacy boundaries are verified, mathematically consistent, and covered by 127 passing automated tests. Phase 07 preflight readiness is established under Mode A.
