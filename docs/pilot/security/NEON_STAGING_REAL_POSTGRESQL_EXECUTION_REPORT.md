# ACREVIA — NEON STAGING DATABASE & REAL POSTGRESQL EXECUTION REPORT
## Execution Readiness, Automated Verification Harness, and Production Safeguards

**Programme:** ACREVIA — Agricultural Intelligence Platform  
**Target Geography:** Telangana, India  
**Document Code:** `NEON_STAGING_REAL_POSTGRESQL_EXECUTION_REPORT.md`  
**Execution Date:** November 9, 2026  
**Audited Target:** Isolated Neon Staging Branch Specification & Verification Harness  
**Operational Status:** `BLOCKED_OWNER_AUTHORIZATION` (Harness Verified Locally; Cloud Execution Awaiting Owner Sign-Off)

---

## 1. Environment & Target Specifications

The staging database environment is specified in `scripts/neon_staging_branch_spec.py`:

```json
{
  "branch_name": "staging-rls-phase05",
  "parent_branch": "main",
  "region": "aws-ap-southeast-1",
  "compute_type": "shared-0.25",
  "database_name": "neondb_staging",
  "runtime_role": "acrevia_staging_app",
  "runtime_role_privileges": {
    "is_superuser": false,
    "bypass_rls": false,
    "can_create_db": false,
    "can_create_role": false,
    "admin_role_membership": false
  },
  "admin_role": "acrevia_admin",
  "migration_role": "neondb_owner",
  "authorization_gate": "OWNER_APPROVAL_REQUIRED_GATE_STAGING_NEON"
}
```

---

## 2. Production Protection Safeguards

To prevent accidental command execution against the production Neon cluster, both `scripts/neon_staging_branch_spec.py` and `scripts/verify_staging_rls.py` enforce programmatic host guards:

```python
PRODUCTION_HOST_INDICATORS = [
    "ep-muddy-mode-a1nd6rrb",
    "prod",
    "production",
]

def is_production_url(db_url: str) -> bool:
    parsed = urlparse(db_url)
    hostname = (parsed.hostname or "").lower()
    for indicator in PRODUCTION_HOST_INDICATORS:
        if indicator in hostname:
            return True
    return False
```

If any connection URL containing production host indicators is provided, the script halts with an exit code of `1` before opening a socket.

---

## 3. Database Role Architecture

Three distinct database roles are established for staging:
1. **`neondb_owner` (DDL Migration Role):**
   - Owns the database schema.
   - Executes Alembic migrations (`a1089411c87d`).
   - Grants `SELECT, INSERT, UPDATE, DELETE` to `acrevia_staging_app`.
   - Never used for running application tenant traffic.
2. **`acrevia_staging_app` (Application Runtime Role):**
   - Least privilege: `NOSUPERUSER`, `NOBYPASSRLS`, `NOCREATEDB`, `NOCREATEROLE`.
   - Subject to `FORCE ROW LEVEL SECURITY`.
   - Cannot bypass RLS via `app.is_admin` GUC parameter.
   - Cannot `SET ROLE acrevia_admin`.
3. **`acrevia_admin` (Dedicated Administrative Role):**
   - Dedicated identity for verified administrative cross-tenant operations.
   - Required for `ADMIN_BYPASS_SQL` evaluation.

---

## 4. Alembic Migration `a1089411c87d` Status

- **Revision:** `a1089411c87d`
- **Down Revision:** `f4894a11c87d`
- **File:** `backend/app/database/migrations/versions/a1089411c87d_enable_postgresql_rls_tenant_isolation.py`
- **Coverage:** Iterates over all 132 entities in `TABLE_CLASSIFICATION`, executing `generate_rls_ddl()`.
- **Dialect Guard:** Verifies `bind.dialect.name == "postgresql"`; skips safely in non-PostgreSQL testing environments.
- **Current Execution State:** Verified syntax and DDL generation in unit tests; cloud execution against Neon strictly deferred until explicit owner sign-off on Decision Gate 1.

---

## 5. Automated Verification Harness Capabilities

The updated verification script `scripts/verify_staging_rls.py` performs the following automated audits when connected to an authorized staging database:
1. **Catalog Inspection (`pg_class`):** Audits `relrowsecurity` and `relforcerowsecurity` across all 132 tables.
2. **Policy Inspection (`pg_policies`):** Verifies that both base `PERMISSIVE` and restrictive tenant isolation policies exist.
3. **Role Privilege Inspection (`pg_roles`):** Confirms `rolsuper=false` and `rolbypassrls=false` for the connected user.
4. **Role Membership Inspection (`pg_auth_members`):** Verifies that the connected runtime role has no membership in `acrevia_admin` or `neondb_owner`.
5. **GUC Self-Escalation Probe:** Attempts `SELECT set_config('app.is_admin', 'true', true);` and verifies that the policy predicate evaluates to `can_bypass = false`.

---

## 6. Real vs Simulated Test Results

| Verification Dimension | Environment | Result | Status |
|---|---|---|---|
| DDL Generation & Structure | Local Unit Test | 132 tables covered | COMPLETE_VERIFIED |
| GUC Self-Escalation Block | Local Test Suite | `test_unprivileged_role_guc_self_escalation_blocked` PASSED | COMPLETE_VERIFIED |
| Dual-Factor Admin Bypass | Local Test Suite | `test_admin_role_bypass_requires_both_role_and_guc` PASSED | COMPLETE_VERIFIED |
| Tenant Context Lifecycle | Local Test Suite | 3 `set_config` statements executed with `is_local=true` | COMPLETE_VERIFIED |
| Cross-Tenant Denial | Local Test Suite | HTTP 403 / 404 returned on cross-tenant access | COMPLETE_VERIFIED |
| Cloud Neon Staging Branch | Remote Neon Cloud | Not Executed | BLOCKED_OWNER_AUTHORIZATION |
| Remote Catalog Query (`pg_class`) | Remote Neon Cloud | Awaiting Staging Branch Creation | BLOCKED_OWNER_AUTHORIZATION |

---

## 7. Handover & Blockers

Physical remote execution on Neon is paused at the owner authorization gate. Once the project owner signs Decision Gate 1 in `docs/pilot/security/PHASE_05_OWNER_INPUT_AND_APPROVAL_CHECKLIST.md`, the branch can be created and `scripts/verify_staging_rls.py` executed in a single operational step.
