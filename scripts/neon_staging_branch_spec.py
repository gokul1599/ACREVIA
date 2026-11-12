"""
ACREVIA - Neon Staging Branch Specification & Safe Deployment Harness.
Phase 07 Security Verification (TASK-S07-01).

Generates safe staging branch specifications, verifies environment constraints,
and provides programmatic safety checks preventing accidental execution against production.
"""

import sys
from enum import Enum
from typing import Dict, Any, Tuple
from urllib.parse import urlparse


PRODUCTION_HOST_INDICATORS = [
    "ep-muddy-mode-a1nd6rrb",
    "prod",
    "production",
]


class TargetValidationResult(str, Enum):
    VALID_STAGING_CANDIDATE = "VALID_STAGING_CANDIDATE"
    PRODUCTION_TARGET_DETECTED = "PRODUCTION_TARGET_DETECTED"
    MISSING_TARGET = "MISSING_TARGET"
    MALFORMED_TARGET = "MALFORMED_TARGET"
    UNCLASSIFIABLE_TARGET = "UNCLASSIFIABLE_TARGET"


def validate_database_target(db_url: str) -> TargetValidationResult:
    """
    Rigorously validates a database connection URL candidate.
    Enforces the fail-closed invariant: UNKNOWN_TARGET_MUST_NOT_PROCEED.
    """
    if db_url is None:
        return TargetValidationResult.MISSING_TARGET

    cleaned_url = db_url.strip()
    if not cleaned_url:
        return TargetValidationResult.MISSING_TARGET

    try:
        parsed = urlparse(cleaned_url)
    except Exception:
        return TargetValidationResult.MALFORMED_TARGET

    scheme = (parsed.scheme or "").lower()
    if not scheme or scheme not in (
        "postgresql",
        "postgres",
        "postgresql+psycopg",
        "postgresql+pg8000",
        "postgresql+asyncpg",
    ):
        return TargetValidationResult.MALFORMED_TARGET

    hostname = (parsed.hostname or "").lower()
    path = (parsed.path or "").lower()

    if not hostname:
        return TargetValidationResult.MALFORMED_TARGET

    for indicator in PRODUCTION_HOST_INDICATORS:
        if indicator in hostname or indicator in path:
            return TargetValidationResult.PRODUCTION_TARGET_DETECTED

    # Hostname must be a classifiable endpoint candidate (Neon staging endpoint or explicit local test host)
    if hostname in ("localhost", "127.0.0.1") or hostname.endswith(".neon.tech"):
        return TargetValidationResult.VALID_STAGING_CANDIDATE

    # Any unrecognized remote endpoint without clear staging qualification is unclassifiable
    return TargetValidationResult.UNCLASSIFIABLE_TARGET


def is_production_url(db_url: str) -> bool:
    """
    Fail-closed production and safety check.
    Returns True if target is production OR cannot be positively verified as a safe staging candidate.
    Enforces: UNKNOWN_TARGET_MUST_NOT_PROCEED.
    """
    result = validate_database_target(db_url)
    return result != TargetValidationResult.VALID_STAGING_CANDIDATE


def is_safe_staging_url(db_url: str) -> bool:
    """
    Returns True ONLY if target is explicitly verified as a valid staging candidate.
    """
    return validate_database_target(db_url) == TargetValidationResult.VALID_STAGING_CANDIDATE


# Authoritative Target Configuration Constants for Phase 07
TARGET_BRANCH_NAME = "staging-rls-phase07"
PARENT_BRANCH_NAME = "main"
PROPOSED_PROJECT_ID = "prj_acrevia_pilot"
TARGET_REGION = "aws-ap-southeast-1"  # Singapore
TARGET_COMPUTE_TYPE = "shared-0.25"
TARGET_AUTOSUSPEND_MINUTES = 5
TARGET_DATABASE_NAME = "neondb_staging"
RUNTIME_APPLICATION_ROLE = "acrevia_staging_app"
ADMIN_POLICY_ROLE = "acrevia_admin"
MIGRATION_OWNER_ROLE = "neondb_owner"


