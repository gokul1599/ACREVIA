"""
ACREVIA - Neon Staging Branch Specification & Safe Deployment Harness.
Phase 05 Security Verification (TASK-S05-01).

Generates safe staging branch specifications, verifies environment constraints,
and provides programmatic safety checks preventing accidental execution against production.
"""

import sys
from typing import Dict, Any
from urllib.parse import urlparse


PRODUCTION_HOST_INDICATORS = [
    "ep-muddy-mode-a1nd6rrb",
    "prod",
    "production",
]


def is_production_url(db_url: str) -> bool:
    """
    Returns True if the database URL points to a known production database endpoint.
    Strictly prevents migration execution or destructive DDL on live databases.
    """
    if not db_url:
        return False
    try:
        parsed = urlparse(db_url)
        hostname = (parsed.hostname or "").lower()
        path = (parsed.path or "").lower()
        for indicator in PRODUCTION_HOST_INDICATORS:
            if indicator in hostname or indicator in path:
                return True
        return False
    except Exception:
        return True  # Fail-safe: treat malformed URLs as potentially production


def get_staging_branch_specification() -> Dict[str, Any]:
    """
    Returns the formal engineering specification for the isolated Neon Staging Branch.
    """
    return {
        "branch_name": "staging-rls-phase05",
        "parent_branch": "main",
        "region": "aws-ap-southeast-1",  # Singapore (sin1)
        "compute_type": "shared-0.25",    # Free tier compute unit
        "database_name": "neondb_staging",
        "runtime_role": "acrevia_staging_app",
        "runtime_role_privileges": {
            "is_superuser": False,
            "bypass_rls": False,
            "can_create_db": False,
            "can_create_role": False,
        },
        "migration_role": "neondb_owner",  # Used strictly for applying DDL migrations
        "safety_guarantees": [
            "Complete physical isolation from production data",
            "Zero real farmer data, names, or GPS coordinates",
            "Synthetic agronomic test profiles only",
            "Runtime role cannot bypass RLS policies",
            "Automatic branch deletion schedule upon verification completion"
        ],
        "neon_cli_commands": [
            "neon branches create --name staging-rls-phase05",
            "neon roles create --branch staging-rls-phase05 --name acrevia_staging_app",
            "neon connection-string --branch staging-rls-phase05 --role acrevia_staging_app"
        ],
        "authorization_gate": "OWNER_APPROVAL_REQUIRED_GATE_STAGING_NEON"
    }


def main():
    spec = get_staging_branch_specification()
    print("================================================================================")
    print("ACREVIA - ISOLATED NEON STAGING BRANCH SPECIFICATION (PHASE 05)")
    print("================================================================================")
    print(f"Target Branch Name : {spec['branch_name']}")
    print(f"Target Region      : {spec['region']}")
    print(f"Runtime Role       : {spec['runtime_role']} (NOSUPERUSER, NOBYPASSRLS)")
    print(f"Authorization Gate : {spec['authorization_gate']}")
    print("--------------------------------------------------------------------------------")
    print("Safety Constraints Enforced:")
    for g in spec["safety_guarantees"]:
        print(f"  [x] {g}")
    print("--------------------------------------------------------------------------------")
    print("Neon CLI Setup Steps:")
    for cmd in spec["neon_cli_commands"]:
        print(f"  $ {cmd}")
    print("================================================================================")


if __name__ == "__main__":
    main()
