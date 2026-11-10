"""
ACREVIA - PostgreSQL RLS Policy Semantics, Authentication Lifecycle & Trust Boundary Test Suite.
Phase 07 Security Remediation (TASK-S07-02).

Independent, offline verification of:
1. Shared-reference policy semantics (public read, admin write, private operational secrecy).
2. Community collaborative table-specific authorization (author ownership, consent privacy, anti-forgery).
3. Authentication context lifecycle under FORCE RLS (context established before user lookup).
4. Farm access validation under FORCE RLS (candidate context lifecycle, membership verification, fail-closed cleanup).
5. Administrative role separation (application ADMIN vs PostgreSQL database roles).
"""

import os
import sys
from unittest.mock import MagicMock, patch
import pytest

# Ensure project root is in sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from backend.app.database.rls import (
    TABLE_CLASSIFICATION,
    TableCategory,
    generate_rls_ddl,
    set_tenant_context,
    clear_tenant_context,
    ADMIN_BYPASS_SQL,
    ADMIN_ROLES,
)
from backend.app.security.dependencies import (
    get_current_user,
    verify_farm_access,
    require_roles,
)
from backend.app.core.security import create_access_token
from backend.app.core.exceptions import AuthenticationException
from backend.app.security.permissions import SystemRole


# ==============================================================================
# PART 1: SHARED REFERENCE POLICY TESTS
# ==============================================================================

def test_shared_reference_public_read_unblocked():
    """Verify public reference tables have PERMISSIVE SELECT and NO restrictive policy blocking read."""
    for tbl in ["crops", "roles", "risk_rules", "crop_varieties", "market_commodities"]:
        ddl = generate_rls_ddl(tbl, TableCategory.SHARED_REFERENCE)
        assert "ALTER TABLE " + tbl + " ENABLE ROW LEVEL SECURITY;" in ddl
        assert "CREATE POLICY " + tbl + "_shared_read_policy ON " + tbl in ddl
        assert "AS PERMISSIVE" in ddl
        assert "FOR SELECT" in ddl
        assert "USING (true)" in ddl
        # Critical security check: NO restrictive FOR ALL policy that would block SELECT
        assert "AS RESTRICTIVE" not in ddl, f"Table {tbl} must NOT have AS RESTRICTIVE policy"


def test_shared_reference_admin_write_permissive():
    """Verify shared reference tables have PERMISSIVE admin write policy requiring ADMIN_BYPASS_SQL."""
    for tbl in ["crops", "roles", "risk_rules"]:
        ddl = generate_rls_ddl(tbl, TableCategory.SHARED_REFERENCE)
        assert "CREATE POLICY " + tbl + "_admin_write_policy ON " + tbl in ddl
        assert "AS PERMISSIVE" in ddl
        assert "FOR ALL" in ddl
        assert ADMIN_BYPASS_SQL in ddl


def test_sensitive_shared_tables_private_operational():
    """Verify sensitive operational tables (ingestion_jobs, partner_integrations) have ZERO public read."""
    for tbl in ["ingestion_jobs", "partner_integrations", "integration_partners"]:
        ddl = generate_rls_ddl(tbl, TableCategory.SHARED_REFERENCE)
        assert "ALTER TABLE " + tbl + " ENABLE ROW LEVEL SECURITY;" in ddl
        assert "ALTER TABLE " + tbl + " FORCE ROW LEVEL SECURITY;" in ddl
        # Must NOT have any public read policy
        assert "_shared_read_policy" not in ddl or "USING (true)" not in ddl
        assert "USING (true)" not in ddl, f"Sensitive table {tbl} must NOT have public USING (true)"
        assert "CREATE POLICY " + tbl + "_admin_write_policy ON " + tbl in ddl
        assert ADMIN_BYPASS_SQL in ddl


# ==============================================================================
# PART 2: COMMUNITY COLLABORATIVE POLICY TESTS
# ==============================================================================

def test_community_posts_author_isolation():
    """Verify community_posts uses author_id for writes and prevents cross-user tampering."""
    ddl = generate_rls_ddl("community_posts", TableCategory.COMMUNITY_COLLABORATIVE)
    assert "ALTER TABLE community_posts ENABLE ROW LEVEL SECURITY;" in ddl
    assert "ALTER TABLE community_posts FORCE ROW LEVEL SECURITY;" in ddl
    assert "CREATE POLICY community_posts_public_read_policy ON community_posts" in ddl
    assert "CREATE POLICY community_posts_author_write_policy ON community_posts" in ddl
    assert "author_id::text = current_setting('app.current_user_id', true)" in ddl
    # Check that generic unverified user condition is replaced with row author equality
    assert "AS RESTRICTIVE" not in ddl


def test_community_reports_strict_privacy():
    """Verify community_reports has zero public read and is visible only to reporter or admin."""
    ddl = generate_rls_ddl("community_reports", TableCategory.COMMUNITY_COLLABORATIVE)
    assert "ALTER TABLE community_reports ENABLE ROW LEVEL SECURITY;" in ddl
    assert "ALTER TABLE community_reports FORCE ROW LEVEL SECURITY;" in ddl
    # Must NOT allow public read
    assert "OR true" not in ddl
    assert "reported_by_user_id::text = current_setting('app.current_user_id', true)" in ddl


