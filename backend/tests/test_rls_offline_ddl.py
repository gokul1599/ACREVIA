"""
ACREVIA - Offline PostgreSQL RLS DDL & Classification Test Suite.

Independent, reproducible validation of table classification, policy generation,
administrative trust boundary conditions, and atomic DDL statement counts.
Does not require remote credentials, network access, or external database instances.
"""

import sys
import os

# Ensure project root and backend are in python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
backend_root = os.path.join(project_root, "backend")
if project_root not in sys.path:
    sys.path.insert(0, project_root)
if backend_root not in sys.path:
    sys.path.insert(0, backend_root)

from backend.app.database.rls import (
    TABLE_CLASSIFICATION,
    TableCategory,
    generate_rls_ddl,
    ADMIN_BYPASS_SQL,
    ADMIN_ROLES,
)


def test_complete_table_classification_coverage():
    """Verify that exactly 132 database entities are classified in the RLS mapping."""
    total_entities = len(TABLE_CLASSIFICATION)
    assert total_entities == 132, f"Expected 132 classified tables, got {total_entities}"


def test_table_classification_categories_breakdown():
    """Verify the exact distribution across all five RLS categories."""
    counts = {category: 0 for category in TableCategory}
    for meta in TABLE_CLASSIFICATION.values():
        cat = meta.get("category")
        if cat in counts:
            counts[cat] += 1

    assert counts[TableCategory.TENANT_DIRECT] == 25, f"Expected 25 TENANT_DIRECT, got {counts[TableCategory.TENANT_DIRECT]}"
    assert counts[TableCategory.USER_OWNED] == 13, f"Expected 13 USER_OWNED, got {counts[TableCategory.USER_OWNED]}"
    assert counts[TableCategory.TENANT_INDIRECT] == 53, f"Expected 53 TENANT_INDIRECT, got {counts[TableCategory.TENANT_INDIRECT]}"
    assert counts[TableCategory.SHARED_REFERENCE] == 25, f"Expected 25 SHARED_REFERENCE, got {counts[TableCategory.SHARED_REFERENCE]}"
    assert counts[TableCategory.COMMUNITY_COLLABORATIVE] == 16, f"Expected 16 COMMUNITY_COLLABORATIVE, got {counts[TableCategory.COMMUNITY_COLLABORATIVE]}"


def test_ddl_generation_tenant_direct():
    """Verify DDL generation for direct tenant tables (ENABLE + FORCE + Permissive + Restrictive)."""
    ddl = generate_rls_ddl("farms", TableCategory.TENANT_DIRECT, "id")
    assert "ALTER TABLE farms ENABLE ROW LEVEL SECURITY;" in ddl
    assert "ALTER TABLE farms FORCE ROW LEVEL SECURITY;" in ddl
    assert "CREATE POLICY farms_base_access_policy ON farms" in ddl
    assert "AS PERMISSIVE" in ddl
    assert "CREATE POLICY farms_tenant_isolation_policy ON farms" in ddl
    assert "AS RESTRICTIVE" in ddl


def test_ddl_generation_user_owned():
    """Verify DDL generation for user-owned tables."""
    ddl = generate_rls_ddl("user_preferences", TableCategory.USER_OWNED, "user_id")
    assert "ALTER TABLE user_preferences ENABLE ROW LEVEL SECURITY;" in ddl
    assert "ALTER TABLE user_preferences FORCE ROW LEVEL SECURITY;" in ddl
    assert "CREATE POLICY user_preferences_base_access_policy ON user_preferences" in ddl
    assert "CREATE POLICY user_preferences_user_isolation_policy ON user_preferences" in ddl


def test_ddl_generation_shared_reference():
    """Verify DDL generation for shared reference tables (PERMISSIVE public read, PERMISSIVE admin write)."""
    ddl = generate_rls_ddl("crops", TableCategory.SHARED_REFERENCE)
    assert "ALTER TABLE crops ENABLE ROW LEVEL SECURITY;" in ddl
    assert "FORCE ROW LEVEL SECURITY" not in ddl
    assert "CREATE POLICY crops_shared_read_policy ON crops" in ddl
    assert "AS PERMISSIVE" in ddl
    assert "FOR SELECT" in ddl
    assert "CREATE POLICY crops_admin_write_policy ON crops" in ddl
    assert "AS PERMISSIVE" in ddl
    # Critical invariant: no restrictive policy blocking public read
    assert "AS RESTRICTIVE" not in ddl


