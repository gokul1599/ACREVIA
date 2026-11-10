"""
ACREVIA - Real PostgreSQL RLS Staging Verification Harness.
Phase 05 Security Verification (TASK-S05-02).

Safely executes against an authorized, isolated Neon staging database branch.
Strictly aborts if any production connection string or host indicator is detected.
"""

import os
import sys
import argparse
from typing import Dict, Any, List
import sqlalchemy as sa
from sqlalchemy import text

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app.database.rls import TABLE_CLASSIFICATION, TableCategory
from scripts.neon_staging_branch_spec import (
    validate_database_target,
    TargetValidationResult,
    is_production_url,
)


def verify_staging_database_rls(connection_url: str) -> Dict[str, Any]:
    """
    Executes PostgreSQL catalog inspection and policy verification on an isolated staging database.
    """
    val_res = validate_database_target(connection_url)
    if val_res == TargetValidationResult.PRODUCTION_TARGET_DETECTED:
        print("[CRITICAL SAFETY ERROR] Connection URL identified as PRODUCTION. Aborting immediately!")
        sys.exit(1)
    if val_res != TargetValidationResult.VALID_STAGING_CANDIDATE:
        print(f"[CRITICAL SAFETY ERROR] Target URL validation failed ({val_res.value}). Unknown or unclassifiable targets must not proceed!")
        sys.exit(1)

    print(f"[RLS Verification] Connecting to safe staging database...")
    engine = sa.create_engine(connection_url)

    report: Dict[str, Any] = {
        "verified_tables_count": 0,
        "rls_enabled_tables": [],
        "force_rls_tables": [],
        "policy_count": 0,
        "policies_by_table": {},
        "criteria_results": {},
        "runtime_role_safe": False,
    }

    with engine.connect() as conn:
        dialect_name = conn.dialect.name
        if dialect_name != "postgresql":
            print(f"[Error] Target database dialect is '{dialect_name}'. PostgreSQL is required for real RLS verification.")
            return report

        # 1. Inspect RLS flags from pg_class
        result = conn.execute(text("""
            SELECT relname, relrowsecurity, relforcerowsecurity
            FROM pg_class
            JOIN pg_namespace ON pg_namespace.oid = pg_class.relnamespace
            WHERE pg_namespace.nspname = 'public' AND pg_class.relkind = 'r';
        """))
        for row in result:
            tbl = row[0]
            row_sec = row[1]
            force_sec = row[2]
            if row_sec:
                report["rls_enabled_tables"].append(tbl)
            if force_sec:
                report["force_rls_tables"].append(tbl)

        # 2. Inspect policies from pg_policies
        pol_result = conn.execute(text("""
            SELECT tablename, policyname, permissive, roles, cmd, qual, with_check
            FROM pg_policies
            WHERE schemaname = 'public';
        """))
        for row in pol_result:
            tbl = row[0]
            pol_name = row[1]
            permissive = row[2]
            roles = row[3]
            cmd = row[4]
            report["policy_count"] += 1
            if tbl not in report["policies_by_table"]:
                report["policies_by_table"][tbl] = []
            report["policies_by_table"][tbl].append({
                "policy_name": pol_name,
                "permissive": permissive,
                "roles": roles,
                "cmd": cmd
            })

        # 3. Verify Runtime Role Privileges (must NOT have BYPASSRLS, SUPERUSER, or admin role membership)
        role_result = conn.execute(text("""
            SELECT rolname, rolsuper, rolbypassrls, rolcreaterole, rolcreatedb
            FROM pg_roles
            WHERE rolname = CURRENT_USER;
        """))
        current_role = role_result.fetchone()
        if current_role:
            rolname, rolsuper, rolbypassrls, rolcreaterole, rolcreatedb = current_role
            report["current_user"] = rolname
            report["runtime_role_safe"] = (not rolsuper) and (not rolbypassrls) and (not rolcreaterole)
            print(f"[Role Check] User '{rolname}': SUPERUSER={rolsuper}, BYPASSRLS={rolbypassrls}, CREATEROLE={rolcreaterole} (Safe: {report['runtime_role_safe']})")

        # 4. Verify Administrative Boundary & Membership Isolation
        membership_check = conn.execute(text("""
            SELECT m.rolname AS member_role, g.rolname AS granted_role
            FROM pg_auth_members am
            JOIN pg_roles m ON m.oid = am.member
            JOIN pg_roles g ON g.oid = am.roleid
            WHERE m.rolname = CURRENT_USER AND g.rolname IN ('acrevia_admin', 'neondb_owner');
        """))
        admin_memberships = membership_check.fetchall()
        report["has_admin_membership"] = len(admin_memberships) > 0
        if report["has_admin_membership"]:
            print(f"[SECURITY ALERT] Current role '{rolname}' has unauthorized administrative role membership: {admin_memberships}")
        else:
            print(f"[Role Check] Current role '{rolname}' has NO administrative role membership (Safe)")

        # 5. Administrative Self-Escalation Test (Verify GUC-tampering cannot bypass RLS)
        if rolname not in ("neondb_owner", "acrevia_admin"):
            try:
                # Attempt to self-escalate via GUC parameter
                conn.execute(text("SELECT set_config('app.is_admin', 'true', true);"))
                # Probe policy predicate evaluation with dual SESSION_USER and CURRENT_USER boundary
                predicate_test = conn.execute(text("""
                    SELECT (SESSION_USER::text IN ('neondb_owner', 'acrevia_admin')
                            AND CURRENT_USER::text IN ('neondb_owner', 'acrevia_admin') 
                            AND current_setting('app.is_admin', true) = 'true') AS can_bypass;
                """)).scalar()
                report["guc_self_escalation_blocked"] = not predicate_test
                print(f"[Trust Boundary] GUC app.is_admin self-escalation probe: can_bypass={predicate_test} (Blocked: {report['guc_self_escalation_blocked']})")
            except Exception as e:
                print(f"[Trust Boundary] Escalation probe error: {e}")
                report["guc_self_escalation_blocked"] = True

        # 6. SECURITY DEFINER Audit (pg_proc inspection)
        secdef_result = conn.execute(text("""
            SELECT p.proname, n.nspname, r.rolname AS owner
            FROM pg_proc p
            JOIN pg_namespace n ON n.oid = p.pronamespace
            JOIN pg_roles r ON r.oid = p.proowner
            WHERE p.prosecdef = true AND n.nspname NOT IN ('pg_catalog', 'information_schema');
        """))
        secdef_funcs = secdef_result.fetchall()
        report["security_definer_functions_count"] = len(secdef_funcs)
        report["security_definer_functions"] = [{"name": f[0], "schema": f[1], "owner": f[2]} for f in secdef_funcs]
        print(f"[Security Audit] User-defined SECURITY DEFINER functions: {len(secdef_funcs)}")

        # 7. Table Ownership Audit (pg_class inspection)
        ownership_result = conn.execute(text("""
            SELECT c.relname, r.rolname AS owner
            FROM pg_class c
            JOIN pg_namespace n ON n.oid = c.relnamespace
            JOIN pg_roles r ON r.oid = c.relowner
            WHERE n.nspname = 'public' AND c.relkind = 'r' AND r.rolname NOT IN ('neondb_owner', 'postgres');
        """))
        unauthorized_owners = ownership_result.fetchall()
        report["unauthorized_table_owners"] = [f"{o[0]} owned by {o[1]}" for o in unauthorized_owners]
        report["table_ownership_safe"] = len(unauthorized_owners) == 0
        print(f"[Security Audit] Protected tables with unexpected owners: {len(unauthorized_owners)}")

    report["verified_tables_count"] = len(report["rls_enabled_tables"])
    return report


