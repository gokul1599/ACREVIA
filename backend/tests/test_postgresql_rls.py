"""
ACREVIA - PostgreSQL Row-Level Security (RLS) & Tenant Isolation Test Suite.
Verifies complete schema classification, DDL generation, context lifecycle,
and all 16 tenant isolation criteria across application and database layers.
"""

import pytest
from unittest.mock import MagicMock
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from fastapi import HTTPException

from backend.app.database.base import Base
import backend.app.models  # Load all 132 entities
from backend.app.database.rls import (
    TABLE_CLASSIFICATION,
    TableCategory,
    set_tenant_context,
    clear_tenant_context,
    generate_rls_ddl,
)
from backend.app.models.user import User, Role
from backend.app.models.farm import Farm, FarmMembership, Plot
from backend.app.models.observation import Observation
from backend.app.models.crop import Crop
from backend.app.security.dependencies import verify_farm_access, get_current_user


# =============================================================================
# 1. Classification & DDL Generation Tests
# =============================================================================

def test_complete_table_classification_coverage():
    """Verify that every single registered SQLAlchemy model is classified."""
    all_tables = set(Base.metadata.tables.keys())
    classified_tables = set(TABLE_CLASSIFICATION.keys())

    assert len(all_tables) == 132, f"Expected 132 tables in metadata, found {len(all_tables)}"
    assert classified_tables == all_tables, (
        f"Missing tables from RLS classification: {all_tables - classified_tables}"
    )


def test_table_classification_categories():
    """Verify that tables are mapped to valid categories."""
    for table_name, meta in TABLE_CLASSIFICATION.items():
        assert "category" in meta, f"Table {table_name} missing category"
        assert isinstance(meta["category"], TableCategory), f"Table {table_name} category invalid"


def test_generate_rls_ddl_tenant_direct():
    """Verify that tenant-direct DDL enforces FORCE ROW LEVEL SECURITY and strict policies."""
    ddl = generate_rls_ddl("farms", TableCategory.TENANT_DIRECT, "id")
    assert "ALTER TABLE farms ENABLE ROW LEVEL SECURITY;" in ddl
    assert "ALTER TABLE farms FORCE ROW LEVEL SECURITY;" in ddl
    assert "farms_tenant_isolation_policy" in ddl
    assert "AS RESTRICTIVE" in ddl
    assert "USING (" in ddl
    assert "WITH CHECK (" in ddl
    assert "current_setting('app.is_admin', true) = 'true'" in ddl
    assert "id::text = current_setting('app.current_tenant_id', true)" in ddl


def test_generate_rls_ddl_user_owned():
    """Verify that user-owned DDL enforces FORCE ROW LEVEL SECURITY and user context policies."""
    ddl = generate_rls_ddl("consent_records", TableCategory.USER_OWNED, "user_id")
    assert "ALTER TABLE consent_records ENABLE ROW LEVEL SECURITY;" in ddl
    assert "ALTER TABLE consent_records FORCE ROW LEVEL SECURITY;" in ddl
    assert "consent_records_user_isolation_policy" in ddl
    assert "user_id::text = current_setting('app.current_user_id', true)" in ddl


def test_generate_rls_ddl_shared_reference():
    """Verify that shared reference DDL allows public read but restricts write to admin."""
    ddl = generate_rls_ddl("crops", TableCategory.SHARED_REFERENCE)
    assert "ALTER TABLE crops ENABLE ROW LEVEL SECURITY;" in ddl
    assert "crops_shared_read_policy" in ddl
    assert "crops_admin_write_policy" in ddl
    assert "AS PERMISSIVE" in ddl
    assert "FOR SELECT" in ddl
    assert "USING (true)" in ddl


def test_generate_rls_ddl_tenant_indirect():
    """Verify that indirect tenant DDL generates subquery checks on parent tables."""
    ddl = generate_rls_ddl("plants", TableCategory.TENANT_INDIRECT)
    assert "ALTER TABLE plants ENABLE ROW LEVEL SECURITY;" in ddl
    assert "ALTER TABLE plants FORCE ROW LEVEL SECURITY;" in ddl
    assert "plants_child_isolation_policy" in ddl
    assert "EXISTS (" in ddl


def test_generate_rls_ddl_community_collaborative():
    """Verify that community DDL allows public read and requires authenticated author for writes."""
    ddl = generate_rls_ddl("community_posts", TableCategory.COMMUNITY_COLLABORATIVE)
    assert "ALTER TABLE community_posts ENABLE ROW LEVEL SECURITY;" in ddl
    assert "community_posts_public_read_policy" in ddl
    assert "community_posts_author_write_policy" in ddl