def test_research_consents_strict_privacy():
    """Verify research_consents is restricted to the farmer who granted consent or admin."""
    ddl = generate_rls_ddl("research_consents", TableCategory.COMMUNITY_COLLABORATIVE)
    assert "ALTER TABLE research_consents ENABLE ROW LEVEL SECURITY;" in ddl
    assert "ALTER TABLE research_consents FORCE ROW LEVEL SECURITY;" in ddl
    # Strict privacy: no public read
    assert "OR true" not in ddl
    assert "farmer_id::text = current_setting('app.current_user_id', true)" in ddl


def test_regional_signals_admin_only_write():
    """Verify regional_signals enforces minimum farms threshold and can ONLY be modified by database admin."""
    ddl = generate_rls_ddl("regional_signals", TableCategory.COMMUNITY_COLLABORATIVE)
    assert "ALTER TABLE regional_signals ENABLE ROW LEVEL SECURITY;" in ddl
    assert "ALTER TABLE regional_signals FORCE ROW LEVEL SECURITY;" in ddl
    assert "CREATE POLICY regional_signals_public_read_policy ON regional_signals" in ddl
    assert "distinct_farms_count >= 3" in ddl
    assert "CREATE POLICY regional_signals_author_write_policy ON regional_signals" in ddl
    # Writes strictly require ADMIN_BYPASS_SQL (no ordinary user write access)
    assert ADMIN_BYPASS_SQL in ddl


# ==============================================================================
# PART 3: AUTHENTICATION CONTEXT ORDERING TESTS
# ==============================================================================

def test_authentication_context_established_before_user_lookup():
    """Verify get_current_user establishes user context before querying db.get(User, user_id)."""
    mock_db = MagicMock()
    mock_user = MagicMock()
    mock_user.id = "usr-test-123"
    mock_user.is_active = True
    role_mock = MagicMock()
    role_mock.id = "FARMER"
    mock_user.roles = [role_mock]

    context_history = []

    def fake_set_tenant_context(session, tenant_id=None, user_id=None, is_admin=False):
        context_history.append(("set_tenant_context", user_id))

    def fake_db_get(model, ident):
        context_history.append(("db_get", ident))
        return mock_user

    mock_db.get.side_effect = fake_db_get

    token = create_access_token(subject="usr-test-123", roles=["FARMER"])

    with patch("backend.app.security.dependencies.set_tenant_context", side_effect=fake_set_tenant_context):
        user = get_current_user(token=token, db=mock_db)

    assert user.id == "usr-test-123"
    # Invariant: set_tenant_context MUST appear before db_get in the execution order
    assert len(context_history) >= 2
    assert context_history[0] == ("set_tenant_context", "usr-test-123"), "Context must be set before user query!"
    assert context_history[1] == ("db_get", "usr-test-123"), "User query must follow context initialization!"


def test_authentication_inactive_user_clears_context():
    """Verify that an inactive user lookup fails and candidate user context is cleared."""
    mock_db = MagicMock()
    mock_user = MagicMock()
    mock_user.id = "usr-inactive"
    mock_user.is_active = False
    mock_db.get.return_value = mock_user

    token = create_access_token(subject="usr-inactive", roles=["FARMER"])
    cleared = []

    def fake_set_tenant_context(session, tenant_id=None, user_id=None, is_admin=False):
        if user_id is None:
            cleared.append(True)

    with patch("backend.app.security.dependencies.set_tenant_context", side_effect=fake_set_tenant_context):
        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(token=token, db=mock_db)
        assert exc_info.value.status_code == 401
        assert len(cleared) > 0, "Context must be cleared on inactive user rejection!"


# ==============================================================================
# PART 4: FARM ACCESS LIFECYCLE TESTS
# ==============================================================================

def test_farm_access_candidate_context_set_before_lookup():
    """Verify verify_farm_access establishes candidate tenant context before db.get(Farm, farm_id)."""
    mock_db = MagicMock()
    mock_user = MagicMock()
    mock_user.id = "usr-owner"
    role_mock = MagicMock()
    role_mock.id = "FARMER"
    mock_user.roles = [role_mock]

    mock_farm = MagicMock()
    mock_farm.id = "farm-101"
    mock_farm.owner_id = "usr-owner"
    mock_farm.is_archived = False

    order = []

    def fake_set_tenant_context(session, tenant_id=None, user_id=None, is_admin=False):
        order.append(("set_tenant_context", tenant_id))

    def fake_db_get(model, ident):
        order.append(("db_get", ident))
        return mock_farm

    mock_db.get.side_effect = fake_db_get

    with patch("backend.app.security.dependencies.set_tenant_context", side_effect=fake_set_tenant_context):
        farm = verify_farm_access(farm_id="farm-101", user=mock_user, db=mock_db)

    assert farm.id == "farm-101"
    assert order[0] == ("set_tenant_context", "farm-101"), "Candidate tenant context must be set before farm query!"
    assert order[1] == ("db_get", "farm-101"), "Farm lookup must follow candidate context initialization!"


