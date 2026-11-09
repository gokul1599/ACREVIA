"""
ACREVIA - PostgreSQL Row-Level Security (RLS) & Tenant Isolation Test Suite.
Verifies complete schema classification, DDL generation, context lifecycle,
and application-layer tenant isolation.
"""

import pytest
from unittest.mock import MagicMock
from sqlalchemy.orm import Session
from sqlalchemy import create_engine

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
from backend.app.models.farm import Farm, FarmMembership
from backend.app.security.dependencies import verify_farm_access, get_current_user


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


def test_verify_farm_access_sets_tenant_context(db_session):
    """Verify that verify_farm_access sets the tenant context on the session."""
    user = User(
        id="owner-test-user-id",
        phone="+919876543210",
        email="owner@example.com",
        full_name="Farm Owner",
        hashed_password="hash"
    )
    db_session.add(user)
    db_session.commit()

    farm = Farm(
        id="target-farm-id-123",
        owner_id=user.id,
        name="Security Test Farm",
        state="Telangana",
        district="Mahabubabad",
        mandal="Malyal",
        village="Malyal",
        total_acreage=2.5
    )
    db_session.add(farm)
    db_session.commit()

    verified_farm = verify_farm_access(farm_id=farm.id, user=user, db=db_session)
    assert verified_farm.id == farm.id

    # Verify session.info tenant_context was set
    ctx = db_session.info.get("tenant_context")
    assert ctx is not None
    assert ctx["tenant_id"] == farm.id
    assert ctx["user_id"] == user.id
    assert ctx["is_admin"] is False
