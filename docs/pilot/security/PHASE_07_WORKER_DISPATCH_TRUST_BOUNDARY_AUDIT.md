# ACREVIA — PHASE 07: RISKCAST WORKER DISPATCH TRUST BOUNDARY & IDENTITY AUDIT

**Programme:** ACREVIA — Agricultural Intelligence Platform  
**Target Geography:** Telangana, India  
**Phase:** Phase 07 — PostgreSQL RLS Tenant Isolation  
**Document ID:** `ACR-SEC-P07-WRK-DISPATCH-AUDIT`  
**Classification:** RESTRICTED — PILOT SECURITY AUDIT  
**Operating Mode:** **`MODE A ONLY`** (Local Source Engineering & Offline Testing)  
**Audit Determination:** **`RESOLVED_LOCALLY_AND_TESTED_WITH_RECORDED_BLOCKERS`**  
- `BOOLEAN_AUTHORIZATION_ELIMINATION`: **`RESOLVED_LOCALLY_AND_TESTED`** (`is_authorized` parameter completely removed; passing boolean raises `TypeError`)  
- `CAPABILITY_AUTHENTICITY_ENFORCEMENT`: **`RESOLVED_LOCALLY_AND_TESTED`** (Direct instantiation blocked via explicit conditional check; requires `DispatchVerifier` authority secret; canonical JSON HMAC-SHA256 tamper digest verified)  
- `COMPLETE_HMAC_PAYLOAD_BINDING`: **`RESOLVED_LOCALLY_AND_TESTED`** (All 10 dimensions bound into canonical UTF-8 JSON payload; timestamp/replay token tampering detected)  
- `FAIL_CLOSED_PRODUCTION_DISPATCH`: **`RESOLVED_LOCALLY_AND_TESTED`** (`ProductionDispatchBlockedError: DISPATCH_NOT_CONFIGURED`)  
- `TRUSTED_ENVIRONMENT_SELECTION`: **`RESOLVED_LOCALLY_AND_TESTED`** (`settings.ENVIRONMENT` governs execution; caller flags cannot override production/staging)  
- `PRE_SESSION_AUTHORIZATION_GATE`: **`RESOLVED_LOCALLY_AND_TESTED`** (`DispatchVerifier.verify_target_authorization` runs on line 1 before database connection or tenant context)  
- `INSTRUMENTED_SESSION_SPY_PROOF`: **`RESOLVED_LOCALLY_AND_TESTED`** (Proved across all 10 invalid conditions: `SessionLocal.call_count == 0`)  
- `THREAD_SAFE_REPLAY_PROTECTION`: **`RESOLVED_LOCALLY_AND_TESTED`** (`threading.Lock()` atomic check-and-consume; 10-thread race test verified)  
- `DISTRIBUTED_REPLAY_PROTECTION`: **`NOT_IMPLEMENTED`** (Process-local memory store; multi-node coordination requires external durable broker)  
- `UNSCOPED_FALLBACK_QUERY_ELIMINATION`: **`RESOLVED_LOCALLY_AND_TESTED`** (`SELECT id FROM farms` completely removed; unbacked calls raise `ValueError`)  
- `FUTURE_DISPATCHER_INTERFACE_CONTRACT`: **`DOCUMENTED_MINIMUM_SPECIFICATION`** (9 dimensions defined)  
- `EXTERNAL_PRODUCTION_SCHEDULER`: **`NOT_IMPLEMENTED`** (Active integration blocker; no external message broker / queue provisioned)  
**Associated Baseline Tests:** `backend/tests/test_worker_security_and_privacy.py` (50 passing tests; 97 across Phase 07 suite; verified under `python -O`)  

---

## 1. Executive Summary & Core Engineering Principle

> [!CRITICAL]
> **A protected-looking Python attribute is not a secret-management system. Immutability $\ne$ Authenticity. A class instance is not an authentic capability.**  
> In this audit, the capability architecture has been subjected to rigorous threat modeling and cryptographic hardening:
> 1. **Assertion Elimination:** Replaced all potential assert-based guards with explicit conditional statements raising dedicated exceptions (`DispatchAuthorizationFailedError`). Verified under optimized Python execution (`python -O`).
> 2. **Canonical Payload Binding:** Eliminated payload ambiguity and replay bypass vulnerabilities by constructing a deterministic UTF-8 JSON canonical representation binding all 10 authorization dimensions (including `schema_version`, `issuer_id`, `actor_identity`, `task_id`, `farm_id`, `purpose`, `environment`, `issued_at`, `expires_at`, and `replay_token`). Altering `issued_at` or `replay_token` invalidates the HMAC signature.
> 3. **Thread-Safe Local Replay Protection:** Wrapped token consumption in a mutex (`threading.Lock()`), verified by concurrent 10-thread race condition tests.
> 4. **Honest Topological Limits:** Explicitly classified distributed multi-node replay protection as **`NOT_IMPLEMENTED`**; an in-memory set cannot coordinate across distributed worker processes.