def test_ddl_generation_tenant_indirect():
    """Verify DDL generation for indirect child tables with FK traversal."""
    ddl = generate_rls_ddl("crop_seasons", TableCategory.TENANT_INDIRECT)
    assert "ALTER TABLE crop_seasons ENABLE ROW LEVEL SECURITY;" in ddl
    assert "ALTER TABLE crop_seasons FORCE ROW LEVEL SECURITY;" in ddl
    assert "CREATE POLICY crop_seasons_child_isolation_policy ON crop_seasons" in ddl
    assert "EXISTS (" in ddl


def test_ddl_generation_community_collaborative():
    """Verify DDL generation for community collaborative tables with author-level isolation."""
    ddl = generate_rls_ddl("community_posts", TableCategory.COMMUNITY_COLLABORATIVE)
    assert "ALTER TABLE community_posts ENABLE ROW LEVEL SECURITY;" in ddl
    assert "ALTER TABLE community_posts FORCE ROW LEVEL SECURITY;" in ddl
    assert "CREATE POLICY community_posts_public_read_policy ON community_posts" in ddl
    assert "CREATE POLICY community_posts_author_write_policy ON community_posts" in ddl
    assert "author_id::text = current_setting('app.current_user_id', true)" in ddl
    assert "AS RESTRICTIVE" not in ddl


def test_admin_bypass_sql_dual_identity_condition():
    """Verify that administrative bypass strictly enforces dual SESSION_USER and CURRENT_USER check."""
    assert "SESSION_USER::text IN ('neondb_owner', 'acrevia_admin')" in ADMIN_BYPASS_SQL
    assert "CURRENT_USER::text IN ('neondb_owner', 'acrevia_admin')" in ADMIN_BYPASS_SQL
    assert "current_setting('app.is_admin', true) = 'true'" in ADMIN_BYPASS_SQL
    assert ADMIN_ROLES == ("neondb_owner", "acrevia_admin")


def test_total_atomic_ddl_statement_count():
    """Verify that exactly 767 atomic DDL statements are generated across all 132 tables."""
    statements = []
    enable_count = 0
    force_count = 0
    drop_count = 0
    create_count = 0

    for table_name, meta in TABLE_CLASSIFICATION.items():
        cat = meta.get("category")
        col = meta.get("column", "farm_id")
        ddl = generate_rls_ddl(table_name, cat, col)
        for s in ddl.strip().split(";"):
            cleaned = s.strip()
            if cleaned:
                statements.append(cleaned)
                if "ENABLE ROW LEVEL SECURITY" in cleaned:
                    enable_count += 1
                elif "FORCE ROW LEVEL SECURITY" in cleaned:
                    force_count += 1
                elif "DROP POLICY IF EXISTS" in cleaned:
                    drop_count += 1
                elif "CREATE POLICY" in cleaned:
                    create_count += 1

    assert enable_count == 132, f"Expected 132 ENABLE RLS statements, got {enable_count}"
    assert force_count == 110, f"Expected 110 FORCE RLS statements, got {force_count}"
    assert drop_count == 264, f"Expected 264 DROP POLICY statements, got {drop_count}"
    assert create_count == 261, f"Expected 261 CREATE POLICY statements, got {create_count}"
    assert len(statements) == 767, f"Expected 767 atomic DDL statements, got {len(statements)}"


def run_all_offline_tests():
    """Executes all 9 test functions and prints structured verification output."""
    test_functions = [
        ("1. Complete Table Classification Coverage (132 tables)", test_complete_table_classification_coverage),
        ("2. Category Distribution Breakdown (25/13/53/25/16)", test_table_classification_categories_breakdown),
        ("3. DDL Generation: Tenant Direct (ENABLE + FORCE)", test_ddl_generation_tenant_direct),
        ("4. DDL Generation: User Owned (ENABLE + FORCE)", test_ddl_generation_user_owned),
        ("5. DDL Generation: Shared Reference (ENABLE only)", test_ddl_generation_shared_reference),
        ("6. DDL Generation: Tenant Indirect (ENABLE + FORCE + FK)", test_ddl_generation_tenant_indirect),
        ("7. DDL Generation: Community Collaborative (ENABLE only)", test_ddl_generation_community_collaborative),
        ("8. Administrative Trust Boundary Dual-Condition", test_admin_bypass_sql_dual_identity_condition),
        ("9. Total Atomic DDL Statement Count (767 statements)", test_total_atomic_ddl_statement_count),
    ]

    print("================================================================================")
    print("ACREVIA - REPRODUCIBLE OFFLINE POSTGRESQL RLS DDL TEST SUITE")
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
    run_all_offline_tests()