def get_staging_branch_specification() -> Dict[str, Any]:
    """
    Returns the formal engineering specification for the isolated Neon Staging Branch.
    All project parameters reference authoritative Phase 07 constants.
    """
    return {
        "branch_name": TARGET_BRANCH_NAME,
        "parent_branch": PARENT_BRANCH_NAME,
        "project_id": PROPOSED_PROJECT_ID,
        "project_id_status": "PROPOSED_PENDING_PROVIDER_VERIFICATION",
        "region": TARGET_REGION,
        "region_status": "PROPOSED_PENDING_PROVIDER_VERIFICATION",
        "compute_type": TARGET_COMPUTE_TYPE,
        "autosuspend_minutes": TARGET_AUTOSUSPEND_MINUTES,
        "database_name": TARGET_DATABASE_NAME,
        "runtime_role": RUNTIME_APPLICATION_ROLE,
        "runtime_role_privileges": {
            "is_superuser": False,
            "bypass_rls": False,
            "can_create_db": False,
            "can_create_role": False,
            "can_truncate": False,
            "can_references": False,
            "can_trigger": False,
            "admin_role_membership": False,
            "status": "UNPROVISIONED_PENDING_GATE_02"
        },
        "admin_role": ADMIN_POLICY_ROLE,
        "admin_role_classification": "POLICY_AUTHORIZED_ADMINISTRATIVE_ROLE",
        "admin_role_privileges": {
            "is_superuser": False,
            "bypass_rls": False,
            "can_create_db": False,
            "can_create_role": False,
            "status": "UNPROVISIONED_PENDING_GATE_02"
        },
        "migration_role": MIGRATION_OWNER_ROLE,
        "migration_role_scope": "MIGRATION_DDL_ONLY_STRICTLY_EXCLUDED_FROM_APPLICATION_POOL",
        "operational_preconditions": [
            "Precondition: Genuine Project Owner sign-off on GATE-01 in authorization register",
            "Precondition: Live parent privacy verification mandatory prior to branch creation",
            "Inheritance notice: Child branch inherits parent branch schema and data state at creation time",
            "Precondition: Synthetic-data provenance must be established separately on parent trunk",
            "Lifecycle governance: Branch deletion is prohibited without separate GATE-05 owner authorization",
            "Post-creation requirement: Branch configuration and compute sizing must be verified post-provisioning"
        ],
        "neon_cli_commands": [
            f"neon branches create --name {TARGET_BRANCH_NAME} --parent {PARENT_BRANCH_NAME} --project-id {PROPOSED_PROJECT_ID}",
            f"neon roles create --branch {TARGET_BRANCH_NAME} --name {RUNTIME_APPLICATION_ROLE} --project-id {PROPOSED_PROJECT_ID}",
            f"neon roles create --branch {TARGET_BRANCH_NAME} --name {ADMIN_POLICY_ROLE} --project-id {PROPOSED_PROJECT_ID}",
            f"neon connection-string --branch {TARGET_BRANCH_NAME} --role {RUNTIME_APPLICATION_ROLE} --project-id {PROPOSED_PROJECT_ID}"
        ],
        "authorization_gate": "OWNER_APPROVAL_REQUIRED_GATE_01"
    }


def main():
    spec = get_staging_branch_specification()
    print("================================================================================")
    print("ACREVIA - ISOLATED NEON STAGING BRANCH SPECIFICATION (PHASE 07)")
    print("================================================================================")
    print(f"Target Branch Name : {spec['branch_name']}")
    print(f"Parent Branch      : {spec['parent_branch']}")
    print(f"Target Project ID  : {spec['project_id']} ({spec['project_id_status']})")
    print(f"Target Region      : {spec['region']} ({spec['region_status']})")
    print(f"Compute Sizing     : {spec['compute_type']} (Auto-suspend: {spec['autosuspend_minutes']}m)")
    print(f"Runtime Role       : {spec['runtime_role']} (NOSUPERUSER, NOBYPASSRLS)")
    print(f"Admin Policy Role  : {spec['admin_role']} ({spec['admin_role_classification']})")
    print(f"Migration Role     : {spec['migration_role']} ({spec['migration_role_scope']})")
    print(f"Authorization Gate : {spec['authorization_gate']}")
    print("--------------------------------------------------------------------------------")
    print("Operational Preconditions & Governance Invariants:")
    for prec in spec["operational_preconditions"]:
        print(f"  [!] {prec}")
    print("--------------------------------------------------------------------------------")
    print("Neon CLI Setup Steps (Execution on hold pending GATE-01 authorization):")
    for cmd in spec["neon_cli_commands"]:
        print(f"  $ {cmd}")
    print("================================================================================")


if __name__ == "__main__":
    main()