---

## 2. Threat Model Disambiguation: Four Security Layers

The system distinguishes four discrete trust and defense boundaries:

```mermaid
flowchart TD
    subgraph L1["Layer 1: Accidental Caller Construction"]
        A["Accidental instantiation in code"] -->|Blocked by _internal_auth_key != secret| B["DispatchAuthorizationFailedError"]
    end

    subgraph L2["Layer 2: Untrusted External Request Data"]
        C["Forged / Tampered API payloads"] -->|Blocked by HMAC-SHA256 signature verification| D["Constant-time hmac.compare_digest()"]
    end

    subgraph L3["Layer 3: Inter-Module In-Process Boundary"]
        E["Untrusted code within same Python interpreter"] -.->|Protected by convention & encapsulation ONLY| F["NOT an impenetrable sandbox boundary"]
    end

    subgraph L4["Layer 4: In-Process Compromise / RCE"]
        G["Arbitrary Code Execution in process"] -.->|Class/Module memory inspection possible| H["In-process secrets CANNOT defend against RCE"]
    end
```

1. **Protection Against Accidental Capability Construction (`RESOLVED_LOCALLY_AND_TESTED`):**
   Callers cannot instantiate `DispatchAuthorization` without supplying `_internal_auth_key == DispatchVerifier.get_internal_authority_secret()`. Passing arbitrary parameters raises `DispatchAuthorizationFailedError("MANUALLY_CONSTRUCTED_CAPABILITY_REJECTED")`. Verified by unit test `test_capability_secret_getter_in_process_boundary`.
2. **Protection Against Untrusted External Request Data (`RESOLVED_LOCALLY_AND_TESTED`):**
   External callers and edge services without access to the signing authority cannot forge a valid HMAC digest over arbitrary farm UUIDs. Constant-time HMAC comparison prevents timing attacks.
3. **Protection Against Other Modules in the Trusted Process (`INFORMATIONAL_LIMITATION`):**
   A leading underscore (`_AUTHORITY_SECRET`) or method getter (`get_internal_authority_secret()`) is a Python modular convention, not a hardware-isolated boundary. Any Python code running in the same interpreter address space can invoke `DispatchVerifier.get_internal_authority_secret()` and construct capabilities. Unit test `test_capability_secret_getter_in_process_boundary` proves that an internal caller can legitimately obtain the key, confirming the boundary is designed against external data forgery and caller mistakes, NOT hostile in-process co-tenants.
4. **Protection Against Arbitrary In-Process Code Execution (`UNPROTECTABLE_IN_PROCESS`):**
   ACREVIA makes **no false claim** that an in-process secret can defend against an attacker with arbitrary code execution (RCE) inside the Python runtime. Process-level compromise requires OS sandboxing, container boundaries, or separate process execution.

---

## 3. Authority Secret Lifecycle & Entropy Analysis

- **Secret Source:** Generated at module load via `secrets.token_hex(32)`.
  - Cryptographically secure pseudorandom number generator (CSPRNG via OS entropy source: `/dev/urandom` / Windows CryptGenRandom).
  - Entropy: 256 bits (32 bytes hex-encoded = 64 characters).
- **Lifecycle Scope:** Ephemeral per Python process instance.
- **Production Requirements (`NOT_IMPLEMENTED`):**
  - In a production distributed architecture, token verification requires an asymmetric key pair (e.g. Ed25519) or an external Key Management Service (AWS KMS / HashiCorp Vault) with automated secret rotation, key-version headers (`kid`), and audit logging.
  - Because no external dispatch provider is configured, production dispatch remains `NOT_IMPLEMENTED` and fails closed with `ProductionDispatchBlockedError: DISPATCH_NOT_CONFIGURED`.

---

## 4. Complete Canonical HMAC Payload Specification

To eliminate canonicalization attacks, timestamp manipulation, and replay token spoofing, [`compute_canonical_capability_payload()`](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/tasks/run_riskcast_batch.py) serializes claims into a strictly ordered, compact UTF-8 JSON byte string:

```python
def compute_canonical_capability_payload(
    schema_version: str,
    issuer_id: str,
    dispatcher_identity: str,
    task_id: str,
    farm_id: str,
    purpose: str,
    environment: str,
    issued_at_iso: str,
    expires_at_iso: str,
    replay_token: str,
) -> bytes:
    payload_dict = {
        "schema_version": schema_version,
        "issuer_id": issuer_id,
        "dispatcher_identity": dispatcher_identity,
        "task_id": task_id,
        "farm_id": farm_id,
        "purpose": purpose,
        "environment": environment,
        "issued_at": issued_at_iso,
        "expires_at": expires_at_iso,
        "replay_token": replay_token,
    }
    return json.dumps(payload_dict, sort_keys=True, separators=(",", ":")).encode("utf-8")
```

### The 10 Bound Dimensions:
1. `schema_version`: Protocol version (`"v1"`).
2. `issuer_id`: Authoritative dispatch authority identifier (`"acrevia:dispatcher:local_authority"`).
3. `dispatcher_identity`: Authenticated dispatch service actor (`actor_identity`).
4. `task_id`: Unique batch task execution identifier.
5. `farm_id`: Exact target farm UUID (strict 1:1 binding).
6. `purpose`: Explicit evaluation purpose (`"DAILY_RISKCAST_EVALUATION"`).
7. `environment`: Deployment audience (`"development"` / `"test"`).
8. `issued_at`: UTC timestamp normalized to ISO 8601 (`"YYYY-MM-DDTHH:MM:SS.ffffff+00:00"`).
9. `expires_at`: UTC expiration timestamp or `"NONE"`.
10. `replay_token`: Unique deterministic replay nonce (`f"tok:{task_id}:{farm_id}:{issued_at_iso}"`).

### Mathematical Integrity Formula:
$$\mathbf{\text{Tamper Digest}} = \text{HMAC-SHA256}\Big(K_{\text{authority}}, \; \text{JSON}_{\text{sorted, compact}}\big(\text{Claims}_{1..10}\big)\Big)$$

### 10-Dimension Independent Mutation Verification:
Verified comprehensively by unit test `test_canonical_capability_all_ten_fields_independent_mutation`, which independently mutates *every single one* of the 10 fields and proves verification fails closed:
1. `schema_version`: Mutation to `"v2"` causes digest mismatch -> `False`.
2. `issuer_id`: Mutation to unauthorized issuer causes digest mismatch -> `False`.
3. `dispatcher_identity`: Mutation of worker identity causes digest mismatch -> `False`.
4. `task_id`: Mutation of task UUID causes digest mismatch -> `False`.
5. `farm_id`: Mutation of farm UUID causes digest mismatch -> `False`.
6. `purpose`: Mutation to unauthorized purpose causes digest mismatch -> `False`.
7. `environment`: Mutation of target environment causes digest mismatch -> `False`.
8. `issued_at`: Mutation of timestamp by even 1 second alters digest -> `False`.
9. `expires_at`: Mutation of expiration timestamp alters digest -> `False`.
10. `replay_token`: Mutation of replay nonce alters digest -> `False`.

### Mandatory Expiration Enforcement Rules:
Verified by unit test `test_mandatory_expiration_enforcement_boundary`:
- Omitted or `None` expiration is strictly rejected (`MANDATORY_EXPIRATION_REQUIRED`).
- Naive datetime lacking UTC timezone is rejected for `issued_at` (`TIMEZONE_AWARE_ISSUED_AT_REQUIRED`) and `expires_at` (`TIMEZONE_AWARE_EXPIRATION_REQUIRED`).
- Negative or zero lifetime (`expires_at <= issued_at`) is rejected (`INVALID_EXPIRATION_WINDOW`).
- Excessive lifetime exceeding 24 hours (`expires_at - issued_at > 24 hours`) is rejected (`EXCESSIVE_EXPIRATION_WINDOW`).
- Expired tokens presented at evaluation time are rejected (`Authorization expired`).

---

## 5. Replay Protection: Thread Safety, Lifecycle & Distributed Limits

### 1. Replay Token Lifecycle Semantics
```mermaid
stateDiagram-v2
    [*] --> ISSUED: DispatchVerifier.issue_test_authorization()
    ISSUED --> PRESENTED: Submitted to evaluate_single_farm()
    PRESENTED --> VERIFIED: Signature, Target, Purpose & Env Match
    VERIFIED --> CONSUMED: Atomic consume_replay_token() under Lock
    CONSUMED --> TASK_STARTED: SessionLocal() acquired & set_tenant_context()
    TASK_STARTED --> TASK_COMPLETED: RiskCast evaluation commits
    TASK_STARTED --> TASK_FAILED: Error during plot evaluation
    TASK_FAILED --> GOVERNED_RETRY: Fresh token issued with new Task ID & Nonce
    CONSUMED --> REPLAY_REJECTED: Re-submitted with same replay_token
```