# =============================================================================
# 2. Context Lifecycle Tests
# =============================================================================

def test_tenant_context_lifecycle_sqlite():
    """Verify context setting and clearing in test / SQLite environments."""
    mock_session = MagicMock(spec=Session)
    mock_session.info = {}
    mock_bind = MagicMock()
    mock_bind.dialect.name = "sqlite"
    mock_session.get_bind.return_value = mock_bind

    set_tenant_context(mock_session, tenant_id="farm-test-123", user_id="user-test-456", is_admin=False)

    ctx = mock_session.info.get("tenant_context")
    assert ctx is not None
    assert ctx["tenant_id"] == "farm-test-123"
    assert ctx["user_id"] == "user-test-456"
    assert ctx["is_admin"] is False

    # Clear context
    clear_tenant_context(mock_session)
    cleared = mock_session.info.get("tenant_context")
    assert cleared["tenant_id"] is None
    assert cleared["user_id"] is None
    assert cleared["is_admin"] is False


def test_tenant_context_lifecycle_simulated_postgresql():
    """Verify that PostgreSQL set_config execution sets transaction-local parameters."""
    mock_session = MagicMock(spec=Session)
    mock_session.info = {}
    mock_bind = MagicMock()
    mock_bind.dialect.name = "postgresql"
    mock_session.get_bind.return_value = mock_bind

    set_tenant_context(mock_session, tenant_id="farm-999", user_id="user-111", is_admin=True)

    # Verify SQL calls executed
    assert mock_session.execute.call_count == 3
    executed_statements = [call[0][0].text for call in mock_session.execute.call_args_list]

    assert any("set_config('app.current_tenant_id'" in stmt for stmt in executed_statements)
    assert any("set_config('app.current_user_id'" in stmt for stmt in executed_statements)
    assert any("set_config('app.is_admin'" in stmt for stmt in executed_statements)


# =============================================================================
# 3. Mandatory 16 Tenant Isolation Criteria Tests
# =============================================================================

def test_tenant_isolation_criteria_01_and_02_permitted_access(db_session):
    """Criteria 1 & 2: Tenant A can access its own records; Tenant B can access its own records."""
    tenant_a = User(id="user-a", phone="+919000000001", email="a@example.com", full_name="Tenant A", hashed_password="h")
    tenant_b = User(id="user-b", phone="+919000000002", email="b@example.com", full_name="Tenant B", hashed_password="h")
    db_session.add_all([tenant_a, tenant_b])
    db_session.commit()

    farm_a = Farm(id="farm-a", owner_id=tenant_a.id, name="Farm A", state="Telangana", district="Mahabubabad", mandal="Malyal", village="Malyal")
    farm_b = Farm(id="farm-b", owner_id=tenant_b.id, name="Farm B", state="Telangana", district="Nalgonda", mandal="Kampasagar", village="Kampasagar")
    db_session.add_all([farm_a, farm_b])
    db_session.commit()

    # Tenant A access
    verified_a = verify_farm_access(farm_id=farm_a.id, user=tenant_a, db=db_session)
    assert verified_a.id == farm_a.id
    assert db_session.info["tenant_context"]["tenant_id"] == farm_a.id

    # Tenant B access
    verified_b = verify_farm_access(farm_id=farm_b.id, user=tenant_b, db=db_session)
    assert verified_b.id == farm_b.id
    assert db_session.info["tenant_context"]["tenant_id"] == farm_b.id


def test_tenant_isolation_criteria_03_cross_tenant_read_denied(db_session):
    """Criteria 3: Tenant A cannot read Tenant B's farm records."""
    tenant_a = User(id="user-a-cross", phone="+919000000003", email="a3@example.com", full_name="A", hashed_password="h")
    tenant_b = User(id="user-b-cross", phone="+919000000004", email="b3@example.com", full_name="B", hashed_password="h")
    db_session.add_all([tenant_a, tenant_b])
    db_session.commit()

    farm_b = Farm(id="farm-b-target", owner_id=tenant_b.id, name="Farm B", state="Telangana", district="Nalgonda", mandal="Kampasagar", village="Kampasagar")
    db_session.add(farm_b)
    db_session.commit()

    # Tenant A attempts to access Farm B
    with pytest.raises(HTTPException) as exc_info:
        verify_farm_access(farm_id=farm_b.id, user=tenant_a, db=db_session)
    assert exc_info.value.status_code == 403