def test_farm_access_unauthorized_clears_candidate_context():
    """Verify unauthorized cross-farm access clears candidate context and raises 403."""
    mock_db = MagicMock()
    mock_user = MagicMock()
    mock_user.id = "usr-intruder"
    role_mock = MagicMock()
    role_mock.id = "FARMER"
    mock_user.roles = [role_mock]

    mock_farm = MagicMock()
    mock_farm.id = "farm-victim"
    mock_farm.owner_id = "usr-real-owner"
    mock_farm.is_archived = False
    mock_db.get.return_value = mock_farm
    mock_db.query.return_value.filter.return_value.first.return_value = None  # No membership

    cleared = []

    def fake_set_tenant_context(session, tenant_id=None, user_id=None, is_admin=False):
        if tenant_id is None:
            cleared.append(True)

    with patch("backend.app.security.dependencies.set_tenant_context", side_effect=fake_set_tenant_context):
        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc_info:
            verify_farm_access(farm_id="farm-victim", user=mock_user, db=mock_db)
        assert exc_info.value.status_code == 403
        assert len(cleared) > 0, "Candidate context must be cleared when access is rejected!"


def test_farm_access_archived_farm_clears_context():
    """Verify accessing an archived farm clears candidate context and raises 404."""
    mock_db = MagicMock()
    mock_user = MagicMock()
    mock_user.id = "usr-owner"
    role_mock = MagicMock()
    role_mock.id = "FARMER"
    mock_user.roles = [role_mock]

    mock_farm = MagicMock()
    mock_farm.id = "farm-archived"
    mock_farm.owner_id = "usr-owner"
    mock_farm.is_archived = True
    mock_db.get.return_value = mock_farm

    cleared = []

    def fake_set_tenant_context(session, tenant_id=None, user_id=None, is_admin=False):
        if tenant_id is None:
            cleared.append(True)

    with patch("backend.app.security.dependencies.set_tenant_context", side_effect=fake_set_tenant_context):
        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc_info:
            verify_farm_access(farm_id="farm-archived", user=mock_user, db=mock_db)
        assert exc_info.value.status_code == 404
        assert len(cleared) > 0, "Candidate context must be cleared for archived farms!"


# ==============================================================================
# PART 5: ADMINISTRATIVE DISTINCTION TESTS
# ==============================================================================

def test_application_admin_is_not_native_bypass():
    """Verify application ADMIN role does not grant native bypass or match database admin roles."""
    assert "acrevia_staging_app" not in ADMIN_ROLES
    assert "FARMER" not in ADMIN_ROLES
    assert "ADMIN" not in ADMIN_ROLES  # Application role string != database role identifier
    assert ADMIN_ROLES == ("neondb_owner", "acrevia_admin")


def test_missing_guc_fails_closed():
    """Verify ADMIN_BYPASS_SQL safely returns null/false when app.is_admin is missing or unset."""
    # Second parameter of current_setting('app.is_admin', true) ensures missing parameter returns NULL (not error)
    assert "current_setting('app.is_admin', true) = 'true'" in ADMIN_BYPASS_SQL


def run_all_policy_semantics_tests():
    test_functions = [
        ("1. Shared Reference: Public Read Unblocked (No RESTRICTIVE FOR ALL)", test_shared_reference_public_read_unblocked),
        ("2. Shared Reference: Admin Write Permissive", test_shared_reference_admin_write_permissive),
        ("3. Sensitive Reference: Ingestion/Integration Private Operational", test_sensitive_shared_tables_private_operational),
        ("4. Community Collaborative: Author ID Equality Isolation", test_community_posts_author_isolation),
        ("5. Community Reports: Strict Reporter Privacy", test_community_reports_strict_privacy),
        ("6. Research Consents: Strict Farmer Privacy", test_research_consents_strict_privacy),
        ("7. Regional Signals: Public Read & Admin-Only Write", test_regional_signals_admin_only_write),
        ("8. Authentication: Context Established Before User Lookup", test_authentication_context_established_before_user_lookup),
        ("9. Authentication: Inactive User Clears Candidate Context", test_authentication_inactive_user_clears_context),
        ("10. Farm Access: Candidate Context Set Before Farm Lookup", test_farm_access_candidate_context_set_before_lookup),
        ("11. Farm Access: Unauthorized Request Clears Context & Raises 403", test_farm_access_unauthorized_clears_candidate_context),
        ("12. Farm Access: Archived Farm Clears Context & Raises 404", test_farm_access_archived_farm_clears_context),
        ("13. Admin Distinction: Application ADMIN is Not Database Role", test_application_admin_is_not_native_bypass),
        ("14. Admin Distinction: Missing GUC Fails Closed", test_missing_guc_fails_closed),
    ]

    print("================================================================================")
    print("ACREVIA - RLS POLICY SEMANTICS, AUTHENTICATION & ACCESS CONTROL REGRESSION SUITE")
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
    run_all_policy_semantics_tests()
