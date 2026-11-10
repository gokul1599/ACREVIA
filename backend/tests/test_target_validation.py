"""
ACREVIA - Offline Database Target URL Validation & Safe Staging Harness Regression Test Suite.
Phase 07 Security Verification (TASK-S07-01).

Validates:
1. Missing targets (None, empty, whitespace) -> MISSING_TARGET (fail-closed, treated as unsafe/production)
2. Malformed URLs -> MALFORMED_TARGET (fail-closed)
3. Known production hostnames and indicators -> PRODUCTION_TARGET_DETECTED (fail-closed)
4. Unclassifiable remote hosts -> UNCLASSIFIABLE_TARGET (fail-closed)
5. Valid Neon staging candidates -> VALID_STAGING_CANDIDATE (safe)
6. scripts/verify_staging_rls.py CLI exit code behavior:
   - Missing URL -> exit code 2 ([BLOCKED])
   - Production URL -> exit code 1 ([CRITICAL SAFETY ERROR])
   - Unclassifiable URL -> exit code 1 ([CRITICAL SAFETY ERROR])
   - Valid staging candidate in --dry-run mode -> exit code 0 ([Dry Run] LOCAL_TARGET_FORMAT_CHECK_PASSED)
"""

import os
import subprocess
import sys
from urllib.parse import urlparse

# Ensure project root is in sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from scripts.neon_staging_branch_spec import (
    validate_database_target,
    is_production_url,
    is_safe_staging_url,
    TargetValidationResult,
    PRODUCTION_HOST_INDICATORS,
)


def test_missing_target_empty_string():
    """Verify empty string URL returns MISSING_TARGET and fails closed."""
    res = validate_database_target("")
    assert res == TargetValidationResult.MISSING_TARGET
    assert is_production_url("") is True
    assert is_safe_staging_url("") is False


def test_missing_target_whitespace():
    """Verify whitespace-only URL returns MISSING_TARGET and fails closed."""
    res = validate_database_target("   \t\n  ")
    assert res == TargetValidationResult.MISSING_TARGET
    assert is_production_url("   \t\n  ") is True
    assert is_safe_staging_url("   \t\n  ") is False


def test_missing_target_none():
    """Verify None target returns MISSING_TARGET and fails closed."""
    res = validate_database_target(None)  # type: ignore
    assert res == TargetValidationResult.MISSING_TARGET
    assert is_production_url(None) is True  # type: ignore
    assert is_safe_staging_url(None) is False  # type: ignore


def test_malformed_targets():
    """Verify non-postgres schemes and malformed strings return MALFORMED_TARGET."""
    malformed_cases = [
        "not-a-valid-url",
        "://invalid-uri",
        "http://neon.tech/db",
        "https://staging-branch.neon.tech/mydb",
        "sqlite:///local.db",
        "mysql://user:pass@ep-staging-01.neon.tech/db",
        "postgresql://",
    ]
    for url in malformed_cases:
        res = validate_database_target(url)
        assert res == TargetValidationResult.MALFORMED_TARGET, f"URL {url} should be MALFORMED_TARGET, got {res}"
        assert is_production_url(url) is True
        assert is_safe_staging_url(url) is False


def test_known_production_target_detected():
    """Verify known production hostnames are positively detected as PRODUCTION_TARGET_DETECTED."""
    prod_urls = [
        "postgresql://neondb_owner:npg_secret@ep-muddy-mode-a1nd6rrb.ap-southeast-1.aws.neon.tech/neondb?sslmode=require",
        "postgresql://user:pass@ep-muddy-mode-a1nd6rrb.neon.tech/mydb",
        "postgresql+psycopg://user:pass@ep-muddy-mode-a1nd6rrb.ap-southeast-1.aws.neon.tech/neondb",
    ]
    for url in prod_urls:
        res = validate_database_target(url)
        assert res == TargetValidationResult.PRODUCTION_TARGET_DETECTED, f"Expected PRODUCTION_TARGET_DETECTED for {url}, got {res}"
        assert is_production_url(url) is True
        assert is_safe_staging_url(url) is False


