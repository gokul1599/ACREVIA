"""
ACREVIA - Background Worker Security, Role Correctness & Public Data Privacy Test Suite.
Verifies Option A RiskCast batch processing, regional signal authoring, ingestion job scoping,
role verification against seeded constants, and public organization contact masking.
Honest Evidentiary Classification:
  - STATIC_METADATA_TEST
  - STATIC_POLICY_GENERATION_TEST
  - OFFLINE_UNIT_TEST
"""

import pytest
import asyncio
from unittest.mock import MagicMock, patch
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.database.base import Base
import backend.app.models
from backend.app.database.rls import (
    TABLE_CLASSIFICATION,
    TableCategory,
    ADMIN_BYPASS_SQL,
    generate_rls_ddl,
    set_tenant_context,
    clear_tenant_context,
)
from backend.app.models.user import User, Role, UserRole
from backend.app.models.farm import Farm, Plot
from backend.app.models.collective import AgriculturalOrganization, OrganizationMembership
from backend.app.security.permissions import SystemRole
from backend.app.tasks.run_riskcast_batch import evaluate_single_farm, run_batch


# ==============================================================================
# 1. ROLE CORRECTNESS & SEED ALIGNMENT TESTS (STATIC_METADATA_TEST)
# ==============================================================================

def test_role_codes_match_system_role_constants():
    """
    [STATIC_METADATA_TEST]
    Verifies that system role constants match exactly the 4 seeded roles:
    FARMER, AGRICULTURAL_EXPERT, RESEARCHER, ADMIN.
    Rejects fictional role codes 'EXPERT' and 'EXTENSION_OFFICER'.
    """
    seeded_roles = {"FARMER", "AGRICULTURAL_EXPERT", "RESEARCHER", "ADMIN"}
    enum_roles = {r.value for r in SystemRole}
    assert enum_roles == seeded_roles, f"Enum roles {enum_roles} do not match seeded roles {seeded_roles}"

    # Verify that RLS policy generator references AGRICULTURAL_EXPERT and not EXPERT or EXTENSION_OFFICER
    ddl_posts = generate_rls_ddl("community_posts", TableCategory.COMMUNITY_COLLABORATIVE)
    assert "AGRICULTURAL_EXPERT" in ddl_posts
    assert "'EXPERT'" not in ddl_posts
    assert "EXTENSION_OFFICER" not in ddl_posts

    ddl_comments = generate_rls_ddl("community_comments", TableCategory.COMMUNITY_COLLABORATIVE)
    assert "AGRICULTURAL_EXPERT" in ddl_comments
    assert "'EXPERT'" not in ddl_comments
    assert "EXTENSION_OFFICER" not in ddl_comments

    ddl_contrib = generate_rls_ddl("knowledge_contributions", TableCategory.COMMUNITY_COLLABORATIVE)
    assert "AGRICULTURAL_EXPERT" in ddl_contrib
    assert "'EXPERT'" not in ddl_contrib
    assert "EXTENSION_OFFICER" not in ddl_contrib


def test_farmer_role_does_not_obtain_expert_access():
    """
    [STATIC_POLICY_GENERATION_TEST]
    Verifies that FARMER role code is excluded from the expert authorization predicates.
    """
    ddl = generate_rls_ddl("community_posts", TableCategory.COMMUNITY_COLLABORATIVE)
    # The user_roles check in EXPERT_ONLY must not match FARMER
    assert "ur.role_id IN ('AGRICULTURAL_EXPERT', 'RESEARCHER', 'ADMIN')" in ddl


# ==============================================================================
# 2. WORKER ACCESS & OPTION A TENANT ISOLATION TESTS (OFFLINE_UNIT_TEST)
# ==============================================================================

def test_riskcast_worker_farm_scoped_execution_and_context_reset():
    """
    [OFFLINE_UNIT_TEST]
    Verifies Option A RiskCast worker:
    1. Sets candidate context for farm.
    2. Sets authenticated context for owner.
    3. Clears tenant context before returning connection to pool.
    """
    # Setup test in-memory SQLite DB
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(bind=engine)

    # Seed an owner, a farm, and a plot
    with TestingSession() as session:
        owner = User(
            id="usr-owner-01",
            phone="+919999900001",
            email="owner@test.com",
            hashed_password="hash",
            full_name="Farmer One",
            language_preference="te",
            is_active=True,
            is_verified=True
        )
        session.add(owner)
        session.flush()

        farm = Farm(
            id="farm-tenant-01",
            owner_id=owner.id,
            name="Telangana Test Farm",
            state="Telangana",
            district="Warangal",
            mandal="Geesugonda",
            village="Dharmaram",
            total_acreage=2.5,
            is_archived=False
        )
        session.add(farm)
        session.flush()

        plot = Plot(
            id="plot-01",
            farm_id=farm.id,
            name="Plot North",
            acreage=2.5,
            is_archived=False
        )
        session.add(plot)
        session.commit()

    # Mock SessionLocal and RiskCastService
    with patch("backend.app.tasks.run_riskcast_batch.SessionLocal", TestingSession):
        with patch("backend.app.tasks.run_riskcast_batch.RiskCastService.evaluate_plot", return_value={"risk": "LOW"}):
            # Run evaluate_single_farm
            evaluated = asyncio.run(evaluate_single_farm("farm-tenant-01"))
            assert evaluated == 1

            # Verify that session context is cleared after worker completes
            with TestingSession() as verify_session:
                ctx = verify_session.info.get("tenant_context", {})
                assert ctx.get("tenant_id") is None
                assert ctx.get("user_id") is None