### 2. Thread Safety & Race-Condition Defense
`DispatchVerifier.consume_replay_token()` executes inside a `threading.Lock()` critical section.
- **Concurrent 10-Thread Race Test:** [`test_replay_store_concurrent_race_and_legitimate_retry`](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/tests/test_worker_security_and_privacy.py) executes 10 concurrent threads racing to consume the exact same token.
- **Observed Result:** Exactly 1 thread successfully consumes the token; all 9 concurrent threads raise `DispatchAuthorizationFailedError: REPLAY_DETECTED`.
- **Legitimate Task Retry Support:** When an evaluation fails, a retry attempt with a freshly issued capability token (with unique task ID and fresh replay token) succeeds.
- **Capacity High-Water & Fail-Closed Guard:** When the in-memory token store exceeds 5,000 entries, it prunes expired tokens. If capacity remains exceeded, it fails closed with `DispatchAuthorizationFailedError: REPLAY_STORE_CAPACITY_EXCEEDED` rather than allowing unmonitored replays (verified by `test_replay_store_capacity_high_water_fail_closed`).

### 3. Limitation Disclosure: Distributed Replay is `NOT_IMPLEMENTED`
- **Process-Local Storage:** `CONSUMED_TOKENS` resides in heap memory of a single Python interpreter.
- **Process Restart:** Replay history is cleared upon process restart.
- **Multi-Node Topologies:** Separate worker instances or containers maintain isolated sets and cannot coordinate replay detection.
- **Classification:** Distributed replay protection is formally classified as **`NOT_IMPLEMENTED`**. Production deployment requires an atomic external datastore (e.g. Redis `SET key value NX PX ttl` or PostgreSQL unique constraint).

---

## 6. Pre-Database Rejection Proof Across All 10 Conditions

Verified via [`test_dispatch_authorization_rejection_pre_database_spies_all_10_conditions`](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/tests/test_worker_security_and_privacy.py):

| # | Tested Condition | Test Input / Attack Vector | Error Raised | Session Checkout (`SessionLocal.call_count`) |
| :-: | :--- | :--- | :--- | :-: |
| **1** | Missing Authorization | `authorization=None` | `DispatchAuthorizationFailedError` | **`0 (BLOCKED)`** |
| **2** | Invalid Capability Type | `authorization="invalid-string"` | `DispatchAuthorizationFailedError` | **`0 (BLOCKED)`** |
| **3** | Direct Manual Construction | `DispatchAuthorization(...)` called directly | `DispatchAuthorizationFailedError` | **`0 (BLOCKED)`** |
| **4** | Tampered Payload / Digest | Mutated payload attribute or corrupted digest | `DispatchAuthorizationFailedError` | **`0 (BLOCKED)`** |
| **5** | Target Farm Mismatch | Token for Farm A presented for Farm B | `DispatchAuthorizationFailedError` | **`0 (BLOCKED)`** |
| **6** | Task Purpose Mismatch | Token for `AD_HOC_SCAN` presented for `DAILY_RISKCAST` | `DispatchAuthorizationFailedError` | **`0 (BLOCKED)`** |
| **7** | Environment Mismatch | Token for `development` presented in `test` | `DispatchAuthorizationFailedError` | **`0 (BLOCKED)`** |
| **8** | Expired Capability Grant | `expires_at < now(utc)` | `DispatchAuthorizationFailedError` | **`0 (BLOCKED)`** |
| **9** | Replayed Capability Token | Token submitted second time after consumption | `DispatchAuthorizationFailedError` | **`0 (BLOCKED)`** |
| **10** | Production Guard Fail-Closed | `settings.ENVIRONMENT = "production"` | `ProductionDispatchBlockedError` | **`0 (BLOCKED)`** |

---

## 7. Test Suite Verification & Execution Evidence

- **Total Phase 07 Tests:** **`97 passed, 1 warning`** across all 5 test files.
- **Worker Security & Privacy Suite:** **`50 passed`** in `backend/tests/test_worker_security_and_privacy.py`.
- **Optimized Python Mode Verification:**
  ```powershell
  $env:VIRTUAL_ENV = "$PWD\.venv"; $env:PYTHONPATH = "$PWD;$PWD\.venv\Lib\site-packages"; & C:\Users\gokul\AppData\Roaming\uv\python\cpython-3.11-windows-x86_64-none\python.exe -O -m pytest backend/tests/test_target_validation.py backend/tests/test_rls_offline_ddl.py backend/tests/test_rls_policy_semantics.py backend/tests/test_orm_rls_alignment.py backend/tests/test_worker_security_and_privacy.py
  ```
  Result: **`97 passed, 2 warnings in 13.11s`** (proving zero authorization guards rely on Python `assert`).