def test_production_indicators_detected():
    """Verify substrings containing 'prod' or 'production' are flagged as production targets."""
    indicator_urls = [
        "postgresql://user:pass@ep-acrevia-prod-branch.neon.tech/neondb",
        "postgresql://user:pass@ep-staging-test.neon.tech/production_db",
        "postgresql://user:pass@ep-app-prod.ap-southeast-1.aws.neon.tech/acrevia",
    ]
    for url in indicator_urls:
        res = validate_database_target(url)
        assert res == TargetValidationResult.PRODUCTION_TARGET_DETECTED, f"Expected PRODUCTION_TARGET_DETECTED for {url}, got {res}"
        assert is_production_url(url) is True
        assert is_safe_staging_url(url) is False


def test_unclassifiable_external_target():
    """Verify non-neon, non-localhost remote databases fail closed as UNCLASSIFIABLE_TARGET."""
    unclassifiable_urls = [
        "postgresql://user:pass@random-cloud-host.example.com/acrevia_staging",
        "postgresql://user:pass@db.internal-network.local/neondb",
        "postgresql://user:pass@192.168.1.100:5432/testdb",
    ]
    for url in unclassifiable_urls:
        res = validate_database_target(url)
        assert res == TargetValidationResult.UNCLASSIFIABLE_TARGET, f"Expected UNCLASSIFIABLE_TARGET for {url}, got {res}"
        assert is_production_url(url) is True, f"Unclassifiable target {url} must fail closed (is_production_url=True)"
        assert is_safe_staging_url(url) is False


def test_valid_staging_candidates():
    """Verify compliant Neon staging branch candidates and localhost test targets are accepted."""
    valid_urls = [
        "postgresql://acrevia_staging_app:secret@ep-staging-rls-phase07.ap-southeast-1.aws.neon.tech/neondb_staging?sslmode=require",
        "postgresql+psycopg://test_user:pass@ep-isolated-stage-99.ap-southeast-1.aws.neon.tech/neondb_staging",
        "postgresql://postgres:postgres@localhost:5432/acrevia_test",
        "postgresql://postgres:postgres@127.0.0.1:5432/acrevia_test",
    ]
    for url in valid_urls:
        res = validate_database_target(url)
        assert res == TargetValidationResult.VALID_STAGING_CANDIDATE, f"Expected VALID_STAGING_CANDIDATE for {url}, got {res}"
        assert is_production_url(url) is False
        assert is_safe_staging_url(url) is True


def test_verify_staging_rls_cli_missing_url():
    """Verify verify_staging_rls.py exits 2 with [BLOCKED] message when no URL is provided."""
    env = os.environ.copy()
    env.pop("STAGING_DATABASE_URL", None)

    cmd = [sys.executable, os.path.join(project_root, "scripts", "verify_staging_rls.py")]
    proc = subprocess.run(cmd, env=env, capture_output=True, text=True)

    assert proc.returncode == 2, f"Expected exit code 2, got {proc.returncode}. Output:\n{proc.stdout}\n{proc.stderr}"
    assert "[BLOCKED]" in proc.stdout, f"Expected '[BLOCKED]' in stdout, got:\n{proc.stdout}"


def test_verify_staging_rls_cli_production_url():
    """Verify verify_staging_rls.py exits 1 with critical safety error for production target."""
    prod_url = "postgresql://neondb_owner:pass@ep-muddy-mode-a1nd6rrb.ap-southeast-1.aws.neon.tech/neondb"
    cmd = [
        sys.executable,
        os.path.join(project_root, "scripts", "verify_staging_rls.py"),
        "--url",
        prod_url,
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)

    assert proc.returncode == 1, f"Expected exit code 1, got {proc.returncode}. Output:\n{proc.stdout}"
    assert "[CRITICAL SAFETY ERROR]" in proc.stdout, f"Expected '[CRITICAL SAFETY ERROR]' in stdout, got:\n{proc.stdout}"