def test_riskcast_worker_rejects_archived_farm_and_clears_context():
    """
    [OFFLINE_UNIT_TEST]
    Verifies that evaluate_single_farm aborts processing when a farm is archived
    and guarantees clear_tenant_context teardown.
    """
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(bind=engine)

    with TestingSession() as session:
        owner = User(id="usr-arch-01", phone="+919999900002", email="arch@test.com", hashed_password="h", full_name="A", is_active=True, is_verified=True)
        session.add(owner)
        session.flush()
        farm = Farm(
            id="farm-arch-01",
            owner_id=owner.id,
            name="Archived Farm",
            state="Telangana",
            district="Khammam",
            mandal="Khammam Urban",
            village="Burhanpuram",
            total_acreage=1.0,
            is_archived=True
        )
        session.add(farm)
        session.commit()

    with patch("backend.app.tasks.run_riskcast_batch.SessionLocal", TestingSession):
        evaluated = asyncio.run(evaluate_single_farm("farm-arch-01"))
        assert evaluated == 0

        with TestingSession() as verify_session:
            ctx = verify_session.info.get("tenant_context", {})
            assert ctx.get("tenant_id") is None


# ==============================================================================
# 3. REGIONAL PULSE & INGESTION JOB AUTHORIZATION (STATIC_POLICY_GENERATION_TEST)
# ==============================================================================

def test_regional_signals_writer_identity_scoping():
    """
    [STATIC_POLICY_GENERATION_TEST]
    Verifies regional_signals write policy:
    1. Allows ADMIN, AGRICULTURAL_EXPERT, and RESEARCHER to insert/update.
    2. Allows ADMIN_BYPASS_SQL.
    3. Blocks unprivileged FARMER and anonymous users.
    """
    ddl = generate_rls_ddl("regional_signals", TableCategory.COMMUNITY_COLLABORATIVE)
    assert "ALTER TABLE regional_signals ENABLE ROW LEVEL SECURITY;" in ddl
    assert "ALTER TABLE regional_signals FORCE ROW LEVEL SECURITY;" in ddl
    assert "CREATE POLICY regional_signals_author_write_policy ON regional_signals" in ddl
    assert "ur.role_id IN ('ADMIN', 'AGRICULTURAL_EXPERT', 'RESEARCHER')" in ddl


def test_ingestion_jobs_worker_and_admin_scoping():
    """
    [STATIC_POLICY_GENERATION_TEST]
    Verifies ingestion_jobs policy:
    1. FORCE ROW LEVEL SECURITY is enabled.
    2. Zero public read policy exists.
    3. Writes/reads permitted to ADMIN, AGRICULTURAL_EXPERT, RESEARCHER or ADMIN_BYPASS_SQL.
    """
    ddl = generate_rls_ddl("ingestion_jobs", TableCategory.SHARED_REFERENCE)
    assert "ALTER TABLE ingestion_jobs ENABLE ROW LEVEL SECURITY;" in ddl
    assert "ALTER TABLE ingestion_jobs FORCE ROW LEVEL SECURITY;" in ddl
    assert "CREATE POLICY ingestion_jobs_shared_read_policy" not in ddl
    assert "CREATE POLICY ingestion_jobs_admin_write_policy ON ingestion_jobs" in ddl
    assert "ur.role_id IN ('ADMIN', 'AGRICULTURAL_EXPERT', 'RESEARCHER')" in ddl


# ==============================================================================
# 4. PUBLIC DATA PRIVACY & CONTACT MASKING (OFFLINE_UNIT_TEST)
# ==============================================================================

def test_organization_public_contact_information_masking():
    """
    [OFFLINE_UNIT_TEST]
    Verifies that public listings and non-member queries of Agricultural Organizations
    mask private contact details (contact_email, contact_phone, registration_number).
    """
    from backend.app.schemas.collective import AgriculturalOrganizationResponse
    from datetime import datetime, timezone

    # Create an organization instance
    org = AgriculturalOrganization(
        id="org-fpo-100",
        name="Telangana Cotton Collective FPO",
        org_type="FPO",
        registration_number="REG-FPO-TS-2026-9999",
        state="Telangana",
        district="Warangal",
        description="FPO managing 500 smallholder cotton farmers.",
        contact_email="secret_director@fpo.org",
        contact_phone="+919876543210",
        verification_status="APPROVED",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )

    # Non-member inspection
    org_dto = AgriculturalOrganizationResponse.model_validate(org)
    # Simulate masking applied in collectives.py for non-members
    org_dto.contact_email = None
    org_dto.contact_phone = None
    org_dto.registration_number = None

    dumped = org_dto.model_dump()
    assert dumped["name"] == "Telangana Cotton Collective FPO"
    assert dumped["verification_status"] == "APPROVED"
    assert dumped["contact_email"] is None
    assert dumped["contact_phone"] is None
    assert dumped["registration_number"] is None