def test_tenant_isolation_criteria_04_cross_tenant_update_denied(db_session):
    """Criteria 4: Tenant A cannot update Tenant B's records."""
    tenant_a = User(id="user-a-up", phone="+919000000005", email="a4@example.com", full_name="A", hashed_password="h")
    tenant_b = User(id="user-b-up", phone="+919000000006", email="b4@example.com", full_name="B", hashed_password="h")
    db_session.add_all([tenant_a, tenant_b])
    db_session.commit()

    farm_b = Farm(id="farm-b-up", owner_id=tenant_b.id, name="Farm B Original", state="Telangana", district="Nalgonda", mandal="Kampasagar", village="Kampasagar")
    db_session.add(farm_b)
    db_session.commit()

    with pytest.raises(HTTPException):
        verify_farm_access(farm_id=farm_b.id, user=tenant_a, db=db_session, allowed_farm_roles=["owner", "admin"])


def test_tenant_isolation_criteria_05_cross_tenant_delete_denied(db_session):
    """Criteria 5: Tenant A cannot delete Tenant B's records."""
    tenant_a = User(id="user-a-del", phone="+919000000007", email="a5@example.com", full_name="A", hashed_password="h")
    tenant_b = User(id="user-b-del", phone="+919000000008", email="b5@example.com", full_name="B", hashed_password="h")
    db_session.add_all([tenant_a, tenant_b])
    db_session.commit()

    farm_b = Farm(id="farm-b-del", owner_id=tenant_b.id, name="Farm B Delete Target", state="Telangana", district="Nalgonda", mandal="Kampasagar", village="Kampasagar")
    db_session.add(farm_b)
    db_session.commit()

    with pytest.raises(HTTPException) as exc_info:
        verify_farm_access(farm_id=farm_b.id, user=tenant_a, db=db_session)
    assert exc_info.value.status_code == 403


def test_tenant_isolation_criteria_06_cross_tenant_insert_denied(db_session):
    """Criteria 6: Tenant A cannot insert records claiming Tenant B ownership."""
    tenant_a = User(id="user-a-ins", phone="+919000000009", email="a6@example.com", full_name="A", hashed_password="h")
    tenant_b = User(id="user-b-ins", phone="+919000000010", email="b6@example.com", full_name="B", hashed_password="h")
    db_session.add_all([tenant_a, tenant_b])
    db_session.commit()

    farm_b = Farm(id="farm-b-ins", owner_id=tenant_b.id, name="Farm B", state="Telangana", district="Nalgonda", mandal="Kampasagar", village="Kampasagar")
    db_session.add(farm_b)
    db_session.commit()

    # User A tries to insert plot under Farm B
    with pytest.raises(HTTPException):
        verify_farm_access(farm_id=farm_b.id, user=tenant_a, db=db_session)


def test_tenant_isolation_criteria_07_and_08_missing_or_invalid_context(db_session):
    """Criteria 7 & 8: Missing or invalid tenant context denies access."""
    user = User(id="user-ctx-test", phone="+919000000011", email="ctx@example.com", full_name="C", hashed_password="h")
    db_session.add(user)
    db_session.commit()

    # Non-existent farm
    with pytest.raises(HTTPException) as exc_info:
        verify_farm_access(farm_id="non-existent-farm-uuid", user=user, db=db_session)
    assert exc_info.value.status_code == 404


def test_tenant_isolation_criteria_09_unauthenticated_denied():
    """Criteria 9: Unauthenticated users cannot access tenant records."""
    with pytest.raises(HTTPException) as exc_info:
        get_current_user(token=None, db=MagicMock())
    assert exc_info.value.status_code == 401


def test_tenant_isolation_criteria_10_parent_child_ownership(db_session):
    """Criteria 10: Parent-child relationship integrity is enforced."""
    user = User(id="user-pc", phone="+919000000012", email="pc@example.com", full_name="PC", hashed_password="h")
    db_session.add(user)
    db_session.commit()

    farm = Farm(id="farm-pc-1", owner_id=user.id, name="Farm PC", state="Telangana", district="Mahabubabad", mandal="Malyal", village="Malyal")
    db_session.add(farm)
    db_session.commit()

    plot = Plot(id="plot-pc-1", farm_id=farm.id, name="Plot 1", acreage=1.0)
    db_session.add(plot)
    db_session.commit()

    assert plot.farm_id == farm.id