def test_verify_staging_rls_cli_unclassifiable_url():
    """Verify verify_staging_rls.py exits 1 with fail-closed error for unclassifiable remote host."""
    unclassifiable_url = "postgresql://user:pass@external-database.org/testdb"
    cmd = [
        sys.executable,
        os.path.join(project_root, "scripts", "verify_staging_rls.py"),
        "--url",
        unclassifiable_url,
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)

    assert proc.returncode == 1, f"Expected exit code 1, got {proc.returncode}. Output:\n{proc.stdout}"
    assert "UNCLASSIFIABLE_TARGET" in proc.stdout, f"Expected 'UNCLASSIFIABLE_TARGET' in stdout, got:\n{proc.stdout}"


def test_verify_staging_rls_cli_dry_run_valid_staging():
    """Verify verify_staging_rls.py exits 0 and reports LOCAL_TARGET_FORMAT_CHECK_PASSED for valid staging candidate."""
    staging_url = "postgresql://acrevia_staging_app:secret@ep-staging-rls-phase07.ap-southeast-1.aws.neon.tech/neondb_staging"
    cmd = [
        sys.executable,
        os.path.join(project_root, "scripts", "verify_staging_rls.py"),
        "--dry-run",
        "--url",
        staging_url,
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)

    assert proc.returncode == 0, f"Expected exit code 0, got {proc.returncode}. Output:\n{proc.stdout}\n{proc.stderr}"
    assert "LOCAL_TARGET_FORMAT_CHECK_PASSED" in proc.stdout, f"Expected 'LOCAL_TARGET_FORMAT_CHECK_PASSED' in stdout, got:\n{proc.stdout}"
    assert "LIVE_STAGING_VERIFIED status requires real remote execution" in proc.stdout, f"Expected live disclaimer in stdout, got:\n{proc.stdout}"


def run_all_target_validation_tests():
    test_functions = [
        ("1. Missing Target (Empty String) -> MISSING_TARGET", test_missing_target_empty_string),
        ("2. Missing Target (Whitespace) -> MISSING_TARGET", test_missing_target_whitespace),
        ("3. Missing Target (None) -> MISSING_TARGET", test_missing_target_none),
        ("4. Malformed URLs -> MALFORMED_TARGET", test_malformed_targets),
        ("5. Known Production Host -> PRODUCTION_TARGET_DETECTED", test_known_production_target_detected),
        ("6. Production Indicators -> PRODUCTION_TARGET_DETECTED", test_production_indicators_detected),
        ("7. Unclassifiable Remote Target -> UNCLASSIFIABLE_TARGET (fail-closed)", test_unclassifiable_external_target),
        ("8. Valid Neon Staging Candidates -> VALID_STAGING_CANDIDATE", test_valid_staging_candidates),
        ("9. CLI Check: Missing URL exits 2 ([BLOCKED])", test_verify_staging_rls_cli_missing_url),
        ("10. CLI Check: Production URL exits 1 ([CRITICAL SAFETY ERROR])", test_verify_staging_rls_cli_production_url),
        ("11. CLI Check: Unclassifiable URL exits 1 (Fail-closed)", test_verify_staging_rls_cli_unclassifiable_url),
        ("12. CLI Check: Valid Staging candidate with --dry-run exits 0", test_verify_staging_rls_cli_dry_run_valid_staging),
    ]

    print("================================================================================")
    print("ACREVIA - DATABASE TARGET VALIDATION & FAIL-CLOSED SAFETY REGRESSION SUITE")
    print("================================================================================")
    passed = 0
    failed = 0
    for name, func in test_functions:
        try:
            func()
            print(f" [PASS] {name}")
            passed += 1
        except AssertionError as err:
            print(f" [FAIL] {name}: {err}")
            failed += 1
        except Exception as exc:
            print(f" [ERROR] {name}: {exc}")
            failed += 1

    print("--------------------------------------------------------------------------------")
    print(f"Summary: {passed} passed, {failed} failed out of {len(test_functions)} tests.")
    print("================================================================================")
    if failed > 0:
        sys.exit(1)


if __name__ == "__main__":
    run_all_target_validation_tests()