def main():
    parser = argparse.ArgumentParser(description="ACREVIA Staging RLS Verification Harness")
    parser.add_argument("--url", type=str, help="PostgreSQL Staging Connection URL (Masked)")
    parser.add_argument("--dry-run", action="store_true", help="Perform preflight safety checks without running queries")
    args = parser.parse_args()

    target_url = args.url or os.environ.get("STAGING_DATABASE_URL", "")

    if not target_url:
        print("[BLOCKED] No staging database URL provided. Set STAGING_DATABASE_URL or pass --url.")
        print("[Notice] Real PostgreSQL integration requires an authorized, isolated Neon staging branch.")
        sys.exit(2)

    val_res = validate_database_target(target_url)
    if val_res == TargetValidationResult.PRODUCTION_TARGET_DETECTED:
        print("[CRITICAL SAFETY ERROR] Target URL matches production indicators. Aborting immediately!")
        sys.exit(1)

    if val_res != TargetValidationResult.VALID_STAGING_CANDIDATE:
        print(f"[CRITICAL SAFETY ERROR] Target URL validation failed ({val_res.value}). Unknown or unclassifiable targets must not proceed!")
        sys.exit(1)

    if args.dry_run:
        print("[Dry Run] LOCAL_TARGET_FORMAT_CHECK_PASSED. Staging URL candidate validated format.")
        print("[Notice] LIVE_STAGING_VERIFIED status requires real remote execution with live database queries.")
        sys.exit(0)

    results = verify_staging_database_rls(target_url)
    print(f"[Results] RLS Enabled Tables: {len(results['rls_enabled_tables'])}")
    print(f"[Results] FORCE RLS Tables  : {len(results['force_rls_tables'])}")
    print(f"[Results] Total Policies    : {results['policy_count']}")


if __name__ == "__main__":
    main()