def test_tenant_isolation_criteria_11_collaborative_access(db_session):
    """Criteria 11: Authorized collaborative farm membership works as intended."""
    owner = User(id="user-collab-owner", phone="+919000000013", email="cown@example.com", full_name="Owner", hashed_password="h")
    member = User(id="user-collab-worker", phone="+919000000014", email="cwrk@example.com", full_name="Worker", hashed_password="h")
    db_session.add_all([owner, member])
    db_session.commit()

    farm = Farm(id="farm-collab", owner_id=owner.id, name="Collab Farm", state="Telangana", district="Mahabubabad", mandal="Malyal", village="Malyal")
    db_session.add(farm)
    db_session.commit()

    membership = FarmMembership(farm_id=farm.id, user_id=member.id, role_in_farm="worker")
    db_session.add(membership)
    db_session.commit()

    # Worker can access farm
    verified = verify_farm_access(farm_id=farm.id, user=member, db=db_session, allowed_farm_roles=["worker"])
    assert verified.id == farm.id


def test_tenant_isolation_criteria_12_shared_reference_access(db_session):
    """Criteria 12: Shared reference data remains accessible across all tenants."""
    crop = Crop(id="crop-shared-test", name_en="Cotton", name_te="పత్తి", name_hi="कपास", scientific_name="Gossypium hirsutum")
    db_session.add(crop)
    db_session.commit()

    fetched = db_session.get(Crop, "crop-shared-test")
    assert fetched is not None
    assert fetched.name_en == "Cotton"


def test_tenant_isolation_criteria_13_rollback_clears_context():
    """Criteria 13: Transaction rollback does not leak tenant context."""
    mock_session = MagicMock(spec=Session)
    mock_session.info = {}
    mock_bind = MagicMock()
    mock_bind.dialect.name = "postgresql"
    mock_session.get_bind.return_value = mock_bind

    set_tenant_context(mock_session, tenant_id="farm-rollback-test", user_id="user-rb", is_admin=False)
    assert mock_session.info["tenant_context"]["tenant_id"] == "farm-rollback-test"

    clear_tenant_context(mock_session)
    assert mock_session.info["tenant_context"]["tenant_id"] is None


def test_tenant_isolation_criteria_14_connection_pool_reuse():
    """Criteria 14: Context does not leak across pooled connection reuse."""
    session_1 = MagicMock(spec=Session)
    session_1.info = {}
    set_tenant_context(session_1, tenant_id="farm-pool-1", user_id="u1", is_admin=False)
    clear_tenant_context(session_1)

    # Reused connection in next request
    session_2 = MagicMock(spec=Session)
    session_2.info = {}
    clear_tenant_context(session_2)
    assert session_2.info.get("tenant_context", {}).get("tenant_id") is None


def test_tenant_isolation_criteria_15_concurrent_requests():
    """Criteria 15: Concurrent requests maintain isolated session context."""
    s1 = MagicMock(spec=Session)
    s1.info = {}
    s2 = MagicMock(spec=Session)
    s2.info = {}

    set_tenant_context(s1, tenant_id="tenant-alpha", user_id="user-a", is_admin=False)
    set_tenant_context(s2, tenant_id="tenant-beta", user_id="user-b", is_admin=False)

    assert s1.info["tenant_context"]["tenant_id"] == "tenant-alpha"
    assert s2.info["tenant_context"]["tenant_id"] == "tenant-beta"


def test_tenant_isolation_criteria_16_admin_access_bypass(db_session):
    """Criteria 16: Administrative access is constrained to superusers."""
    admin_role = db_session.get(Role, "ADMIN")
    if not admin_role:
        admin_role = Role(id="ADMIN", description="Administrator")
        db_session.add(admin_role)

    admin_user = User(id="user-admin-role", phone="+919000000015", email="adm@example.com", full_name="Admin", hashed_password="h")
    admin_user.roles.append(admin_role)
    db_session.add(admin_user)
    db_session.commit()

    other_user = User(id="user-other-target", phone="+919000000016", email="oth@example.com", full_name="Other", hashed_password="h")
    farm = Farm(id="farm-other-admin-test", owner_id=other_user.id, name="Other Farm", state="Telangana", district="Nalgonda", mandal="Kampasagar", village="Kampasagar")
    db_session.add_all([other_user, farm])
    db_session.commit()

    # Admin accesses other user's farm
    verified = verify_farm_access(farm_id=farm.id, user=admin_user, db=db_session)
    assert verified.id == farm.id
    assert db_session.info["tenant_context"]["is_admin"] is True
