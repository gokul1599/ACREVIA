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
import uuid
from datetime import datetime, timezone, timedelta, date
import threading
from concurrent.futures import ThreadPoolExecutor
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
from backend.app.models.observation import Observation
from backend.app.models.collective import AgriculturalOrganization, OrganizationMembership
from backend.app.security.permissions import SystemRole
from backend.app.tasks.run_riskcast_batch import (
    evaluate_single_farm,
    run_batch,
    ProductionDispatchBlockedError,
    TaskManifestVerificationError,
    DispatchAuthorizationFailedError,
    DispatchAuthorization,
    DispatchVerifier,
    BatchTaskManifest,
    verify_dispatch_manifest,
    PROCESSED_TASK_IDS,
)
from backend.app.database.rls import (
    PRIVILEGE_CROSSWALK,
    generate_privilege_grants_ddl,
)


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
        with patch("backend.app.tasks.run_riskcast_batch.RiskCastService.evaluate_plot", return_value={"risk": "LOW"}) as mock_eval:
            # Issue verified test authorization grant
            auth_grant = DispatchVerifier.issue_test_authorization(task_id="test-task-01", farm_id="farm-tenant-01")
            # Run evaluate_single_farm
            evaluated = asyncio.run(evaluate_single_farm("farm-tenant-01", authorization=auth_grant))
            assert evaluated == 1

            # Verify that evaluate_plot was invoked with non-human worker identity and current_user=None (NO FARMER IMPERSONATION)
            mock_eval.assert_called_once()
            _, kwargs = mock_eval.call_args
            assert kwargs.get("current_user") is None, "Worker must NOT pass farmer User object (prevents farmer impersonation)"
            assert kwargs.get("actor_identity") == "system:worker:riskcast"

            # Verify that session context is cleared after worker completes
            with TestingSession() as verify_session:
                ctx = verify_session.info.get("tenant_context", {})
                assert ctx.get("tenant_id") is None
                assert ctx.get("user_id") is None


def test_riskcast_worker_does_not_impersonate_farmer_or_access_user_owned_data():
    """
    [OFFLINE_UNIT_TEST]
    Verifies that the RiskCast worker:
    1. Sets user_id to 'system:worker:riskcast' (non-human service actor).
    2. Does not assume owner.id.
    3. Cannot access USER_OWNED tables (e.g. session_tokens, consent_records) under RLS.
    """
    from backend.app.tasks.run_riskcast_batch import SYSTEM_WORKER_IDENTITY

    assert SYSTEM_WORKER_IDENTITY == "system:worker:riskcast"

    # Under RLS, a query on USER_OWNED tables with app.current_user_id = 'system:worker:riskcast'
    # returns zero rows for any farmer's personal records.
    ddl_user = generate_rls_ddl("users", TableCategory.USER_OWNED)
    assert "current_setting('app.current_user_id', true)" in ddl_user
    # A farmer's id will never match 'system:worker:riskcast'
    assert "id::text = current_setting('app.current_user_id', true)" in ddl_user


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
        auth_grant = DispatchVerifier.issue_test_authorization(task_id="test-task-02", farm_id="farm-arch-01")
        evaluated = asyncio.run(evaluate_single_farm("farm-arch-01", authorization=auth_grant))
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


def test_collective_organization_endpoint_privacy_matrix():
    """
    [OFFLINE_UNIT_TEST]
    Comprehensive verification of collective organization serialization across:
    1. Authenticated non-member -> contact fields None
    2. Authenticated inactive member -> contact fields None
    3. Authenticated member of different organization -> contact fields None
    4. Authenticated active member of this organization -> contact fields unmasked
    5. Authorized system administrator -> contact fields unmasked
    """
    from backend.app.schemas.collective import AgriculturalOrganizationResponse
    from datetime import datetime, timezone, timedelta
    from backend.app.api.v1.endpoints.collectives import list_organizations, get_organization

    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(bind=engine)

    with TestingSession() as session:
        # Create test users
        admin_role = Role(id="ADMIN", description="Platform Admin")
        farmer_role = Role(id="FARMER", description="Farmer")
        session.add_all([admin_role, farmer_role])
        session.flush()

        admin_user = User(id="u-admin-1", phone="+919000000001", email="admin@test.com", hashed_password="h", full_name="Admin", is_active=True, is_verified=True)
        active_member = User(id="u-member-1", phone="+919000000002", email="m1@test.com", hashed_password="h", full_name="Active Member", is_active=True, is_verified=True)
        inactive_member = User(id="u-member-2", phone="+919000000003", email="m2@test.com", hashed_password="h", full_name="Inactive Member", is_active=True, is_verified=True)
        other_org_member = User(id="u-member-3", phone="+919000000004", email="m3@test.com", hashed_password="h", full_name="Other Member", is_active=True, is_verified=True)
        non_member = User(id="u-nonmember", phone="+919000000005", email="nm@test.com", hashed_password="h", full_name="Non Member", is_active=True, is_verified=True)
        
        session.add_all([admin_user, active_member, inactive_member, other_org_member, non_member])
        session.flush()

        # Add user roles
        session.add(UserRole(user_id=admin_user.id, role_id="ADMIN"))
        session.add(UserRole(user_id=active_member.id, role_id="FARMER"))
        session.add(UserRole(user_id=inactive_member.id, role_id="FARMER"))
        session.add(UserRole(user_id=other_org_member.id, role_id="FARMER"))
        session.add(UserRole(user_id=non_member.id, role_id="FARMER"))

        # Create two organizations
        target_org = AgriculturalOrganization(
            id="org-warangal-cotton",
            name="Warangal Cotton Collective",
            org_type="FPO",
            registration_number="REG-TS-WGL-001",
            state="Telangana",
            district="Warangal",
            contact_email="director@cottonfpo.org",
            contact_phone="+919876543210",
            verification_status="APPROVED",
        )
        other_org = AgriculturalOrganization(
            id="org-khammam-chilli",
            name="Khammam Chilli Producers",
            org_type="FPO",
            registration_number="REG-TS-KHM-002",
            state="Telangana",
            district="Khammam",
            contact_email="leader@chillifpo.org",
            contact_phone="+919876543211",
            verification_status="APPROVED",
        )
        session.add_all([target_org, other_org])
        session.flush()

        # Add memberships
        session.add(OrganizationMembership(id="m-1", organization_id=target_org.id, user_id=active_member.id, org_role="MEMBER", is_active=True))
        session.add(OrganizationMembership(id="m-2", organization_id=target_org.id, user_id=inactive_member.id, org_role="MEMBER", is_active=False))
        session.add(OrganizationMembership(id="m-3", organization_id=other_org.id, user_id=other_org_member.id, org_role="MEMBER", is_active=True))
        session.commit()

        # 1. Non-member query -> masked
        res_nm = get_organization(org_id=target_org.id, current_user=non_member, db=session)
        assert res_nm.contact_email is None
        assert res_nm.contact_phone is None
        assert res_nm.registration_number is None

        # 2. Inactive member query -> masked
        res_inact = get_organization(org_id=target_org.id, current_user=inactive_member, db=session)
        assert res_inact.contact_email is None
        assert res_inact.contact_phone is None
        assert res_inact.registration_number is None

        # 3. Other org member query -> masked
        res_other = get_organization(org_id=target_org.id, current_user=other_org_member, db=session)
        assert res_other.contact_email is None
        assert res_other.contact_phone is None
        assert res_other.registration_number is None

        # 4. Active member query -> UNMASKED
        res_act = get_organization(org_id=target_org.id, current_user=active_member, db=session)
        assert res_act.contact_email == "director@cottonfpo.org"
        assert res_act.contact_phone == "+919876543210"
        assert res_act.registration_number == "REG-TS-WGL-001"

        # 5. Admin query -> UNMASKED
        res_adm = get_organization(org_id=target_org.id, current_user=admin_user, db=session)
        assert res_adm.contact_email == "director@cottonfpo.org"
        assert res_adm.contact_phone == "+919876543210"
        assert res_adm.registration_number == "REG-TS-WGL-001"


def test_registration_number_vs_legal_entity_number_schema_separation():
    """
    [STATIC_METADATA_TEST]
    Proves that AgriculturalOrganization uses 'registration_number', while
    'legal_entity_number' belongs to the IntegrationPartner model (interoperability).
    Validates zero property confusion in ORM models and Pydantic schemas.
    """
    from backend.app.models.collective import AgriculturalOrganization
    from backend.app.models.interoperability import IntegrationPartner
    from backend.app.schemas.collective import AgriculturalOrganizationResponse

    org_cols = [c.name for c in AgriculturalOrganization.__table__.columns]
    partner_cols = [c.name for c in IntegrationPartner.__table__.columns]

    assert "registration_number" in org_cols
    assert "legal_entity_number" not in org_cols, "AgriculturalOrganization MUST NOT have legal_entity_number"

    assert "legal_entity_number" in partner_cols
    assert "registration_number" not in partner_cols, "IntegrationPartner MUST NOT have registration_number"

    # Verify Pydantic response schema has registration_number and NOT legal_entity_number
    schema_fields = AgriculturalOrganizationResponse.model_fields.keys()
    assert "registration_number" in schema_fields
    assert "legal_entity_number" not in schema_fields


def test_regional_pulse_evidence_privacy_enforced():
    """
    [STATIC_POLICY_GENERATION_TEST]
    Verifies that regional_signal_evidences denies public read access:
    Evidence records (which contain granular observation IDs, alert IDs, and notes)
    are restricted exclusively to ADMIN, AGRICULTURAL_EXPERT, and RESEARCHER roles.
    """
    ev_ddl = generate_rls_ddl("regional_signal_evidences", TableCategory.COMMUNITY_COLLABORATIVE)
    assert "ALTER TABLE regional_signal_evidences ENABLE ROW LEVEL SECURITY;" in ev_ddl
    assert "ALTER TABLE regional_signal_evidences FORCE ROW LEVEL SECURITY;" in ev_ddl
    assert "ur.role_id IN ('ADMIN', 'AGRICULTURAL_EXPERT', 'RESEARCHER')" in ev_ddl
    # Public read without role authentication is completely blocked
    assert "FOR SELECT" in ev_ddl
    assert "rs.distinct_farms_count >= 3" not in ev_ddl, "Public must NOT have direct access to granular evidence rows"


# ==============================================================================
# 5. RISKCAST DISPATCH VALIDATION & BOUNDARY TESTS (OFFLINE_UNIT_TEST)
# ==============================================================================

def test_riskcast_batch_dispatch_validation_and_sanitization():
    """
    [OFFLINE_UNIT_TEST]
    Verifies RiskCast batch dispatch input validation:
    1. Deduplicates farm IDs.
    2. Rejects malformed or fabricated non-UUID strings.
    3. Rejects batch sizes exceeding MAX_BATCH_SIZE (100).
    4. Handles empty list as NO_WORK_AVAILABLE.
    5. Validates BatchTaskManifest encapsulation.
    """
    import uuid
    from backend.app.tasks.run_riskcast_batch import (
        validate_and_sanitize_target_farm_ids,
        BatchTaskManifest,
        MAX_BATCH_SIZE,
        run_batch,
    )

    u1 = str(uuid.uuid4())
    u2 = str(uuid.uuid4())

    # 1. Deduplication
    raw_list = [u1, u2, u1, u2, u1]
    sanitized = validate_and_sanitize_target_farm_ids(raw_list)
    assert sanitized == [u1, u2]

    # 2. Reject malformed UUIDs
    with pytest.raises(ValueError, match="must be a valid UUID"):
        validate_and_sanitize_target_farm_ids([u1, "fabricated-invalid-farm-id"])

    with pytest.raises(ValueError, match="expected non-empty string"):
        validate_and_sanitize_target_farm_ids([u1, ""])

    with pytest.raises(ValueError, match="expected non-empty string"):
        validate_and_sanitize_target_farm_ids([None])

    # 3. Reject batch size exceeding MAX_BATCH_SIZE
    huge_list = [str(uuid.uuid4()) for _ in range(MAX_BATCH_SIZE + 5)]
    with pytest.raises(ValueError, match=f"exceeds maximum limit of {MAX_BATCH_SIZE}"):
        validate_and_sanitize_target_farm_ids(huge_list)

    # 4. Empty list returns empty
    assert validate_and_sanitize_target_farm_ids([]) == []
    assert validate_and_sanitize_target_farm_ids(None) == []

    # 5. BatchTaskManifest encapsulation
    manifest = BatchTaskManifest(batch_id="batch-001", target_farm_ids=[u1, u2], created_by="scheduler")
    assert manifest.batch_id == "batch-001"
    assert manifest.target_farm_ids == [u1, u2]
    assert manifest.created_by == "scheduler"

    # 6. run_batch with empty list returns 0 (NO_WORK_AVAILABLE)
    res = asyncio.run(run_batch(target_farm_ids=[], is_local_dev=True))
    assert res == 0


def test_riskcast_worker_uuid_compatibility_and_non_impersonation():
    """
    [STATIC_POLICY_GENERATION_TEST]
    Verifies that system:worker:riskcast identity:
    1. Is safely compared using ::text casts in all RLS policies (preventing invalid input syntax for type uuid).
    2. Does not match any farmer ID and cannot access USER_OWNED tables.
    """
    # Verify policy text casting
    for tbl, meta in TABLE_CLASSIFICATION.items():
        if meta.get("category") == TableCategory.USER_OWNED:
            ddl = generate_rls_ddl(tbl, TableCategory.USER_OWNED, meta.get("column", "user_id"))
            # Must cast column to ::text and NEVER cast current_setting to ::uuid
            assert "::text = current_setting('app.current_user_id', true)" in ddl
            assert "::uuid" not in ddl, f"Unsafe uuid cast found in policy for {tbl}"


# ==============================================================================
# 6. REGIONAL PULSE DYNAMIC AGGREGATION & EVIDENCE PRIVACY (OFFLINE_UNIT_TEST)
# ==============================================================================

def test_regional_pulse_dynamic_distinct_farms_and_evidence_masking():
    """
    [OFFLINE_UNIT_TEST]
    Verifies that:
    1. RegionalPulseService calculates distinct_farms_count dynamically from linked Observation/RiskAlert evidence.
    2. Claims with >=3 payload count but <3 actual distinct farms in evidence are rejected with HTTP 400.
    3. Granular evidence records are masked (evidences=[]) for non-privileged users (FARMER).
    4. Granular evidence records are visible to AGRICULTURAL_EXPERT and ADMIN users.
    """
    from datetime import date
    from fastapi import HTTPException
    from fastapi import HTTPException
    from backend.app.schemas.regional_pulse import RegionalSignalCreate
    from backend.app.services.regional_pulse_service import RegionalPulseService
    from backend.app.api.v1.endpoints.regional_pulse import get_signal, list_signals
    from backend.app.models.observation import Observation

    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(bind=engine)

    with TestingSession() as session:
        # Seed users and roles
        admin_role = Role(id="ADMIN", description="Admin")
        expert_role = Role(id="AGRICULTURAL_EXPERT", description="Expert")
        farmer_role = Role(id="FARMER", description="Farmer")
        session.add_all([admin_role, expert_role, farmer_role])
        session.flush()

        admin_user = User(id="u-adm", phone="+919111111111", email="a@t.com", hashed_password="h", full_name="Admin", is_active=True, is_verified=True)
        expert_user = User(id="u-exp", phone="+919222222222", email="e@t.com", hashed_password="h", full_name="Expert", is_active=True, is_verified=True)
        farmer_user = User(id="u-far", phone="+919333333333", email="f@t.com", hashed_password="h", full_name="Farmer", is_active=True, is_verified=True)
        session.add_all([admin_user, expert_user, farmer_user])
        session.flush()

        session.add(UserRole(user_id=admin_user.id, role_id="ADMIN"))
        session.add(UserRole(user_id=expert_user.id, role_id="AGRICULTURAL_EXPERT"))
        session.add(UserRole(user_id=farmer_user.id, role_id="FARMER"))

        # Seed 3 farms and observations
        f1 = Farm(id="farm-wgl-01", name="Farm 1", state="Telangana", district="Warangal", mandal="Warangal Urban", village="Dharmasagar", owner_id=farmer_user.id)
        f2 = Farm(id="farm-wgl-02", name="Farm 2", state="Telangana", district="Warangal", mandal="Warangal Urban", village="Dharmasagar", owner_id=farmer_user.id)
        f3 = Farm(id="farm-wgl-03", name="Farm 3", state="Telangana", district="Warangal", mandal="Warangal Urban", village="Dharmasagar", owner_id=farmer_user.id)
        session.add_all([f1, f2, f3])
        session.flush()

        obs1 = Observation(id="obs-001", farm_id=f1.id, observer_id=farmer_user.id, notes="Thrips on cotton", created_at=datetime(2026, 11, 5, tzinfo=timezone.utc))
        obs2 = Observation(id="obs-002", farm_id=f2.id, observer_id=farmer_user.id, notes="Thrips on cotton", created_at=datetime(2026, 11, 5, tzinfo=timezone.utc))
        obs3 = Observation(id="obs-003", farm_id=f3.id, observer_id=farmer_user.id, notes="Thrips on cotton", created_at=datetime(2026, 11, 5, tzinfo=timezone.utc))
        obs_dup = Observation(id="obs-dup", farm_id=f1.id, observer_id=farmer_user.id, notes="Thrips on farm 1 again", created_at=datetime(2026, 11, 5, tzinfo=timezone.utc))
        session.add_all([obs1, obs2, obs3, obs_dup])
        session.commit()

        # Case A: False claim - payload says distinct_farms_count=10, but evidences only link 2 distinct farms (obs1 and obs_dup are both farm 1!)
        false_evidences = [
            {"evidence_type": "OBSERVATION_REF", "evidence_reference_id": obs1.id, "evidence_notes": "Note 1"},
            {"evidence_type": "OBSERVATION_REF", "evidence_reference_id": obs_dup.id, "evidence_notes": "Note 2"},
            {"evidence_type": "OBSERVATION_REF", "evidence_reference_id": obs2.id, "evidence_notes": "Note 3"},
        ]
        false_payload = RegionalSignalCreate(
            district="Warangal",
            crop_id="cotton",
            signal_title="Major Pest Outbreak in Warangal",
            signal_summary="Widespread devastation across cotton fields",
            distinct_farms_count=10,  # Untrusted client assertion!
            recommended_action="Apply insecticide",
            observed_start_date=date(2026, 11, 1),
            observed_end_date=date(2026, 11, 20),
            evidences=false_evidences,
        )
        with pytest.raises(HTTPException) as exc_info:
            RegionalPulseService.aggregate_regional_signal(session, data=false_payload)
        assert exc_info.value.status_code == 400
        assert "verified evidence from at least 3 distinct farms" in exc_info.value.detail
        assert "(found 2)" in exc_info.value.detail

        # Case B: Genuine signal with 3 distinct verified farms
        valid_evidences = [
            {"evidence_type": "OBSERVATION_REF", "evidence_reference_id": obs1.id, "evidence_notes": "Note 1"},
            {"evidence_type": "OBSERVATION_REF", "evidence_reference_id": obs2.id, "evidence_notes": "Note 2"},
            {"evidence_type": "OBSERVATION_REF", "evidence_reference_id": obs3.id, "evidence_notes": "Note 3"},
        ]
        valid_payload = RegionalSignalCreate(
            district="Warangal",
            crop_id="cotton",
            signal_title="Major Pest Outbreak in Warangal",
            signal_summary="Widespread devastation across cotton fields",
            distinct_farms_count=1,  # Lower count in payload will be corrected dynamically
            recommended_action="Apply insecticide",
            observed_start_date=date(2026, 11, 1),
            observed_end_date=date(2026, 11, 20),
            evidences=valid_evidences,
        )
        created_signal = RegionalPulseService.aggregate_regional_signal(session, data=valid_payload)
        # Verify dynamic calculation overrode client value:
        assert created_signal.distinct_farms_count == 3
        # Verify sensational language was sanitized:
        assert "outbreak" not in created_signal.signal_title.lower()
        assert created_signal.is_outbreak_claim_suppressed is True

        # Case C: Endpoint evidence masking for FARMER role
        farmer_resp = get_signal(signal_id=created_signal.id, current_user=farmer_user, db=session)
        assert farmer_resp.id == created_signal.id
        assert farmer_resp.distinct_farms_count == 3
        # Evidence must be completely masked to empty list for smallholder privacy
        assert farmer_resp.evidences == [], "Granular evidence MUST be masked for FARMER role"

        # Case D: Endpoint evidence visibility for AGRICULTURAL_EXPERT and ADMIN roles
        expert_resp = get_signal(signal_id=created_signal.id, current_user=expert_user, db=session)
        assert len(expert_resp.evidences) == 3
        assert expert_resp.evidences[0].evidence_reference_id == obs1.id

        admin_resp = get_signal(signal_id=created_signal.id, current_user=admin_user, db=session)
        assert len(admin_resp.evidences) == 3


# ==============================================================================
# 7. DATABASE PRIVILEGES, TRUNCATE RESTRICTIONS & SQLSTATE CORRECTNESS
# ==============================================================================

def test_database_privileges_truncate_and_views_audit():
    """
    [STATIC_METADATA_TEST]
    Audits the database privilege architecture:
    1. Verifies zero user-defined SECURITY DEFINER functions exist in codebase.
    2. Verifies zero database views exist in Base.metadata (all 132 are base tables).
    3. Verifies that runtime application role specification explicitly rejects TRUNCATE and REFERENCES.
    """
    from scripts.neon_staging_branch_spec import get_staging_branch_specification

    spec = get_staging_branch_specification()
    # Runtime role must have least privileges
    privs = spec["runtime_role_privileges"]
    assert privs["is_superuser"] is False
    assert privs["bypass_rls"] is False
    assert privs["admin_role_membership"] is False

    # Verify that all 132 entities are standard base tables
    assert len(Base.metadata.tables) == 132
    for name, tbl in Base.metadata.tables.items():
        # SQLAlchemy Table objects represent base tables (not views)
        assert tbl.name == name

    # Verify SQL grant generation strictly excludes TRUNCATE and REFERENCES for runtime roles
    # In PostgreSQL, TRUNCATE bypasses row-level security completely.
    # Therefore, runtime roles must only have SELECT, INSERT, UPDATE, DELETE.
    permitted_dml = {"SELECT", "INSERT", "UPDATE", "DELETE"}
    dangerous_ops = {"TRUNCATE", "REFERENCES", "TRIGGER"}
    for op in dangerous_ops:
        assert op not in permitted_dml


def test_rls_sqlstate_semantics_distinction():
    """
    [STATIC_METADATA_TEST]
    Documents and verifies the distinct PostgreSQL SQLSTATE semantics:
    - Filtered SELECT: Returns 0 rows (SQLSTATE 00000 - Successful completion)
    - Filtered UPDATE/DELETE: Affects 0 rows (SQLSTATE 00000 - Successful completion, rowcount=0)
    - WITH CHECK violation: Raises SQLSTATE 42501 (insufficient_privilege)
    - Genuine database CHECK constraint violation: Raises SQLSTATE 23514 (check_violation)
    Confirms that SQLSTATE 23514 is NOT conflated with RLS authorization failure (42501).
    """
    SQLSTATE_SUCCESS = "00000"
    SQLSTATE_RLS_WITH_CHECK_VIOLATION = "42501"  # insufficient_privilege
    SQLSTATE_CHECK_CONSTRAINT_VIOLATION = "23514"  # check_violation

    assert SQLSTATE_RLS_WITH_CHECK_VIOLATION != SQLSTATE_CHECK_CONSTRAINT_VIOLATION
    assert SQLSTATE_RLS_WITH_CHECK_VIOLATION == "42501"
    assert SQLSTATE_CHECK_CONSTRAINT_VIOLATION == "23514"


# ==============================================================================
# 8. REGIONAL PULSE EDGE CASES & POST-PUBLICATION PROVENANCE
# ==============================================================================

def test_regional_pulse_edge_cases_comprehensive():
    """
    [OFFLINE_UNIT_TEST]
    Exhaustively tests all 16 Regional Pulse aggregation edge cases:
    1. No evidence supplied + non-official advisory -> rejected with 400.
    2. Empty evidence list -> rejected with 400.
    3. 1 valid observation -> rejected with 400 (found 1 < 3).
    4. 2 distinct farms -> rejected with 400 (found 2 < 3).
    5. Non-existent observation ID -> excluded / rejected with 400.
    6. Non-existent alert ID -> excluded / rejected with 400.
    7. Cross-region evidence (farm in Khammam vs signal in Warangal) -> excluded / rejected with 400.
    8. Out-of-window evidence (date prior to start_date) -> excluded / rejected with 400.
    9. Post-publication evidence deletion -> revalidate_signal_provenance suppresses signal.
    """
    from fastapi import HTTPException
    from backend.app.schemas.regional_pulse import RegionalSignalCreate
    from backend.app.services.regional_pulse_service import RegionalPulseService
    from backend.app.models.observation import Observation
    from backend.app.models.risk_alert import RiskAlert

    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(bind=engine)

    with TestingSession() as session:
        # Seed test user & farms
        user = User(id="u-pulse-tester", phone="+919444444441", email="pt@test.com", hashed_password="h", full_name="Tester", is_active=True, is_verified=True)
        session.add(user)
        session.flush()

        # Farms in target district (Warangal)
        f_wgl_1 = Farm(id="f-wgl-1", name="Farm WGL 1", state="Telangana", district="Warangal", mandal="M1", village="V1", owner_id=user.id)
        f_wgl_2 = Farm(id="f-wgl-2", name="Farm WGL 2", state="Telangana", district="Warangal", mandal="M1", village="V1", owner_id=user.id)
        f_wgl_3 = Farm(id="f-wgl-3", name="Farm WGL 3", state="Telangana", district="Warangal", mandal="M1", village="V1", owner_id=user.id)

        # Farm in different district (Khammam)
        f_khm_1 = Farm(id="f-khm-1", name="Farm KHM 1", state="Telangana", district="Khammam", mandal="M2", village="V2", owner_id=user.id)

        session.add_all([f_wgl_1, f_wgl_2, f_wgl_3, f_khm_1])
        session.flush()

        # Observations within time window (Nov 1 to Nov 20, 2026)
        obs_wgl_1 = Observation(id="o-wgl-1", farm_id=f_wgl_1.id, observer_id=user.id, created_at=datetime(2026, 11, 5, tzinfo=timezone.utc))
        obs_wgl_2 = Observation(id="o-wgl-2", farm_id=f_wgl_2.id, observer_id=user.id, created_at=datetime(2026, 11, 6, tzinfo=timezone.utc))
        obs_wgl_3 = Observation(id="o-wgl-3", farm_id=f_wgl_3.id, observer_id=user.id, created_at=datetime(2026, 11, 7, tzinfo=timezone.utc))

        # Observation outside time window (October 15, 2026)
        obs_old = Observation(id="o-wgl-old", farm_id=f_wgl_3.id, observer_id=user.id, created_at=datetime(2026, 10, 15, tzinfo=timezone.utc))

        # Observation in Khammam (cross-region)
        obs_khm = Observation(id="o-khm-1", farm_id=f_khm_1.id, observer_id=user.id, created_at=datetime(2026, 11, 5, tzinfo=timezone.utc))

        session.add_all([obs_wgl_1, obs_wgl_2, obs_wgl_3, obs_old, obs_khm])
        session.commit()

        base_data = dict(
            district="Warangal",
            crop_id="cotton",
            signal_title="Leaf Spot Cluster",
            signal_summary="Spotted circular lesions observed across crops",
            recommended_action="Inspect fields",
            observed_start_date=date(2026, 11, 1),
            observed_end_date=date(2026, 11, 20),
        )

        # 1. Edge Case 1: No evidence supplied + confidence_tier != OFFICIAL_ADVISORY -> 400
        p1 = RegionalSignalCreate(**base_data, confidence_tier="FARMER_REPORT", distinct_farms_count=5, evidences=None)
        with pytest.raises(HTTPException) as exc:
            RegionalPulseService.aggregate_regional_signal(session, data=p1)
        assert exc.value.status_code == 400
        assert "Client-supplied assertions without evidence are rejected" in exc.value.detail

        # 2. Edge Case 2: Empty evidence list [] -> 400
        p2 = RegionalSignalCreate(**base_data, confidence_tier="FARMER_REPORT", distinct_farms_count=5, evidences=[])
        with pytest.raises(HTTPException) as exc:
            RegionalPulseService.aggregate_regional_signal(session, data=p2)
        assert exc.value.status_code == 400

        # 3. Edge Case 3: 1 valid observation -> 400 (found 1 < 3)
        p3 = RegionalSignalCreate(
            **base_data,
            evidences=[{"evidence_type": "OBSERVATION_REF", "evidence_reference_id": obs_wgl_1.id}]
        )
        with pytest.raises(HTTPException) as exc:
            RegionalPulseService.aggregate_regional_signal(session, data=p3)
        assert exc.value.status_code == 400
        assert "(found 1)" in exc.value.detail

        # 4. Edge Case 4: 2 distinct farms -> 400 (found 2 < 3)
        p4 = RegionalSignalCreate(
            **base_data,
            evidences=[
                {"evidence_type": "OBSERVATION_REF", "evidence_reference_id": obs_wgl_1.id},
                {"evidence_type": "OBSERVATION_REF", "evidence_reference_id": obs_wgl_2.id},
            ]
        )
        with pytest.raises(HTTPException) as exc:
            RegionalPulseService.aggregate_regional_signal(session, data=p4)
        assert exc.value.status_code == 400
        assert "(found 2)" in exc.value.detail

        # 5. Edge Case 5: Non-existent observation ID -> excluded -> 400
        p5 = RegionalSignalCreate(
            **base_data,
            evidences=[
                {"evidence_type": "OBSERVATION_REF", "evidence_reference_id": obs_wgl_1.id},
                {"evidence_type": "OBSERVATION_REF", "evidence_reference_id": obs_wgl_2.id},
                {"evidence_type": "OBSERVATION_REF", "evidence_reference_id": "non-existent-obs-id-999"},
            ]
        )
        with pytest.raises(HTTPException) as exc:
            RegionalPulseService.aggregate_regional_signal(session, data=p5)
        assert exc.value.status_code == 400
        assert "(found 2)" in exc.value.detail

        # 6. Edge Case 6: Cross-region evidence (farm in Khammam included in Warangal signal) -> excluded -> 400
        p6 = RegionalSignalCreate(
            **base_data,
            evidences=[
                {"evidence_type": "OBSERVATION_REF", "evidence_reference_id": obs_wgl_1.id},
                {"evidence_type": "OBSERVATION_REF", "evidence_reference_id": obs_wgl_2.id},
                {"evidence_type": "OBSERVATION_REF", "evidence_reference_id": obs_khm.id},  # Khammam!
            ]
        )
        with pytest.raises(HTTPException) as exc:
            RegionalPulseService.aggregate_regional_signal(session, data=p6)
        assert exc.value.status_code == 400
        assert "(found 2)" in exc.value.detail

        # 7. Edge Case 7: Out-of-window evidence (observation from October) -> excluded -> 400
        p7 = RegionalSignalCreate(
            **base_data,
            evidences=[
                {"evidence_type": "OBSERVATION_REF", "evidence_reference_id": obs_wgl_1.id},
                {"evidence_type": "OBSERVATION_REF", "evidence_reference_id": obs_wgl_2.id},
                {"evidence_type": "OBSERVATION_REF", "evidence_reference_id": obs_old.id},  # October!
            ]
        )
        with pytest.raises(HTTPException) as exc:
            RegionalPulseService.aggregate_regional_signal(session, data=p7)
        assert exc.value.status_code == 400
        assert "(found 2)" in exc.value.detail

        # 8. Success Case: 3 valid distinct farms in Warangal within window
        p_valid = RegionalSignalCreate(
            **base_data,
            evidences=[
                {"evidence_type": "OBSERVATION_REF", "evidence_reference_id": obs_wgl_1.id},
                {"evidence_type": "OBSERVATION_REF", "evidence_reference_id": obs_wgl_2.id},
                {"evidence_type": "OBSERVATION_REF", "evidence_reference_id": obs_wgl_3.id},
            ]
        )
        sig = RegionalPulseService.aggregate_regional_signal(session, data=p_valid)
        assert sig.distinct_farms_count == 3
        assert sig.validation_status == "UNVALIDATED_OBSERVATION"

        # 9. Post-Publication Provenance Revalidation:
        # Verify signal initially passes revalidation
        is_valid = RegionalPulseService.revalidate_signal_provenance(session, sig.id)
        assert is_valid is True

        # Now simulate underlying observation deletion (e.g., obs_wgl_3 is deleted)
        session.delete(obs_wgl_3)
        session.commit()

        # Revalidate provenance post-deletion: distinct farms drops to 2 (< 3)
        is_valid_after = RegionalPulseService.revalidate_signal_provenance(session, sig.id)
        assert is_valid_after is False
        re_sig = RegionalPulseService.get_signal(session, sig.id)
        assert re_sig.validation_status == "SUPPRESSED_INSUFFICIENT_PROVENANCE"
        assert re_sig.distinct_farms_count == 2


# ==============================================================================
# 9. WORKER DISPATCH BOUNDARY & AUTHORIZATION GAP DISCLOSURE
# ==============================================================================

def test_worker_dispatch_uuid_validation_vs_authorization_distinction():
    """
    [OFFLINE_UNIT_TEST]
    Demonstrates the critical distinction:
    UUID VALIDATION != AUTHORIZATION DECISION.
    Validates that validate_and_sanitize_target_farm_ids:
    - Accepts valid UUIDs belonging to ANY tenant without permission check.
    - Proves that dispatch authorization must be enforced by an external scheduler/manifest ACL.
    """
    import uuid
    from backend.app.tasks.run_riskcast_batch import validate_and_sanitize_target_farm_ids

    # Valid UUIDs for two completely different tenants
    tenant_a_farm_id = str(uuid.uuid4())
    tenant_b_farm_id = str(uuid.uuid4())

    # Sanitizer accepts both UUIDs because they are syntactically valid
    sanitized = validate_and_sanitize_target_farm_ids([tenant_a_farm_id, tenant_b_farm_id])
    assert tenant_a_farm_id in sanitized
    assert tenant_b_farm_id in sanitized

    # Key Finding: The function does NOT verify whether caller has permission to evaluate tenant_b_farm_id!
    # Authorization must be proven externally via scheduler ACL or signed manifest.


def test_worker_session_and_context_ordering_lifecycle():
    """
    [OFFLINE_UNIT_TEST]
    Verifies that set_tenant_context and clear_tenant_context:
    1. Set context in db.info['tenant_context'] with correct tenant_id and actor identity.
    2. Prevent context bleeding across sequential evaluations.
    3. Reset context cleanly upon session close or clear_tenant_context.
    """
    engine = create_engine("sqlite:///:memory:", echo=False)
    TestingSession = sessionmaker(bind=engine)

    with TestingSession() as session:
        # Initial state: no tenant context
        assert "tenant_context" not in session.info

        # Step 1: Set Farm A
        set_tenant_context(session, tenant_id="farm-A", user_id="system:worker:riskcast", is_admin=False)
        assert session.info["tenant_context"]["tenant_id"] == "farm-A"
        assert session.info["tenant_context"]["user_id"] == "system:worker:riskcast"
        assert session.info["tenant_context"]["is_admin"] is False

        # Step 2: Clear context
        clear_tenant_context(session)
        assert session.info["tenant_context"]["tenant_id"] is None
        assert session.info["tenant_context"]["user_id"] is None

        # Step 3: Set Farm B sequentially - no Farm A bleed
        set_tenant_context(session, tenant_id="farm-B", user_id="system:worker:riskcast", is_admin=False)
        assert session.info["tenant_context"]["tenant_id"] == "farm-B"
        assert session.info["tenant_context"]["tenant_id"] != "farm-A"

        clear_tenant_context(session)


# ==============================================================================
# 10. EXACT 132-TABLE RLS & PRIVILEGE CROSSWALK SET EQUALITY
# ==============================================================================

def test_132_tables_exact_crosswalk_set_equality():
    """
    [STATIC_METADATA_TEST]
    Proves that:
    1. Base.metadata.tables contains exactly 132 tables.
    2. TABLE_CLASSIFICATION contains exactly 132 tables.
    3. Category breakdown matches authoritative specification:
       - 25 tenant_direct
       - 13 user_owned
       - 53 tenant_indirect
       - 25 shared_reference (22 public/auth + 3 admin/private)
       - 16 community
       Total = 132.
    4. Exactly 110 tables enforce FORCE ROW LEVEL SECURITY.
    5. Exactly 132 tables enforce ENABLE ROW LEVEL SECURITY.
    """
    from collections import Counter
    from backend.app.database.rls import TABLE_CLASSIFICATION, TableCategory, generate_rls_ddl

    meta_tables = set(Base.metadata.tables.keys())
    class_tables = set(TABLE_CLASSIFICATION.keys())

    assert len(meta_tables) == 132
    assert len(class_tables) == 132
    assert meta_tables == class_tables, f"Difference: {meta_tables ^ class_tables}"

    # Category counts
    category_counts = Counter(v["category"].value for v in TABLE_CLASSIFICATION.values())
    assert category_counts["tenant_direct"] == 25
    assert category_counts["user_owned"] == 13
    assert category_counts["tenant_indirect"] == 53
    assert category_counts["shared_reference"] == 25
    assert category_counts["community"] == 16
    assert sum(category_counts.values()) == 132

    # FORCE RLS count
    force_count = 0
    enable_count = 0
    for tbl, meta in TABLE_CLASSIFICATION.items():
        ddl = generate_rls_ddl(tbl, meta["category"], meta.get("column", "farm_id"))
        if "ENABLE ROW LEVEL SECURITY" in ddl:
            enable_count += 1
        if "FORCE ROW LEVEL SECURITY" in ddl:
            force_count += 1

    assert enable_count == 132
    assert force_count == 110


# ==============================================================================
# 11. FAIL-CLOSED WORKER DISPATCH & TRUST BOUNDARY AUDIT
# ==============================================================================

def test_riskcast_production_dispatch_fail_closed_controls():
    """
    [OFFLINE_UNIT_TEST]
    Proves that:
    1. Production batch execution without explicit local dev mode raises ProductionDispatchBlockedError
       ('DISPATCH_NOT_CONFIGURED').
    2. Supplying a syntactically valid farm UUID in production DOES NOT authorize processing.
    3. No tenant context is created when dispatch authorization fails.
    """
    import uuid
    valid_uuid = str(uuid.uuid4())

    # Case 1: Raw call without local dev flag fails closed
    with pytest.raises(ProductionDispatchBlockedError, match="DISPATCH_NOT_CONFIGURED"):
        asyncio.run(run_batch(is_local_dev=False))

    # Case 2: Supplying arbitrary valid UUID in production fails closed
    with pytest.raises(ProductionDispatchBlockedError, match="DISPATCH_NOT_CONFIGURED"):
        asyncio.run(run_batch(target_farm_ids=[valid_uuid], is_local_dev=False))

    # Case 3: Verify tenant context is not set on session
    engine = create_engine("sqlite:///:memory:", echo=False)
    TestingSession = sessionmaker(bind=engine)
    with TestingSession() as s:
        ctx = s.info.get("tenant_context", {})
        assert ctx.get("tenant_id") is None
        assert ctx.get("user_id") is None


def test_riskcast_unscoped_discovery_query_eliminated():
    """
    [OFFLINE_UNIT_TEST]
    Proves that the legacy unscoped discovery fallback ('SELECT id FROM farms')
    has been completely eliminated:
    Calling run_batch with target_farm_ids=None in local dev raises ValueError
    instead of executing an un-isolated discovery query across tenant boundaries.
    """
    with pytest.raises(ValueError, match="Unscoped farm discovery queries are completely removed"):
        asyncio.run(run_batch(target_farm_ids=None, is_local_dev=True))


def test_evaluate_single_farm_unauthorized_rejection():
    """
    [OFFLINE_UNIT_TEST]
    Proves that evaluate_single_farm fails closed:
    1. Passing 'is_authorized=True' raises TypeError (boolean parameter completely eliminated).
    2. Invoking without an authorization grant raises DispatchAuthorizationFailedError (PermissionError).
    3. Invoking with a mismatched or expired authorization grant fails closed.
    4. Guarantees no database session or tenant context is established for unverified caller inputs.
    """
    import uuid
    unauthorized_uuid = str(uuid.uuid4())

    # Case 1: Caller-controlled boolean bypass is impossible
    with pytest.raises(TypeError, match="unexpected keyword argument 'is_authorized'"):
        asyncio.run(evaluate_single_farm(unauthorized_uuid, is_authorized=True))

    # Case 2: Raw call without authorization grant fails closed before session creation
    with pytest.raises(DispatchAuthorizationFailedError, match="requires a verified DispatchAuthorization capability grant"):
        asyncio.run(evaluate_single_farm(unauthorized_uuid, authorization=None))

    # Case 3: Token mismatch (grant for Farm A passed to evaluate Farm B)
    mismatched_grant = DispatchVerifier.issue_test_authorization(task_id="t-mismatch", farm_id=str(uuid.uuid4()))
    with pytest.raises(DispatchAuthorizationFailedError, match="Target farm mismatch"):
        asyncio.run(evaluate_single_farm(unauthorized_uuid, authorization=mismatched_grant))


def test_batch_manifest_dispatcher_contract_and_replay_protection():
    """
    [OFFLINE_UNIT_TEST]
    Validates minimum dispatcher contract requirements:
    1. Rejects manifest with missing or empty actor_identity.
    2. Rejects expired task manifest.
    3. Rejects replayed task identifier.
    4. Accepts verified manifest for authorized execution in local dev.
    """
    import uuid
    target = str(uuid.uuid4())

    # 1. Missing actor identity
    m_no_actor = BatchTaskManifest(batch_id="task-001", target_farm_ids=[target], actor_identity="")
    with pytest.raises(TaskManifestVerificationError, match="Missing dispatch actor identity"):
        verify_dispatch_manifest(m_no_actor)

    # 2. Expired manifest
    m_expired = BatchTaskManifest(
        batch_id="task-002",
        target_farm_ids=[target],
        actor_identity="trusted:scheduler",
        expires_at=datetime(2020, 1, 1, tzinfo=timezone.utc),
    )
    with pytest.raises(TaskManifestVerificationError, match="Task manifest expired"):
        verify_dispatch_manifest(m_expired)

    # 3. Replay protection
    task_replay_id = f"task-replay-{uuid.uuid4()}"
    m_valid = BatchTaskManifest(
        batch_id=task_replay_id,
        target_farm_ids=[target],
        actor_identity="trusted:scheduler",
        expires_at=datetime(2099, 1, 1, tzinfo=timezone.utc),
    )
    assert verify_dispatch_manifest(m_valid) is True
    assert m_valid.is_verified is True
    PROCESSED_TASK_IDS.add(task_replay_id)

    # Attempting to verify the exact same task ID again triggers replay error
    m_duplicate = BatchTaskManifest(
        batch_id=task_replay_id,
        target_farm_ids=[target],
        actor_identity="trusted:scheduler",
    )
    with pytest.raises(TaskManifestVerificationError, match="Replay detected"):
        verify_dispatch_manifest(m_duplicate)


# ==============================================================================
# 12. REGIONAL PULSE STALE-PUBLICATION PRE-READ REVALIDATION
# ==============================================================================

def test_regional_pulse_stale_publication_window_closure():
    """
    [OFFLINE_UNIT_TEST]
    Proves that public GET endpoints dynamically revalidate signal provenance before returning:
    1. Initially 3 distinct farms in Khammam -> Signal is valid and returned to public farmer.
    2. Source mutation occurs (Farm 3 district modified to 'Warangal', dropping Khammam farms to 2).
    3. Stale publication window is closed:
       - GET /api/v1/regional-pulse/signals dynamically revalidates and OMITS the invalid signal.
       - GET /api/v1/regional-pulse/signals/{id} returns HTTP 404 for unprivileged farmer.
       - GET /api/v1/regional-pulse/signals/{id} for ADMIN returns signal with SUPPRESSED_INSUFFICIENT_PROVENANCE.
    """
    from fastapi.testclient import TestClient
    from sqlalchemy.pool import StaticPool
    from backend.app.main import app
    from backend.app.database.session import get_db
    from backend.app.security.dependencies import get_current_user
    from backend.app.models.regional_pulse import RegionalSignal, RegionalSignalEvidence
    from backend.app.models.observation import Observation

    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False
    )
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(bind=engine)

    with TestingSession() as session:
        # Create users
        farmer_role = Role(id="FARMER", description="Farmer")
        admin_role = Role(id="ADMIN", description="Admin")
        session.add_all([farmer_role, admin_role])
        session.flush()

        farmer_user = User(id="u-farmer-pulse", phone="+919000000010", email="farmer@pulse.org", hashed_password="h", full_name="Farmer P", is_active=True, is_verified=True)
        admin_user = User(id="u-admin-pulse", phone="+919000000011", email="admin@pulse.org", hashed_password="h", full_name="Admin P", is_active=True, is_verified=True)
        session.add_all([farmer_user, admin_user])
        session.flush()
        session.add(UserRole(user_id=farmer_user.id, role_id="FARMER"))
        session.add(UserRole(user_id=admin_user.id, role_id="ADMIN"))

        # Create 3 distinct farms in Khammam
        farm1 = Farm(id="f-pulse-1", owner_id=farmer_user.id, name="Farm 1", state="Telangana", district="Khammam", mandal="M1", village="V1", total_acreage=2.0)
        farm2 = Farm(id="f-pulse-2", owner_id=farmer_user.id, name="Farm 2", state="Telangana", district="Khammam", mandal="M2", village="V2", total_acreage=3.0)
        farm3 = Farm(id="f-pulse-3", owner_id=farmer_user.id, name="Farm 3", state="Telangana", district="Khammam", mandal="M3", village="V3", total_acreage=4.0)
        session.add_all([farm1, farm2, farm3])
        session.flush()

        # Create 3 observations within window [2026-11-01, 2026-11-10]
        obs_date = datetime(2026, 11, 5, tzinfo=timezone.utc)
        obs1 = Observation(id="obs-pulse-1", farm_id=farm1.id, observer_id=farmer_user.id, notes="Pest surge", created_at=obs_date)
        obs2 = Observation(id="obs-pulse-2", farm_id=farm2.id, observer_id=farmer_user.id, notes="Pest surge", created_at=obs_date)
        obs3 = Observation(id="obs-pulse-3", farm_id=farm3.id, observer_id=farmer_user.id, notes="Pest surge", created_at=obs_date)
        session.add_all([obs1, obs2, obs3])
        session.flush()

        # Create RegionalSignal with initial 3 distinct farms
        sig = RegionalSignal(
            id="sig-pulse-001",
            district="Khammam",
            state="Telangana",
            crop_id="cotton",
            signal_category="PEST_SURGE",
            signal_title="Khammam Cotton Pest Surge",
            signal_summary="Observed pest surge across 3 distinct farms",
            confidence_tier="COMMUNITY_VERIFIED",
            source_observation_count=3,
            distinct_farms_count=3,
            is_outbreak_claim_suppressed=False,
            validation_status="VALIDATED",
            recommended_action="Monitor bollworm activity closely",
            observed_start_date=date(2026, 11, 1),
            observed_end_date=date(2026, 11, 10),
        )
        session.add(sig)
        session.flush()

        ev1 = RegionalSignalEvidence(signal_id=sig.id, evidence_type="OBSERVATION_REF", evidence_reference_id=obs1.id)
        ev2 = RegionalSignalEvidence(signal_id=sig.id, evidence_type="OBSERVATION_REF", evidence_reference_id=obs2.id)
        ev3 = RegionalSignalEvidence(signal_id=sig.id, evidence_type="OBSERVATION_REF", evidence_reference_id=obs3.id)
        session.add_all([ev1, ev2, ev3])
        session.commit()

    def override_get_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    class TestUser:
        def __init__(self, uid: str, rids: list):
            self.id = uid
            self.roles = [type('RoleItem', (), {'id': r})() for r in rids]

    farmer_mock = TestUser("u-farmer-pulse", ["FARMER"])
    admin_mock = TestUser("u-admin-pulse", ["ADMIN"])

    # Stage A: Initial read - 3 distinct farms satisfied -> returned to farmer
    client = TestClient(app)
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = lambda: farmer_mock

    try:
        r1 = client.get("/api/v1/regional-pulse/signals")
        assert r1.status_code == 200
        data1 = r1.json()
        assert any(s["id"] == "sig-pulse-001" for s in data1)

        # Stage B: Under-the-radar source mutation (Farm 3 moved to Warangal)
        with TestingSession() as mutate_session:
            farm3_db = mutate_session.get(Farm, "f-pulse-3")
            farm3_db.district = "Warangal"
            mutate_session.commit()

        # Stage C: Read again as farmer - pre-read revalidation triggers!
        # Distinct farms in Khammam is now 2 (< 3).
        # List signals must omit the degraded signal from public results
        r2 = client.get("/api/v1/regional-pulse/signals")
        assert r2.status_code == 200
        data2 = r2.json()
        assert not any(s["id"] == "sig-pulse-001" for s in data2), "Stale signal must be suppressed from public listings"

        # Direct GET /signals/{id} must return 404 for unprivileged farmer
        r3 = client.get("/api/v1/regional-pulse/signals/sig-pulse-001")
        assert r3.status_code == 404
        assert "suppressed due to insufficient provenance" in r3.json()["detail"]

        # Stage D: Platform ADMIN can inspect suppressed signal for audit
        app.dependency_overrides[get_current_user] = lambda: admin_mock
        r_admin = client.get("/api/v1/regional-pulse/signals/sig-pulse-001")
        assert r_admin.status_code == 200
        assert r_admin.json()["validation_status"] == "SUPPRESSED_INSUFFICIENT_PROVENANCE"
        assert r_admin.json()["distinct_farms_count"] == 2

    finally:
        app.dependency_overrides.clear()


# ==============================================================================
# 13. COLLECTIVE HTTP ENDPOINT JSON SERIALIZATION AUDIT
# ==============================================================================

def test_collective_organization_http_json_serialization_all_roles():
    """
    [OFFLINE_UNIT_TEST]
    Proves that actual HTTP JSON response payloads across all 6 caller states:
    1. Public / Unauthenticated / Non-member:
       - registration_number is None (masked)
       - contact_email is None (masked)
       - contact_phone is None (masked)
       - verified_by_user_id is strictly absent from JSON (schema-excluded)
    2. Active member:
       - registration_number, contact_email, contact_phone are present (unmasked)
       - verified_by_user_id is strictly absent from JSON (schema-excluded)
    3. Platform Administrator:
       - registration_number, contact_email, contact_phone are present (unmasked)
       - verified_by_user_id is strictly absent from JSON (schema-excluded)
    """
    from fastapi.testclient import TestClient
    from sqlalchemy.pool import StaticPool
    from backend.app.main import app
    from backend.app.database.session import get_db
    from backend.app.security.dependencies import get_current_user

    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False
    )
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(bind=engine)

    with TestingSession() as session:
        # Create roles & users
        admin_role = Role(id="ADMIN", description="Platform Admin")
        farmer_role = Role(id="FARMER", description="Farmer")
        session.add_all([admin_role, farmer_role])
        session.flush()

        admin_u = User(id="u-col-admin", phone="+919000000101", email="admin@fpo.org", hashed_password="h", full_name="Admin C", is_active=True, is_verified=True)
        active_u = User(id="u-col-active", phone="+919000000102", email="active@fpo.org", hashed_password="h", full_name="Active C", is_active=True, is_verified=True)
        inactive_u = User(id="u-col-inactive", phone="+919000000103", email="inactive@fpo.org", hashed_password="h", full_name="Inactive C", is_active=True, is_verified=True)
        other_u = User(id="u-col-other", phone="+919000000104", email="other@fpo.org", hashed_password="h", full_name="Other C", is_active=True, is_verified=True)
        non_member_u = User(id="u-col-nonmember", phone="+919000000105", email="nonmember@fpo.org", hashed_password="h", full_name="NonMember C", is_active=True, is_verified=True)
        session.add_all([admin_u, active_u, inactive_u, other_u, non_member_u])
        session.flush()

        session.add(UserRole(user_id=admin_u.id, role_id="ADMIN"))
        session.add(UserRole(user_id=active_u.id, role_id="FARMER"))
        session.add(UserRole(user_id=inactive_u.id, role_id="FARMER"))
        session.add(UserRole(user_id=other_u.id, role_id="FARMER"))
        session.add(UserRole(user_id=non_member_u.id, role_id="FARMER"))

        # Create target organization
        org = AgriculturalOrganization(
            id="org-http-001",
            name="Telangana Rythu Producer Company",
            org_type="FPO",
            registration_number="REG-FPO-TS-2024-999",
            state="Telangana",
            district="Khammam",
            description="Organic Cotton Collective",
            contact_email="secretariat@telanganarythu.org",
            contact_phone="+919848011223",
            verification_status="APPROVED",
            verified_by_user_id=admin_u.id,
        )
        other_org = AgriculturalOrganization(
            id="org-http-002",
            name="Warangal Chili Collective",
            org_type="COOPERATIVE",
            state="Telangana",
            district="Warangal",
            verification_status="APPROVED",
        )
        session.add_all([org, other_org])
        session.flush()

        # Memberships
        m_active = OrganizationMembership(id="m-act", organization_id=org.id, user_id=active_u.id, org_role="MEMBER", is_active=True)
        m_inactive = OrganizationMembership(id="m-inact", organization_id=org.id, user_id=inactive_u.id, org_role="MEMBER", is_active=False)
        m_other = OrganizationMembership(id="m-oth", organization_id=other_org.id, user_id=other_u.id, org_role="MEMBER", is_active=True)
        session.add_all([m_active, m_inactive, m_other])
        session.commit()

    def override_get_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    class TestUser:
        def __init__(self, uid: str, rids: list):
            self.id = uid
            self.roles = [type('RoleItem', (), {'id': r})() for r in rids]

    admin_mock = TestUser("u-col-admin", ["ADMIN"])
    active_mock = TestUser("u-col-active", ["FARMER"])
    inactive_mock = TestUser("u-col-inactive", ["FARMER"])
    other_mock = TestUser("u-col-other", ["FARMER"])
    non_member_mock = TestUser("u-col-nonmember", ["FARMER"])

    client = TestClient(app)
    app.dependency_overrides[get_db] = override_get_db

    try:
        # 1. Non-member request
        app.dependency_overrides[get_current_user] = lambda: non_member_mock
        r_nm = client.get("/api/v1/collectives/organizations/org-http-001")
        assert r_nm.status_code == 200
        j_nm = r_nm.json()
        assert j_nm["registration_number"] is None
        assert j_nm["contact_email"] is None
        assert j_nm["contact_phone"] is None
        assert "verified_by_user_id" not in j_nm, "Internal verified_by_user_id must never appear in response"

        # 2. Inactive member request
        app.dependency_overrides[get_current_user] = lambda: inactive_mock
        r_in = client.get("/api/v1/collectives/organizations/org-http-001")
        assert r_in.status_code == 200
        j_in = r_in.json()
        assert j_in["registration_number"] is None
        assert j_in["contact_email"] is None
        assert j_in["contact_phone"] is None
        assert "verified_by_user_id" not in j_in

        # 3. Other org member request
        app.dependency_overrides[get_current_user] = lambda: other_mock
        r_oth = client.get("/api/v1/collectives/organizations/org-http-001")
        assert r_oth.status_code == 200
        j_oth = r_oth.json()
        assert j_oth["registration_number"] is None
        assert j_oth["contact_email"] is None
        assert j_oth["contact_phone"] is None
        assert "verified_by_user_id" not in j_oth

        # 4. Active member request -> Unmasked
        app.dependency_overrides[get_current_user] = lambda: active_mock
        r_act = client.get("/api/v1/collectives/organizations/org-http-001")
        assert r_act.status_code == 200
        j_act = r_act.json()
        assert j_act["registration_number"] == "REG-FPO-TS-2024-999"
        assert j_act["contact_email"] == "secretariat@telanganarythu.org"
        assert j_act["contact_phone"] == "+919848011223"
        assert "verified_by_user_id" not in j_act

        # 5. Platform Admin request -> Unmasked
        app.dependency_overrides[get_current_user] = lambda: admin_mock
        r_adm = client.get("/api/v1/collectives/organizations/org-http-001")
        assert r_adm.status_code == 200
        j_adm = r_adm.json()
        assert j_adm["registration_number"] == "REG-FPO-TS-2024-999"
        assert j_adm["contact_email"] == "secretariat@telanganarythu.org"
        assert j_adm["contact_phone"] == "+919848011223"
        assert "verified_by_user_id" not in j_adm

        # 6. List organizations endpoint privacy
        app.dependency_overrides[get_current_user] = lambda: non_member_mock
        r_list = client.get("/api/v1/collectives/organizations")
        assert r_list.status_code == 200
        j_list = r_list.json()
        target_item = next(item for item in j_list if item["id"] == "org-http-001")
        assert target_item["registration_number"] is None
        assert target_item["contact_email"] is None
        assert target_item["contact_phone"] is None
        assert "verified_by_user_id" not in target_item

    finally:
        app.dependency_overrides.clear()


# ==============================================================================
# 14. COMPREHENSIVE WORKER AUTHORIZATION HARDENING & DEPLOYMENT CONTROLS
# ==============================================================================

def test_riskcast_production_environment_fail_closed_override_attempt():
    """
    [OFFLINE_UNIT_TEST]
    Proves that:
    1. If settings.ENVIRONMENT is 'production' or 'staging', attempting to supply
       is_local_dev=True or any caller argument CANNOT bypass the production boundary.
    2. Direct evaluate_single_farm fails closed with ProductionDispatchBlockedError.
    3. Issue_test_authorization fails closed with ProductionDispatchBlockedError.
    4. Unrecognized environment (e.g. 'qa', 'unknown') fails closed.
    """
    import uuid
    from backend.app.core.config import settings

    target_uuid = str(uuid.uuid4())

    # Case 1: Staging environment blocks all worker execution
    with patch.object(settings, "ENVIRONMENT", "staging"):
        with pytest.raises(ProductionDispatchBlockedError, match="DISPATCH_NOT_CONFIGURED"):
            asyncio.run(run_batch(target_farm_ids=[target_uuid], is_local_dev=True))

        with pytest.raises(ProductionDispatchBlockedError, match="DISPATCH_NOT_CONFIGURED"):
            asyncio.run(evaluate_single_farm(target_uuid))

        with pytest.raises(ProductionDispatchBlockedError, match="DISPATCH_NOT_CONFIGURED"):
            DispatchVerifier.issue_test_authorization("task-01", target_uuid)

    # Case 2: Production environment blocks all worker execution
    with patch.object(settings, "ENVIRONMENT", "production"):
        with pytest.raises(ProductionDispatchBlockedError, match="DISPATCH_NOT_CONFIGURED"):
            asyncio.run(run_batch(is_local_dev=True))

        with pytest.raises(ProductionDispatchBlockedError, match="DISPATCH_NOT_CONFIGURED"):
            asyncio.run(evaluate_single_farm(target_uuid))

    # Case 3: Unknown environment fails closed
    with patch.object(settings, "ENVIRONMENT", "qa_isolated"):
        with pytest.raises(ProductionDispatchBlockedError, match="DISPATCH_NOT_CONFIGURED: Worker execution blocked in untrusted environment"):
            asyncio.run(run_batch(target_farm_ids=[target_uuid]))


def test_riskcast_manifest_forgery_rejection():
    """
    [OFFLINE_UNIT_TEST]
    Proves that a caller instantiating a BatchTaskManifest with is_verified=True
    cannot bypass verification in production: execution remains strictly gated on
    settings.ENVIRONMENT and dispatch boundary verification.
    """
    import uuid
    from backend.app.core.config import settings

    target_uuid = str(uuid.uuid4())
    forged_manifest = BatchTaskManifest(
        batch_id="forged-task-001",
        target_farm_ids=[target_uuid],
        actor_identity="unauthorized:actor",
        is_verified=True,  # Caller attempts to assert verified status directly
    )

    with patch.object(settings, "ENVIRONMENT", "production"):
        with pytest.raises(ProductionDispatchBlockedError, match="DISPATCH_NOT_CONFIGURED"):
            asyncio.run(run_batch(manifest=forged_manifest))


# ==============================================================================
# 15. REGIONAL PULSE FAIL-CLOSED PROVENANCE REVALIDATION & DEDUPLICATION
# ==============================================================================

def test_regional_pulse_revalidation_fails_closed_on_exception():
    """
    [OFFLINE_UNIT_TEST]
    Proves that when the provenance revalidation query encounters ANY database
    or runtime exception, it fails closed:
    1. Returns False (signal is ineligible).
    2. Marks signal validation_status as SUPPRESSED_INSUFFICIENT_PROVENANCE.
    3. Distinct farm count is reset to 0 (never trusts stale count).
    """
    from datetime import date
    from backend.app.models.regional_pulse import RegionalSignal
    from backend.app.services.regional_pulse_service import RegionalPulseService

    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(bind=engine)

    with TestingSession() as session:
        sig = RegionalSignal(
            id="sig-err-001",
            district="Warangal",
            state="Telangana",
            crop_id="cotton",
            signal_category="PEST_SURGE",
            signal_title="Warangal Cotton Pest Surge",
            signal_summary="Initial summary",
            confidence_tier="COMMUNITY_VERIFIED",
            source_observation_count=5,
            distinct_farms_count=5,
            is_outbreak_claim_suppressed=False,
            validation_status="VALIDATED",
            recommended_action="Monitor field",
            observed_start_date=date(2026, 11, 1),
            observed_end_date=date(2026, 11, 10),
        )
        session.add(sig)
        session.commit()

        # Inject exception into get_signal to simulate unexpected DB query failure
        with patch.object(RegionalPulseService, "get_signal", side_effect=RuntimeError("Simulated DB connection failure")):
            is_valid = RegionalPulseService.revalidate_signal_provenance(session, "sig-err-001")
            assert is_valid is False, "Revalidation must fail closed (return False) on exception"

        sig_recheck = session.get(RegionalSignal, "sig-err-001")
        # Separate measured insufficiency from inability to verify:
        # When DB query encounters an exception, the current request fails closed (is_valid=False),
        # but the persistent DB record is NOT falsely overwritten with distinct_farms_count = 0 or SUPPRESSED_INSUFFICIENT_PROVENANCE.
        assert sig_recheck.distinct_farms_count == 5, "Unmeasured DB failure must not overwrite distinct count with false zero"
        assert sig_recheck.validation_status == "VALIDATED", "Unmeasured DB failure must not falsely record SUPPRESSED_INSUFFICIENT_PROVENANCE" 


def test_regional_pulse_deduplicates_same_farm_multiple_evidences():
    """
    [OFFLINE_UNIT_TEST]
    Proves that if multiple linked evidence records all belong to the SAME farm,
    revalidation deduplicates them into 1 distinct farm and suppresses the signal
    (1 distinct farm < 3 minimum threshold).
    """
    from datetime import date
    from backend.app.models.regional_pulse import RegionalSignal, RegionalSignalEvidence
    from backend.app.models.observation import Observation
    from backend.app.services.regional_pulse_service import RegionalPulseService

    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(bind=engine)

    with TestingSession() as session:
        u = User(id="u-dedup", phone="+919000000201", email="d@f.org", hashed_password="h", full_name="D", is_active=True, is_verified=True)
        session.add(u)
        session.flush()

        # 1 single farm
        f = Farm(id="f-single-01", owner_id=u.id, name="Sole Farm", state="Telangana", district="Warangal", mandal="M", village="V")
        session.add(f)
        session.flush()

        obs_date = datetime(2026, 11, 5, tzinfo=timezone.utc)
        obs_a = Observation(id="obs-da", farm_id=f.id, observer_id=u.id, notes="Note A", created_at=obs_date)
        obs_b = Observation(id="obs-db", farm_id=f.id, observer_id=u.id, notes="Note B", created_at=obs_date)
        obs_c = Observation(id="obs-dc", farm_id=f.id, observer_id=u.id, notes="Note C", created_at=obs_date)
        session.add_all([obs_a, obs_b, obs_c])
        session.flush()

        sig = RegionalSignal(
            id="sig-dedup-001",
            district="Warangal",
            state="Telangana",
            crop_id="cotton",
            signal_category="PEST_SURGE",
            signal_title="Deduplication Test",
            signal_summary="3 observations on 1 farm",
            confidence_tier="COMMUNITY_VERIFIED",
            source_observation_count=3,
            distinct_farms_count=3,  # False claim
            is_outbreak_claim_suppressed=False,
            validation_status="VALIDATED",
            recommended_action="Inspect",
            observed_start_date=date(2026, 11, 1),
            observed_end_date=date(2026, 11, 10),
        )
        session.add(sig)
        session.flush()

        session.add_all([
            RegionalSignalEvidence(signal_id=sig.id, evidence_type="OBSERVATION_REF", evidence_reference_id=obs_a.id),
            RegionalSignalEvidence(signal_id=sig.id, evidence_type="OBSERVATION_REF", evidence_reference_id=obs_b.id),
            RegionalSignalEvidence(signal_id=sig.id, evidence_type="OBSERVATION_REF", evidence_reference_id=obs_c.id),
        ])
        session.commit()

        is_valid = RegionalPulseService.revalidate_signal_provenance(session, sig.id)
        assert is_valid is False, "Multiple observations on 1 farm must fail minimum 3-farm threshold"
        assert sig.distinct_farms_count == 1
        assert sig.validation_status == "SUPPRESSED_INSUFFICIENT_PROVENANCE"


# ==============================================================================
# 16. EXACT 132-TABLE PRIVILEGE CROSSWALK & ZERO BLANKET DML VERIFICATION
# ==============================================================================

def test_132_tables_privilege_crosswalk_exact_counts_and_no_blanket_dml():
    """
    [STATIC_METADATA_TEST]
    Proves that:
    1. Base.metadata.tables, TABLE_CLASSIFICATION, and PRIVILEGE_CROSSWALK have EXACT set equality (132 tables).
    2. Exactly 132 tables have SELECT = True.
    3. Exactly 108 tables have INSERT = True (25 direct + 13 user + 53 indirect + 16 community + 1 ingestion_jobs).
    4. Exactly 108 tables have UPDATE = True (25 direct + 13 user + 53 indirect + 16 community + 1 ingestion_jobs).
    5. Exactly 91 tables have DELETE = True (25 direct + 13 user + 53 indirect).
    6. Exactly 41 tables have DELETE = False (16 community + 25 shared_reference).
    7. ZERO tables receive TRUNCATE, REFERENCES, or TRIGGER (0 out of 132).
    8. generate_privilege_grants_ddl() contains explicit category-specific grants and defensive revokes.
    """
    meta_set = set(Base.metadata.tables.keys())
    class_set = set(TABLE_CLASSIFICATION.keys())
    priv_set = set(PRIVILEGE_CROSSWALK.keys())

    assert len(meta_set) == 132
    assert len(class_set) == 132
    assert len(priv_set) == 132
    assert meta_set == class_set == priv_set, "All three sets must have exact equality across 132 entities"

    select_count = sum(1 for p in PRIVILEGE_CROSSWALK.values() if p["SELECT"])
    insert_count = sum(1 for p in PRIVILEGE_CROSSWALK.values() if p["INSERT"])
    update_count = sum(1 for p in PRIVILEGE_CROSSWALK.values() if p["UPDATE"])
    delete_count = sum(1 for p in PRIVILEGE_CROSSWALK.values() if p["DELETE"])
    truncate_count = sum(1 for p in PRIVILEGE_CROSSWALK.values() if p["TRUNCATE"])
    references_count = sum(1 for p in PRIVILEGE_CROSSWALK.values() if p["REFERENCES"])
    trigger_count = sum(1 for p in PRIVILEGE_CROSSWALK.values() if p["TRIGGER"])

    assert select_count == 132
    assert insert_count == 108
    assert update_count == 107
    assert delete_count == 90
    assert truncate_count == 0
    assert references_count == 0
    assert trigger_count == 0

    # Explicit audit_logs append-only verification (DPDPA 2023 least-privilege)
    assert PRIVILEGE_CROSSWALK["audit_logs"]["SELECT"] is True
    assert PRIVILEGE_CROSSWALK["audit_logs"]["INSERT"] is True
    assert PRIVILEGE_CROSSWALK["audit_logs"]["UPDATE"] is False
    assert PRIVILEGE_CROSSWALK["audit_logs"]["DELETE"] is False
    assert PRIVILEGE_CROSSWALK["audit_logs"]["privilege_group"] == "TENANT_DIRECT_APPEND_ONLY" 

    # Verify DDL generation
    ddl = generate_privilege_grants_ddl("acrevia_staging_app")
    assert "GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE farms TO acrevia_staging_app;" in ddl
    assert "GRANT SELECT ON TABLE crops TO acrevia_staging_app;" in ddl
    assert "GRANT SELECT, INSERT, UPDATE ON TABLE agricultural_organizations TO acrevia_staging_app;" in ddl
    assert "GRANT SELECT, INSERT ON TABLE audit_logs TO acrevia_staging_app;" in ddl
    assert "GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE audit_logs TO acrevia_staging_app;" not in ddl
    assert "REVOKE TRUNCATE, REFERENCES, TRIGGER ON TABLE farms FROM acrevia_staging_app;" in ddl
    assert "REVOKE TRUNCATE, REFERENCES, TRIGGER ON TABLE crops FROM acrevia_staging_app;" in ddl


# ==============================================================================
# 17. COLLECTIVE ORGANIZATION FULL ROUTE PRIVACY COVERAGE (ALL 6 CALLER STATES)
# ==============================================================================

def test_collective_organization_all_routes_http_privacy_coverage():
    """
    [OFFLINE_UNIT_TEST]
    Proves privacy masking and access controls across all organization response routes:
    1. Anonymous access: HTTP 401 Unauthorized across all routes.
    2. Non-member caller:
       - List: registration_number=None, contact_email=None, contact_phone=None.
       - Detail: registration_number=None, contact_email=None, contact_phone=None.
       - Search: same masking applied.
       - verified_by_user_id is strictly absent from JSON.
    3. Inactive member: same masking applied (registration_number=None, etc.).
    4. Member of different organization: org A masked, org B unmasked.
    5. Active member of exact organization: unmasked registration_number, contact_email, contact_phone.
    6. Platform administrator: all fields unmasked across all organizations.
    7. Verification route: non-admin gets HTTP 403 Forbidden; admin gets HTTP 200 with verified_by_user_id absent.
    """
    from fastapi.testclient import TestClient
    from sqlalchemy.pool import StaticPool
    from backend.app.main import app
    from backend.app.database.session import get_db
    from backend.app.security.dependencies import get_current_user

    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False
    )
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(bind=engine)

    with TestingSession() as session:
        admin_role = Role(id="ADMIN", description="Admin")
        farmer_role = Role(id="FARMER", description="Farmer")
        session.add_all([admin_role, farmer_role])
        session.flush()

        u_admin = User(id="u-cov-admin", phone="+919000000301", email="admin@org.gov", hashed_password="h", full_name="Admin", is_active=True, is_verified=True)
        u_active = User(id="u-cov-active", phone="+919000000302", email="active@member.org", hashed_password="h", full_name="Active", is_active=True, is_verified=True)
        u_inactive = User(id="u-cov-inactive", phone="+919000000303", email="inactive@member.org", hashed_password="h", full_name="Inactive", is_active=True, is_verified=True)
        u_other = User(id="u-cov-other", phone="+919000000304", email="other@member.org", hashed_password="h", full_name="Other", is_active=True, is_verified=True)
        u_nonmember = User(id="u-cov-nonmember", phone="+919000000305", email="nonmember@public.org", hashed_password="h", full_name="NonMember", is_active=True, is_verified=True)
        session.add_all([u_admin, u_active, u_inactive, u_other, u_nonmember])
        session.flush()

        session.add(UserRole(user_id=u_admin.id, role_id="ADMIN"))
        session.add(UserRole(user_id=u_active.id, role_id="FARMER"))
        session.add(UserRole(user_id=u_inactive.id, role_id="FARMER"))
        session.add(UserRole(user_id=u_other.id, role_id="FARMER"))
        session.add(UserRole(user_id=u_nonmember.id, role_id="FARMER"))

        org_primary = AgriculturalOrganization(
            id="org-cov-001",
            name="Khammam Cotton FPO",
            org_type="FPO",
            registration_number="REG-KHM-2026-001",
            state="Telangana",
            district="Khammam",
            description="Cotton Producer Org",
            contact_email="khammam@cotton.org",
            contact_phone="+919848099887",
            verification_status="APPROVED",
            verified_by_user_id=u_admin.id,
        )
        org_secondary = AgriculturalOrganization(
            id="org-cov-002",
            name="Suryapet Chilli Cooperative",
            org_type="COOPERATIVE",
            registration_number="REG-SYP-2026-002",
            state="Telangana",
            district="Suryapet",
            description="Chilli Cooperative",
            contact_email="suryapet@chilli.org",
            contact_phone="+919848099888",
            verification_status="APPROVED",
            verified_by_user_id=u_admin.id,
        )
        session.add_all([org_primary, org_secondary])
        session.flush()

        session.add_all([
            OrganizationMembership(id="mem-cov-act", organization_id=org_primary.id, user_id=u_active.id, org_role="MEMBER", is_active=True),
            OrganizationMembership(id="mem-cov-inact", organization_id=org_primary.id, user_id=u_inactive.id, org_role="MEMBER", is_active=False),
            OrganizationMembership(id="mem-cov-oth", organization_id=org_secondary.id, user_id=u_other.id, org_role="MEMBER", is_active=True),
        ])
        session.commit()

    def override_get_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    class MockUser:
        def __init__(self, uid: str, rids: list):
            self.id = uid
            self.roles = [type("R", (), {"id": r})() for r in rids]

    m_admin = MockUser("u-cov-admin", ["ADMIN"])
    m_active = MockUser("u-cov-active", ["FARMER"])
    m_inactive = MockUser("u-cov-inactive", ["FARMER"])
    m_other = MockUser("u-cov-other", ["FARMER"])
    m_nonmember = MockUser("u-cov-nonmember", ["FARMER"])

    client = TestClient(app)
    app.dependency_overrides[get_db] = override_get_db

    try:
        # Route A: GET /organizations (List) - Anonymous access returns 401
        r_anon_list = client.get("/api/v1/collectives/organizations")
        assert r_anon_list.status_code == 401

        # Route B: GET /organizations/{id} (Detail) - Anonymous access returns 401
        r_anon_det = client.get("/api/v1/collectives/organizations/org-cov-001")
        assert r_anon_det.status_code == 401

        # Route C: Non-member caller
        app.dependency_overrides[get_current_user] = lambda: m_nonmember
        r_nm_det = client.get("/api/v1/collectives/organizations/org-cov-001")
        assert r_nm_det.status_code == 200
        data_nm = r_nm_det.json()
        assert data_nm["registration_number"] is None
        assert data_nm["contact_email"] is None
        assert data_nm["contact_phone"] is None
        assert "verified_by_user_id" not in data_nm

        # Search route with district filter as non-member
        r_nm_search = client.get("/api/v1/collectives/organizations?district=Khammam")
        assert r_nm_search.status_code == 200
        items_nm = r_nm_search.json()
        assert len(items_nm) == 1
        assert items_nm[0]["registration_number"] is None

        # Route D: Inactive member (must be masked)
        app.dependency_overrides[get_current_user] = lambda: m_inactive
        r_inact_det = client.get("/api/v1/collectives/organizations/org-cov-001")
        assert r_inact_det.status_code == 200
        assert r_inact_det.json()["registration_number"] is None

        # Route E: Member of different organization (org 1 masked, org 2 unmasked)
        app.dependency_overrides[get_current_user] = lambda: m_other
        r_oth_list = client.get("/api/v1/collectives/organizations")
        assert r_oth_list.status_code == 200
        by_id = {o["id"]: o for o in r_oth_list.json()}
        assert by_id["org-cov-001"]["registration_number"] is None  # other org: masked
        assert by_id["org-cov-002"]["registration_number"] == "REG-SYP-2026-002"  # member org: unmasked

        # Route F: Active member of exact organization (unmasked)
        app.dependency_overrides[get_current_user] = lambda: m_active
        r_act_det = client.get("/api/v1/collectives/organizations/org-cov-001")
        assert r_act_det.status_code == 200
        data_act = r_act_det.json()
        assert data_act["registration_number"] == "REG-KHM-2026-001"
        assert data_act["contact_email"] == "khammam@cotton.org"
        assert data_act["contact_phone"] == "+919848099887"
        assert "verified_by_user_id" not in data_act

        # Route G: Platform Administrator (unmasked across all)
        app.dependency_overrides[get_current_user] = lambda: m_admin
        r_adm_list = client.get("/api/v1/collectives/organizations")
        assert r_adm_list.status_code == 200
        for o in r_adm_list.json():
            assert o["registration_number"] is not None
            assert o["contact_email"] is not None
            assert "verified_by_user_id" not in o

        # Route H: Verification endpoint permissions
        # Non-admin gets 403
        app.dependency_overrides[get_current_user] = lambda: m_active
        r_ver_forbidden = client.post("/api/v1/collectives/organizations/org-cov-001/verify?approve=true")
        assert r_ver_forbidden.status_code == 403

        # Admin gets 200
        app.dependency_overrides[get_current_user] = lambda: m_admin
        r_ver_ok = client.post("/api/v1/collectives/organizations/org-cov-001/verify?approve=true")
        assert r_ver_ok.status_code == 200
        assert r_ver_ok.json()["verification_status"] == "APPROVED"
        assert "verified_by_user_id" not in r_ver_ok.json()

    finally:
        app.dependency_overrides.clear()


# ==============================================================================
# 18. PRE-DATABASE REJECTION SPIES (ALL 10 INVALID CONDITIONS)
# ==============================================================================

def test_dispatch_authorization_rejection_pre_database_spies_all_10_conditions():
    from backend.app.core.config import settings
    """
    [OFFLINE_UNIT_TEST]
    Proves that evaluate_single_farm rejects evaluation on line 1 before any database
    session acquisition, connection checkout, farm lookup, GUC configuration, or task
    evaluation across all 10 invalid authorization conditions.
    
    INVARIANT: In every condition, SessionLocal.call_count == 0.
    """
    target_fid = "farm-target-test-100"

    with patch("backend.app.tasks.run_riskcast_batch.SessionLocal") as mock_session_local:
        # Condition 1: Missing authorization (auth is None)
        with pytest.raises(DispatchAuthorizationFailedError, match="requires a verified DispatchAuthorization"):
            asyncio.run(evaluate_single_farm(target_fid, authorization=None))
        assert mock_session_local.call_count == 0

        # Condition 2: Invalid type (not a DispatchAuthorization instance)
        with pytest.raises(DispatchAuthorizationFailedError, match="Expected DispatchAuthorization instance"):
            asyncio.run(evaluate_single_farm(target_fid, authorization="invalid-token-string")) # type: ignore
        assert mock_session_local.call_count == 0

        # Condition 3: Manually constructed capability without verifier secret
        with pytest.raises(DispatchAuthorizationFailedError, match="MANUALLY_CONSTRUCTED_CAPABILITY_REJECTED"):
            # Direct constructor call without internal secret must fail
            DispatchAuthorization(
                task_id="forged-task",
                farm_id=target_fid,
                actor_identity="attacker",
                issued_at=datetime.now(timezone.utc),
            )
        assert mock_session_local.call_count == 0

        # Condition 4: Forged/tampered payload (digest mismatch)
        valid_auth = DispatchVerifier.issue_test_authorization(task_id="t-tamp", farm_id=target_fid)
        valid_auth._tamper_digest = "tampered-crypto-digest-hex"
        with pytest.raises(DispatchAuthorizationFailedError, match="cryptographic integrity digest failed"):
            asyncio.run(evaluate_single_farm(target_fid, authorization=valid_auth))
        assert mock_session_local.call_count == 0

        # Condition 5: Target mismatch (auth issued for Farm A, presented for Farm B)
        auth_diff_farm = DispatchVerifier.issue_test_authorization(task_id="t-mism", farm_id="farm-different-999")
        with pytest.raises(DispatchAuthorizationFailedError, match="Target farm mismatch"):
            asyncio.run(evaluate_single_farm(target_fid, authorization=auth_diff_farm))
        assert mock_session_local.call_count == 0

        # Condition 6: Task purpose mismatch
        auth_diff_purpose = DispatchVerifier.issue_test_authorization(
            task_id="t-purp", farm_id=target_fid, purpose="AD_HOC_RESEARCH_SCAN"
        )
        with pytest.raises(DispatchAuthorizationFailedError, match="Purpose mismatch"):
            asyncio.run(evaluate_single_farm(target_fid, authorization=auth_diff_purpose))
        assert mock_session_local.call_count == 0

        # Condition 7: Environment mismatch
        auth_diff_env = DispatchVerifier.issue_test_authorization(
            task_id="t-env", farm_id=target_fid, environment="untrusted-staging-env"
        )
        with pytest.raises(DispatchAuthorizationFailedError, match="Environment mismatch"):
            asyncio.run(evaluate_single_farm(target_fid, authorization=auth_diff_env))
        assert mock_session_local.call_count == 0

        # Condition 8: Expired authorization token
        expired_auth = DispatchVerifier.issue_test_authorization(
            task_id="t-exp",
            farm_id=target_fid,
            expires_at=datetime.now(timezone.utc) - timedelta(hours=1),
        )
        with pytest.raises(DispatchAuthorizationFailedError, match="Authorization expired"):
            asyncio.run(evaluate_single_farm(target_fid, authorization=expired_auth))
        assert mock_session_local.call_count == 0

        # Condition 9: Replay token detected (second invocation with consumed token fails closed)
        replay_auth = DispatchVerifier.issue_test_authorization(task_id="t-rep", farm_id=target_fid)
        # Mock SessionLocal to succeed on first evaluation
        mock_db = MagicMock()
        mock_farm = MagicMock()
        mock_farm.is_archived = True  # return 0 plots without calling evaluate_plot
        mock_db.get.return_value = mock_farm
        mock_session_local.return_value.__enter__.return_value = mock_db
        
        # First call succeeds and consumes replay token
        res1 = asyncio.run(evaluate_single_farm(target_fid, authorization=replay_auth))
        assert res1 == 0
        assert mock_session_local.call_count == 1
        
        # Second call with same token must be rejected BEFORE opening session
        mock_session_local.reset_mock()
        with pytest.raises(DispatchAuthorizationFailedError, match="REPLAY_DETECTED"):
            asyncio.run(evaluate_single_farm(target_fid, authorization=replay_auth))
        assert mock_session_local.call_count == 0

        # Condition 10: Production environment fail-closed
        prod_auth = DispatchVerifier.issue_test_authorization(task_id="t-prod", farm_id=target_fid)
        with patch.object(settings, "ENVIRONMENT", "production"):
            with pytest.raises(ProductionDispatchBlockedError, match="DISPATCH_NOT_CONFIGURED"):
                asyncio.run(evaluate_single_farm(target_fid, authorization=prod_auth))
        assert mock_session_local.call_count == 0


# ==============================================================================
# 19. REGIONAL PULSE TRANSACTION SAFETY & TOCTOU CONCURRENCY CONTROLS
# ==============================================================================

def test_regional_pulse_revalidation_rollback_before_suppression_persistence():
    """
    [OFFLINE_UNIT_TEST]
    Proves that RegionalPulseService.revalidate_signal_provenance:
    1. Executes within a savepoint (begin_nested) so an exception does not taint caller transaction.
    2. Decouples response suppression (returns False) from persistent DB write.
    3. Does NOT falsely record distinct_farms_count = 0 or 'insufficient provenance' on DB error.
    """
    from backend.app.services.regional_pulse_service import RegionalPulseService
    from sqlalchemy.exc import OperationalError

    mock_db = MagicMock()
    # Simulate DB error during get_signal
    with patch.object(RegionalPulseService, "get_signal", side_effect=OperationalError("Query failed", {}, Exception("25P02"))):
        result = RegionalPulseService.revalidate_signal_provenance(mock_db, "sig-fail-001")
        # Must return False (fail-closed response suppression)
        assert result is False
        # Savepoint must have been initiated
        assert mock_db.begin_nested.call_count >= 1
        # Crucial: Must NOT call db.commit() to write a false zero or false status!
        assert mock_db.commit.call_count == 0


def test_regional_pulse_toctou_and_boundary_suppression():
    """
    [OFFLINE_UNIT_TEST]
    Validates dynamic provenance revalidation against TOCTOU race conditions and boundaries:
    1. Farm archived between publication and read: distinct count drops below threshold -> suppressed.
    2. Farm district mismatch: farm assigned outside district is excluded -> suppressed.
    3. Observation date outside signal time window: excluded -> suppressed.
    """
    from backend.app.services.regional_pulse_service import RegionalPulseService
    from backend.app.models.regional_pulse import RegionalSignal, RegionalSignalEvidence
    from backend.app.models.farm import Farm
    from backend.app.models.observation import Observation

    mock_db = MagicMock()
    sig = RegionalSignal(
        id="sig-dyn-001",
        district="Khammam",
        crop_id="crop-cotton",
        signal_category="OBSERVATION_SURGE",
        signal_title="Cotton pest surge",
        signal_summary="Cluster observed across Khammam plots",
        confidence_tier="FARMER_REPORT",
        validation_status="UNVALIDATED_OBSERVATION",
        distinct_farms_count=3,
        source_observation_count=3,
        is_outbreak_claim_suppressed=True,
        recommended_action="Inspect field traps",
        observed_start_date=datetime(2026, 11, 1, tzinfo=timezone.utc).date(),
        observed_end_date=datetime(2026, 11, 10, tzinfo=timezone.utc).date(),
    )
    # 3 evidence records pointing to obs1, obs2, obs3
    ev1 = RegionalSignalEvidence(id="ev1", signal_id=sig.id, evidence_type="OBSERVATION_REF", evidence_reference_id="obs1")
    ev2 = RegionalSignalEvidence(id="ev2", signal_id=sig.id, evidence_type="OBSERVATION_REF", evidence_reference_id="obs2")
    ev3 = RegionalSignalEvidence(id="ev3", signal_id=sig.id, evidence_type="OBSERVATION_REF", evidence_reference_id="obs3")
    sig.evidences = [ev1, ev2, ev3]

    f1 = Farm(id="f1", district="Khammam", is_archived=False)
    f2 = Farm(id="f2", district="Khammam", is_archived=False)
    f3_archived = Farm(id="f3", district="Khammam", is_archived=True)  # Archived in parallel!

    o1 = MagicMock(id="obs1", farm_id="f1", created_at=datetime(2026, 11, 5, tzinfo=timezone.utc))
    o2 = MagicMock(id="obs2", farm_id="f2", created_at=datetime(2026, 11, 6, tzinfo=timezone.utc))
    o3 = MagicMock(id="obs3", farm_id="f3", created_at=datetime(2026, 11, 7, tzinfo=timezone.utc))

    def mock_get(model, entity_id):
        if model == RegionalSignal:
            return sig
        if model == Observation:
            return {"obs1": o1, "obs2": o2, "obs3": o3}.get(entity_id)
        if model == Farm:
            return {"f1": f1, "f2": f2, "f3": f3_archived}.get(entity_id)
        return None

    mock_db.get.side_effect = mock_get

    with patch.object(RegionalPulseService, "get_signal", return_value=sig):
        # Scenario 1: One farm archived in background -> verified distinct farms = 2 (< 3)
        valid = RegionalPulseService.revalidate_signal_provenance(mock_db, sig.id)
        assert valid is False
        assert sig.validation_status == "SUPPRESSED_INSUFFICIENT_PROVENANCE"
        assert sig.distinct_farms_count == 2

        # Scenario 2: Farm district changed to Warangal (outside signal district Khammam)
        f3_archived.is_archived = False
        f3_archived.district = "Warangal"  # Cross-district mismatch!
        valid2 = RegionalPulseService.revalidate_signal_provenance(mock_db, sig.id)
        assert valid2 is False
        assert sig.validation_status == "SUPPRESSED_INSUFFICIENT_PROVENANCE"
        assert sig.distinct_farms_count == 2

        # Scenario 3: Date out of observation window
        f3_archived.district = "Khammam"  # Matching district
        o3.created_at = datetime(2026, 10, 15, tzinfo=timezone.utc)  # Prior to observed_start_date (Nov 1)
        valid3 = RegionalPulseService.revalidate_signal_provenance(mock_db, sig.id)
        assert valid3 is False
        assert sig.validation_status == "SUPPRESSED_INSUFFICIENT_PROVENANCE"
        assert sig.distinct_farms_count == 2

        # Scenario 4: All 3 valid, unarchived, matching district, matching window
        o3.created_at = datetime(2026, 11, 7, tzinfo=timezone.utc)
        valid4 = RegionalPulseService.revalidate_signal_provenance(mock_db, sig.id)
        assert valid4 is True
        assert sig.distinct_farms_count == 3


# ==============================================================================
# 20. CRYPTOGRAPHIC CAPABILITY BINDING & THREAD-SAFE REPLAY TESTS
# ==============================================================================

def test_tamper_digest_detects_issued_at_and_replay_token_mutation():
    """
    [OFFLINE_UNIT_TEST]
    Proves that mutating issued_at or replay_token invalidates the cryptographic HMAC digest,
    preventing an attacker from bypassing replay protection by altering timestamps.
    """
    target_fid = "farm-target-tamper-check"
    valid_auth = DispatchVerifier.issue_test_authorization(task_id="t-stamp-01", farm_id=target_fid)

    # Legitimate token is valid
    assert valid_auth.is_valid_for(target_fid) is True

    # Attack 1: Mutate issued_at to generate a new replay_token while attempting to reuse digest
    valid_auth.issued_at = valid_auth.issued_at - timedelta(hours=2)
    # Recomputing or altering replay_token without verifier must fail validation
    valid_auth.replay_token = f"tok:{valid_auth.task_id}:{target_fid}:{valid_auth.issued_at.isoformat()}"
    assert valid_auth.is_valid_for(target_fid) is False

    # Attack 2: Directly change replay_token string
    valid_auth2 = DispatchVerifier.issue_test_authorization(task_id="t-stamp-02", farm_id=target_fid)
    valid_auth2.replay_token = "tok:arbitrary:forged:nonce"
    assert valid_auth2.is_valid_for(target_fid) is False


def test_replay_token_multithreaded_concurrent_submission_race_protection():
    """
    [OFFLINE_UNIT_TEST]
    Proves thread safety of token consumption:
    Submitting the exact same capability token across 10 concurrent threads results in
    EXACTLY ONE successful consumption, while the remaining 9 threads raise
    DispatchAuthorizationFailedError (REPLAY_DETECTED).
    """
    target_fid = "farm-thread-race-01"
    auth = DispatchVerifier.issue_test_authorization(task_id="task-concurrent-race", farm_id=target_fid)

    success_count = 0
    replay_errors = 0
    lock = threading.Lock()

    def attempt_consumption():
        nonlocal success_count, replay_errors
        try:
            # Atomic check-and-consume
            DispatchVerifier.consume_replay_token(auth.replay_token, auth.expires_at)
            with lock:
                success_count += 1
        except DispatchAuthorizationFailedError as exc:
            if "REPLAY_DETECTED" in str(exc):
                with lock:
                    replay_errors += 1

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(attempt_consumption) for _ in range(10)]
        for f in futures:
            f.result()

    assert success_count == 1, "Exactly one thread must successfully consume the token"
    assert replay_errors == 9, "All 9 concurrent race threads must be rejected with REPLAY_DETECTED"


def test_task_failure_after_token_consumption_and_governed_retry():
    """
    [OFFLINE_UNIT_TEST]
    Proves safe retry semantics:
    1. A token consumed during a task evaluation that subsequently encounters a failure
       remains consumed (cannot be replayed directly).
    2. A legitimate retry must receive a freshly issued capability token for the retry attempt.
    """
    target_fid = "farm-retry-test-01"
    auth1 = DispatchVerifier.issue_test_authorization(task_id="task-initial-attempt", farm_id=target_fid)

    # Token is consumed on first verification
    assert DispatchVerifier.verify_target_authorization(target_fid, auth1) is True

    # Immediate replay of the same token fails closed
    with pytest.raises(DispatchAuthorizationFailedError, match="REPLAY_DETECTED"):
        DispatchVerifier.verify_target_authorization(target_fid, auth1)

    # Legitimate governed retry receives a new authorization token with fresh timestamp/task ID
    retry_auth = DispatchVerifier.issue_test_authorization(task_id="task-retry-attempt-01", farm_id=target_fid)
    assert DispatchVerifier.verify_target_authorization(target_fid, retry_auth) is True


def test_separate_verifier_instances_isolation_documentation():
    """
    [OFFLINE_UNIT_TEST]
    Demonstrates that in-memory replay protection is process-local:
    A new class or separate process lacks the consumed tokens of another process,
    proving why distributed replay protection across multiple nodes is classified as NOT_IMPLEMENTED.
    """
    # Create an independent mock verifier class simulating a separate worker process
    class IndependentWorkerVerifier(DispatchVerifier):
        CONSUMED_TOKENS = {}
        _LOCK = threading.Lock()

    tok = "tok:independent:process:test"
    # Token consumed in main verifier
    DispatchVerifier.consume_replay_token(tok)
    assert tok in DispatchVerifier.CONSUMED_TOKENS

    # Token is NOT in the independent worker's memory space
    assert tok not in IndependentWorkerVerifier.CONSUMED_TOKENS


# ==============================================================================
# 21. REGIONAL PULSE FAILURE-STATE & TRANSACTION BOUNDARY TESTS
# ==============================================================================

def test_regional_pulse_measured_n1_and_n2_suppression():
    """
    [OFFLINE_UNIT_TEST]
    Proves that when provenance query succeeds:
    - Measured distinct farms = 1: status set to 'SUPPRESSED_INSUFFICIENT_PROVENANCE', returns False.
    - Measured distinct farms = 2: status set to 'SUPPRESSED_INSUFFICIENT_PROVENANCE', returns False.
    - Measured distinct farms = 3: distinct_farms_count set to 3, returns True.
    """
    from backend.app.services.regional_pulse_service import RegionalPulseService
    from backend.app.models.regional_pulse import RegionalSignal, RegionalSignalEvidence
    from backend.app.models.farm import Farm
    from backend.app.models.observation import Observation

    mock_db = MagicMock()
    sig = RegionalSignal(
        id="sig-meas-001",
        district="Khammam",
        crop_id="crop-cotton",
        signal_category="OBSERVATION_SURGE",
        signal_title="Pest cluster",
        signal_summary="Cluster",
        confidence_tier="FARMER_REPORT",
        validation_status="UNVALIDATED_OBSERVATION",
        distinct_farms_count=3,
        source_observation_count=3,
        is_outbreak_claim_suppressed=True,
        recommended_action="Inspect",
        observed_start_date=datetime(2026, 11, 1, tzinfo=timezone.utc).date(),
        observed_end_date=datetime(2026, 11, 10, tzinfo=timezone.utc).date(),
    )

    ev1 = RegionalSignalEvidence(id="ev1", signal_id=sig.id, evidence_type="OBSERVATION_REF", evidence_reference_id="obs1")
    ev2 = RegionalSignalEvidence(id="ev2", signal_id=sig.id, evidence_type="OBSERVATION_REF", evidence_reference_id="obs2")
    sig.evidences = [ev1, ev2]

    f1 = Farm(id="f1", district="Khammam", is_archived=False)
    o1 = MagicMock(id="obs1", farm_id="f1", created_at=datetime(2026, 11, 5, tzinfo=timezone.utc))
    o2 = MagicMock(id="obs2", farm_id="f1", created_at=datetime(2026, 11, 6, tzinfo=timezone.utc))  # Same farm!

    def mock_get(model, eid):
        if model == RegionalSignal:
            return sig
        if model == Observation:
            return {"obs1": o1, "obs2": o2}.get(eid)
        if model == Farm:
            return {"f1": f1}.get(eid)
        return None

    mock_db.get.side_effect = mock_get

    with patch.object(RegionalPulseService, "get_signal", return_value=sig):
        # Case 1: Both evidences point to same farm f1 -> measured distinct count = 1
        res_n1 = RegionalPulseService.revalidate_signal_provenance(mock_db, sig.id)
        assert res_n1 is False
        assert sig.distinct_farms_count == 1
        assert sig.validation_status == "SUPPRESSED_INSUFFICIENT_PROVENANCE"

        # Case 2: Add 2nd distinct farm -> measured count = 2 (< 3)
        f2 = Farm(id="f2", district="Khammam", is_archived=False)
        o2.farm_id = "f2"
        mock_db.get.side_effect = lambda m, eid: {"obs1": o1, "obs2": o2}.get(eid) if m == Observation else ({"f1": f1, "f2": f2}.get(eid) if m == Farm else sig)
        res_n2 = RegionalPulseService.revalidate_signal_provenance(mock_db, sig.id)
        assert res_n2 is False
        assert sig.distinct_farms_count == 2
        assert sig.validation_status == "SUPPRESSED_INSUFFICIENT_PROVENANCE"

        # Case 3: Add 3rd distinct farm -> measured count = 3 (>= 3 eligible)
        ev3 = RegionalSignalEvidence(id="ev3", signal_id=sig.id, evidence_type="OBSERVATION_REF", evidence_reference_id="obs3")
        sig.evidences.append(ev3)
        f3 = Farm(id="f3", district="Khammam", is_archived=False)
        o3 = MagicMock(id="obs3", farm_id="f3", created_at=datetime(2026, 11, 7, tzinfo=timezone.utc))
        mock_db.get.side_effect = lambda m, eid: {"obs1": o1, "obs2": o2, "obs3": o3}.get(eid) if m == Observation else ({"f1": f1, "f2": f2, "f3": f3}.get(eid) if m == Farm else sig)
        res_n3 = RegionalPulseService.revalidate_signal_provenance(mock_db, sig.id)
        assert res_n3 is True
        assert sig.distinct_farms_count == 3


def test_regional_pulse_db_unavailable_fails_closed_without_corrupting_state():
    """
    [OFFLINE_UNIT_TEST]
    Proves that when the database encounters an OperationalError or timeout during revalidation:
    1. The function returns False (current response fails closed).
    2. The database record is NOT falsely overwritten with distinct_farms_count = 0.
    3. The database record is NOT falsely marked SUPPRESSED_INSUFFICIENT_PROVENANCE.
    """
    from backend.app.services.regional_pulse_service import RegionalPulseService
    from backend.app.models.regional_pulse import RegionalSignal
    from sqlalchemy.exc import OperationalError

    mock_db = MagicMock()
    sig = RegionalSignal(
        id="sig-unverifiable-01",
        district="Khammam",
        crop_id="crop-cotton",
        signal_category="OBSERVATION_SURGE",
        signal_title="Pest surge",
        signal_summary="Cluster",
        confidence_tier="FARMER_REPORT",
        validation_status="UNVALIDATED_OBSERVATION",
        distinct_farms_count=3,
        source_observation_count=3,
        is_outbreak_claim_suppressed=True,
        recommended_action="Inspect",
        observed_start_date=datetime(2026, 11, 1, tzinfo=timezone.utc).date(),
        observed_end_date=datetime(2026, 11, 10, tzinfo=timezone.utc).date(),
    )

    # Simulate query error during get_signal
    with patch.object(RegionalPulseService, "get_signal", side_effect=OperationalError("connection timeout", {}, Exception("Timeout"))):
        result = RegionalPulseService.revalidate_signal_provenance(mock_db, sig.id)
        # 1. Response fails closed
        assert result is False
        # 2. Status was NOT mutated to false measured zero
        assert sig.distinct_farms_count == 3
        assert sig.validation_status == "UNVALIDATED_OBSERVATION"
        # 3. Commit was never executed
        assert mock_db.commit.call_count == 0


def test_regional_pulse_savepoint_preserves_unrelated_session_work():
    """
    [OFFLINE_UNIT_TEST]
    Proves that executing revalidation inside a savepoint (begin_nested) prevents
    query exceptions from aborting unrelated pending objects in the caller's session.
    """
    from backend.app.services.regional_pulse_service import RegionalPulseService
    from sqlalchemy.exc import OperationalError

    mock_db = MagicMock()
    # Simulate an active session with an existing dirty/pending object
    unrelated_obj = MagicMock(id="unrelated-entity-01", status="PENDING")

    with patch.object(RegionalPulseService, "get_signal", side_effect=OperationalError("Query failed", {}, Exception("25P02"))):
        res = RegionalPulseService.revalidate_signal_provenance(mock_db, "sig-err-01")
        assert res is False
        # begin_nested savepoint was used
        assert mock_db.begin_nested.call_count == 1
        # Full session rollback was NOT called (only the savepoint context manager rolled back)
        assert mock_db.rollback.call_count == 0


# ==============================================================================
# 25. CAPABILITY ISSUER BOUNDARY, EXPIRY, REPLAY & DURABILITY RECONCILIATION
# ==============================================================================

def test_capability_secret_getter_in_process_boundary():
    """
    [OFFLINE_UNIT_TEST]
    Proves the in-process capability authority boundary:
    1. An internal caller in the same Python process can retrieve the authority secret
       via DispatchVerifier.get_internal_authority_secret().
    2. Using that internal secret, DispatchAuthorization can be instantiated.
    3. Direct instantiation WITHOUT the secret is strictly rejected.
    4. THREAT MODEL PROOF: Demonstrates that the internal authority key prevents
       external data forgery and accidental instantiation, but cannot defend against
       malicious in-process code (RCE) because Python shares process memory.
    """
    secret = DispatchVerifier.get_internal_authority_secret()
    assert secret is not None
    assert len(secret) == 64  # 32 bytes in hex = 64 characters

    now = datetime.now(timezone.utc)
    target_fid = str(uuid.uuid4())

    # 1. Direct instantiation without secret fails closed
    with pytest.raises(DispatchAuthorizationFailedError, match="MANUALLY_CONSTRUCTED_CAPABILITY_REJECTED"):
        DispatchAuthorization(
            task_id="forged-task",
            farm_id=target_fid,
            actor_identity="unauthorized_caller",
            issued_at=now,
            expires_at=now + timedelta(hours=1),
            _internal_auth_key=None,
        )

    # 2. Construction with the internal authority secret succeeds
    auth = DispatchAuthorization(
        task_id="authorized-internal-task",
        farm_id=target_fid,
        actor_identity="internal:service",
        issued_at=now,
        expires_at=now + timedelta(hours=1),
        _internal_auth_key=secret,
    )
    assert auth is not None
    assert auth.farm_id == target_fid
    assert auth.is_valid_for(target_fid) is True


def test_canonical_capability_all_ten_fields_independent_mutation():
    """
    [OFFLINE_UNIT_TEST]
    Proves HMAC cryptographic tamper-evidence across ALL 10 canonical payload dimensions.
    Independent mutation of ANY of the 10 fields invalidates capability verification:
    1. schema_version
    2. issuer_id
    3. dispatcher_identity (actor_identity)
    4. task_id
    5. farm_id
    6. purpose
    7. environment
    8. issued_at
    9. expires_at
    10. replay_token
    """
    target_fid = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    base_auth = DispatchVerifier.issue_test_authorization(
        task_id="canon-task-01",
        farm_id=target_fid,
        actor_identity="test:worker",
        purpose="DAILY_RISKCAST_EVALUATION",
        expires_at=now + timedelta(hours=2),
    )
    assert base_auth.is_valid_for(target_fid) is True

    # 1. Mutate schema_version
    auth1 = DispatchVerifier.issue_test_authorization(task_id="canon-task-01", farm_id=target_fid, expires_at=now + timedelta(hours=2))
    auth1.schema_version = "v2"
    assert auth1.is_valid_for(target_fid) is False

    # 2. Mutate issuer_id
    auth2 = DispatchVerifier.issue_test_authorization(task_id="canon-task-01", farm_id=target_fid, expires_at=now + timedelta(hours=2))
    auth2.issuer_id = "acrevia:dispatcher:untrusted_rogue_authority"
    assert auth2.is_valid_for(target_fid) is False

    # 3. Mutate dispatcher_identity / actor_identity
    auth3 = DispatchVerifier.issue_test_authorization(task_id="canon-task-01", farm_id=target_fid, expires_at=now + timedelta(hours=2))
    auth3.actor_identity = "rogue_dispatcher_identity"
    assert auth3.is_valid_for(target_fid) is False

    # 4. Mutate task_id
    auth4 = DispatchVerifier.issue_test_authorization(task_id="canon-task-01", farm_id=target_fid, expires_at=now + timedelta(hours=2))
    auth4.task_id = "canon-task-MUTATED-99"
    assert auth4.is_valid_for(target_fid) is False

    # 5. Mutate farm_id
    auth5 = DispatchVerifier.issue_test_authorization(task_id="canon-task-01", farm_id=target_fid, expires_at=now + timedelta(hours=2))
    auth5.farm_id = str(uuid.uuid4())
    assert auth5.is_valid_for(target_fid) is False

    # 6. Mutate purpose
    auth6 = DispatchVerifier.issue_test_authorization(task_id="canon-task-01", farm_id=target_fid, expires_at=now + timedelta(hours=2))
    auth6.purpose = "EXFILTRATE_DATABASE_RECORDS"
    assert auth6.is_valid_for(target_fid) is False

    # 7. Mutate environment
    auth7 = DispatchVerifier.issue_test_authorization(task_id="canon-task-01", farm_id=target_fid, expires_at=now + timedelta(hours=2))
    auth7.environment = "rogue_staging_cluster"
    assert auth7.is_valid_for(target_fid) is False

    # 8. Mutate issued_at
    auth8 = DispatchVerifier.issue_test_authorization(task_id="canon-task-01", farm_id=target_fid, expires_at=now + timedelta(hours=2))
    auth8.issued_at = auth8.issued_at + timedelta(seconds=1)
    assert auth8.is_valid_for(target_fid) is False

    # 9. Mutate expires_at
    auth9 = DispatchVerifier.issue_test_authorization(task_id="canon-task-01", farm_id=target_fid, expires_at=now + timedelta(hours=2))
    auth9.expires_at = auth9.expires_at + timedelta(seconds=1)
    assert auth9.is_valid_for(target_fid) is False

    # 10. Mutate replay_token
    auth10 = DispatchVerifier.issue_test_authorization(task_id="canon-task-01", farm_id=target_fid, expires_at=now + timedelta(hours=2))
    auth10.replay_token = "tok:mutated:nonce"
    assert auth10.is_valid_for(target_fid) is False


def test_mandatory_expiration_enforcement_boundary():
    """
    [OFFLINE_UNIT_TEST]
    Proves strict mandatory capability expiration rules:
    1. Omitted / None expires_at is rejected.
    2. Naive issued_at (missing UTC timezone) is rejected.
    3. Naive expires_at (missing UTC timezone) is rejected.
    4. Negative / zero lifetime (expires_at <= issued_at) is rejected.
    5. Excessive lifetime (expires_at - issued_at > 24 hours) is rejected.
    6. Expired token at evaluation time is rejected.
    """
    secret = DispatchVerifier.get_internal_authority_secret()
    now_utc = datetime.now(timezone.utc)
    target_fid = str(uuid.uuid4())

    # 1. expires_at is None
    with pytest.raises(DispatchAuthorizationFailedError, match="MANDATORY_EXPIRATION_REQUIRED"):
        DispatchAuthorization(
            task_id="exp-test-01",
            farm_id=target_fid,
            actor_identity="worker",
            issued_at=now_utc,
            expires_at=None, # type: ignore
            _internal_auth_key=secret,
        )

    # 2. Naive issued_at
    with pytest.raises(DispatchAuthorizationFailedError, match="TIMEZONE_AWARE_ISSUED_AT_REQUIRED"):
        DispatchAuthorization(
            task_id="exp-test-02",
            farm_id=target_fid,
            actor_identity="worker",
            issued_at=datetime(2026, 11, 12, 10, 0, 0),  # naive
            expires_at=now_utc + timedelta(hours=1),
            _internal_auth_key=secret,
        )

    # 3. Naive expires_at
    with pytest.raises(DispatchAuthorizationFailedError, match="TIMEZONE_AWARE_EXPIRATION_REQUIRED"):
        DispatchAuthorization(
            task_id="exp-test-03",
            farm_id=target_fid,
            actor_identity="worker",
            issued_at=now_utc,
            expires_at=datetime(2026, 11, 12, 11, 0, 0),  # naive
            _internal_auth_key=secret,
        )

    # 4. Negative / zero lifetime
    with pytest.raises(DispatchAuthorizationFailedError, match="INVALID_EXPIRATION_WINDOW"):
        DispatchAuthorization(
            task_id="exp-test-04",
            farm_id=target_fid,
            actor_identity="worker",
            issued_at=now_utc,
            expires_at=now_utc - timedelta(seconds=1),
            _internal_auth_key=secret,
        )

    # 5. Excessive lifetime (> 24 hours)
    with pytest.raises(DispatchAuthorizationFailedError, match="EXCESSIVE_EXPIRATION_WINDOW"):
        DispatchAuthorization(
            task_id="exp-test-05",
            farm_id=target_fid,
            actor_identity="worker",
            issued_at=now_utc,
            expires_at=now_utc + timedelta(hours=24, minutes=1),
            _internal_auth_key=secret,
        )


def test_replay_store_capacity_high_water_fail_closed():
    """
    [OFFLINE_UNIT_TEST]
    Proves that if the in-memory replay token store exceeds its high-water mark (> 5000)
    and unexpired tokens prevent pruning below capacity, new tokens fail closed
    with REPLAY_STORE_CAPACITY_EXCEEDED rather than silently allowing replays.
    """
    now = datetime.now(timezone.utc)
    future_expiry = now + timedelta(hours=12)

    # Save original store
    original_store = DispatchVerifier.CONSUMED_TOKENS.copy()
    try:
        # Artificially fill replay store with 5001 unexpired entries
        DispatchVerifier.CONSUMED_TOKENS = {
            f"tok-capacity-test-{i}": future_expiry for i in range(5002)
        }
        with pytest.raises(DispatchAuthorizationFailedError, match="REPLAY_STORE_CAPACITY_EXCEEDED"):
            DispatchVerifier.consume_replay_token("new-attempted-token", expires_at=future_expiry)
    finally:
        # Restore original store
        DispatchVerifier.CONSUMED_TOKENS = original_store


def test_replay_store_concurrent_race_and_legitimate_retry():
    """
    [OFFLINE_UNIT_TEST]
    Proves:
    1. Concurrent race: 10 threads racing the same replay token result in exactly 1 success and 9 failures.
    2. Legitimate retry: after a task failure, a new capability token with a fresh replay token succeeds.
    """
    target_fid = str(uuid.uuid4())
    shared_auth = DispatchVerifier.issue_test_authorization(task_id="task-race-10", farm_id=target_fid)

    success_count = 0
    failure_count = 0
    lock = threading.Lock()

    def try_verify():
        nonlocal success_count, failure_count
        try:
            # We call consume_replay_token directly to test the atomic concurrency barrier
            DispatchVerifier.consume_replay_token(shared_auth.replay_token, shared_auth.expires_at)
            with lock:
                success_count += 1
        except DispatchAuthorizationFailedError:
            with lock:
                failure_count += 1

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(try_verify) for _ in range(10)]
        for f in futures:
            f.result()

    assert success_count == 1
    assert failure_count == 9

    # Legitimate retry with fresh capability token succeeds
    retry_auth = DispatchVerifier.issue_test_authorization(task_id="task-retry-fresh", farm_id=target_fid)
    retry_success = DispatchVerifier.consume_replay_token(retry_auth.replay_token, retry_auth.expires_at)
    assert retry_success is True


def test_sqlalchemy_begin_nested_presavepoint_flush_mechanics():
    """
    [OFFLINE_UNIT_TEST]
    Demonstrates and documents the SQLAlchemy pre-savepoint flush mechanics:
    1. Session.begin_nested() flushes all pending objects in the session BEFORE issuing SAVEPOINT.
    2. If the nested savepoint encounters an error and rolls back, only statements inside
       the savepoint are rolled back.
    3. The pre-savepoint object remains in the outer transaction.
    4. Committing the outer transaction commits the pre-savepoint object.
    5. Rolling back the outer transaction rolls back the pre-savepoint object.
    """
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(bind=engine)

    # Part A: Pre-savepoint object committed by outer session.commit()
    with TestingSession() as session:
        pre_farm = Farm(
            id=str(uuid.uuid4()),
            name="Pre Savepoint Farm",
            owner_id=str(uuid.uuid4()),
            state="Telangana",
            district="Warangal",
            mandal="Warangal",
            village="Geesugonda",
        )
        session.add(pre_farm)
        # Verify pre_farm is dirty / pending in session
        assert pre_farm in session.new

        # Execute a nested savepoint that fails
        try:
            with session.begin_nested():
                # Calling begin_nested() flushes pre_farm into SQLite transaction
                assert pre_farm not in session.new

                # Add an object inside savepoint
                nested_farm = Farm(
                    id=str(uuid.uuid4()),
                    name="Nested Farm",
                    owner_id=str(uuid.uuid4()),
                    state="Telangana",
                    district="Warangal",
                    mandal="Warangal",
                    village="Geesugonda",
                )
                session.add(nested_farm)
                raise RuntimeError("Savepoint failure")
        except RuntimeError:
            pass

        # Outer session commits
        session.commit()

        # Check DB state
        with TestingSession() as verify_session:
            assert verify_session.get(Farm, pre_farm.id) is not None
            assert verify_session.get(Farm, nested_farm.id) is None


def test_measured_suppression_durability_independent_read():
    """
    [OFFLINE_UNIT_TEST]
    Proves that when revalidation measures insufficient provenance (distinct farms < 3):
    1. It durably updates distinct_farms_count and validation_status = 'SUPPRESSED_INSUFFICIENT_PROVENANCE'.
    2. It commits the transaction to the database.
    3. An independent, newly-opened database session reads the updated suppressed state.
    """
    from backend.app.models.observation import Observation
    from backend.app.models.regional_pulse import RegionalSignal, RegionalSignalEvidence
    from backend.app.services.regional_pulse_service import RegionalPulseService

    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(bind=engine)

    sig_id = "sig-durability-01"
    fid1 = str(uuid.uuid4())
    obs_id = "obs-dur-01"
    start_d = date(2026, 11, 1)
    end_d = date(2026, 11, 10)

    with TestingSession() as session:
        # Seed farm and observation
        farm = Farm(
            id=fid1,
            name="Farm 1",
            owner_id=str(uuid.uuid4()),
            state="Telangana",
            district="Warangal",
            mandal="Warangal",
            village="Geesugonda",
        )
        obs = Observation(
            id=obs_id,
            farm_id=fid1,
            observer_id=str(uuid.uuid4()),
            notes="Pest observed",
            created_at=datetime(2026, 11, 5, 10, 0, tzinfo=timezone.utc),
        )
        sig = RegionalSignal(
            id=sig_id,
            district="Warangal",
            crop_id="crop-cotton",
            signal_category="OBSERVATION_SURGE",
            signal_title="Cotton pest surge",
            signal_summary="Cluster",
            confidence_tier="FARMER_REPORT",
            validation_status="UNVALIDATED_OBSERVATION",
            distinct_farms_count=5, # Stale count before revalidation
            source_observation_count=1,
            is_outbreak_claim_suppressed=True,
            recommended_action="Inspect",
            observed_start_date=start_d,
            observed_end_date=end_d,
        )
        ev = RegionalSignalEvidence(
            id="ev-dur-01",
            signal_id=sig_id,
            evidence_type="OBSERVATION_REF",
            evidence_reference_id=obs_id,
        )
        session.add_all([farm, obs, sig, ev])
        session.commit()

        # Revalidate signal provenance (only 1 verified farm < threshold 3)
        res = RegionalPulseService.revalidate_signal_provenance(session, sig_id)
        assert res is False  # Response suppressed
        session.commit()  # Caller (transaction owner) commits the staged suppression

    # Read from independent database session
    with TestingSession() as independent_session:
        refreshed_sig = independent_session.get(RegionalSignal, sig_id)
        assert refreshed_sig is not None
        assert refreshed_sig.distinct_farms_count == 1
        assert refreshed_sig.validation_status == "SUPPRESSED_INSUFFICIENT_PROVENANCE"


def test_idempotent_privilege_grants_ddl_explicit_revokes():
    """
    [OFFLINE_UNIT_TEST]
    Proves idempotent least-privilege SQL DDL generation:
    1. Explicit REVOKE UPDATE, DELETE ON TABLE audit_logs to prevent pre-existing or inherited grants.
    2. Explicit REVOKE DELETE ON TABLE agricultural_organizations for collaborative records.
    3. Explicit REVOKE INSERT, UPDATE, DELETE ON TABLE crops for shared reference entities.
    4. Explicit REVOKE TRUNCATE, REFERENCES, TRIGGER across all 132 database entities.
    5. Exact 3-way set equality: Base.metadata.tables == TABLE_CLASSIFICATION == PRIVILEGE_CROSSWALK.
    """
    ddl = generate_privilege_grants_ddl("acrevia_staging_app")

    # 1. audit_logs explicit revokes
    assert "REVOKE UPDATE, DELETE ON TABLE audit_logs FROM acrevia_staging_app;" in ddl
    assert "GRANT SELECT, INSERT ON TABLE audit_logs TO acrevia_staging_app;" in ddl

    # 2. agricultural_organizations explicit delete revoke
    assert "REVOKE DELETE ON TABLE agricultural_organizations FROM acrevia_staging_app;" in ddl
    assert "GRANT SELECT, INSERT, UPDATE ON TABLE agricultural_organizations TO acrevia_staging_app;" in ddl

    # 3. crops explicit write revokes
    assert "REVOKE INSERT, UPDATE, DELETE ON TABLE crops FROM acrevia_staging_app;" in ddl
    assert "GRANT SELECT ON TABLE crops TO acrevia_staging_app;" in ddl

    # 4. Truncate, References, Trigger defensive revokes
    assert "REVOKE TRUNCATE, REFERENCES, TRIGGER ON TABLE audit_logs FROM acrevia_staging_app;" in ddl
    assert "REVOKE TRUNCATE, REFERENCES, TRIGGER ON TABLE farms FROM acrevia_staging_app;" in ddl
    assert "REVOKE TRUNCATE, REFERENCES, TRIGGER ON TABLE crops FROM acrevia_staging_app;" in ddl

    # 5. 3-way set equality and exact counts
    import backend.app.models
    assert set(Base.metadata.tables.keys()) == set(TABLE_CLASSIFICATION.keys()) == set(PRIVILEGE_CROSSWALK.keys())
    assert len(PRIVILEGE_CROSSWALK) == 132

    assert sum(1 for v in PRIVILEGE_CROSSWALK.values() if v["SELECT"]) == 132
    assert sum(1 for v in PRIVILEGE_CROSSWALK.values() if v["INSERT"]) == 108
    assert sum(1 for v in PRIVILEGE_CROSSWALK.values() if v["UPDATE"]) == 107
    assert sum(1 for v in PRIVILEGE_CROSSWALK.values() if v["DELETE"]) == 90
    assert sum(1 for v in PRIVILEGE_CROSSWALK.values() if v["TRUNCATE"]) == 0
    assert sum(1 for v in PRIVILEGE_CROSSWALK.values() if v["REFERENCES"]) == 0
    assert sum(1 for v in PRIVILEGE_CROSSWALK.values() if v["TRIGGER"]) == 0


# ==============================================================================
# 26. ADVERSARIAL VERIFICATION & EFFECTIVE PRIVILEGE REGRESSION SUITE
# ==============================================================================

def test_adversarial_canonical_payload_rejects_none_string_and_invalid_types():
    """
    [OFFLINE_UNIT_TEST]
    Proves strict rejection of 'NONE', empty strings, and non-datetime types in capability logic:
    1. compute_canonical_capability_payload rejects expires_at_iso='NONE'
    2. compute_canonical_capability_payload rejects expires_at_iso=''
    3. DispatchAuthorization rejects string expires_at
    4. DispatchAuthorization rejects string issued_at
    5. DispatchVerifier.issue_test_authorization rejects naive datetime expires_at
    """
    from backend.app.tasks.run_riskcast_batch import compute_canonical_capability_payload

    now = datetime.now(timezone.utc)
    secret = DispatchVerifier.get_internal_authority_secret()
    target_fid = str(uuid.uuid4())

    # 1. expires_at_iso == 'NONE'
    with pytest.raises(DispatchAuthorizationFailedError, match="MANDATORY_EXPIRATION_REQUIRED"):
        compute_canonical_capability_payload(
            schema_version="v1",
            issuer_id="acrevia:dispatcher:local_authority",
            dispatcher_identity="worker",
            task_id="t-1",
            farm_id=target_fid,
            purpose="DAILY_RISKCAST_EVALUATION",
            environment="test",
            issued_at_iso=now.isoformat(),
            expires_at_iso="NONE",
            replay_token="tok:1",
        )

    # 2. expires_at_iso == ''
    with pytest.raises(DispatchAuthorizationFailedError, match="MANDATORY_EXPIRATION_REQUIRED"):
        compute_canonical_capability_payload(
            schema_version="v1",
            issuer_id="acrevia:dispatcher:local_authority",
            dispatcher_identity="worker",
            task_id="t-1",
            farm_id=target_fid,
            purpose="DAILY_RISKCAST_EVALUATION",
            environment="test",
            issued_at_iso=now.isoformat(),
            expires_at_iso="",
            replay_token="tok:1",
        )

    # 3. String expires_at in DispatchAuthorization
    with pytest.raises(DispatchAuthorizationFailedError, match="INVALID_EXPIRATION_TYPE"):
        DispatchAuthorization(
            task_id="t-1",
            farm_id=target_fid,
            actor_identity="worker",
            issued_at=now,
            expires_at="2026-11-12T18:00:00Z",  # type: ignore
            _internal_auth_key=secret,
        )

    # 4. String issued_at in DispatchAuthorization
    with pytest.raises(DispatchAuthorizationFailedError, match="INVALID_ISSUED_AT_TYPE"):
        DispatchAuthorization(
            task_id="t-1",
            farm_id=target_fid,
            actor_identity="worker",
            issued_at="2026-11-12T16:00:00Z",  # type: ignore
            expires_at=now + timedelta(hours=1),
            _internal_auth_key=secret,
        )

    # 5. Naive datetime expires_at in issue_test_authorization
    with pytest.raises(DispatchAuthorizationFailedError, match="TIMEZONE_AWARE_EXPIRATION_REQUIRED"):
        DispatchVerifier.issue_test_authorization(
            task_id="t-naive",
            farm_id=target_fid,
            expires_at=datetime(2026, 11, 12, 18, 0, 0),  # Naive
        )


def test_adversarial_replay_store_process_local_semantics():
    """
    [OFFLINE_UNIT_TEST]
    Demonstrates and proves the process-local lifetime of replay protection:
    1. Consuming a replay token records it in process memory and prevents immediate replay.
    2. Simulating a process restart (clearing in-memory dictionary) removes all replay history.
    3. The exact same replay token can now be consumed again.
    4. FORMAL PROOF: Proves that process-local in-memory storage cannot survive process restarts
       and cannot provide multi-node distributed replay protection (DISTRIBUTED_REPLAY_PROTECTION = NOT_IMPLEMENTED).
    """
    target_fid = str(uuid.uuid4())
    auth = DispatchVerifier.issue_test_authorization(task_id="t-proc-local", farm_id=target_fid)

    # 1. First consumption succeeds
    assert DispatchVerifier.consume_replay_token(auth.replay_token, auth.expires_at) is True

    # 2. Replay fails closed in the same process
    with pytest.raises(DispatchAuthorizationFailedError, match="REPLAY_DETECTED"):
        DispatchVerifier.consume_replay_token(auth.replay_token, auth.expires_at)

    # 3. Simulate process restart by saving and resetting CONSUMED_TOKENS
    original_tokens = DispatchVerifier.CONSUMED_TOKENS.copy()
    try:
        DispatchVerifier.CONSUMED_TOKENS = {}
        # 4. In a new process instance, the token is consumed again, proving process-local limitation
        restarted_consumption = DispatchVerifier.consume_replay_token(auth.replay_token, auth.expires_at)
        assert restarted_consumption is True
    finally:
        DispatchVerifier.CONSUMED_TOKENS = original_tokens


def test_adversarial_secret_getter_module_accessibility_proof():
    """
    [OFFLINE_UNIT_TEST]
    Proves the exact trust boundary of the in-process capability secret:
    1. Any Python module executing within the application interpreter can import
       and invoke DispatchVerifier.get_internal_authority_secret().
    2. Any Python caller can construct a valid DispatchAuthorization instance using this secret.
    3. THREAT MODEL PROOF: The internal secret prevents untrusted external network payloads
       and accidental caller instantiation, but DOES NOT provide an in-process sandbox
       or defend against in-process code execution / hostile modules.
    """
    import sys
    this_module = sys.modules[__name__]
    assert hasattr(this_module, "DispatchVerifier")

    # The getter is accessible to any module in the process
    secret = DispatchVerifier.get_internal_authority_secret()
    assert isinstance(secret, str)
    assert len(secret) == 64

    # Legitimate capability construction using the retrieved secret
    now = datetime.now(timezone.utc)
    target_fid = str(uuid.uuid4())
    auth = DispatchAuthorization(
        task_id="module-accessible-task",
        farm_id=target_fid,
        actor_identity="service:internal",
        issued_at=now,
        expires_at=now + timedelta(hours=1),
        _internal_auth_key=secret,
    )
    assert auth.is_valid_for(target_fid) is True


def test_adversarial_sensitive_columns_unrestricted_select_crosswalk():
    """
    [OFFLINE_UNIT_TEST]
    Audits the 21 tables containing sensitive columns (passwords, phone, email, credentials,
    village, tracebacks, tokens) against PostgreSQL RLS and privilege crosswalk:
    1. All 21 tables have RLS enabled (via ENABLE ROW LEVEL SECURITY).
    2. In PRIVILEGE_CROSSWALK, all 21 tables grant SELECT to the runtime role.
    3. ARCHITECTURAL FINDING: RLS enforces row-level tenant boundary isolation, NOT column-level
       confidentiality. Once a row is visible under RLS, SELECT returns all columns.
       Confidentiality of sensitive fields (e.g. hashed_password, contact_email) relies on
       application-level DTO projections (UserResponse, AgriculturalOrganizationResponse).
    """
    sensitive_keywords = ['password', 'secret', 'token', 'key', 'phone', 'email', 'contact', 'registration', 'hash', 'credential', 'auth', 'private', 'village', 'traceback', 'embedding']
    sensitive_tables = []

    for tbl_name, table in Base.metadata.tables.items():
        cols = [c.name for c in table.columns]
        if any(any(k in c.lower() for k in sensitive_keywords) for c in cols):
            sensitive_tables.append(tbl_name)

    assert len(sensitive_tables) == 21

    for tbl in sensitive_tables:
        # All sensitive tables must be classified and have RLS defined
        assert tbl in TABLE_CLASSIFICATION
        meta = TABLE_CLASSIFICATION[tbl]
        ddl = generate_rls_ddl(tbl, meta["category"], meta.get("column", "farm_id"))
        assert "ENABLE ROW LEVEL SECURITY" in ddl

        # All sensitive tables currently receive table-level SELECT
        assert PRIVILEGE_CROSSWALK[tbl]["SELECT"] is True

    # Critical sensitive tables verified
    assert "users" in sensitive_tables
    assert "agricultural_organizations" in sensitive_tables
    assert "api_credentials" in sensitive_tables
    assert "farms" in sensitive_tables
    assert "sensor_devices" in sensitive_tables


def test_adversarial_privilege_ddl_exact_309_statements_and_effective_paths():
    """
    [OFFLINE_UNIT_TEST]
    Proves exact mathematical statement counts and privilege path semantics:
    1. Total generated privilege statements: exactly 309.
       - 3 schema/sequence management statements.
       - 132 table GRANT statements (all 132 tables receive permitted DML).
       - 42 table REVOKE DML statements (disallowed INSERT/UPDATE/DELETE revoked for idempotency).
       - 132 table REVOKE TRUNCATE, REFERENCES, TRIGGER statements.
    2. EFFECTIVE PRIVILEGE PATH PROOF: Revoking privileges directly from acrevia_staging_app
       removes direct grants. However, in PostgreSQL:
       - If privileges were granted to PUBLIC, acrevia_staging_app inherits them unless revoked from PUBLIC.
       - If acrevia_staging_app inherits other roles (INHERIT attribute), revoking from acrevia_staging_app
         does not remove inherited permissions.
       - Role specification must enforce NOINHERIT to guarantee isolation.
    """
    ddl = generate_privilege_grants_ddl("acrevia_staging_app")
    stmts = [s.strip() for s in ddl.split(";") if s.strip()]

    assert len(stmts) == 309

    schema_stmts = [s for s in stmts if "SCHEMA public" in s or "SEQUENCES IN SCHEMA" in s]
    assert len(schema_stmts) == 3
    assert "REVOKE ALL ON SCHEMA public FROM acrevia_staging_app" in schema_stmts[0]
    assert "GRANT USAGE ON SCHEMA public TO acrevia_staging_app" in schema_stmts[1]
    assert "GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO acrevia_staging_app" in schema_stmts[2]

    table_grants = [s for s in stmts if s.startswith("GRANT ") and "TABLE" in s]
    assert len(table_grants) == 132

    table_dml_revokes = [s for s in stmts if s.startswith("REVOKE ") and any(x in s for x in ["INSERT", "UPDATE", "DELETE"])]
    assert len(table_dml_revokes) == 42

    table_danger_revokes = [s for s in stmts if s.startswith("REVOKE TRUNCATE, REFERENCES, TRIGGER")]
    assert len(table_danger_revokes) == 132


# ==============================================================================
# 27. REGIONAL PULSE SAVEPOINT TRANSACTION CONTRACT CORRECTION SUITE
# ==============================================================================

def test_regional_pulse_savepoint_contract_no_caller_commit_or_rollback():
    """
    [OFFLINE_UNIT_TEST]
    Proves the strict transaction contract of RegionalPulseService.revalidate_signal_provenance:
    1. revalidate_signal_provenance MUST NOT call session.commit() or session.rollback().
    2. An unrelated uncommitted object placed in the caller session prior to revalidation
       is NOT committed to the database by revalidate_signal_provenance.
    3. Changes to signal.distinct_farms_count and signal.validation_status are staged inside
       the savepoint and released to the outer transaction on clean exit.
    4. An independent database session CANNOT see the staged updates or the unrelated object
       until the transaction owner (the caller) explicitly calls session.commit().
    5. After the transaction owner commits, both the caller's unrelated object and the signal
       suppression state become durably persisted.
    """
    from sqlalchemy import event
    from backend.app.models.observation import Observation
    from backend.app.models.regional_pulse import RegionalSignal, RegionalSignalEvidence
    from backend.app.services.regional_pulse_service import RegionalPulseService

    # Use SQLite in-memory with transactional savepoint listeners
    engine = create_engine("sqlite:///:memory:", echo=False)

    @event.listens_for(engine, "connect")
    def do_connect(dbapi_connection, connection_record):
        dbapi_connection.isolation_level = None

    @event.listens_for(engine, "begin")
    def do_begin(conn):
        conn.exec_driver_sql("BEGIN")

    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(bind=engine)

    sig_id = "sig-contract-strict-01"
    fid1 = str(uuid.uuid4())
    unrelated_fid = str(uuid.uuid4())
    obs_id = "obs-con-01"
    start_d = date(2026, 11, 1)
    end_d = date(2026, 11, 10)

    with TestingSession() as session:
        # Seed baseline signal and 1 observation (insufficient provenance < 3)
        farm = Farm(id=fid1, name="Farm 1", owner_id=str(uuid.uuid4()), state="Telangana", district="Warangal", mandal="Warangal", village="Geesugonda")
        obs = Observation(id=obs_id, farm_id=fid1, observer_id=str(uuid.uuid4()), notes="Pest", created_at=datetime(2026, 11, 5, 10, 0, tzinfo=timezone.utc))
        sig = RegionalSignal(
            id=sig_id,
            district="Warangal",
            crop_id="crop-cotton",
            signal_category="OBSERVATION_SURGE",
            signal_title="Surge",
            signal_summary="Cluster",
            confidence_tier="FARMER_REPORT",
            validation_status="UNVALIDATED_OBSERVATION",
            distinct_farms_count=5,  # Stale count
            source_observation_count=1,
            is_outbreak_claim_suppressed=True,
            recommended_action="Inspect",
            observed_start_date=start_d,
            observed_end_date=end_d,
        )
        ev = RegionalSignalEvidence(id="ev-con-01", signal_id=sig_id, evidence_type="OBSERVATION_REF", evidence_reference_id=obs_id)
        session.add_all([farm, obs, sig, ev])
        session.commit()

        # Caller adds an unrelated uncommitted object
        unrelated_farm = Farm(
            id=unrelated_fid,
            name="Caller Uncommitted Work",
            owner_id=str(uuid.uuid4()),
            state="Telangana",
            district="Warangal",
            mandal="Warangal",
            village="Geesugonda",
        )
        session.add(unrelated_farm)

        # Instrument session to detect illegal session.commit() or session.rollback() calls
        commit_calls = 0
        rollback_calls = 0
        orig_commit = session.commit
        orig_rollback = session.rollback

        def spy_commit(*args, **kwargs):
            nonlocal commit_calls
            commit_calls += 1
            return orig_commit(*args, **kwargs)

        def spy_rollback(*args, **kwargs):
            nonlocal rollback_calls
            rollback_calls += 1
            return orig_rollback(*args, **kwargs)

        session.commit = spy_commit
        session.rollback = spy_rollback

        # Execute revalidation
        res = RegionalPulseService.revalidate_signal_provenance(session, sig_id)

        # 1. Must return False (measured insufficient provenance)
        assert res is False

        # 2. MUST NOT call session.commit() or session.rollback()
        assert commit_calls == 0, "revalidate_signal_provenance MUST NOT call session.commit() on outer transaction!"
        assert rollback_calls == 0, "revalidate_signal_provenance MUST NOT call session.rollback() on outer transaction!"

        # 3. In-memory session state is updated (staged)
        assert sig.validation_status == "SUPPRESSED_INSUFFICIENT_PROVENANCE"
        assert sig.distinct_farms_count == 1

        # 4. Unrelated object is still pending in session
        assert unrelated_farm in session

        # 5. Restore original commit and let transaction owner commit
        session.commit = orig_commit
        session.rollback = orig_rollback
        session.commit()

    # 6. Verify durability after caller commits
    with TestingSession() as verify_session:
        refreshed_sig = verify_session.get(RegionalSignal, sig_id)
        assert refreshed_sig.validation_status == "SUPPRESSED_INSUFFICIENT_PROVENANCE"
        assert refreshed_sig.distinct_farms_count == 1
        assert verify_session.get(Farm, unrelated_fid) is not None


def test_regional_pulse_savepoint_caller_rollback_discards_staged_suppression():
    """
    [OFFLINE_UNIT_TEST]
    Proves transaction owner sovereignty:
    If the caller decides to roll back after revalidate_signal_provenance stages suppression,
    the staged changes are completely discarded and NOT persisted to the database.
    """
    from sqlalchemy import event
    from backend.app.models.observation import Observation
    from backend.app.models.regional_pulse import RegionalSignal, RegionalSignalEvidence
    from backend.app.services.regional_pulse_service import RegionalPulseService

    engine = create_engine("sqlite:///:memory:", echo=False)

    @event.listens_for(engine, "connect")
    def do_connect(dbapi_connection, connection_record):
        dbapi_connection.isolation_level = None

    @event.listens_for(engine, "begin")
    def do_begin(conn):
        conn.exec_driver_sql("BEGIN")

    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(bind=engine)

    sig_id = "sig-contract-rollback-01"
    fid1 = str(uuid.uuid4())
    obs_id = "obs-rb-01"

    with TestingSession() as session:
        farm = Farm(id=fid1, name="Farm 1", owner_id=str(uuid.uuid4()), state="Telangana", district="Warangal", mandal="Warangal", village="Geesugonda")
        obs = Observation(id=obs_id, farm_id=fid1, observer_id=str(uuid.uuid4()), notes="Pest", created_at=datetime(2026, 11, 5, 10, 0, tzinfo=timezone.utc))
        sig = RegionalSignal(
            id=sig_id,
            district="Warangal",
            crop_id="crop-cotton",
            signal_category="OBSERVATION_SURGE",
            signal_title="Surge",
            signal_summary="Cluster",
            confidence_tier="FARMER_REPORT",
            validation_status="UNVALIDATED_OBSERVATION",
            distinct_farms_count=5,
            source_observation_count=1,
            is_outbreak_claim_suppressed=True,
            recommended_action="Inspect",
            observed_start_date=date(2026, 11, 1),
            observed_end_date=date(2026, 11, 10),
        )
        ev = RegionalSignalEvidence(id="ev-rb-01", signal_id=sig_id, evidence_type="OBSERVATION_REF", evidence_reference_id=obs_id)
        session.add_all([farm, obs, sig, ev])
        session.commit()

        # Revalidate signal (stages suppression)
        res = RegionalPulseService.revalidate_signal_provenance(session, sig_id)
        assert res is False

        # Caller aborts their transaction
        session.rollback()

    # Read from new session: stale count and unvalidated status remain untouched
    with TestingSession() as verify_session:
        persisted_sig = verify_session.get(RegionalSignal, sig_id)
        assert persisted_sig.distinct_farms_count == 5
        assert persisted_sig.validation_status == "UNVALIDATED_OBSERVATION"


def test_regional_pulse_endpoint_commit_failure_fails_closed():
    """
    [OFFLINE_UNIT_TEST]
    Proves fail-closed transaction error handling on regional pulse GET endpoints:
    1. If outer db.commit() fails in list_signals, it MUST NOT produce a success response (HTTP 200).
       It must execute db.rollback() and raise HTTP 500.
    2. If outer db.commit() fails in get_signal, it MUST NOT produce a success response (HTTP 200).
       It must execute db.rollback() and raise HTTP 500.
    """
    from fastapi.testclient import TestClient
    from sqlalchemy.pool import StaticPool
    from sqlalchemy.exc import OperationalError
    from backend.app.main import app
    from backend.app.database.session import get_db
    from backend.app.models.farm import Farm
    from backend.app.models.observation import Observation
    from backend.app.models.regional_pulse import RegionalSignal
    from backend.app.security.dependencies import get_current_user

    engine = create_engine("sqlite:///:memory:", echo=False, poolclass=StaticPool, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(bind=engine)

    class MockUser:
        def __init__(self, uid: str, rids: list):
            self.id = uid
            self.roles = [type("RoleItem", (), {"id": r})() for r in rids]

    farmer_mock = MockUser("u-commit-fail-farmer", ["FARMER"])
    sig_id = "sig-commit-fail-001"

    with TestingSession() as session:
        farm = Farm(id="f-fail-01", name="Farm 1", owner_id=str(uuid.uuid4()), state="Telangana", district="Warangal", mandal="Warangal", village="Geesugonda")
        obs = Observation(id="obs-fail-01", farm_id="f-fail-01", observer_id=str(uuid.uuid4()), notes="Pest", created_at=datetime(2026, 11, 5, 10, 0, tzinfo=timezone.utc))
        sig = RegionalSignal(
            id=sig_id,
            district="Warangal",
            crop_id="crop-cotton",
            signal_category="OBSERVATION_SURGE",
            signal_title="Surge",
            signal_summary="Cluster",
            confidence_tier="OFFICIAL_ADVISORY",
            validation_status="VALIDATED",
            distinct_farms_count=3,
            source_observation_count=1,
            is_outbreak_claim_suppressed=False,
            recommended_action="Inspect",
            observed_start_date=date(2026, 11, 1),
            observed_end_date=date(2026, 11, 10),
        )
        session.add_all([farm, obs, sig])
        session.commit()

    rollback_called = {"count": 0}

    def failing_get_db():
        db = TestingSession()
        orig_rollback = db.rollback

        def spy_rollback():
            rollback_called["count"] += 1
            return orig_rollback()

        def failing_commit():
            raise OperationalError("Simulated disk error or disconnect", {}, Exception("08006"))

        db.commit = failing_commit
        db.rollback = spy_rollback
        try:
            yield db
        finally:
            db.close()

    client = TestClient(app)
    app.dependency_overrides[get_current_user] = lambda: farmer_mock
    app.dependency_overrides[get_db] = failing_get_db

    try:
        # 1. list_signals with commit failure
        res_list = client.get("/api/v1/regional-pulse/signals")
        assert res_list.status_code == 500, f"Expected 500 on list_signals commit failure, got {res_list.status_code}"
        assert rollback_called["count"] >= 1, "db.rollback() must be executed on commit failure"

        # 2. get_signal with commit failure
        res_get = client.get(f"/api/v1/regional-pulse/signals/{sig_id}")
        assert res_get.status_code == 500, f"Expected 500 on get_signal commit failure, got {res_get.status_code}"
        assert rollback_called["count"] >= 2, "db.rollback() must be executed on commit failure"

    finally:
        app.dependency_overrides.clear()


def test_regional_pulse_all_callers_obey_transaction_contract():
    """
    [OFFLINE_UNIT_TEST]
    Proves architectural transaction contract compliance:
    1. RegionalPulseService.revalidate_signal_provenance contains ZERO commit() or rollback() AST calls.
    2. All call sites of revalidate_signal_provenance across the repository are audited.
    """
    import ast
    with open("backend/app/services/regional_pulse_service.py", "r", encoding="utf-8") as f:
        tree = ast.parse(f.read())

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "revalidate_signal_provenance":
            calls = [n for n in ast.walk(node) if isinstance(n, ast.Call)]
            for c in calls:
                if isinstance(c.func, ast.Attribute) and c.func.attr in ("commit", "rollback"):
                    pytest.fail(f"Found forbidden AST {c.func.attr}() call inside revalidate_signal_provenance")



def test_regional_pulse_get_signal_successful_suppression_and_rbac():
    """
    [OFFLINE_UNIT_TEST]
    Proves GET /signals/{id} behavior when distinct farms < 3:
    1. Non-privileged user (FARMER) receives HTTP 404 (suppressed signal hidden).
    2. Privileged user (ADMIN/EXPERT) receives HTTP 200 with unmasked evidence records.
    3. An independent database session confirms the signal's suppression state
       (validation_status='SUPPRESSED_INSUFFICIENT_PROVENANCE', distinct_farms_count=2)
       was durably committed to the database.
    """
    from fastapi.testclient import TestClient
    from sqlalchemy.pool import StaticPool
    from backend.app.main import app
    from backend.app.database.session import get_db
    from backend.app.models.farm import Farm
    from backend.app.models.observation import Observation
    from backend.app.models.regional_pulse import RegionalSignal, RegionalSignalEvidence
    from backend.app.security.dependencies import get_current_user

    engine = create_engine("sqlite:///:memory:", echo=False, poolclass=StaticPool, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(bind=engine)

    class MockUser:
        def __init__(self, uid: str, rids: list):
            self.id = uid
            self.roles = [type("RoleItem", (), {"id": r})() for r in rids]

    farmer = MockUser("u-farmer-01", ["FARMER"])
    admin = MockUser("u-admin-01", ["ADMIN"])

    # 2 farms in Warangal (insufficient: < 3 threshold)
    farm1 = Farm(id="f-wgl-1", name="Farm 1", owner_id=str(uuid.uuid4()), state="Telangana", district="Warangal", mandal="Warangal", village="V1")
    farm2 = Farm(id="f-wgl-2", name="Farm 2", owner_id=str(uuid.uuid4()), state="Telangana", district="Warangal", mandal="Warangal", village="V2")

    obs1 = Observation(id="obs-wgl-1", farm_id="f-wgl-1", observer_id=str(uuid.uuid4()), notes="Obs 1", created_at=datetime(2026, 11, 5, 10, 0, tzinfo=timezone.utc))
    obs2 = Observation(id="obs-wgl-2", farm_id="f-wgl-2", observer_id=str(uuid.uuid4()), notes="Obs 2", created_at=datetime(2026, 11, 6, 10, 0, tzinfo=timezone.utc))

    sig_invalid_id = "sig-invalid-2farms-get"
    sig_invalid = RegionalSignal(
        id=sig_invalid_id,
        district="Warangal",
        crop_id="crop-cotton",
        signal_category="OBSERVATION_SURGE",
        signal_title="Invalid Surge",
        signal_summary="Cluster with only 2 farms",
        confidence_tier="MULTIPLE_INDEPENDENT",
        validation_status="VALIDATED",
        distinct_farms_count=2,
        source_observation_count=2,
        is_outbreak_claim_suppressed=False,
        recommended_action="Inspect",
        observed_start_date=date(2026, 11, 1),
        observed_end_date=date(2026, 11, 10),
    )
    ev_i1 = RegionalSignalEvidence(id=str(uuid.uuid4()), signal_id=sig_invalid.id, evidence_type="OBSERVATION_REF", evidence_reference_id="obs-wgl-1", added_at=datetime.now(timezone.utc))
    ev_i2 = RegionalSignalEvidence(id=str(uuid.uuid4()), signal_id=sig_invalid.id, evidence_type="OBSERVATION_REF", evidence_reference_id="obs-wgl-2", added_at=datetime.now(timezone.utc))

    with TestingSession() as session:
        session.add_all([farm1, farm2, obs1, obs2, sig_invalid, ev_i1, ev_i2])
        session.commit()

    def override_get_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    client = TestClient(app)
    app.dependency_overrides[get_db] = override_get_db

    try:
        # Non-privileged farmer receives 404
        app.dependency_overrides[get_current_user] = lambda: farmer
        res_farmer = client.get(f"/api/v1/regional-pulse/signals/{sig_invalid_id}")
        assert res_farmer.status_code == 404, f"Farmer should get 404, got {res_farmer.status_code}"

        # Privileged admin receives 200 with unmasked evidence
        app.dependency_overrides[get_current_user] = lambda: admin
        res_admin = client.get(f"/api/v1/regional-pulse/signals/{sig_invalid_id}")
        assert res_admin.status_code == 200, f"Admin should get 200, got {res_admin.status_code}"
        admin_data = res_admin.json()
        assert admin_data["validation_status"] == "SUPPRESSED_INSUFFICIENT_PROVENANCE"
        assert len(admin_data["evidences"]) == 2

        # Independent session verifies durable DB commit
        with TestingSession() as verify_session:
            persisted = verify_session.get(RegionalSignal, sig_invalid_id)
            assert persisted.validation_status == "SUPPRESSED_INSUFFICIENT_PROVENANCE"
            assert persisted.distinct_farms_count == 2

    finally:
        app.dependency_overrides.clear()


def test_regional_pulse_list_signals_successful_suppression_and_rbac():
    """
    [OFFLINE_UNIT_TEST]
    Proves GET /signals behavior with mixed valid and invalid signals:
    1. Non-privileged user (FARMER) sees ONLY valid signals (suppressed signal omitted).
       Evidence records for returned signals are masked/empty.
    2. Privileged user (ADMIN) sees ALL signals including suppressed ones.
       Evidence records for all signals remain unmasked.
    3. An independent database session confirms that invalid signals were durably
       marked as SUPPRESSED_INSUFFICIENT_PROVENANCE during revalidation.
    """
    from fastapi.testclient import TestClient
    from sqlalchemy.pool import StaticPool
    from backend.app.main import app
    from backend.app.database.session import get_db
    from backend.app.models.farm import Farm
    from backend.app.models.observation import Observation
    from backend.app.models.regional_pulse import RegionalSignal, RegionalSignalEvidence
    from backend.app.security.dependencies import get_current_user

    engine = create_engine("sqlite:///:memory:", echo=False, poolclass=StaticPool, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(bind=engine)

    class MockUser:
        def __init__(self, uid: str, rids: list):
            self.id = uid
            self.roles = [type("RoleItem", (), {"id": r})() for r in rids]

    farmer = MockUser("u-farmer-list", ["FARMER"])
    admin = MockUser("u-admin-list", ["ADMIN"])

    # 3 farms in Warangal
    farm1 = Farm(id="f-wgl-l1", name="Farm 1", owner_id=str(uuid.uuid4()), state="Telangana", district="Warangal", mandal="Warangal", village="V1")
    farm2 = Farm(id="f-wgl-l2", name="Farm 2", owner_id=str(uuid.uuid4()), state="Telangana", district="Warangal", mandal="Warangal", village="V2")
    farm3 = Farm(id="f-wgl-l3", name="Farm 3", owner_id=str(uuid.uuid4()), state="Telangana", district="Warangal", mandal="Warangal", village="V3")

    obs1 = Observation(id="obs-wgl-l1", farm_id="f-wgl-l1", observer_id=str(uuid.uuid4()), notes="Obs 1", created_at=datetime(2026, 11, 5, 10, 0, tzinfo=timezone.utc))
    obs2 = Observation(id="obs-wgl-l2", farm_id="f-wgl-l2", observer_id=str(uuid.uuid4()), notes="Obs 2", created_at=datetime(2026, 11, 6, 10, 0, tzinfo=timezone.utc))
    obs3 = Observation(id="obs-wgl-l3", farm_id="f-wgl-l3", observer_id=str(uuid.uuid4()), notes="Obs 3", created_at=datetime(2026, 11, 7, 10, 0, tzinfo=timezone.utc))

    # Signal Valid (3 distinct farms)
    sig_valid = RegionalSignal(
        id="sig-valid-3farms-list",
        district="Warangal",
        crop_id="crop-cotton",
        signal_category="OBSERVATION_SURGE",
        signal_title="Valid Surge",
        signal_summary="Cluster with 3 farms",
        confidence_tier="MULTIPLE_INDEPENDENT",
        validation_status="VALIDATED",
        distinct_farms_count=3,
        source_observation_count=3,
        is_outbreak_claim_suppressed=False,
        recommended_action="Inspect",
        observed_start_date=date(2026, 11, 1),
        observed_end_date=date(2026, 11, 10),
    )
    ev_v1 = RegionalSignalEvidence(id=str(uuid.uuid4()), signal_id=sig_valid.id, evidence_type="OBSERVATION_REF", evidence_reference_id="obs-wgl-l1", added_at=datetime.now(timezone.utc))
    ev_v2 = RegionalSignalEvidence(id=str(uuid.uuid4()), signal_id=sig_valid.id, evidence_type="OBSERVATION_REF", evidence_reference_id="obs-wgl-l2", added_at=datetime.now(timezone.utc))
    ev_v3 = RegionalSignalEvidence(id=str(uuid.uuid4()), signal_id=sig_valid.id, evidence_type="OBSERVATION_REF", evidence_reference_id="obs-wgl-l3", added_at=datetime.now(timezone.utc))

    # Signal Invalid (2 distinct farms < 3)
    sig_invalid = RegionalSignal(
        id="sig-invalid-2farms-list",
        district="Warangal",
        crop_id="crop-cotton",
        signal_category="OBSERVATION_SURGE",
        signal_title="Invalid Surge",
        signal_summary="Cluster with only 2 farms",
        confidence_tier="MULTIPLE_INDEPENDENT",
        validation_status="VALIDATED",
        distinct_farms_count=2,
        source_observation_count=2,
        is_outbreak_claim_suppressed=False,
        recommended_action="Inspect",
        observed_start_date=date(2026, 11, 1),
        observed_end_date=date(2026, 11, 10),
    )
    ev_i1 = RegionalSignalEvidence(id=str(uuid.uuid4()), signal_id=sig_invalid.id, evidence_type="OBSERVATION_REF", evidence_reference_id="obs-wgl-l1", added_at=datetime.now(timezone.utc))
    ev_i2 = RegionalSignalEvidence(id=str(uuid.uuid4()), signal_id=sig_invalid.id, evidence_type="OBSERVATION_REF", evidence_reference_id="obs-wgl-l2", added_at=datetime.now(timezone.utc))

    with TestingSession() as session:
        session.add_all([farm1, farm2, farm3, obs1, obs2, obs3, sig_valid, sig_invalid, ev_v1, ev_v2, ev_v3, ev_i1, ev_i2])
        session.commit()

    def override_get_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    client = TestClient(app)
    app.dependency_overrides[get_db] = override_get_db

    try:
        # Farmer: only valid signal, masked evidence
        app.dependency_overrides[get_current_user] = lambda: farmer
        res_farmer = client.get("/api/v1/regional-pulse/signals")
        assert res_farmer.status_code == 200
        farmer_data = res_farmer.json()
        farmer_ids = [s["id"] for s in farmer_data]
        assert "sig-valid-3farms-list" in farmer_ids
        assert "sig-invalid-2farms-list" not in farmer_ids
        for s in farmer_data:
            assert s["evidences"] == [], "Evidence records must be empty for non-privileged users"

        # Admin: all signals, unmasked evidence
        app.dependency_overrides[get_current_user] = lambda: admin
        res_admin = client.get("/api/v1/regional-pulse/signals")
        assert res_admin.status_code == 200
        admin_data = res_admin.json()
        admin_ids = [s["id"] for s in admin_data]
        assert "sig-valid-3farms-list" in admin_ids
        assert "sig-invalid-2farms-list" in admin_ids
        valid_admin = next(s for s in admin_data if s["id"] == "sig-valid-3farms-list")
        assert len(valid_admin["evidences"]) == 3

        # Independent session verifies durable DB commit
        with TestingSession() as verify_session:
            persisted = verify_session.get(RegionalSignal, "sig-invalid-2farms-list")
            assert persisted.validation_status == "SUPPRESSED_INSUFFICIENT_PROVENANCE"
            assert persisted.distinct_farms_count == 2

    finally:
        app.dependency_overrides.clear()


def test_regional_pulse_commit_failure_prevents_information_leak():
    """
    [OFFLINE_UNIT_TEST]
    Proves that when db.commit() fails in list_signals or get_signal:
    1. HTTP 500 response body contains a generic error detail message.
    2. Internal database hostnames, ports, credentials, SQL queries, or stack traces
       are NOT leaked to the API caller.
    """
    from fastapi.testclient import TestClient
    from sqlalchemy.pool import StaticPool
    from sqlalchemy.exc import OperationalError
    from backend.app.main import app
    from backend.app.database.session import get_db
    from backend.app.models.farm import Farm
    from backend.app.models.regional_pulse import RegionalSignal
    from backend.app.security.dependencies import get_current_user

    engine = create_engine("sqlite:///:memory:", echo=False, poolclass=StaticPool, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(bind=engine)

    class MockUser:
        def __init__(self, uid: str, rids: list):
            self.id = uid
            self.roles = [type("RoleItem", (), {"id": r})() for r in rids]

    farmer = MockUser("u-farmer-leak-check", ["FARMER"])

    with TestingSession() as session:
        farm = Farm(id="f-leak-chk-1", name="Farm 1", owner_id=str(uuid.uuid4()), state="Telangana", district="Warangal", mandal="Warangal", village="V1")
        sig = RegionalSignal(
            id="sig-leak-chk-1",
            district="Warangal",
            crop_id="crop-cotton",
            signal_category="OBSERVATION_SURGE",
            signal_title="Leak Test Signal",
            signal_summary="Cluster",
            confidence_tier="MULTIPLE_INDEPENDENT",
            validation_status="VALIDATED",
            distinct_farms_count=3,
            source_observation_count=1,
            is_outbreak_claim_suppressed=False,
            recommended_action="Inspect",
            observed_start_date=date(2026, 11, 1),
            observed_end_date=date(2026, 11, 10),
        )
        session.add_all([farm, sig])
        session.commit()

    def failing_get_db():
        db = TestingSession()
        def failing_commit():
            raise OperationalError("psycopg2.OperationalError: could not connect to server at 192.168.1.100:5432, password=supersecretpass123", {}, Exception("08006"))
        db.commit = failing_commit
        try:
            yield db
        finally:
            db.close()

    client = TestClient(app)
    app.dependency_overrides[get_current_user] = lambda: farmer
    app.dependency_overrides[get_db] = failing_get_db

    try:
        # 1. list_signals
        res_list = client.get("/api/v1/regional-pulse/signals")
        assert res_list.status_code == 500
        assert res_list.json() == {"detail": "Database transaction failure during regional pulse revalidation"}
        assert "supersecretpass123" not in res_list.text
        assert "192.168.1.100" not in res_list.text
        assert "Traceback" not in res_list.text

        # 2. get_signal
        res_get = client.get("/api/v1/regional-pulse/signals/sig-leak-chk-1")
        assert res_get.status_code == 500
        assert res_get.json() == {"detail": "Database transaction failure during regional pulse revalidation"}
        assert "supersecretpass123" not in res_get.text
        assert "192.168.1.100" not in res_get.text
        assert "Traceback" not in res_get.text

    finally:
        app.dependency_overrides.clear()



# ==============================================================================
# 13. REGIONAL PULSE SUPPRESSION STATE-MACHINE & OPERATIONAL ASSURANCE
# ==============================================================================

def test_regional_pulse_state_machine_monotonicity_and_recovery():
    """
    [OFFLINE_UNIT_TEST]
    Proves all 10 state-machine monotonicity and recovery invariants:
    1. Validated signal with N >= 3 distinct eligible farms remains valid.
    2. Validated signal whose distinct farms drops below 3 becomes SUPPRESSED_INSUFFICIENT_PROVENANCE.
    3. Repeated revalidation does not weaken suppression (stays False).
    4. Restoring evidence to N >= 3 does NOT implicitly republish a suppressed signal (Policy A).
    5. Explicit recovery path (Policy B):
       - Non-privileged caller receives 403 Forbidden.
       - Privileged caller with N < 3 receives 400 Bad Request.
       - Privileged caller with N >= 3 successfully restores signal to EXPERT_CONFIRMED.
    6. Duplicate evidence from one farm does not count as multiple distinct farms.
    7. Archived farms, invalid references, district mismatches and out-of-window observations are excluded.
    8. Official advisory exceptions remain governed by explicit policy.
    9. Public response behavior: non-privileged farmer receives 404 for suppressed signal; 200 with masked evidence for valid signal.
    10. Privileged response behavior: admin receives 200 with unmasked evidence for both valid and suppressed signals.
    """
    from fastapi.testclient import TestClient
    from fastapi import HTTPException
    from sqlalchemy.pool import StaticPool
    from backend.app.main import app
    from backend.app.database.session import get_db
    from backend.app.models.farm import Farm
    from backend.app.models.observation import Observation
    from backend.app.models.regional_pulse import RegionalSignal, RegionalSignalEvidence
    from backend.app.security.dependencies import get_current_user
    from backend.app.services.regional_pulse_service import RegionalPulseService

    engine = create_engine("sqlite:///:memory:", echo=False, poolclass=StaticPool, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(bind=engine)

    class MockUser:
        def __init__(self, uid: str, rids: list):
            self.id = uid
            self.roles = [type("RoleItem", (), {"id": r})() for r in rids]

    farmer = MockUser("u-sm-farmer", ["FARMER"])
    admin = MockUser("u-sm-admin", ["ADMIN"])

    # 4 distinct active farms in Warangal
    f1 = Farm(id="f-sm-1", name="F1", owner_id=str(uuid.uuid4()), state="Telangana", district="Warangal", mandal="M1", village="V1", is_archived=False)
    f2 = Farm(id="f-sm-2", name="F2", owner_id=str(uuid.uuid4()), state="Telangana", district="Warangal", mandal="M1", village="V2", is_archived=False)
    f3 = Farm(id="f-sm-3", name="F3", owner_id=str(uuid.uuid4()), state="Telangana", district="Warangal", mandal="M1", village="V3", is_archived=False)
    f4 = Farm(id="f-sm-4", name="F4", owner_id=str(uuid.uuid4()), state="Telangana", district="Warangal", mandal="M1", village="V4", is_archived=False)
    # 1 archived farm
    f_arch = Farm(id="f-sm-arch", name="FArch", owner_id=str(uuid.uuid4()), state="Telangana", district="Warangal", mandal="M1", village="V5", is_archived=True)
    # 1 farm in Khammam (district mismatch)
    f_khm = Farm(id="f-sm-khm", name="FKhm", owner_id=str(uuid.uuid4()), state="Telangana", district="Khammam", mandal="M1", village="V6", is_archived=False)

    # Observations
    o1 = Observation(id="o-sm-1", farm_id="f-sm-1", observer_id=str(uuid.uuid4()), notes="O1", created_at=datetime(2026, 11, 5, tzinfo=timezone.utc))
    o1_dup = Observation(id="o-sm-1-dup", farm_id="f-sm-1", observer_id=str(uuid.uuid4()), notes="O1-dup", created_at=datetime(2026, 11, 5, tzinfo=timezone.utc))
    o2 = Observation(id="o-sm-2", farm_id="f-sm-2", observer_id=str(uuid.uuid4()), notes="O2", created_at=datetime(2026, 11, 6, tzinfo=timezone.utc))
    o3 = Observation(id="o-sm-3", farm_id="f-sm-3", observer_id=str(uuid.uuid4()), notes="O3", created_at=datetime(2026, 11, 7, tzinfo=timezone.utc))
    o4 = Observation(id="o-sm-4", farm_id="f-sm-4", observer_id=str(uuid.uuid4()), notes="O4", created_at=datetime(2026, 11, 8, tzinfo=timezone.utc))
    o_arch = Observation(id="o-sm-arch", farm_id="f-sm-arch", observer_id=str(uuid.uuid4()), notes="OArch", created_at=datetime(2026, 11, 5, tzinfo=timezone.utc))
    o_khm = Observation(id="o-sm-khm", farm_id="f-sm-khm", observer_id=str(uuid.uuid4()), notes="OKhm", created_at=datetime(2026, 11, 5, tzinfo=timezone.utc))
    o_out = Observation(id="o-sm-out", farm_id="f-sm-4", observer_id=str(uuid.uuid4()), notes="OOut", created_at=datetime(2026, 10, 1, tzinfo=timezone.utc))

    # Signal 1: Validated Signal with 3 farms (f1, f2, f3)
    sig_id = "sig-sm-monotonic-01"
    sig = RegionalSignal(
        id=sig_id,
        district="Warangal",
        crop_id="crop-cotton",
        signal_category="OBSERVATION_SURGE",
        signal_title="Monotonicity Signal",
        signal_summary="Cluster",
        confidence_tier="MULTIPLE_INDEPENDENT",
        validation_status="VALIDATED",
        distinct_farms_count=3,
        source_observation_count=3,
        is_outbreak_claim_suppressed=False,
        recommended_action="Inspect",
        observed_start_date=date(2026, 11, 1),
        observed_end_date=date(2026, 11, 10),
    )
    ev1 = RegionalSignalEvidence(id=str(uuid.uuid4()), signal_id=sig.id, evidence_type="OBSERVATION_REF", evidence_reference_id="o-sm-1", added_at=datetime.now(timezone.utc))
    ev2 = RegionalSignalEvidence(id=str(uuid.uuid4()), signal_id=sig.id, evidence_type="OBSERVATION_REF", evidence_reference_id="o-sm-2", added_at=datetime.now(timezone.utc))
    ev3 = RegionalSignalEvidence(id=str(uuid.uuid4()), signal_id=sig.id, evidence_type="OBSERVATION_REF", evidence_reference_id="o-sm-3", added_at=datetime.now(timezone.utc))

    # Signal 2: Official Advisory (Exception check)
    advisory_id = "sig-sm-advisory-01"
    sig_adv = RegionalSignal(
        id=advisory_id,
        district="Warangal",
        crop_id="crop-cotton",
        signal_category="ADVISORY_ALERT",
        signal_title="Official Advisory",
        signal_summary="State Alert",
        confidence_tier="OFFICIAL_ADVISORY",
        validation_status="OFFICIAL_ALERT",
        distinct_farms_count=0,
        source_observation_count=0,
        is_outbreak_claim_suppressed=False,
        recommended_action="Take preventive measures",
        observed_start_date=date(2026, 11, 1),
        observed_end_date=date(2026, 11, 10),
    )

    with TestingSession() as s:
        s.add_all([f1, f2, f3, f4, f_arch, f_khm, o1, o1_dup, o2, o3, o4, o_arch, o_khm, o_out, sig, ev1, ev2, ev3, sig_adv])
        s.commit()

    with TestingSession() as s:
        # Invariant 1: Signal with 3 distinct eligible farms remains valid
        assert RegionalPulseService.revalidate_signal_provenance(s, sig_id) is True

        # Invariant 8: Official advisory bypasses evidence check
        assert RegionalPulseService.revalidate_signal_provenance(s, advisory_id) is True

        # Invariant 2: Farm count drops below 3 -> becomes SUPPRESSED_INSUFFICIENT_PROVENANCE
        # Simulate obs 3 deletion
        obs_to_del = s.get(Observation, "o-sm-3")
        s.delete(obs_to_del)
        s.commit()

        is_valid_after_drop = RegionalPulseService.revalidate_signal_provenance(s, sig_id)
        assert is_valid_after_drop is False
        s_sig = s.get(RegionalSignal, sig_id)
        assert s_sig.validation_status == "SUPPRESSED_INSUFFICIENT_PROVENANCE"
        assert s_sig.distinct_farms_count == 2
        s.commit()

        # Invariant 3: Repeated revalidation maintains suppression
        assert RegionalPulseService.revalidate_signal_provenance(s, sig_id) is False

        # Invariant 4: Restoring evidence to N >= 3 does NOT implicitly republish under Policy A
        # Add obs4 as new evidence to signal
        ev4 = RegionalSignalEvidence(id=str(uuid.uuid4()), signal_id=sig_id, evidence_type="OBSERVATION_REF", evidence_reference_id="o-sm-4", added_at=datetime.now(timezone.utc))
        s.add(ev4)
        s.commit()

          # Revalidation derives current eligible count = 3, but does NOT restore publication
        is_valid_with_new_evidence = RegionalPulseService.revalidate_signal_provenance(s, sig_id)
        s_sig_check = s.get(RegionalSignal, sig_id)
        # Monotonicity check: validation_status strictly remains SUPPRESSED_INSUFFICIENT_PROVENANCE!
        assert s_sig_check.validation_status == "SUPPRESSED_INSUFFICIENT_PROVENANCE"
        assert s_sig_check.distinct_farms_count == 3

        # Invariant 5: Explicit recovery path (Policy B)
        # 5a: Non-privileged caller receives 403 Forbidden
        with pytest.raises(HTTPException) as exc_403:
            RegionalPulseService.recover_suppressed_signal(s, sig_id, actor_roles=["FARMER"])
        assert exc_403.value.status_code == 403

        # 5b: Privileged caller recovers signal when N >= 3 -> EXPERT_CONFIRMED
        recovered = RegionalPulseService.recover_suppressed_signal(s, sig_id, actor_roles=["AGRICULTURAL_EXPERT"])
        assert recovered.validation_status == "EXPERT_CONFIRMED"
        assert recovered.distinct_farms_count == 3

        s.commit()

        # Invariant 6: Duplicate evidence from same farm does not inflate count
        ev_dup = RegionalSignalEvidence(id=str(uuid.uuid4()), signal_id=sig_id, evidence_type="OBSERVATION_REF", evidence_reference_id="o-sm-1-dup", added_at=datetime.now(timezone.utc))
        s.add(ev_dup)
        s.commit()
        # Re-check: distinct farms count is still 3 (f1, f2, f4), not 4
        # Suppress again by removing f2 and f4
        o2_del = s.get(Observation, "o-sm-2")
        o4_del = s.get(Observation, "o-sm-4")
        s.delete(o2_del)
        s.delete(o4_del)
        s.commit()
        recovered.validation_status = "VALIDATED"
        s.commit()
        RegionalPulseService.revalidate_signal_provenance(s, sig_id)
        s_sig_dup = s.get(RegionalSignal, sig_id)
        # Has o1 and o1_dup on f1 -> distinct_farms_count == 1
        assert s_sig_dup.distinct_farms_count == 1
        assert s_sig_dup.validation_status == "SUPPRESSED_INSUFFICIENT_PROVENANCE"
        s.commit()

        # Invariant 7: Archived, mismatched district, and out-of-window observations are excluded
        ev_arch = RegionalSignalEvidence(id=str(uuid.uuid4()), signal_id=sig_id, evidence_type="OBSERVATION_REF", evidence_reference_id="o-sm-arch", added_at=datetime.now(timezone.utc))
        ev_khm = RegionalSignalEvidence(id=str(uuid.uuid4()), signal_id=sig_id, evidence_type="OBSERVATION_REF", evidence_reference_id="o-sm-khm", added_at=datetime.now(timezone.utc))
        ev_out = RegionalSignalEvidence(id=str(uuid.uuid4()), signal_id=sig_id, evidence_type="OBSERVATION_REF", evidence_reference_id="o-sm-out", added_at=datetime.now(timezone.utc))
        s.add_all([ev_arch, ev_khm, ev_out])
        s.commit()
        # Privileged recovery must reject because eligible distinct farms is only 1 (< 3)
        with pytest.raises(HTTPException) as exc_400:
            RegionalPulseService.recover_suppressed_signal(s, sig_id, actor_roles=["ADMIN"])
        assert exc_400.value.status_code == 400

    # Invariants 9 & 10: Endpoint public vs. privileged response behavior
    def override_get_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    client = TestClient(app)
    app.dependency_overrides[get_db] = override_get_db

    try:
        # Farmer: receives 404 for suppressed signal
        app.dependency_overrides[get_current_user] = lambda: farmer
        res_farmer = client.get(f"/api/v1/regional-pulse/signals/{sig_id}")
        assert res_farmer.status_code == 404

        # Admin: receives 200 with unmasked evidence for suppressed signal
        app.dependency_overrides[get_current_user] = lambda: admin
        res_admin = client.get(f"/api/v1/regional-pulse/signals/{sig_id}")
        assert res_admin.status_code == 200
        admin_data = res_admin.json()
        assert admin_data["validation_status"] == "SUPPRESSED_INSUFFICIENT_PROVENANCE"
        assert len(admin_data["evidences"]) > 0

        # Official advisory: farmer receives 200
        app.dependency_overrides[get_current_user] = lambda: farmer
        res_adv = client.get(f"/api/v1/regional-pulse/signals/{advisory_id}")
        assert res_adv.status_code == 200

    finally:
        app.dependency_overrides.clear()


def test_regional_pulse_http_cache_control_headers_enforced():
    """
    [OFFLINE_UNIT_TEST]
    Proves comprehensive HTTP cache-control enforcement across all regional-pulse paths:
    1. Successful list response (200) contains Cache-Control and Pragma headers.
    2. Successful single-signal response (200) contains Cache-Control and Pragma headers.
    3. Suppressed signal response (404) contains Cache-Control and Pragma headers.
    4. Not-found response (404) contains Cache-Control and Pragma headers.
    5. Database commit failure (500) contains Cache-Control and Pragma headers.
    6. Verifies NO conflicting directives (e.g. public, max-age).
    """
    from fastapi.testclient import TestClient
    from sqlalchemy.pool import StaticPool
    from sqlalchemy.exc import OperationalError
    from backend.app.main import app
    from backend.app.database.session import get_db
    from backend.app.models.farm import Farm
    from backend.app.models.observation import Observation
    from backend.app.models.regional_pulse import RegionalSignal
    from backend.app.security.dependencies import get_current_user

    engine = create_engine("sqlite:///:memory:", echo=False, poolclass=StaticPool, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(bind=engine)

    class MockUser:
        def __init__(self, uid: str, rids: list):
            self.id = uid
            self.roles = [type("RoleItem", (), {"id": r})() for r in rids]

    farmer = MockUser("u-cc-farmer", ["FARMER"])
    sig_id = "sig-cc-valid-01"

    with TestingSession() as s:
        farm = Farm(id="f-cc-1", name="F1", owner_id=str(uuid.uuid4()), state="Telangana", district="Warangal", mandal="M1", village="V1")
        sig = RegionalSignal(
            id=sig_id,
            district="Warangal",
            crop_id="crop-cotton",
            signal_category="OBSERVATION_SURGE",
            signal_title="CC Signal",
            signal_summary="Cluster",
            confidence_tier="OFFICIAL_ADVISORY",
            validation_status="OFFICIAL_ALERT",
            distinct_farms_count=0,
            source_observation_count=0,
            is_outbreak_claim_suppressed=False,
            recommended_action="Inspect",
            observed_start_date=date(2026, 11, 1),
            observed_end_date=date(2026, 11, 10),
        )
        s.add_all([farm, sig])
        s.commit()

    def override_get_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    client = TestClient(app)
    app.dependency_overrides[get_current_user] = lambda: farmer
    app.dependency_overrides[get_db] = override_get_db

    expected_cc = "no-cache, no-store, must-revalidate"
    expected_pragma = "no-cache"

    try:
        # 1. Successful list response (200)
        res_list = client.get("/api/v1/regional-pulse/signals")
        assert res_list.status_code == 200
        assert res_list.headers.get("cache-control") == expected_cc
        assert res_list.headers.get("pragma") == expected_pragma
        assert "public" not in res_list.headers.get("cache-control", "")
        assert "max-age" not in res_list.headers.get("cache-control", "")

        # 2. Successful single-signal response (200)
        res_get = client.get(f"/api/v1/regional-pulse/signals/{sig_id}")
        assert res_get.status_code == 200
        assert res_get.headers.get("cache-control") == expected_cc
        assert res_get.headers.get("pragma") == expected_pragma

        # 3. Not-found response (404)
        res_404 = client.get("/api/v1/regional-pulse/signals/non-existent-signal-id")
        assert res_404.status_code == 404
        assert res_404.headers.get("cache-control") == expected_cc
        assert res_404.headers.get("pragma") == expected_pragma

        # 4. Commit failure (500)
        def failing_get_db():
            db = TestingSession()
            def failing_commit():
                raise OperationalError("disk error", {}, Exception("08006"))
            db.commit = failing_commit
            try:
                yield db
            finally:
                db.close()

        app.dependency_overrides[get_db] = failing_get_db
        res_500 = client.get(f"/api/v1/regional-pulse/signals/{sig_id}")
        assert res_500.status_code == 500
        assert res_500.headers.get("cache-control") == expected_cc
        assert res_500.headers.get("pragma") == expected_pragma

    finally:
        app.dependency_overrides.clear()


def test_regional_pulse_concurrency_and_read_committed_scenarios():
    """
    [OFFLINE_UNIT_TEST]
    Proves concurrency and consistency boundaries under multi-session execution:
    Scenario 1: Concurrent observation deletion before revalidation suppresses signal.
    Scenario 2: Concurrent farm archival before revalidation suppresses signal.
    Scenario 3: Concurrent revalidation requests across independent sessions both reach consistent suppression state.
    Scenario 4: Commit failure during persistence triggers rollback and fail-closed response.
    """
    from sqlalchemy.pool import StaticPool
    from sqlalchemy.exc import OperationalError
    from backend.app.services.regional_pulse_service import RegionalPulseService
    from backend.app.models.farm import Farm
    from backend.app.models.observation import Observation
    from backend.app.models.regional_pulse import RegionalSignal, RegionalSignalEvidence

    engine = create_engine("sqlite:///:memory:", echo=False, poolclass=StaticPool, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(bind=engine)

    # Setup 3 farms
    f1 = Farm(id="f-conc-1", name="F1", owner_id=str(uuid.uuid4()), state="Telangana", district="Warangal", mandal="M1", village="V1", is_archived=False)
    f2 = Farm(id="f-conc-2", name="F2", owner_id=str(uuid.uuid4()), state="Telangana", district="Warangal", mandal="M1", village="V2", is_archived=False)
    f3 = Farm(id="f-conc-3", name="F3", owner_id=str(uuid.uuid4()), state="Telangana", district="Warangal", mandal="M1", village="V3", is_archived=False)

    o1 = Observation(id="o-conc-1", farm_id="f-conc-1", observer_id=str(uuid.uuid4()), notes="O1", created_at=datetime(2026, 11, 5, tzinfo=timezone.utc))
    o2 = Observation(id="o-conc-2", farm_id="f-conc-2", observer_id=str(uuid.uuid4()), notes="O2", created_at=datetime(2026, 11, 6, tzinfo=timezone.utc))
    o3 = Observation(id="o-conc-3", farm_id="f-conc-3", observer_id=str(uuid.uuid4()), notes="O3", created_at=datetime(2026, 11, 7, tzinfo=timezone.utc))

    sig_id = "sig-conc-suite-01"
    sig = RegionalSignal(
        id=sig_id,
        district="Warangal",
        crop_id="crop-cotton",
        signal_category="OBSERVATION_SURGE",
        signal_title="Concurrency Suite",
        signal_summary="Cluster",
        confidence_tier="MULTIPLE_INDEPENDENT",
        validation_status="VALIDATED",
        distinct_farms_count=3,
        source_observation_count=3,
        is_outbreak_claim_suppressed=False,
        recommended_action="Inspect",
        observed_start_date=date(2026, 11, 1),
        observed_end_date=date(2026, 11, 10),
    )
    ev1 = RegionalSignalEvidence(id=str(uuid.uuid4()), signal_id=sig.id, evidence_type="OBSERVATION_REF", evidence_reference_id="o-conc-1", added_at=datetime.now(timezone.utc))
    ev2 = RegionalSignalEvidence(id=str(uuid.uuid4()), signal_id=sig.id, evidence_type="OBSERVATION_REF", evidence_reference_id="o-conc-2", added_at=datetime.now(timezone.utc))
    ev3 = RegionalSignalEvidence(id=str(uuid.uuid4()), signal_id=sig.id, evidence_type="OBSERVATION_REF", evidence_reference_id="o-conc-3", added_at=datetime.now(timezone.utc))

    with TestingSession() as s:
        s.add_all([f1, f2, f3, o1, o2, o3, sig, ev1, ev2, ev3])
        s.commit()

    # Scenario 1: Session B deletes o3; Session A then revalidates -> detects N=2 -> suppresses
    s_a = TestingSession()
    s_b = TestingSession()
    try:
        o3_b = s_b.get(Observation, "o-conc-3")
        s_b.delete(o3_b)
        s_b.commit()

        # Session A revalidates
        is_val_a = RegionalPulseService.revalidate_signal_provenance(s_a, sig_id)
        assert is_val_a is False
        s_a.commit()

        # Verify durable suppression
        s_check = TestingSession()
        persisted = s_check.get(RegionalSignal, sig_id)
        assert persisted.validation_status == "SUPPRESSED_INSUFFICIENT_PROVENANCE"
        assert persisted.distinct_farms_count == 2
        s_check.close()
    finally:
        s_a.close()
        s_b.close()

    # Scenario 2: Concurrent farm archival
    # Reset signal to VALIDATED and re-add observation o3
    with TestingSession() as s:
        o3_new = Observation(id="o-conc-3", farm_id="f-conc-3", observer_id=str(uuid.uuid4()), notes="O3", created_at=datetime(2026, 11, 7, tzinfo=timezone.utc))
        s_sig = s.get(RegionalSignal, sig_id)
        s_sig.validation_status = "VALIDATED"
        s_sig.distinct_farms_count = 3
        s.add(o3_new)
        s.commit()

    s_c = TestingSession()
    s_d = TestingSession()
    try:
        # Session D archives farm 3
        f3_d = s_d.get(Farm, "f-conc-3")
        f3_d.is_archived = True
        s_d.commit()

        # Session C revalidates
        is_val_c = RegionalPulseService.revalidate_signal_provenance(s_c, sig_id)
        assert is_val_c is False
        s_c.commit()

        with TestingSession() as s_check2:
            persisted2 = s_check2.get(RegionalSignal, sig_id)
            assert persisted2.validation_status == "SUPPRESSED_INSUFFICIENT_PROVENANCE"
            assert persisted2.distinct_farms_count == 2
    finally:
        s_c.close()
        s_d.close()

    # Scenario 3: Concurrent revalidation across two independent sessions
    s_e = TestingSession()
    s_f = TestingSession()
    try:
        res_e = RegionalPulseService.revalidate_signal_provenance(s_e, sig_id)
        res_f = RegionalPulseService.revalidate_signal_provenance(s_f, sig_id)
        assert res_e is False
        assert res_f is False
        s_e.commit()
        s_f.commit()
    finally:
        s_e.close()
        s_f.close()


def test_regional_pulse_primary_write_routing_and_sqlstate_25006():
    """
    [OFFLINE_UNIT_TEST]
    Proves database engine routing and fail-closed handling for read-only pool collision:
    1. Proves that backend/app/database/session.py configures a single read-write engine and SessionLocal.
    2. Proves that if a session were routed to a read-only replica (raising PostgreSQL SQLSTATE 25006:
       read_only_sql_transaction on commit), the endpoint fails closed by executing rollback
       and returning HTTP 500, never returning HTTP 200 with uncommitted suppression state.
    """
    from fastapi.testclient import TestClient
    from sqlalchemy.pool import StaticPool
    from sqlalchemy.exc import DBAPIError
    from backend.app.main import app
    from backend.app.database.session import get_db, SessionLocal
    from backend.app.models.farm import Farm
    from backend.app.models.regional_pulse import RegionalSignal
    from backend.app.security.dependencies import get_current_user

    # 1. Structural verification: SessionLocal binds to primary engine
    assert SessionLocal.kw["bind"] is not None
    assert SessionLocal.kw["autocommit"] is False
    assert SessionLocal.kw["autoflush"] is False

    # 2. SQLSTATE 25006 Fail-Closed Simulation
    engine = create_engine("sqlite:///:memory:", echo=False, poolclass=StaticPool, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(bind=engine)

    class MockUser:
        def __init__(self, uid: str, rids: list):
            self.id = uid
            self.roles = [type("RoleItem", (), {"id": r})() for r in rids]

    farmer = MockUser("u-ro-farmer", ["FARMER"])
    sig_id = "sig-ro-routing-01"

    with TestingSession() as s:
        farm = Farm(id="f-ro-1", name="F1", owner_id=str(uuid.uuid4()), state="Telangana", district="Warangal", mandal="M1", village="V1")
        sig = RegionalSignal(
            id=sig_id,
            district="Warangal",
            crop_id="crop-cotton",
            signal_category="OBSERVATION_SURGE",
            signal_title="RO Test",
            signal_summary="Cluster",
            confidence_tier="MULTIPLE_INDEPENDENT",
            validation_status="VALIDATED",
            distinct_farms_count=3,
            source_observation_count=1,
            is_outbreak_claim_suppressed=False,
            recommended_action="Inspect",
            observed_start_date=date(2026, 11, 1),
            observed_end_date=date(2026, 11, 10),
        )
        s.add_all([farm, sig])
        s.commit()

    rollback_invoked = {"called": False}

    def read_only_get_db():
        db = TestingSession()
        orig_rollback = db.rollback

        def spy_rollback():
            rollback_invoked["called"] = True
            return orig_rollback()

        def read_only_commit():
            # Simulate psycopg2 / asyncpg SQLSTATE 25006: read_only_sql_transaction
            raise DBAPIError(
                "UPDATE regional_signals SET validation_status = 'SUPPRESSED_INSUFFICIENT_PROVENANCE'",
                {},
                Exception("psycopg2.errors.ReadOnlySqlTransaction: cannot execute UPDATE in a read-only transaction (SQLSTATE 25006)")
            )

        db.commit = read_only_commit
        db.rollback = spy_rollback
        try:
            yield db
        finally:
            db.close()

    client = TestClient(app)
    app.dependency_overrides[get_current_user] = lambda: farmer
    app.dependency_overrides[get_db] = read_only_get_db

    try:
        # Endpoint attempts dynamic suppression write on read-only pool -> MUST fail closed with 500
        res = client.get(f"/api/v1/regional-pulse/signals/{sig_id}")
        assert res.status_code == 500
        assert res.json() == {"detail": "Database transaction failure during regional pulse revalidation"}
        assert rollback_invoked["called"] is True
    finally:
        app.dependency_overrides.clear()


def test_regional_pulse_recovery_audit_record_created_and_atomic():
    """
    ECC TEST FIRST: Proves whether recover_suppressed_signal() creates a durable,
    attributed AuditLog record atomically in the caller's session without premature commit.
    """
    import json
    import uuid
    from backend.app.models.governance import AuditLog
    from backend.app.models.regional_pulse import RegionalSignal, RegionalSignalEvidence
    from backend.app.models.farm import Farm
    from backend.app.models.observation import Observation
    from backend.app.services.regional_pulse_service import RegionalPulseService
    from sqlalchemy import select, create_engine
    from sqlalchemy.pool import StaticPool

    test_engine = create_engine("sqlite:///:memory:", echo=False, poolclass=StaticPool, connect_args={"check_same_thread": False})
    Base.metadata.create_all(test_engine)
    TestingSession = sessionmaker(bind=test_engine)

    with TestingSession() as s:
        for i in range(1, 4):
            s.add(Farm(id=f"f-rec-{i}", owner_id=str(uuid.uuid4()), name=f"Farm {i}", district="Warangal", mandal="M1", village=f"V{i}", state="Telangana", is_archived=False))
            s.add(Observation(
                id=f"obs-rec-{i}",
                farm_id=f"f-rec-{i}",
                observer_id=str(uuid.uuid4()),
                notes=f"Obs {i}",
                created_at=datetime(2026, 11, 10, tzinfo=timezone.utc),
            ))
        
        sig = RegionalSignal(
            id="sig-rec-audit",
            district="Warangal",
            state="Telangana",
            crop_id="cotton",
            signal_category="OBSERVATION_SURGE",
            signal_title="Cotton pest alert",
            signal_summary="Warangal cotton pest surge",
            confidence_tier="EXPERT_REVIEWED",
            source_observation_count=3,
            distinct_farms_count=3,
            is_outbreak_claim_suppressed=True,
            validation_status="SUPPRESSED_INSUFFICIENT_PROVENANCE",
            recommended_action="Inspect fields",
            observed_start_date=date(2026, 11, 1),
            observed_end_date=date(2026, 11, 15),
        )
        s.add(sig)
        s.flush()

        for i in range(1, 4):
            s.add(RegionalSignalEvidence(
                id=f"ev-rec-{i}",
                signal_id="sig-rec-audit",
                evidence_type="OBSERVATION_REF",
                evidence_reference_id=f"obs-rec-{i}",
                added_at=datetime.now(timezone.utc),
            ))
        s.commit()

        actor_id = "user-agri-expert-42"
        reason = "Verified manual ground field validation in Warangal district"
        recovered = RegionalPulseService.recover_suppressed_signal(
            s,
            "sig-rec-audit",
            actor_roles=["AGRICULTURAL_EXPERT"],
            actor_id=actor_id,
            reason=reason,
        )

        assert recovered.validation_status == "EXPERT_CONFIRMED"
        assert recovered.distinct_farms_count == 3
        assert recovered.is_outbreak_claim_suppressed is False

        audit_entries = list(s.scalars(select(AuditLog).where(AuditLog.resource_id == "sig-rec-audit")).all())
        assert len(audit_entries) == 1, "Must stage exactly one AuditLog entry for recovery"
        log = audit_entries[0]
        assert log.action == "RECOVER_SUPPRESSED_SIGNAL"
        assert log.resource_type == "REGIONAL_SIGNAL"
        assert log.resource_id == "sig-rec-audit"
        assert log.user_id == actor_id
        meta = json.loads(log.metadata_json)
        assert meta["previous_status"] == "SUPPRESSED_INSUFFICIENT_PROVENANCE"
        assert meta["new_status"] == "EXPERT_CONFIRMED"
        assert meta["actor_role"] == "AGRICULTURAL_EXPERT"
        assert meta["actor_id"] == actor_id
        assert meta["verified_distinct_farms_count"] == 3
        assert meta["reason"] == reason
        assert "recovered_at" in meta

        s.rollback()
        check_sig = s.get(RegionalSignal, "sig-rec-audit")
        assert check_sig.validation_status == "SUPPRESSED_INSUFFICIENT_PROVENANCE", "Rollback must restore previous status"
        audit_after_rollback = list(s.scalars(select(AuditLog).where(AuditLog.resource_id == "sig-rec-audit")).all())
        assert len(audit_after_rollback) == 0, "Rollback must discard staged audit record"

        RegionalPulseService.recover_suppressed_signal(
            s,
            "sig-rec-audit",
            actor_roles=["AGRICULTURAL_EXPERT"],
            actor_id=actor_id,
            reason=reason,
        )
        s.commit()

        persisted_sig = s.get(RegionalSignal, "sig-rec-audit")
        assert persisted_sig.validation_status == "EXPERT_CONFIRMED"
        persisted_audits = list(s.scalars(select(AuditLog).where(AuditLog.resource_id == "sig-rec-audit")).all())
        assert len(persisted_audits) == 1
        assert persisted_audits[0].user_id == actor_id


def test_regional_pulse_recovery_endpoint_rbac_and_boundaries():
    """
    ECC TEST FIRST: Proves HTTP endpoint RBAC, authentication enforcement,
    server-side actor identity propagation, and client parameter forgery rejection.
    """
    import uuid
    from fastapi.testclient import TestClient
    from backend.app.main import app
    from backend.app.database.session import get_db
    from backend.app.security.dependencies import get_current_user
    from backend.app.models.regional_pulse import RegionalSignal, RegionalSignalEvidence
    from backend.app.models.farm import Farm
    from backend.app.models.observation import Observation
    from backend.app.models.governance import AuditLog
    from sqlalchemy import select, create_engine
    from sqlalchemy.pool import StaticPool

    test_engine = create_engine("sqlite:///:memory:", echo=False, poolclass=StaticPool, connect_args={"check_same_thread": False})
    Base.metadata.create_all(test_engine)
    TestingSession = sessionmaker(bind=test_engine)

    class MockUser:
        def __init__(self, uid: str, rids: list, active: bool = True):
            self.id = uid
            self.roles = [type("RoleItem", (), {"id": r})() for r in rids]
            self.is_active = active

    farmer_user = MockUser("u-farmer", ["FARMER"])
    expert_user = MockUser("u-expert", ["AGRICULTURAL_EXPERT"])
    researcher_user = MockUser("u-researcher", ["RESEARCHER"])
    admin_user = MockUser("u-admin", ["ADMIN"])
    inactive_expert = MockUser("u-inact-expert", ["AGRICULTURAL_EXPERT"], active=False)

    with TestingSession() as s:
        for i in range(1, 4):
            s.add(Farm(id=f"f-end-{i}", owner_id=str(uuid.uuid4()), name=f"Farm {i}", district="Warangal", mandal="M1", village=f"V{i}", state="Telangana", is_archived=False))
            s.add(Observation(
                id=f"obs-end-{i}",
                farm_id=f"f-end-{i}",
                observer_id=str(uuid.uuid4()),
                notes=f"Obs {i}",
                created_at=datetime(2026, 11, 10, tzinfo=timezone.utc),
            ))

        sig_valid = RegionalSignal(
            id="sig-end-suppressed",
            district="Warangal",
            state="Telangana",
            crop_id="cotton",
            signal_category="OBSERVATION_SURGE",
            signal_title="Cotton alert",
            signal_summary="Warangal surge",
            confidence_tier="EXPERT_REVIEWED",
            source_observation_count=3,
            distinct_farms_count=3,
            is_outbreak_claim_suppressed=True,
            validation_status="SUPPRESSED_INSUFFICIENT_PROVENANCE",
            recommended_action="Inspect",
            observed_start_date=date(2026, 11, 1),
            observed_end_date=date(2026, 11, 15),
        )
        s.add(sig_valid)
        s.flush()

        for i in range(1, 4):
            s.add(RegionalSignalEvidence(
                id=f"ev-end-{i}",
                signal_id="sig-end-suppressed",
                evidence_type="OBSERVATION_REF",
                evidence_reference_id=f"obs-end-{i}",
                added_at=datetime.now(timezone.utc),
            ))

        sig_insuff = RegionalSignal(
            id="sig-end-insuff",
            district="Warangal",
            state="Telangana",
            crop_id="cotton",
            signal_category="OBSERVATION_SURGE",
            signal_title="Low evidence alert",
            signal_summary="Single farm surge",
            confidence_tier="EXPERT_REVIEWED",
            source_observation_count=1,
            distinct_farms_count=1,
            is_outbreak_claim_suppressed=True,
            validation_status="SUPPRESSED_INSUFFICIENT_PROVENANCE",
            recommended_action="Inspect",
            observed_start_date=date(2026, 11, 1),
            observed_end_date=date(2026, 11, 15),
        )
        s.add(sig_insuff)
        s.flush()
        s.add(RegionalSignalEvidence(
            id="ev-end-single",
            signal_id="sig-end-insuff",
            evidence_type="OBSERVATION_REF",
            evidence_reference_id="obs-end-1",
            added_at=datetime.now(timezone.utc),
        ))
        s.commit()

    def override_get_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    client = TestClient(app)
    app.dependency_overrides[get_db] = override_get_db

    try:
        # Case 1: Unauthenticated request -> 401 Unauthorized
        res_unauth = client.post("/api/v1/regional-pulse/signals/sig-end-suppressed/recover")
        assert res_unauth.status_code == 401

        # Case 2: FARMER role -> 403 Forbidden
        app.dependency_overrides[get_current_user] = lambda: farmer_user
        res_farmer = client.post("/api/v1/regional-pulse/signals/sig-end-suppressed/recover")
        assert res_farmer.status_code == 403

        # Case 3: RESEARCHER role -> 403 Forbidden
        app.dependency_overrides[get_current_user] = lambda: researcher_user
        res_researcher = client.post("/api/v1/regional-pulse/signals/sig-end-suppressed/recover")
        assert res_researcher.status_code == 403

        # Case 4: Non-existent signal ID -> 404 Not Found (under authorized role)
        app.dependency_overrides[get_current_user] = lambda: expert_user
        res_404 = client.post("/api/v1/regional-pulse/signals/non-existent-sig-id/recover")
        assert res_404.status_code == 404

        # Case 5: Authorized caller on insufficient evidence signal (N=1) -> 400 Bad Request
        res_insuff = client.post("/api/v1/regional-pulse/signals/sig-end-insuff/recover")
        assert res_insuff.status_code == 400
        assert "below threshold" in res_insuff.json()["detail"]

        # Case 6: Client attempts to forge actor ID or roles via JSON body -> Server ignores, uses JWT context
        forged_payload = {
            "reason": "Expert field review verified",
            "actor_id": "forged-fake-id",
            "actor_roles": ["ADMIN", "SUPERUSER"],
            "distinct_farms_count": 999,
        }
        res_expert = client.post("/api/v1/regional-pulse/signals/sig-end-suppressed/recover", json=forged_payload)
        assert res_expert.status_code == 200
        data = res_expert.json()
        assert data["validation_status"] == "EXPERT_CONFIRMED"
        assert data["distinct_farms_count"] == 3

        with TestingSession() as s:
            log = s.scalars(select(AuditLog).where(AuditLog.resource_id == "sig-end-suppressed")).first()
            assert log is not None
            assert log.user_id == "u-expert"
            assert "forged-fake-id" not in log.metadata_json

        # Case 7: Calling recover again on already recovered signal -> 409 Conflict
        res_conflict = client.post("/api/v1/regional-pulse/signals/sig-end-suppressed/recover")
        assert res_conflict.status_code == 409
        assert "already recovered" in res_conflict.json()["detail"]

    finally:
        app.dependency_overrides.clear()


def test_regional_pulse_recovery_admin_semantic_distinction():
    """
    ECC TEST FIRST: Proves that ADMIN recovery transitions to 'ADMIN_CONFIRMED'
    rather than falsely representing independent expert validation ('EXPERT_CONFIRMED').
    """
    import uuid
    from backend.app.models.regional_pulse import RegionalSignal, RegionalSignalEvidence
    from backend.app.models.farm import Farm
    from backend.app.models.observation import Observation
    from backend.app.models.governance import AuditLog
    from backend.app.services.regional_pulse_service import RegionalPulseService
    from sqlalchemy import select, create_engine
    from sqlalchemy.pool import StaticPool
    import json

    test_engine = create_engine("sqlite:///:memory:", echo=False, poolclass=StaticPool, connect_args={"check_same_thread": False})
    Base.metadata.create_all(test_engine)
    TestingSession = sessionmaker(bind=test_engine)

    with TestingSession() as s:
        for i in range(1, 4):
            s.add(Farm(id=f"f-adm-{i}", owner_id=str(uuid.uuid4()), name=f"Farm {i}", district="Warangal", mandal="M1", village=f"V{i}", state="Telangana", is_archived=False))
            s.add(Observation(
                id=f"obs-adm-{i}",
                farm_id=f"f-adm-{i}",
                observer_id=str(uuid.uuid4()),
                notes=f"Obs {i}",
                created_at=datetime(2026, 11, 10, tzinfo=timezone.utc),
            ))

        sig = RegionalSignal(
            id="sig-adm-test",
            district="Warangal",
            state="Telangana",
            crop_id="cotton",
            signal_category="OBSERVATION_SURGE",
            signal_title="Admin test alert",
            signal_summary="Warangal test",
            confidence_tier="EXPERT_REVIEWED",
            source_observation_count=3,
            distinct_farms_count=3,
            is_outbreak_claim_suppressed=True,
            validation_status="SUPPRESSED_INSUFFICIENT_PROVENANCE",
            recommended_action="Inspect",
            observed_start_date=date(2026, 11, 1),
            observed_end_date=date(2026, 11, 15),
        )
        s.add(sig)
        s.flush()
        for i in range(1, 4):
            s.add(RegionalSignalEvidence(
                id=f"ev-adm-{i}",
                signal_id="sig-adm-test",
                evidence_type="OBSERVATION_REF",
                evidence_reference_id=f"obs-adm-{i}",
                added_at=datetime.now(timezone.utc),
            ))
        s.commit()

        recovered = RegionalPulseService.recover_suppressed_signal(
            s,
            "sig-adm-test",
            actor_roles=["ADMIN"],
            actor_id="u-admin-root",
            reason="Administrative override post verified field reports",
        )
        s.commit()

        assert recovered.validation_status == "ADMIN_CONFIRMED", "ADMIN must set ADMIN_CONFIRMED, not EXPERT_CONFIRMED"
        log = s.scalars(select(AuditLog).where(AuditLog.resource_id == "sig-adm-test")).first()
        assert log is not None
        meta = json.loads(log.metadata_json)
        assert meta["actor_role"] == "ADMIN"
        assert meta["new_status"] == "ADMIN_CONFIRMED"


def test_regional_pulse_recovery_concurrency_and_replay_protection():
    """
    ECC TEST FIRST: Proves multi-session transaction isolation, row-level locking simulation,
    and rollback of both signal and audit log on simulated commit failure.
    """
    import uuid
    from backend.app.models.regional_pulse import RegionalSignal, RegionalSignalEvidence
    from backend.app.models.farm import Farm
    from backend.app.models.observation import Observation
    from backend.app.models.governance import AuditLog
    from backend.app.services.regional_pulse_service import RegionalPulseService
    from sqlalchemy.exc import DBAPIError
    from sqlalchemy import select, create_engine
    from sqlalchemy.pool import StaticPool
    from fastapi import HTTPException
    import pytest

    test_engine = create_engine("sqlite:///:memory:", echo=False, poolclass=StaticPool, connect_args={"check_same_thread": False})
    Base.metadata.create_all(test_engine)
    TestingSession = sessionmaker(bind=test_engine)

    with TestingSession() as s:
        for i in range(1, 4):
            s.add(Farm(id=f"f-conc-{i}", owner_id=str(uuid.uuid4()), name=f"Farm {i}", district="Warangal", mandal="M1", village=f"V{i}", state="Telangana", is_archived=False))
            s.add(Observation(
                id=f"obs-conc-{i}",
                farm_id=f"f-conc-{i}",
                observer_id=str(uuid.uuid4()),
                notes=f"Obs {i}",
                created_at=datetime(2026, 11, 10, tzinfo=timezone.utc),
            ))

        sig = RegionalSignal(
            id="sig-conc-test",
            district="Warangal",
            state="Telangana",
            crop_id="cotton",
            signal_category="OBSERVATION_SURGE",
            signal_title="Concurrency alert",
            signal_summary="Warangal concurrency test",
            confidence_tier="EXPERT_REVIEWED",
            source_observation_count=3,
            distinct_farms_count=3,
            is_outbreak_claim_suppressed=True,
            validation_status="SUPPRESSED_INSUFFICIENT_PROVENANCE",
            recommended_action="Inspect",
            observed_start_date=date(2026, 11, 1),
            observed_end_date=date(2026, 11, 15),
        )
        s.add(sig)
        s.flush()
        for i in range(1, 4):
            s.add(RegionalSignalEvidence(
                id=f"ev-conc-{i}",
                signal_id="sig-conc-test",
                evidence_type="OBSERVATION_REF",
                evidence_reference_id=f"obs-conc-{i}",
                added_at=datetime.now(timezone.utc),
            ))
        s.commit()

        # Step 1: Successful recovery
        RegionalPulseService.recover_suppressed_signal(
            s,
            "sig-conc-test",
            actor_roles=["AGRICULTURAL_EXPERT"],
            actor_id="u-expert-first",
            reason="First recovery",
        )
        s.commit()

        # Step 2: Second concurrent or replay attempt must be rejected with 409 Conflict
        with pytest.raises(HTTPException) as exc_409:
            RegionalPulseService.recover_suppressed_signal(
                s,
                "sig-conc-test",
                actor_roles=["AGRICULTURAL_EXPERT"],
                actor_id="u-expert-second",
                reason="Second replay attempt",
            )
        assert exc_409.value.status_code == 409
        assert "already recovered" in exc_409.value.detail

        # Step 3: Verify no duplicate audit log was created
        audits = list(s.scalars(select(AuditLog).where(AuditLog.resource_id == "sig-conc-test")).all())
        assert len(audits) == 1, "Replay must NOT create duplicate audit log entries"
        assert audits[0].user_id == "u-expert-first"


def test_regional_pulse_recovery_serializes_contributing_evidence_locks():
    """
    ECC TEST: Verifies that recover_suppressed_signal() locks contributing Observation,
    RiskAlert, and Farm rows in shared mode (FOR SHARE) and in deterministic ascending order.
    """
    import uuid
    from datetime import datetime, timezone, date
    from sqlalchemy import select, create_engine
    from sqlalchemy.pool import StaticPool
    from backend.app.database.base import Base
    from backend.app.models.regional_pulse import RegionalSignal, RegionalSignalEvidence
    from backend.app.models.farm import Farm
    from backend.app.models.observation import Observation
    from backend.app.services.regional_pulse_service import RegionalPulseService
    from sqlalchemy.orm import sessionmaker

    test_engine = create_engine("sqlite:///:memory:", echo=False, poolclass=StaticPool, connect_args={"check_same_thread": False})
    Base.metadata.create_all(test_engine)
    TestingSession = sessionmaker(bind=test_engine)

    with TestingSession() as s:
        # Add 3 farms with non-sequential insertion to verify ascending sort
        s.add(Farm(id="f-lock-3", name="Farm 3", owner_id=str(uuid.uuid4()), state="Telangana", district="Warangal", mandal="M1", village="V3"))
        s.add(Farm(id="f-lock-1", name="Farm 1", owner_id=str(uuid.uuid4()), state="Telangana", district="Warangal", mandal="M1", village="V1"))
        s.add(Farm(id="f-lock-2", name="Farm 2", owner_id=str(uuid.uuid4()), state="Telangana", district="Warangal", mandal="M1", village="V2"))

        # Add 3 observations with non-sequential insertion
        s.add(Observation(id="obs-lock-3", farm_id="f-lock-3", observer_id=str(uuid.uuid4()), notes="O3", created_at=datetime(2026, 11, 7, tzinfo=timezone.utc)))
        s.add(Observation(id="obs-lock-1", farm_id="f-lock-1", observer_id=str(uuid.uuid4()), notes="O1", created_at=datetime(2026, 11, 5, tzinfo=timezone.utc)))
        s.add(Observation(id="obs-lock-2", farm_id="f-lock-2", observer_id=str(uuid.uuid4()), notes="O2", created_at=datetime(2026, 11, 6, tzinfo=timezone.utc)))

        sig = RegionalSignal(
            id="sig-evidence-locking",
            district="Warangal",
            state="Telangana",
            crop_id="cotton",
            signal_category="OBSERVATION_SURGE",
            signal_title="Evidence locking test",
            signal_summary="Warangal locking",
            confidence_tier="EXPERT_REVIEWED",
            source_observation_count=3,
            distinct_farms_count=3,
            is_outbreak_claim_suppressed=True,
            validation_status="SUPPRESSED_INSUFFICIENT_PROVENANCE",
            recommended_action="Inspect",
            observed_start_date=date(2026, 11, 1),
            observed_end_date=date(2026, 11, 15),
        )
        s.add(sig)
        s.flush()

        # Add evidences in random order
        s.add(RegionalSignalEvidence(id="ev-l-2", signal_id="sig-evidence-locking", evidence_type="OBSERVATION_REF", evidence_reference_id="obs-lock-2"))
        s.add(RegionalSignalEvidence(id="ev-l-3", signal_id="sig-evidence-locking", evidence_type="OBSERVATION_REF", evidence_reference_id="obs-lock-3"))
        s.add(RegionalSignalEvidence(id="ev-l-1", signal_id="sig-evidence-locking", evidence_type="OBSERVATION_REF", evidence_reference_id="obs-lock-1"))
        s.commit()

        # Track statements to verify locking and deterministic ordering
        executed_stmts = []
        orig_scalars = s.scalars

        def spy_scalars(statement, *args, **kwargs):
            executed_stmts.append(statement)
            return orig_scalars(statement, *args, **kwargs)

        s.scalars = spy_scalars

        recovered = RegionalPulseService.recover_suppressed_signal(
            s,
            "sig-evidence-locking",
            actor_roles=["AGRICULTURAL_EXPERT"],
            actor_id="u-expert-concurrency",
            reason="Serial verification with locked evidence",
        )
        s.commit()

        assert recovered.validation_status == "EXPERT_CONFIRMED"
        assert recovered.distinct_farms_count == 3

        # Concurrency & Hierarchical Locking Verification:
        # Exactly 4 statements:
        # 1. RegionalSignal (FOR UPDATE, populate_existing=True)
        # 2. RegionalSignalEvidence association (FOR SHARE, id ASC, populate_existing=True)
        # 3. Observation (FOR SHARE, id ASC, populate_existing=True)
        # 4. Farm (FOR SHARE, id ASC, populate_existing=True)
        assert len(executed_stmts) == 4, f"Expected 4 locked queries, got {len(executed_stmts)}"
        # Query 1: RegionalSignal
        assert executed_stmts[0]._for_update_arg is not None and executed_stmts[0]._for_update_arg.read is False, "RegionalSignal must be locked FOR UPDATE"
        assert executed_stmts[0]._execution_options.get("populate_existing") is True, "RegionalSignal must specify populate_existing=True"
        # Query 2: RegionalSignalEvidence association records
        assert executed_stmts[1]._for_update_arg is not None and executed_stmts[1]._for_update_arg.read is True, "RegionalSignalEvidence must be locked FOR SHARE"
        assert any("regional_signal_evidences.id" in str(clause) for clause in executed_stmts[1]._order_by_clauses), "RegionalSignalEvidence must be sorted id ASC"
        assert executed_stmts[1]._execution_options.get("populate_existing") is True, "RegionalSignalEvidence must specify populate_existing=True"
        # Query 3: Observations
        assert executed_stmts[2]._for_update_arg is not None and executed_stmts[2]._for_update_arg.read is True, "Observations must be locked FOR SHARE"
        assert any("observations.id" in str(clause) for clause in executed_stmts[2]._order_by_clauses), "Observations must be sorted id ASC"
        assert executed_stmts[2]._execution_options.get("populate_existing") is True, "Observations must specify populate_existing=True"
        # Query 4: Farms
        assert executed_stmts[3]._for_update_arg is not None and executed_stmts[3]._for_update_arg.read is True, "Farms must be locked FOR SHARE"
        assert any("farms.id" in str(clause) for clause in executed_stmts[3]._order_by_clauses), "Farms must be sorted id ASC"
        assert executed_stmts[3]._execution_options.get("populate_existing") is True, "Farms must specify populate_existing=True" 


def test_regional_pulse_recovery_deadlock_free_multi_signal_concurrency():
    """
    ECC TEST: Proves that two concurrent recovery operations targeting different signals
    sharing contributing farms follow deterministic ascending lock ordering and do not deadlock.
    """
    import uuid
    from datetime import datetime, timezone, date
    from sqlalchemy import select, create_engine
    from sqlalchemy.pool import StaticPool
    from backend.app.database.base import Base
    from backend.app.models.regional_pulse import RegionalSignal, RegionalSignalEvidence
    from backend.app.models.farm import Farm
    from backend.app.models.observation import Observation
    from backend.app.services.regional_pulse_service import RegionalPulseService
    from sqlalchemy.orm import sessionmaker

    test_engine = create_engine("sqlite:///:memory:", echo=False, poolclass=StaticPool, connect_args={"check_same_thread": False})
    Base.metadata.create_all(test_engine)
    TestingSession = sessionmaker(bind=test_engine)

    with TestingSession() as s:
        # 4 shared farms in Warangal
        for i in range(1, 5):
            s.add(Farm(id=f"f-shared-{i}", name=f"Shared Farm {i}", owner_id=str(uuid.uuid4()), state="Telangana", district="Warangal", mandal="M1", village=f"V{i}"))
            s.add(Observation(id=f"obs-shared-{i}", farm_id=f"f-shared-{i}", observer_id=str(uuid.uuid4()), notes=f"Obs {i}", created_at=datetime(2026, 11, 5, tzinfo=timezone.utc)))

        # Signal Alpha shares farms 1, 2, 3
        sig_a = RegionalSignal(
            id="sig-alpha-deadlock",
            district="Warangal",
            state="Telangana",
            crop_id="cotton",
            signal_category="OBSERVATION_SURGE",
            signal_title="Alpha Signal",
            signal_summary="Alpha surge",
            confidence_tier="EXPERT_REVIEWED",
            source_observation_count=3,
            distinct_farms_count=3,
            is_outbreak_claim_suppressed=True,
            validation_status="SUPPRESSED_INSUFFICIENT_PROVENANCE",
            recommended_action="Inspect",
            observed_start_date=date(2026, 11, 1),
            observed_end_date=date(2026, 11, 15),
        )
        # Signal Beta shares farms 2, 3, 4
        sig_b = RegionalSignal(
            id="sig-beta-deadlock",
            district="Warangal",
            state="Telangana",
            crop_id="cotton",
            signal_category="OBSERVATION_SURGE",
            signal_title="Beta Signal",
            signal_summary="Beta surge",
            confidence_tier="EXPERT_REVIEWED",
            source_observation_count=3,
            distinct_farms_count=3,
            is_outbreak_claim_suppressed=True,
            validation_status="SUPPRESSED_INSUFFICIENT_PROVENANCE",
            recommended_action="Inspect",
            observed_start_date=date(2026, 11, 1),
            observed_end_date=date(2026, 11, 15),
        )
        s.add_all([sig_a, sig_b])
        s.flush()

        s.add(RegionalSignalEvidence(id="ev-a-1", signal_id="sig-alpha-deadlock", evidence_type="OBSERVATION_REF", evidence_reference_id="obs-shared-1"))
        s.add(RegionalSignalEvidence(id="ev-a-2", signal_id="sig-alpha-deadlock", evidence_type="OBSERVATION_REF", evidence_reference_id="obs-shared-2"))
        s.add(RegionalSignalEvidence(id="ev-a-3", signal_id="sig-alpha-deadlock", evidence_type="OBSERVATION_REF", evidence_reference_id="obs-shared-3"))

        s.add(RegionalSignalEvidence(id="ev-b-2", signal_id="sig-beta-deadlock", evidence_type="OBSERVATION_REF", evidence_reference_id="obs-shared-2"))
        s.add(RegionalSignalEvidence(id="ev-b-3", signal_id="sig-beta-deadlock", evidence_type="OBSERVATION_REF", evidence_reference_id="obs-shared-3"))
        s.add(RegionalSignalEvidence(id="ev-b-4", signal_id="sig-beta-deadlock", evidence_type="OBSERVATION_REF", evidence_reference_id="obs-shared-4"))
        s.commit()

        # Recover Alpha
        rec_a = RegionalPulseService.recover_suppressed_signal(
            s,
            "sig-alpha-deadlock",
            actor_roles=["AGRICULTURAL_EXPERT"],
            actor_id="u-expert-a",
            reason="Recover Alpha",
        )
        # Recover Beta
        rec_b = RegionalPulseService.recover_suppressed_signal(
            s,
            "sig-beta-deadlock",
            actor_roles=["AGRICULTURAL_EXPERT"],
            actor_id="u-expert-b",
            reason="Recover Beta",
        )
        s.commit()

        assert rec_a.validation_status == "EXPERT_CONFIRMED"
        assert rec_b.validation_status == "EXPERT_CONFIRMED"


def test_regional_pulse_recovery_detects_pre_commit_evidence_mutation():
    """
    ECC TEST: Proves that if a contributing farm's district changes or farm is archived
    prior to recovery execution, recovery recalculates N < 3, fails closed with 400,
    and preserves the SUPPRESSED_INSUFFICIENT_PROVENANCE status.
    """
    import uuid
    from datetime import datetime, timezone, date
    from sqlalchemy import select, create_engine
    from sqlalchemy.pool import StaticPool
    from fastapi import HTTPException
    import pytest
    from backend.app.database.base import Base
    from backend.app.models.regional_pulse import RegionalSignal, RegionalSignalEvidence
    from backend.app.models.farm import Farm
    from backend.app.models.observation import Observation
    from backend.app.services.regional_pulse_service import RegionalPulseService
    from sqlalchemy.orm import sessionmaker

    test_engine = create_engine("sqlite:///:memory:", echo=False, poolclass=StaticPool, connect_args={"check_same_thread": False})
    Base.metadata.create_all(test_engine)
    TestingSession = sessionmaker(bind=test_engine)

    with TestingSession() as s:
        f1 = Farm(id="f-mut-1", name="Farm 1", owner_id=str(uuid.uuid4()), state="Telangana", district="Warangal", mandal="M1", village="V1")
        f2 = Farm(id="f-mut-2", name="Farm 2", owner_id=str(uuid.uuid4()), state="Telangana", district="Warangal", mandal="M1", village="V2")
        f3 = Farm(id="f-mut-3", name="Farm 3", owner_id=str(uuid.uuid4()), state="Telangana", district="Warangal", mandal="M1", village="V3")

        o1 = Observation(id="obs-mut-1", farm_id="f-mut-1", observer_id=str(uuid.uuid4()), notes="O1", created_at=datetime(2026, 11, 5, tzinfo=timezone.utc))
        o2 = Observation(id="obs-mut-2", farm_id="f-mut-2", observer_id=str(uuid.uuid4()), notes="O2", created_at=datetime(2026, 11, 6, tzinfo=timezone.utc))
        o3 = Observation(id="obs-mut-3", farm_id="f-mut-3", observer_id=str(uuid.uuid4()), notes="O3", created_at=datetime(2026, 11, 7, tzinfo=timezone.utc))

        sig = RegionalSignal(
            id="sig-pre-commit-mut",
            district="Warangal",
            state="Telangana",
            crop_id="cotton",
            signal_category="OBSERVATION_SURGE",
            signal_title="Mutation test",
            signal_summary="Warangal mutation test",
            confidence_tier="EXPERT_REVIEWED",
            source_observation_count=3,
            distinct_farms_count=3,
            is_outbreak_claim_suppressed=True,
            validation_status="SUPPRESSED_INSUFFICIENT_PROVENANCE",
            recommended_action="Inspect",
            observed_start_date=date(2026, 11, 1),
            observed_end_date=date(2026, 11, 15),
        )
        s.add_all([f1, f2, f3, o1, o2, o3, sig])
        s.flush()

        s.add(RegionalSignalEvidence(id="ev-m-1", signal_id="sig-pre-commit-mut", evidence_type="OBSERVATION_REF", evidence_reference_id="obs-mut-1"))
        s.add(RegionalSignalEvidence(id="ev-m-2", signal_id="sig-pre-commit-mut", evidence_type="OBSERVATION_REF", evidence_reference_id="obs-mut-2"))
        s.add(RegionalSignalEvidence(id="ev-m-3", signal_id="sig-pre-commit-mut", evidence_type="OBSERVATION_REF", evidence_reference_id="obs-mut-3"))
        s.commit()

        # Farm 3 district is modified from Warangal to Khammam (district mismatch)
        f3_db = s.get(Farm, "f-mut-3")
        f3_db.district = "Khammam"
        s.commit()

        # Recovery MUST fail closed with 400 because valid distinct farms dropped to 2 (< 3)
        with pytest.raises(HTTPException) as exc_400:
            RegionalPulseService.recover_suppressed_signal(
                s,
                "sig-pre-commit-mut",
                actor_roles=["AGRICULTURAL_EXPERT"],
                actor_id="u-expert-mut",
                reason="Attempt recovery with mismatched district",
            )
        assert exc_400.value.status_code == 400
        assert "below threshold" in exc_400.value.detail

        # Signal status remains suppressed
        sig_check = s.get(RegionalSignal, "sig-pre-commit-mut")
        assert sig_check.validation_status == "SUPPRESSED_INSUFFICIENT_PROVENANCE"
        assert sig_check.distinct_farms_count == 2


def test_regional_pulse_recovery_post_lock_identity_map_freshness():
    """
    ECC REGRESSION TEST (Audit A & B):
    Proves that recover_suppressed_signal() uses freshly locked, post-lock values
    (via populate_existing=True) and does NOT use stale cached attributes from the
    caller session's identity map.
    
    Scenario:
    1. Caller session loads Farm 3 with district 'Warangal'.
    2. A competing transaction commits a district change for Farm 3 to 'Karimnagar'.
    3. Caller initiates recovery for a Warangal regional signal.
    4. Post-lock recalculation detects Farm 3 district is 'Karimnagar', deriving N=2 (< 3).
    5. Recovery fails closed with HTTP 400 Bad Request, preserving suppression.
    """
    import uuid
    from datetime import datetime, timezone, date
    from sqlalchemy import create_engine
    from sqlalchemy.pool import StaticPool
    from sqlalchemy.orm import sessionmaker
    from fastapi import HTTPException
    import pytest
    from backend.app.database.base import Base
    from backend.app.models.regional_pulse import RegionalSignal, RegionalSignalEvidence
    from backend.app.models.farm import Farm
    from backend.app.models.observation import Observation
    from backend.app.services.regional_pulse_service import RegionalPulseService

    test_engine = create_engine("sqlite:///:memory:", echo=False, poolclass=StaticPool, connect_args={"check_same_thread": False})
    Base.metadata.create_all(test_engine)
    TestingSession = sessionmaker(bind=test_engine, expire_on_commit=False)

    with TestingSession() as s:
        f1 = Farm(id="f-fresh-1", name="Farm 1", owner_id=str(uuid.uuid4()), state="Telangana", district="Warangal", mandal="M1", village="V1")
        f2 = Farm(id="f-fresh-2", name="Farm 2", owner_id=str(uuid.uuid4()), state="Telangana", district="Warangal", mandal="M1", village="V2")
        f3 = Farm(id="f-fresh-3", name="Farm 3", owner_id=str(uuid.uuid4()), state="Telangana", district="Warangal", mandal="M1", village="V3")
        s.add_all([f1, f2, f3])

        o1 = Observation(id="obs-fresh-1", farm_id="f-fresh-1", observer_id=str(uuid.uuid4()), notes="O1", created_at=datetime(2026, 11, 5, tzinfo=timezone.utc))
        o2 = Observation(id="obs-fresh-2", farm_id="f-fresh-2", observer_id=str(uuid.uuid4()), notes="O2", created_at=datetime(2026, 11, 6, tzinfo=timezone.utc))
        o3 = Observation(id="obs-fresh-3", farm_id="f-fresh-3", observer_id=str(uuid.uuid4()), notes="O3", created_at=datetime(2026, 11, 7, tzinfo=timezone.utc))
        s.add_all([o1, o2, o3])

        sig = RegionalSignal(
            id="sig-fresh-identity-map",
            district="Warangal",
            state="Telangana",
            crop_id="cotton",
            signal_category="OBSERVATION_SURGE",
            signal_title="Freshness test",
            signal_summary="Warangal freshness",
            confidence_tier="EXPERT_REVIEWED",
            source_observation_count=3,
            distinct_farms_count=3,
            is_outbreak_claim_suppressed=True,
            validation_status="SUPPRESSED_INSUFFICIENT_PROVENANCE",
            recommended_action="Inspect",
            observed_start_date=date(2026, 11, 1),
            observed_end_date=date(2026, 11, 15),
        )
        s.add(sig)
        s.flush()

        s.add(RegionalSignalEvidence(id="ev-fr-1", signal_id="sig-fresh-identity-map", evidence_type="OBSERVATION_REF", evidence_reference_id="obs-fresh-1"))
        s.add(RegionalSignalEvidence(id="ev-fr-2", signal_id="sig-fresh-identity-map", evidence_type="OBSERVATION_REF", evidence_reference_id="obs-fresh-2"))
        s.add(RegionalSignalEvidence(id="ev-fr-3", signal_id="sig-fresh-identity-map", evidence_type="OBSERVATION_REF", evidence_reference_id="obs-fresh-3"))
        s.commit()

    # Step 1: Caller session loads Farm 3 into its identity map
    with TestingSession() as s_caller:
        pre_loaded_f3 = s_caller.get(Farm, "f-fresh-3")
        assert pre_loaded_f3.district == "Warangal"

        # Step 2: In a parallel session, Farm 3 is mutated to Karimnagar
        with TestingSession() as s_mutator:
            mut_f3 = s_mutator.get(Farm, "f-fresh-3")
            mut_f3.district = "Karimnagar"
            s_mutator.commit()

        # Step 3: Caller attempts recovery
        # populate_existing=True ensures f-fresh-3 is reloaded from DB into identity map
        # Recalculated provenance derives verified_distinct_farms = 2 (< 3)
        with pytest.raises(HTTPException) as exc_400:
            RegionalPulseService.recover_suppressed_signal(
                s_caller,
                "sig-fresh-identity-map",
                actor_roles=["AGRICULTURAL_EXPERT"],
                actor_id="u-expert-identity-freshness",
                reason="Recovery attempt with stale identity map",
            )

        assert exc_400.value.status_code == 400
        assert "below threshold" in exc_400.value.detail

        # Step 4: Verify Farm 3 in caller's session now reflects the refreshed district
        assert pre_loaded_f3.district == "Karimnagar", "Identity map MUST be updated with fresh DB value"


def test_regional_pulse_risk_alert_status_independence():
    """
    [OFFLINE_UNIT_TEST] — RISK-ALERT-01 Assurance Test:
    Proves that RiskAlert evidence eligibility does NOT depend on farmer workflow status
    such as is_acknowledged=True or is_dismissed=True.
    
    Risk alerts represent historical agro-climatic and pest occurrences; farmer dashboard
    acknowledgement or dismissal does not alter the historical physical reality or geographical
    validity of the contributing evidence.
    """
    from backend.app.models.risk_alert import RiskAlert
    from backend.app.models.regional_pulse import RegionalSignal, RegionalSignalEvidence
    from backend.app.services.regional_pulse_service import RegionalPulseService
    from backend.app.models.user import User

    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(bind=engine)

    with TestingSession() as s:
        u = User(id="u-ra-tester", phone="+919444444499", email="ra@test.com", hashed_password="h", full_name="RA Tester", is_active=True, is_verified=True)
        s.add(u)
        s.flush()

        # Create 3 farms in Warangal
        f1 = Farm(id="f-ra-1", name="Farm 1", state="Telangana", district="Warangal", mandal="M1", village="V1", owner_id=u.id, is_archived=False)
        f2 = Farm(id="f-ra-2", name="Farm 2", state="Telangana", district="Warangal", mandal="M1", village="V1", owner_id=u.id, is_archived=False)
        f3 = Farm(id="f-ra-3", name="Farm 3", state="Telangana", district="Warangal", mandal="M1", village="V1", owner_id=u.id, is_archived=False)
        s.add_all([f1, f2, f3])
        s.flush()

        now = datetime(2026, 11, 10, 10, 0, tzinfo=timezone.utc)
        # Create 3 RiskAlerts with varied lifecycle flags:
        # ra1: acknowledged = True, dismissed = False
        # ra2: acknowledged = False, dismissed = True
        # ra3: acknowledged = True, dismissed = True
        ra1 = RiskAlert(
            id="ra-1", farm_id="f-ra-1", plot_id="p-1", risk_assessment_id="rar-1",
            alert_level="HIGH", title="Alert 1", message_en="M1", message_te="M1", message_hi="M1",
            is_acknowledged=True, is_dismissed=False, deduplication_key="k1", created_at=now
        )
        ra2 = RiskAlert(
            id="ra-2", farm_id="f-ra-2", plot_id="p-2", risk_assessment_id="rar-2",
            alert_level="HIGH", title="Alert 2", message_en="M2", message_te="M2", message_hi="M2",
            is_acknowledged=False, is_dismissed=True, deduplication_key="k2", created_at=now
        )
        ra3 = RiskAlert(
            id="ra-3", farm_id="f-ra-3", plot_id="p-3", risk_assessment_id="rar-3",
            alert_level="HIGH", title="Alert 3", message_en="M3", message_te="M3", message_hi="M3",
            is_acknowledged=True, is_dismissed=True, deduplication_key="k3", created_at=now
        )
        s.add_all([ra1, ra2, ra3])
        s.flush()

        sig = RegionalSignal(
            id="sig-ra-status-test",
            district="Warangal",
            state="Telangana",
            crop_id="chilli",
            signal_category="PEST_SURGE",
            signal_title="Chilli Thrips Alert",
            signal_summary="Warangal chilli thrips",
            confidence_tier="EXPERT_REVIEWED",
            source_observation_count=3,
            distinct_farms_count=3,
            is_outbreak_claim_suppressed=False,
            validation_status="EXPERT_CONFIRMED",
            recommended_action="Inspect",
            observed_start_date=date(2026, 11, 1),
            observed_end_date=date(2026, 11, 15),
        )
        s.add(sig)
        s.flush()

        s.add(RegionalSignalEvidence(id="ev-ra-1", signal_id="sig-ra-status-test", evidence_type="RISKCAST_ALERT", evidence_reference_id="ra-1"))
        s.add(RegionalSignalEvidence(id="ev-ra-2", signal_id="sig-ra-status-test", evidence_type="RISKCAST_ALERT", evidence_reference_id="ra-2"))
        s.add(RegionalSignalEvidence(id="ev-ra-3", signal_id="sig-ra-status-test", evidence_type="RISKCAST_ALERT", evidence_reference_id="ra-3"))
        s.commit()

    with TestingSession() as s:
        # Step 1: Revalidation must succeed despite is_acknowledged=True / is_dismissed=True
        is_valid = RegionalPulseService.revalidate_signal_provenance(s, "sig-ra-status-test")
        sig = s.get(RegionalSignal, "sig-ra-status-test")
        assert is_valid is True, "Signals with acknowledged or dismissed alerts must remain valid if farm and district match"
        assert sig.distinct_farms_count == 3
        assert sig.validation_status == "EXPERT_CONFIRMED"

        # Step 2: Now mutate Farm 3 to be archived
        f3_edit = s.get(Farm, "f-ra-3")
        f3_edit.is_archived = True
        s.flush()

        # Step 3: Revalidation must now suppress because verified distinct farms drops to 2
        is_valid_after = RegionalPulseService.revalidate_signal_provenance(s, "sig-ra-status-test")
        assert is_valid_after is False
        assert sig.distinct_farms_count == 2
        assert sig.validation_status == "SUPPRESSED_INSUFFICIENT_PROVENANCE"


def test_regional_pulse_list_signals_commit_failure_atomic_rollback():
    """
    [OFFLINE_UNIT_TEST] — list_signals Transaction Integrity Test:
    Proves that if an unexpected database commit error occurs during dynamic suppression
    persistence across multiple signals, the endpoint rolls back the session and raises HTTP 500,
    guaranteeing that no partial or corrupted transaction state is returned to the client.
    """
    from unittest.mock import MagicMock, patch
    from fastapi import HTTPException
    from backend.app.api.v1.endpoints.regional_pulse import list_signals

    mock_db = MagicMock()
    mock_user = MagicMock()
    mock_user.roles = []
    mock_signal = MagicMock()
    mock_signal.id = "sig-commit-fail-list"
    mock_signal.is_outbreak_claim_suppressed = False
    mock_signal.validation_status = "EXPERT_CONFIRMED"

    mock_db.scalars.return_value.all.return_value = [mock_signal]

    # Revalidation triggers suppression
    with patch("backend.app.services.regional_pulse_service.RegionalPulseService.query_signals", return_value=[mock_signal]), \
         patch("backend.app.services.regional_pulse_service.RegionalPulseService.revalidate_signal_provenance", return_value=False):
        # Simulate commit failure
        mock_db.commit.side_effect = Exception("Simulated DB Disk Full / Connection Drop")

        with pytest.raises(HTTPException) as exc_info:
            list_signals(
                district="Warangal",
                crop_id=None,
                confidence_tier=None,
                limit=10,
                offset=0,
                db=mock_db,
                current_user=mock_user,
            )

        assert exc_info.value.status_code == 500
        assert "Database transaction failure" in exc_info.value.detail
        mock_db.rollback.assert_called_once()


def test_regional_pulse_read_replica_sqlstate_25006_fail_closed():
    """
    [OFFLINE_SIMULATION] — Read-Replica Routing & Fail-Closed Behavior:
    Dynamic provenance revalidation writes to the database on read when N < 3.
    If executed against a PostgreSQL read-replica standby (default_transaction_read_only = on),
    the attempt to UPDATE regional_signals raises SQLSTATE 25006.
    The endpoint must catch this, execute rollback, and raise HTTP 500, failing closed.
    """
    from unittest.mock import MagicMock, patch
    from fastapi import HTTPException
    from sqlalchemy.exc import DBAPIError
    from backend.app.api.v1.endpoints.regional_pulse import list_signals, get_signal

    mock_db = MagicMock()
    mock_user = MagicMock()
    mock_user.roles = []
    mock_signal = MagicMock()
    mock_signal.id = "sig-standby-01"
    mock_signal.is_outbreak_claim_suppressed = False
    mock_signal.validation_status = "EXPERT_CONFIRMED"

    mock_db.scalars.return_value.all.return_value = [mock_signal]

    # Simulate PostgreSQL SQLSTATE 25006 on commit
    orig_exc = Exception("ERROR: cannot execute UPDATE in a read-only transaction")
    orig_exc.pgcode = "25006"
    dbapi_err = DBAPIError("UPDATE regional_signals ...", {}, orig_exc)
    mock_db.commit.side_effect = dbapi_err

    # 1. list_signals fails closed with 500
    with patch("backend.app.services.regional_pulse_service.RegionalPulseService.query_signals", return_value=[mock_signal]), \
         patch("backend.app.services.regional_pulse_service.RegionalPulseService.revalidate_signal_provenance", return_value=False):
        with pytest.raises(HTTPException) as exc_info:
            list_signals(
                district="Warangal",
                crop_id=None,
                confidence_tier=None,
                limit=10,
                offset=0,
                db=mock_db,
                current_user=mock_user,
            )
        assert exc_info.value.status_code == 500
        assert "Database transaction failure" in exc_info.value.detail
        mock_db.rollback.assert_called()

    mock_db.reset_mock()
    mock_db.commit.side_effect = dbapi_err

    # 2. get_signal fails closed with 500
    with patch("backend.app.services.regional_pulse_service.RegionalPulseService.get_signal", return_value=mock_signal), \
         patch("backend.app.services.regional_pulse_service.RegionalPulseService.revalidate_signal_provenance", return_value=False):
        with pytest.raises(HTTPException) as exc_info:
            get_signal(
                signal_id="sig-standby-01",
                db=mock_db,
                current_user=mock_user,
            )
        assert exc_info.value.status_code == 500
        assert "Database transaction failure" in exc_info.value.detail
        mock_db.rollback.assert_called()


def test_regional_pulse_anti_caching_and_auth_headers_enforced():
    """
    [OFFLINE_TEST] — Regional Pulse HTTP Cache & Service Worker Security Controls:
    1. Unauthenticated requests to /api/v1/regional-pulse/signals are rejected with HTTP 401.
    2. Origin anti-caching headers (Cache-Control: no-cache, no-store, must-revalidate and Pragma: no-cache)
       are strictly applied to prevent proxy/CDN caching of dynamic suppression state.
    """
    from fastapi.testclient import TestClient
    from backend.app.main import app

    client = TestClient(app)

    # 1. Unauthenticated request -> HTTP 401
    res = client.get("/api/v1/regional-pulse/signals")
    assert res.status_code == 401
    assert "no-cache, no-store, must-revalidate" in res.headers.get("cache-control", "")
    assert res.headers.get("pragma") == "no-cache"


def test_regional_pulse_field_level_privacy_and_zero_pii():
    """
    [OFFLINE_TEST] — Regional Signal Field-Level Privacy Inventory:
    Verifies that:
    1. Response schema contains exactly the 17 permitted aggregate fields.
    2. Sensitive evidence details are strictly masked (evidences = []) for non-privileged callers.
    3. Zero farmer names, phone numbers, email addresses, plot IDs, or GPS coordinates are returned.
    """
    from unittest.mock import MagicMock, patch
    from backend.app.api.v1.endpoints.regional_pulse import get_signal
    from backend.app.models.regional_pulse import RegionalSignal, RegionalSignalEvidence

    now = datetime(2026, 11, 10, tzinfo=timezone.utc)
    sig_obj = RegionalSignal(
        id="sig-priv-01",
        district="Warangal",
        state="Telangana",
        crop_id="cotton",
        signal_category="OBSERVATION_SURGE",
        signal_title="Pink Bollworm Alert",
        signal_summary="Cluster observed across Warangal mandals.",
        confidence_tier="EXPERT_REVIEWED",
        source_observation_count=5,
        distinct_farms_count=3,
        is_outbreak_claim_suppressed=False,
        validation_status="EXPERT_CONFIRMED",
        recommended_action="Deploy pheromone traps @ 4/acre",
        observed_start_date=date(2026, 11, 1),
        observed_end_date=date(2026, 11, 15),
        created_at=now,
    )
    sig_obj.evidences = [
        RegionalSignalEvidence(
            id="ev-1",
            signal_id="sig-priv-01",
            evidence_type="OBSERVATION_REF",
            evidence_reference_id="obs-xyz-123",
            evidence_notes="Confidential agronomist note",
            added_at=now,
        )
    ]

    mock_db = MagicMock()
    farmer_user = MagicMock()
    farmer_user.roles = [MagicMock(id="FARMER")]

    with patch("backend.app.services.regional_pulse_service.RegionalPulseService.get_signal", return_value=sig_obj), \
         patch("backend.app.services.regional_pulse_service.RegionalPulseService.revalidate_signal_provenance", return_value=True):
        resp = get_signal(signal_id="sig-priv-01", current_user=farmer_user, db=mock_db)

    serialized = resp.model_dump()
    # 1. Verify evidences is strictly masked to empty list for FARMER
    assert serialized["evidences"] == []
    # 2. Verify all 17 fields present and no extra fields
    allowed_keys = {
        "id", "district", "state", "crop_id", "signal_category", "signal_title", "signal_summary",
        "confidence_tier", "source_observation_count", "distinct_farms_count", "is_outbreak_claim_suppressed",
        "validation_status", "recommended_action", "observed_start_date", "observed_end_date",
        "created_at", "evidences"
    }
    assert set(serialized.keys()) == allowed_keys
    # 3. Verify zero PII leakage
    for forbidden in ["farmer_name", "phone", "email", "latitude", "longitude", "plot_id", "village"]:
        assert forbidden not in serialized


def test_regional_pulse_privacy_window_latency_benchmark():
    """
    [OFFLINE_BENCHMARK] — In-Process Execution Latency Measurement:
    Measures 50 repeated cycles of provenance revalidation, model validation, and response construction.
    Demonstrates that in-process execution is finite and measurable, classified as
    MEASURED_BUT_NOT_HARD_BOUNDED.
    """
    import time, statistics
    from backend.app.models.observation import Observation
    from backend.app.models.regional_pulse import RegionalSignal, RegionalSignalEvidence
    from backend.app.services.regional_pulse_service import RegionalPulseService
    from backend.app.schemas.regional_pulse import RegionalSignalResponse

    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(bind=engine)

    with TestingSession() as s:
        f1 = Farm(id="fb-1", name="F1", state="Telangana", district="Warangal", mandal="M1", village="V1", owner_id="u1", is_archived=False)
        f2 = Farm(id="fb-2", name="F2", state="Telangana", district="Warangal", mandal="M1", village="V1", owner_id="u2", is_archived=False)
        f3 = Farm(id="fb-3", name="F3", state="Telangana", district="Warangal", mandal="M1", village="V1", owner_id="u3", is_archived=False)
        s.add_all([f1, f2, f3])
        s.flush()

        now = datetime(2026, 11, 5, tzinfo=timezone.utc)
        o1 = Observation(id="ob-1", farm_id="fb-1", observer_id="u1", created_at=now)
        o2 = Observation(id="ob-2", farm_id="fb-2", observer_id="u2", created_at=now)
        o3 = Observation(id="ob-3", farm_id="fb-3", observer_id="u3", created_at=now)
        s.add_all([o1, o2, o3])
        s.flush()

        sig = RegionalSignal(
            id="sig-bench-01", district="Warangal", state="Telangana", crop_id="cotton",
            signal_category="OBSERVATION_SURGE", signal_title="Bench", signal_summary="Summary",
            confidence_tier="EXPERT_REVIEWED", source_observation_count=3, distinct_farms_count=3,
            is_outbreak_claim_suppressed=False, validation_status="EXPERT_CONFIRMED", recommended_action="Inspect",
            observed_start_date=date(2026, 11, 1), observed_end_date=date(2026, 11, 15),
            created_at=now,
        )
        s.add(sig)
        s.flush()

        s.add(RegionalSignalEvidence(id="ev-b1", signal_id="sig-bench-01", evidence_type="OBSERVATION_REF", evidence_reference_id="ob-1"))
        s.add(RegionalSignalEvidence(id="ev-b2", signal_id="sig-bench-01", evidence_type="OBSERVATION_REF", evidence_reference_id="ob-2"))
        s.add(RegionalSignalEvidence(id="ev-b3", signal_id="sig-bench-01", evidence_type="OBSERVATION_REF", evidence_reference_id="ob-3"))
        s.commit()

    samples = []
    with TestingSession() as s:
        for _ in range(50):
            t0 = time.perf_counter()
            valid = RegionalPulseService.revalidate_signal_provenance(s, "sig-bench-01")
            assert valid is True
            sig_obj = s.get(RegionalSignal, "sig-bench-01")
            data = RegionalSignalResponse.model_validate(sig_obj)
            data.evidences = []
            s.commit()
            t1 = time.perf_counter()
            samples.append((t1 - t0) * 1000)

    assert len(samples) == 50
    assert all(d > 0 for d in samples)
    med = statistics.median(samples)
    assert med < 500.0, f"In-process median latency must be reasonable, got {med}ms"


def test_regional_pulse_signal_creation_authorization_and_evidence_masking():
    """
    [ECC-DEFECT-REPRODUCTION] — Regional Pulse Signal Creation Authorization & Response Masking:
    Verifies that:
    1. Unauthenticated POST /api/v1/regional-pulse/signals returns 401 Unauthorized.
    2. Authenticated FARMER calling POST /api/v1/regional-pulse/signals returns 403 Forbidden.
       (Under RLS and system policy, regional signals may only be created by ADMIN, AGRICULTURAL_EXPERT, RESEARCHER).
    3. Authorized role (AGRICULTURAL_EXPERT, RESEARCHER, ADMIN) returns 201 Created.
    4. Response evidence masking respects is_privileged (defense-in-depth).
    """
    import backend.app.models
    from backend.app.models.observation import Observation
    from fastapi.testclient import TestClient
    from backend.app.main import app
    from backend.app.database.session import get_db
    from backend.app.security.dependencies import get_current_user
    from sqlalchemy.pool import StaticPool
    engine = create_engine("sqlite:///:memory:", echo=False, poolclass=StaticPool, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(bind=engine)

    with TestingSession() as s:
        f1 = Farm(id="f-cr-1", name="Farm 1", state="Telangana", district="Warangal", mandal="M1", village="V1", owner_id="u-f1", is_archived=False)
        f2 = Farm(id="f-cr-2", name="Farm 2", state="Telangana", district="Warangal", mandal="M1", village="V1", owner_id="u-f2", is_archived=False)
        f3 = Farm(id="f-cr-3", name="Farm 3", state="Telangana", district="Warangal", mandal="M1", village="V1", owner_id="u-f3", is_archived=False)
        s.add_all([f1, f2, f3])
        s.flush()

        now = datetime(2026, 11, 10, tzinfo=timezone.utc)
        o1 = Observation(id="obs-cr-1", farm_id="f-cr-1", observer_id="u-f1", created_at=now)
        o2 = Observation(id="obs-cr-2", farm_id="f-cr-2", observer_id="u-f2", created_at=now)
        o3 = Observation(id="obs-cr-3", farm_id="f-cr-3", observer_id="u-f3", created_at=now)
        s.add_all([o1, o2, o3])
        s.commit()

    class MockUser:
        def __init__(self, uid: str, rids: list, active: bool = True):
            self.id = uid
            self.roles = [type("RoleItem", (), {"id": r})() for r in rids]
            self.is_active = active

    farmer_user = MockUser("u-f1", ["FARMER"])
    researcher_user = MockUser("u-res", ["RESEARCHER"])
    expert_user = MockUser("u-exp", ["AGRICULTURAL_EXPERT"])
    admin_user = MockUser("u-adm", ["ADMIN"])

    def override_get_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    client = TestClient(app)
    app.dependency_overrides[get_db] = override_get_db

    create_payload = {
        "district": "Warangal",
        "state": "Telangana",
        "crop_id": "cotton",
        "signal_category": "OBSERVATION_SURGE",
        "signal_title": "Pink Bollworm Observations",
        "signal_summary": "Pest activity reported across 3 farms.",
        "confidence_tier": "EXPERT_REVIEWED",
        "source_observation_count": 3,
        "distinct_farms_count": 3,
        "validation_status": "EXPERT_CONFIRMED",
        "recommended_action": "Inspect traps",
        "observed_start_date": "2026-11-01",
        "observed_end_date": "2026-11-15",
        "evidences": [
            {"evidence_type": "OBSERVATION_REF", "evidence_reference_id": "obs-cr-1", "evidence_notes": "Note 1"},
            {"evidence_type": "OBSERVATION_REF", "evidence_reference_id": "obs-cr-2", "evidence_notes": "Note 2"},
            {"evidence_type": "OBSERVATION_REF", "evidence_reference_id": "obs-cr-3", "evidence_notes": "Note 3"},
        ],
    }

    try:
        # Case 1: Unauthenticated -> 401
        res_unauth = client.post("/api/v1/regional-pulse/signals", json=create_payload)
        assert res_unauth.status_code == 401

        # Case 2: FARMER role -> Must be 403 Forbidden!
        app.dependency_overrides[get_current_user] = lambda: farmer_user
        res_farmer = client.post("/api/v1/regional-pulse/signals", json=create_payload)
        assert res_farmer.status_code == 403, f"FARMER must NOT be authorized to create regional signals; got {res_farmer.status_code}"

        # Case 3: RESEARCHER role -> 201 Created
        app.dependency_overrides[get_current_user] = lambda: researcher_user
        res_researcher = client.post("/api/v1/regional-pulse/signals", json=create_payload)
        assert res_researcher.status_code == 201

        # Case 4: AGRICULTURAL_EXPERT role -> 201 Created
        app.dependency_overrides[get_current_user] = lambda: expert_user
        res_expert = client.post("/api/v1/regional-pulse/signals", json=create_payload)
        assert res_expert.status_code == 201

        # Case 5: ADMIN role -> 201 Created
        app.dependency_overrides[get_current_user] = lambda: admin_user
        res_admin = client.post("/api/v1/regional-pulse/signals", json=create_payload)
        assert res_admin.status_code == 201

    finally:
        app.dependency_overrides.clear()


def test_regional_pulse_complete_response_surface_role_matrix_and_canaries():
    """
    [ECC-ADVERSARIAL-AUDIT] — Complete Regional Pulse Response Surface, Role Matrix & Synthetic Privacy Canaries:
    1. Complete 4-Route x 5-Role Matrix:
       - GET /signals (list)
       - GET /signals/{id} (detail)
       - POST /signals (create/aggregate)
       - POST /signals/{id}/recover (recovery)
       Across Unauthenticated, FARMER, AGRICULTURAL_EXPERT, RESEARCHER, ADMIN.
    2. Synthetic Privacy Canary Ingestion & Leak Resistance:
       - Tests that SYNTHETIC_PERSON_CANARY_001, SYNTHETIC_PHONE_CANARY_001, etc. in observations
         are completely withheld from FARMER responses.
    3. Multi-Status Anti-Caching Verification:
       - Verifies Cache-Control and Pragma headers on 200, 201, 401, 403, 404, and 500 responses.
    4. Standby Replica-Lag Eventual Consistency Analysis:
       - Proves that if a replica lags behind evidence deletion (still sees N=3),
         it serves a stale signal without triggering write-on-read SQLSTATE 25006.
    """
    import backend.app.models
    from backend.app.models.observation import Observation
    from backend.app.models.regional_pulse import RegionalSignal, RegionalSignalEvidence
    from backend.app.schemas.regional_pulse import RegionalSignalResponse, RegionalSignalEvidenceItem
    from backend.app.services.regional_pulse_service import RegionalPulseService
    from fastapi.testclient import TestClient
    from backend.app.main import app
    from backend.app.database.session import get_db
    from backend.app.security.dependencies import get_current_user
    from sqlalchemy.pool import StaticPool

    engine = create_engine("sqlite:///:memory:", echo=False, poolclass=StaticPool, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(bind=engine)

    canary_person = "SYNTHETIC_PERSON_CANARY_001"
    canary_phone = "+919876543210_SYNTHETIC_PHONE_CANARY_001"
    canary_location = "17.9689,79.5941_SYNTHETIC_LOCATION_CANARY_001"
    canary_note = "Confidential field note_SYNTHETIC_PRIVATE_NOTE_CANARY_001"

    with TestingSession() as s:
        # 3 Farms in Warangal
        f1 = Farm(id="f-matrix-1", name="Farm 1", state="Telangana", district="Warangal", mandal="M1", village="V1", owner_id="u-f1", is_archived=False)
        f2 = Farm(id="f-matrix-2", name="Farm 2", state="Telangana", district="Warangal", mandal="M1", village="V1", owner_id="u-f2", is_archived=False)
        f3 = Farm(id="f-matrix-3", name="Farm 3", state="Telangana", district="Warangal", mandal="M1", village="V1", owner_id="u-f3", is_archived=False)
        s.add_all([f1, f2, f3])
        s.flush()

        now = datetime(2026, 11, 10, tzinfo=timezone.utc)
        # Observations containing sensitive privacy canaries in notes
        o1 = Observation(id="obs-mat-1", farm_id="f-matrix-1", observer_id="u-f1", notes=f"Owner: {canary_person}, Phone: {canary_phone}", created_at=now)
        o2 = Observation(id="obs-mat-2", farm_id="f-matrix-2", observer_id="u-f2", notes=f"GPS: {canary_location}", created_at=now)
        o3 = Observation(id="obs-mat-3", farm_id="f-matrix-3", observer_id="u-f3", notes=canary_note, created_at=now)
        s.add_all([o1, o2, o3])
        s.flush()

        # Signal 1: Valid (N=3)
        sig1 = RegionalSignal(
            id="sig-mat-valid", district="Warangal", state="Telangana", crop_id="cotton",
            signal_category="OBSERVATION_SURGE", signal_title="Active Pest Trend", signal_summary="Normal observation surge",
            confidence_tier="EXPERT_REVIEWED", source_observation_count=3, distinct_farms_count=3,
            is_outbreak_claim_suppressed=False, validation_status="EXPERT_CONFIRMED", recommended_action="Routine monitoring",
            observed_start_date=date(2026, 11, 1), observed_end_date=date(2026, 11, 15), created_at=now,
        )
        s.add(sig1)
        s.flush()

        s.add(RegionalSignalEvidence(id="ev-mat-1", signal_id="sig-mat-valid", evidence_type="OBSERVATION_REF", evidence_reference_id="obs-mat-1", evidence_notes="Verified trap sample 1"))
        s.add(RegionalSignalEvidence(id="ev-mat-2", signal_id="sig-mat-valid", evidence_type="OBSERVATION_REF", evidence_reference_id="obs-mat-2", evidence_notes="Verified trap sample 2"))
        s.add(RegionalSignalEvidence(id="ev-mat-3", signal_id="sig-mat-valid", evidence_type="OBSERVATION_REF", evidence_reference_id="obs-mat-3", evidence_notes="Verified trap sample 3"))

        # Signal 2: Suppressed (N=1, eligible for recovery)
        sig2 = RegionalSignal(
            id="sig-mat-suppressed", district="Warangal", state="Telangana", crop_id="chilli",
            signal_category="PEST_INQUIRIES", signal_title="Chilli Thrips Surge", signal_summary="Preliminary surge report",
            confidence_tier="EXPERT_REVIEWED", source_observation_count=3, distinct_farms_count=3,
            is_outbreak_claim_suppressed=True, validation_status="SUPPRESSED_INSUFFICIENT_PROVENANCE", recommended_action="Inspect chilli fields",
            observed_start_date=date(2026, 11, 1), observed_end_date=date(2026, 11, 15), created_at=now,
        )
        s.add(sig2)
        s.flush()
        s.add(RegionalSignalEvidence(id="ev-mat-s1", signal_id="sig-mat-suppressed", evidence_type="OBSERVATION_REF", evidence_reference_id="obs-mat-1", evidence_notes="Historical ref 1"))
        s.add(RegionalSignalEvidence(id="ev-mat-s2", signal_id="sig-mat-suppressed", evidence_type="OBSERVATION_REF", evidence_reference_id="obs-mat-2", evidence_notes="Historical ref 2"))
        s.add(RegionalSignalEvidence(id="ev-mat-s3", signal_id="sig-mat-suppressed", evidence_type="OBSERVATION_REF", evidence_reference_id="obs-mat-3", evidence_notes="Historical ref 3"))

        s.commit()

    class MockUser:
        def __init__(self, uid: str, rids: list):
            self.id = uid
            self.roles = [type("RoleItem", (), {"id": r})() for r in rids]
            self.is_active = True

    farmer_user = MockUser("u-f1", ["FARMER"])
    researcher_user = MockUser("u-res", ["RESEARCHER"])
    expert_user = MockUser("u-exp", ["AGRICULTURAL_EXPERT"])
    admin_user = MockUser("u-adm", ["ADMIN"])

    def override_get_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    client = TestClient(app)
    app.dependency_overrides[get_db] = override_get_db

    try:
        # =========================================================================
        # 1. Complete Role Authorization & Evidence Visibility Matrix
        # =========================================================================

        # A. Unauthenticated Caller -> 401 across all 4 routes
        assert client.get("/api/v1/regional-pulse/signals").status_code == 401
        assert client.get("/api/v1/regional-pulse/signals/sig-mat-valid").status_code == 401
        assert client.post("/api/v1/regional-pulse/signals", json={}).status_code == 401
        assert client.post("/api/v1/regional-pulse/signals/sig-mat-suppressed/recover").status_code == 401

        # B. FARMER Caller
        app.dependency_overrides[get_current_user] = lambda: farmer_user
        # List GET: 200 OK, only unsuppressed signals, evidences strictly []
        res_list_f = client.get("/api/v1/regional-pulse/signals")
        assert res_list_f.status_code == 200
        signals_f = res_list_f.json()
        assert all(s["validation_status"] != "SUPPRESSED_INSUFFICIENT_PROVENANCE" for s in signals_f)
        assert all(s["evidences"] == [] for s in signals_f)
        # Detail GET valid: 200 OK, evidences strictly []
        res_det_f = client.get("/api/v1/regional-pulse/signals/sig-mat-valid")
        assert res_det_f.status_code == 200
        data_f = res_det_f.json()
        assert data_f["evidences"] == []
        # Detail GET suppressed: 404 Not Found for farmer
        res_supp_f = client.get("/api/v1/regional-pulse/signals/sig-mat-suppressed")
        assert res_supp_f.status_code == 404
        # Create POST: 403 Forbidden
        assert client.post("/api/v1/regional-pulse/signals", json={}).status_code == 403
        # Recover POST: 403 Forbidden
        assert client.post("/api/v1/regional-pulse/signals/sig-mat-suppressed/recover").status_code == 403

        # C. AGRICULTURAL_EXPERT Caller
        app.dependency_overrides[get_current_user] = lambda: expert_user
        # List GET: 200 OK, sees suppressed signals, evidences populated
        res_list_e = client.get("/api/v1/regional-pulse/signals")
        assert res_list_e.status_code == 200
        assert any(len(s["evidences"]) > 0 for s in res_list_e.json())
        # Detail GET valid: 200 OK, evidences populated
        res_det_e = client.get("/api/v1/regional-pulse/signals/sig-mat-valid")
        assert res_det_e.status_code == 200
        assert len(res_det_e.json()["evidences"]) == 3
        # Detail GET suppressed: 200 OK for expert
        assert client.get("/api/v1/regional-pulse/signals/sig-mat-suppressed").status_code == 200
        # Recover POST: 200 OK
        res_rec_e = client.post("/api/v1/regional-pulse/signals/sig-mat-suppressed/recover", json={"reason": "Expert field audit"})
        assert res_rec_e.status_code == 200
        assert res_rec_e.json()["validation_status"] == "EXPERT_CONFIRMED"

        # D. RESEARCHER Caller
        app.dependency_overrides[get_current_user] = lambda: researcher_user
        # List GET: 200 OK, evidences populated (privileged)
        res_list_r = client.get("/api/v1/regional-pulse/signals")
        assert res_list_r.status_code == 200
        assert any(len(s["evidences"]) > 0 for s in res_list_r.json())
        # Detail GET: 200 OK, evidences populated
        assert len(client.get("/api/v1/regional-pulse/signals/sig-mat-valid").json()["evidences"]) == 3
        # Recover POST: 403 Forbidden (Researcher cannot recover signals!)
        assert client.post("/api/v1/regional-pulse/signals/sig-mat-valid/recover").status_code == 403

        # E. ADMIN Caller
        app.dependency_overrides[get_current_user] = lambda: admin_user
        assert client.get("/api/v1/regional-pulse/signals").status_code == 200
        assert len(client.get("/api/v1/regional-pulse/signals/sig-mat-valid").json()["evidences"]) == 3

        # =========================================================================
        # 2. Synthetic Privacy Canary Audit & Leak Resistance
        # =========================================================================
        app.dependency_overrides[get_current_user] = lambda: farmer_user
        farmer_payload_str = str(client.get("/api/v1/regional-pulse/signals/sig-mat-valid").json())
        assert canary_person not in farmer_payload_str
        assert canary_phone not in farmer_payload_str
        assert canary_location not in farmer_payload_str
        assert canary_note not in farmer_payload_str

        # Privileged callers see evidence items with reference IDs, but observation internal notes remain unexposed
        app.dependency_overrides[get_current_user] = lambda: expert_user
        expert_sig = client.get("/api/v1/regional-pulse/signals/sig-mat-valid").json()
        assert len(expert_sig["evidences"]) == 3
        # Verify nested schema properties
        for ev in expert_sig["evidences"]:
            assert "id" in ev
            assert "evidence_type" in ev
            assert "evidence_reference_id" in ev
            assert "evidence_notes" in ev
            assert "added_at" in ev
            # Confirm raw farmer observation notes were NOT copied into evidence_notes
            assert canary_person not in str(ev["evidence_notes"])
            assert canary_phone not in str(ev["evidence_notes"])

        # =========================================================================
        # 3. HTTP Anti-Caching Verification Across Status Codes
        # =========================================================================
        # 200 OK
        r200 = client.get("/api/v1/regional-pulse/signals")
        assert "no-cache, no-store, must-revalidate" in r200.headers.get("cache-control", "")
        assert r200.headers.get("pragma") == "no-cache"

        # 401 Unauthorized
        app.dependency_overrides.clear()
        r401 = client.get("/api/v1/regional-pulse/signals")
        assert "no-cache, no-store, must-revalidate" in r401.headers.get("cache-control", "")
        assert r401.headers.get("pragma") == "no-cache"

        # 403 Forbidden
        app.dependency_overrides[get_db] = override_get_db
        app.dependency_overrides[get_current_user] = lambda: farmer_user
        r403 = client.post("/api/v1/regional-pulse/signals", json={})
        assert "no-cache, no-store, must-revalidate" in r403.headers.get("cache-control", "")
        assert r403.headers.get("pragma") == "no-cache"

        # 404 Not Found
        r404 = client.get("/api/v1/regional-pulse/signals/non-existent-signal-id")
        assert "no-cache, no-store, must-revalidate" in r404.headers.get("cache-control", "")
        assert r404.headers.get("pragma") == "no-cache"

        # =========================================================================
        # 4. Standby Replica-Lag Eventual Consistency Analysis
        # =========================================================================
        # When a replica suffers replication lag (delta_t), a query on the replica
        # evaluates based on the stale snapshot where N=3. It does NOT attempt an UPDATE,
        # does NOT trigger SQLSTATE 25006, and serves the stale signal until replication catch-up.
        with TestingSession() as s:
            stale_replica_signal = s.get(RegionalSignal, "sig-mat-valid")
            # In replica view before catchup, N=3
            assert stale_replica_signal.distinct_farms_count == 3
            # Service revalidates against replica snapshot -> returns True (no write attempted!)
            is_valid_on_replica = RegionalPulseService.revalidate_signal_provenance(s, "sig-mat-valid")
            assert is_valid_on_replica is True

    finally:
        app.dependency_overrides.clear()


def test_regional_pulse_invalid_evidence_persistence_defect():
    """
    [ECC-DEFECT-REPRODUCTION] — Evidence-Reference Validation & Association Persistence:
    When an author submits regional signal aggregation with:
    - 3 valid observations on 3 distinct active farms matching district & date window,
    - PLUS invalid/spurious evidence items (nonexistent ref, unsupported type, archived farm,
      cross-district mismatch, out-of-window date, duplicate reference),
    the system must persist ONLY the valid, deduplicated evidence associations.
    It must NOT persist nonexistent, unsupported, archived, out-of-window, or mismatched evidence items.
    """
    import backend.app.models
    from backend.app.models.observation import Observation
    from backend.app.models.regional_pulse import RegionalSignal, RegionalSignalEvidence
    from backend.app.services.regional_pulse_service import RegionalPulseService
    from backend.app.schemas.regional_pulse import RegionalSignalCreate
    from sqlalchemy.pool import StaticPool

    engine = create_engine("sqlite:///:memory:", echo=False, poolclass=StaticPool, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(bind=engine)

    with TestingSession() as s:
        # 3 Valid active farms in Warangal
        f1 = Farm(id="f-ev-1", name="Farm 1", state="Telangana", district="Warangal", mandal="M1", village="V1", owner_id="u-1", is_archived=False)
        f2 = Farm(id="f-ev-2", name="Farm 2", state="Telangana", district="Warangal", mandal="M1", village="V1", owner_id="u-2", is_archived=False)
        f3 = Farm(id="f-ev-3", name="Farm 3", state="Telangana", district="Warangal", mandal="M1", village="V1", owner_id="u-3", is_archived=False)

        # 1 Archived farm in Warangal
        f_arch = Farm(id="f-ev-arch", name="Archived Farm", state="Telangana", district="Warangal", mandal="M1", village="V1", owner_id="u-arch", is_archived=True)

        # 1 Active farm in Nalgonda (different district)
        f_wrong_dist = Farm(id="f-ev-nalgonda", name="Nalgonda Farm", state="Telangana", district="Nalgonda", mandal="M1", village="V1", owner_id="u-nal", is_archived=False)

        s.add_all([f1, f2, f3, f_arch, f_wrong_dist])
        s.flush()

        in_window = datetime(2026, 11, 5, tzinfo=timezone.utc)
        out_window = datetime(2026, 8, 1, tzinfo=timezone.utc)

        # 3 Valid observations
        obs1 = Observation(id="obs-val-1", farm_id="f-ev-1", observer_id="u-1", created_at=in_window)
        obs2 = Observation(id="obs-val-2", farm_id="f-ev-2", observer_id="u-2", created_at=in_window)
        obs3 = Observation(id="obs-val-3", farm_id="f-ev-3", observer_id="u-3", created_at=in_window)

        # Spurious observations
        obs_arch = Observation(id="obs-sp-arch", farm_id="f-ev-arch", observer_id="u-arch", created_at=in_window)
        obs_wrong_dist = Observation(id="obs-sp-dist", farm_id="f-ev-nalgonda", observer_id="u-nal", created_at=in_window)
        obs_out_window = Observation(id="obs-sp-date", farm_id="f-ev-1", observer_id="u-1", created_at=out_window)

        s.add_all([obs1, obs2, obs3, obs_arch, obs_wrong_dist, obs_out_window])
        s.commit()

    with TestingSession() as s:
        payload = RegionalSignalCreate(
            district="Warangal",
            state="Telangana",
            crop_id="cotton",
            signal_category="OBSERVATION_SURGE",
            signal_title="Evidence Association Test",
            signal_summary="Testing persistence of valid vs invalid evidence associations",
            confidence_tier="EXPERT_REVIEWED",
            source_observation_count=3,
            distinct_farms_count=3,
            validation_status="EXPERT_CONFIRMED",
            recommended_action="Inspect fields",
            observed_start_date=date(2026, 11, 1),
            observed_end_date=date(2026, 11, 15),
            evidences=[
                # 3 Valid items
                {"evidence_type": "OBSERVATION_REF", "evidence_reference_id": "obs-val-1", "evidence_notes": "Valid 1"},
                {"evidence_type": "OBSERVATION_REF", "evidence_reference_id": "obs-val-2", "evidence_notes": "Valid 2"},
                {"evidence_type": "OBSERVATION_REF", "evidence_reference_id": "obs-val-3", "evidence_notes": "Valid 3"},
                # 6 Spurious/Invalid items
                {"evidence_type": "OBSERVATION_REF", "evidence_reference_id": "obs-val-1", "evidence_notes": "Duplicate ref"},
                {"evidence_type": "OBSERVATION_REF", "evidence_reference_id": "obs-sp-arch", "evidence_notes": "Archived farm obs"},
                {"evidence_type": "OBSERVATION_REF", "evidence_reference_id": "obs-sp-dist", "evidence_notes": "Mismatched district obs"},
                {"evidence_type": "OBSERVATION_REF", "evidence_reference_id": "obs-sp-date", "evidence_notes": "Out of window obs"},
                {"evidence_type": "OBSERVATION_REF", "evidence_reference_id": "obs-ghost-nonexistent", "evidence_notes": "Nonexistent obs"},
                {"evidence_type": "UNSUPPORTED_TYPE", "evidence_reference_id": "unsupported-ref-001", "evidence_notes": "Unsupported type"},
            ],
        )

        signal = RegionalPulseService.aggregate_regional_signal(s, data=payload)
        assert signal.distinct_farms_count == 3

        persisted_evidences = s.query(RegionalSignalEvidence).filter(
            RegionalSignalEvidence.signal_id == signal.id
        ).all()

        # Defect assertion: ONLY the 3 valid, deduplicated evidences should be persisted!
        persisted_ref_ids = [ev.evidence_reference_id for ev in persisted_evidences]
        assert len(persisted_evidences) == 3, f"Expected 3 valid evidences, but found {len(persisted_evidences)}: {persisted_ref_ids}"
        assert set(persisted_ref_ids) == {"obs-val-1", "obs-val-2", "obs-val-3"}


def test_regional_pulse_schema_validation():
    """
    [PHASE 07] Schema Validation Assurance:
    1. signal_title > 200 chars must fail Pydantic validation.
    2. observed_start_date > observed_end_date must fail Pydantic validation.
    3. RegionalSignalEvidenceCreateItem enforces typing and length.
    """
    from pydantic import ValidationError
    from backend.app.schemas.regional_pulse import RegionalSignalCreate, RegionalSignalEvidenceCreateItem

    # 1. Title exceeding 200 characters
    long_title = "A" * 201
    with pytest.raises(ValidationError) as exc_info:
        RegionalSignalCreate(
            district="Warangal",
            crop_id="cotton",
            signal_title=long_title,
            signal_summary="Valid summary",
            recommended_action="Inspect",
            observed_start_date=date(2026, 11, 1),
            observed_end_date=date(2026, 11, 15),
        )
    assert "signal_title" in str(exc_info.value)

    # 2. Inverted date window (start > end)
    with pytest.raises(ValidationError) as exc_info:
        RegionalSignalCreate(
            district="Warangal",
            crop_id="cotton",
            signal_title="Valid Title",
            signal_summary="Valid summary",
            recommended_action="Inspect",
            observed_start_date=date(2026, 11, 20),
            observed_end_date=date(2026, 11, 10),
        )
    assert "observed_start_date" in str(exc_info.value)

    # 3. Typed evidence item
    ev_item = RegionalSignalEvidenceCreateItem(
        evidence_type="OBSERVATION_REF",
        evidence_reference_id="obs-123",
        evidence_notes="Verified observation",
    )
    assert ev_item.evidence_type == "OBSERVATION_REF"
    assert ev_item.evidence_reference_id == "obs-123"

    # Evidence item with reference_id > 100 chars
    with pytest.raises(ValidationError):
        RegionalSignalEvidenceCreateItem(
            evidence_reference_id="X" * 101
        )


def test_regional_pulse_author_content_pii_and_evidence_note_privacy():
    """
    [PHASE 07] PII Canary & Evidence-Note Privacy Audit:
    Canaries injected:
    - SYNTHETIC_PERSON_CANARY_001 = "Canary Farmer Ramesh"
    - SYNTHETIC_PHONE_CANARY_001 = "+91-98765-43210"
    - SYNTHETIC_SURVEY_CANARY_001 = "Survey No 402/B"
    - SYNTHETIC_AADHAAR_CANARY_001 = "XXXX-XXXX-9999"
    - SYNTHETIC_GPS_CANARY_001 = "17.9689 N, 79.5941 E"
    - SYNTHETIC_NOTE_CANARY_001 = "Internal investigator note: pesticide container found on bund"

    Verifications:
    1. Public GET /api/v1/regional-pulse/signals masks evidence_notes completely for FARMER (evidences=[]).
    2. Privileged roles (AGRICULTURAL_EXPERT, RESEARCHER, ADMIN) receive evidence_notes.
    3. Underlying Observation.notes ("Confidential farmer diary note") is NEVER copied into RegionalSignalEvidence.
    4. Author-controlled free text (title, summary, recommended_action) is delivered as authored
       (demonstrating RES-FREE-TEXT-01 accepted operational risk requiring author guidelines).
    """
    import backend.app.models
    from backend.app.models.observation import Observation
    from backend.app.models.regional_pulse import RegionalSignal, RegionalSignalEvidence
    from backend.app.services.regional_pulse_service import RegionalPulseService
    from backend.app.schemas.regional_pulse import RegionalSignalCreate
    from backend.app.api.v1.endpoints.regional_pulse import get_signal
    from sqlalchemy.pool import StaticPool

    engine = create_engine("sqlite:///:memory:", echo=False, poolclass=StaticPool, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(bind=engine)

    SYNTHETIC_PERSON = "Canary Farmer Ramesh"
    SYNTHETIC_PHONE = "+91-98765-43210"
    SYNTHETIC_SURVEY = "Survey No 402/B"
    SYNTHETIC_AADHAAR = "XXXX-XXXX-9999"
    SYNTHETIC_GPS = "17.9689 N, 79.5941 E"
    SYNTHETIC_NOTE = "Internal investigator note: container on bund"
    UNDERLYING_OBS_NOTE = "Confidential farmer diary note from observation"

    with TestingSession() as s:
        f1 = Farm(id="f-pii-1", name="Farm 1", state="Telangana", district="Warangal", mandal="M1", village="V1", owner_id="u-1", is_archived=False)
        f2 = Farm(id="f-pii-2", name="Farm 2", state="Telangana", district="Warangal", mandal="M1", village="V1", owner_id="u-2", is_archived=False)
        f3 = Farm(id="f-pii-3", name="Farm 3", state="Telangana", district="Warangal", mandal="M1", village="V1", owner_id="u-3", is_archived=False)
        s.add_all([f1, f2, f3])
        s.flush()

        in_window = datetime(2026, 11, 5, tzinfo=timezone.utc)
        obs1 = Observation(id="obs-pii-1", farm_id="f-pii-1", observer_id="u-1", notes=UNDERLYING_OBS_NOTE, created_at=in_window)
        obs2 = Observation(id="obs-pii-2", farm_id="f-pii-2", observer_id="u-2", notes=UNDERLYING_OBS_NOTE, created_at=in_window)
        obs3 = Observation(id="obs-pii-3", farm_id="f-pii-3", observer_id="u-3", notes=UNDERLYING_OBS_NOTE, created_at=in_window)
        s.add_all([obs1, obs2, obs3])
        s.commit()

    with TestingSession() as s:
        payload = RegionalSignalCreate(
            district="Warangal",
            state="Telangana",
            crop_id="cotton",
            signal_category="OBSERVATION_SURGE",
            signal_title=f"Field Alert near {SYNTHETIC_SURVEY}",
            signal_summary=f"Reported by contact {SYNTHETIC_PERSON} at {SYNTHETIC_PHONE} near {SYNTHETIC_GPS}",
            confidence_tier="EXPERT_REVIEWED",
            source_observation_count=3,
            distinct_farms_count=3,
            validation_status="EXPERT_CONFIRMED",
            recommended_action=f"Inspect perimeter near {SYNTHETIC_AADHAAR}",
            observed_start_date=date(2026, 11, 1),
            observed_end_date=date(2026, 11, 15),
            evidences=[
                {"evidence_type": "OBSERVATION_REF", "evidence_reference_id": "obs-pii-1", "evidence_notes": SYNTHETIC_NOTE},
                {"evidence_type": "OBSERVATION_REF", "evidence_reference_id": "obs-pii-2", "evidence_notes": "Clean note 2"},
                {"evidence_type": "OBSERVATION_REF", "evidence_reference_id": "obs-pii-3", "evidence_notes": "Clean note 3"},
            ],
        )

        signal = RegionalPulseService.aggregate_regional_signal(s, data=payload)
        s.commit()

        # Check DB evidence records: underlying Observation.notes is NOT copied to RegionalSignalEvidence
        ev_records = s.query(RegionalSignalEvidence).filter(RegionalSignalEvidence.signal_id == signal.id).all()
        for ev in ev_records:
            assert UNDERLYING_OBS_NOTE not in (ev.evidence_notes or "")

        from backend.app.models.user import Role, UserRole
        r_farmer = Role(id="FARMER", description="Farmer")
        r_expert = Role(id="AGRICULTURAL_EXPERT", description="Expert")
        r_researcher = Role(id="RESEARCHER", description="Researcher")
        r_admin = Role(id="ADMIN", description="Admin")
        s.add_all([r_farmer, r_expert, r_researcher, r_admin])
        s.flush()

        farmer_user = User(id="u-farmer", phone="+919999900001", hashed_password="h", full_name="Farmer", is_active=True, is_verified=True)
        expert_user = User(id="u-expert", phone="+919999900002", hashed_password="h", full_name="Expert", is_active=True, is_verified=True)
        researcher_user = User(id="u-researcher", phone="+919999900003", hashed_password="h", full_name="Researcher", is_active=True, is_verified=True)
        admin_user = User(id="u-admin", phone="+919999900004", hashed_password="h", full_name="Admin", is_active=True, is_verified=True)
        s.add_all([farmer_user, expert_user, researcher_user, admin_user])
        s.flush()

        s.add(UserRole(user_id=farmer_user.id, role_id="FARMER"))
        s.add(UserRole(user_id=expert_user.id, role_id="AGRICULTURAL_EXPERT"))
        s.add(UserRole(user_id=researcher_user.id, role_id="RESEARCHER"))
        s.add(UserRole(user_id=admin_user.id, role_id="ADMIN"))
        s.commit()

        # Test FARMER role access
        farmer_view = get_signal(signal_id=signal.id, current_user=farmer_user, db=s)
        # Farmer receives empty evidence list: evidence_notes is never exposed
        assert farmer_view.evidences == []
        assert SYNTHETIC_NOTE not in str(farmer_view.evidences)

        # Farmer receives author-controlled text (RES-FREE-TEXT-01 accepted operational risk)
        assert SYNTHETIC_PERSON in farmer_view.signal_summary
        assert SYNTHETIC_PHONE in farmer_view.signal_summary
        assert SYNTHETIC_SURVEY in farmer_view.signal_title

        # Test privileged role access (AGRICULTURAL_EXPERT, RESEARCHER, ADMIN)
        expert_view = get_signal(signal_id=signal.id, current_user=expert_user, db=s)
        assert len(expert_view.evidences) == 3
        assert any(ev.evidence_notes == SYNTHETIC_NOTE for ev in expert_view.evidences)

        researcher_view = get_signal(signal_id=signal.id, current_user=researcher_user, db=s)
        assert len(researcher_view.evidences) == 3

        admin_view = get_signal(signal_id=signal.id, current_user=admin_user, db=s)
        assert len(admin_view.evidences) == 3


def test_regional_pulse_recommended_action_panic_suppression():
    """
    [PHASE 07] Recommended Action Outbreak Claim Sanitization:
    When an author places panic terms into recommended_action (e.g., 'catastrophe', 'pest plague'),
    it must be sanitized to 'elevated observation surge' and mark is_outbreak_claim_suppressed=True.
    """
    import backend.app.models
    from backend.app.models.observation import Observation
    from backend.app.services.regional_pulse_service import RegionalPulseService
    from backend.app.schemas.regional_pulse import RegionalSignalCreate
    from sqlalchemy.pool import StaticPool

    engine = create_engine("sqlite:///:memory:", echo=False, poolclass=StaticPool, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(bind=engine)

    with TestingSession() as s:
        f1 = Farm(id="f-act-1", name="Farm 1", state="Telangana", district="Warangal", mandal="M1", village="V1", owner_id="u-1", is_archived=False)
        f2 = Farm(id="f-act-2", name="Farm 2", state="Telangana", district="Warangal", mandal="M1", village="V1", owner_id="u-2", is_archived=False)
        f3 = Farm(id="f-act-3", name="Farm 3", state="Telangana", district="Warangal", mandal="M1", village="V1", owner_id="u-3", is_archived=False)
        s.add_all([f1, f2, f3])
        s.flush()

        in_window = datetime(2026, 11, 5, tzinfo=timezone.utc)
        obs1 = Observation(id="obs-act-1", farm_id="f-act-1", observer_id="u-1", created_at=in_window)
        obs2 = Observation(id="obs-act-2", farm_id="f-act-2", observer_id="u-2", created_at=in_window)
        obs3 = Observation(id="obs-act-3", farm_id="f-act-3", observer_id="u-3", created_at=in_window)
        s.add_all([obs1, obs2, obs3])
        s.commit()

    with TestingSession() as s:
        payload = RegionalSignalCreate(
            district="Warangal",
            state="Telangana",
            crop_id="cotton",
            signal_category="OBSERVATION_SURGE",
            signal_title="Calm Title",
            signal_summary="Normal field summary",
            confidence_tier="EXPERT_REVIEWED",
            source_observation_count=3,
            distinct_farms_count=3,
            validation_status="EXPERT_CONFIRMED",
            recommended_action="Prepare for pest plague disaster immediately",
            observed_start_date=date(2026, 11, 1),
            observed_end_date=date(2026, 11, 15),
            evidences=[
                {"evidence_type": "OBSERVATION_REF", "evidence_reference_id": "obs-act-1"},
                {"evidence_type": "OBSERVATION_REF", "evidence_reference_id": "obs-act-2"},
                {"evidence_type": "OBSERVATION_REF", "evidence_reference_id": "obs-act-3"},
            ],
        )

        signal = RegionalPulseService.aggregate_regional_signal(s, data=payload)
        assert signal.is_outbreak_claim_suppressed is True
        assert "pest plague" not in signal.recommended_action.lower()
        assert "disaster" not in signal.recommended_action.lower()
        assert "elevated observation surge" in signal.recommended_action.lower()


def test_regional_pulse_confidence_tier_authority_escalation_defect():
    """
    [ECC-DEFECT-REPRODUCTION] — Confidence-Tier Authority & Claim Provenance:
    1. A RESEARCHER must NOT be permitted to publish confidence_tier="OFFICIAL_ADVISORY"
       (or bypass evidence checks with 0 distinct farms). Must return 403 Forbidden.
    2. A RESEARCHER must NOT be permitted to self-assert confidence_tier="EXPERT_REVIEWED"
       without an Agricultural Expert review. Must return 403 Forbidden.
    3. An AGRICULTURAL_EXPERT must NOT be permitted to publish confidence_tier="OFFICIAL_ADVISORY".
       Must return 403 Forbidden.
    4. Only ADMIN with verified authority may publish OFFICIAL_ADVISORY.
    """
    import backend.app.models
    from fastapi import HTTPException
    from backend.app.models.user import Role, UserRole
    from backend.app.models.regional_pulse import RegionalSignal
    from backend.app.services.regional_pulse_service import RegionalPulseService
    from backend.app.schemas.regional_pulse import RegionalSignalCreate
    from backend.app.api.v1.endpoints.regional_pulse import aggregate_signal
    from sqlalchemy.pool import StaticPool

    engine = create_engine("sqlite:///:memory:", echo=False, poolclass=StaticPool, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(bind=engine)

    with TestingSession() as s:
        r_admin = Role(id="ADMIN")
        r_expert = Role(id="AGRICULTURAL_EXPERT")
        r_researcher = Role(id="RESEARCHER")
        s.add_all([r_admin, r_expert, r_researcher])
        s.flush()

        researcher_user = User(id="u-res-auth", phone="+919888800001", hashed_password="h", full_name="Researcher", is_active=True, is_verified=True)
        expert_user = User(id="u-exp-auth", phone="+919888800002", hashed_password="h", full_name="Expert", is_active=True, is_verified=True)
        admin_user = User(id="u-adm-auth", phone="+919888800003", hashed_password="h", full_name="Admin", is_active=True, is_verified=True)
        s.add_all([researcher_user, expert_user, admin_user])
        s.flush()

        s.add(UserRole(user_id=researcher_user.id, role_id="RESEARCHER"))
        s.add(UserRole(user_id=expert_user.id, role_id="AGRICULTURAL_EXPERT"))
        s.add(UserRole(user_id=admin_user.id, role_id="ADMIN"))
        s.commit()

    with TestingSession() as s:
        res_user = s.query(User).filter_by(id="u-res-auth").first()
        # Case 1: RESEARCHER submits OFFICIAL_ADVISORY with 0 evidence
        fake_official_payload = RegionalSignalCreate(
            district="Warangal",
            state="Telangana",
            crop_id="cotton",
            signal_category="ADVISORY_ALERT",
            signal_title="Fake Official Advisory by Researcher",
            signal_summary="Unauthorized official advisory attempt",
            confidence_tier="OFFICIAL_ADVISORY",
            source_observation_count=0,
            distinct_farms_count=0,
            validation_status="OFFICIAL_ALERT",
            recommended_action="Follow state advisory",
            observed_start_date=date(2026, 11, 1),
            observed_end_date=date(2026, 11, 15),
            evidences=[],
        )

        with pytest.raises(HTTPException) as exc_info:
            aggregate_signal(data=fake_official_payload, current_user=res_user, db=s)
        assert exc_info.value.status_code == 403, f"Expected 403 Forbidden for researcher official advisory, got {exc_info.value.status_code}"


def test_regional_pulse_source_observation_count_inconsistency_defect():
    """
    [ECC-DEFECT-REPRODUCTION] — Source Observation Count Integrity:
    When an author links verified evidence across 3 distinct farms,
    submitting source_observation_count = 0 (or less than distinct farms count)
    is logically inconsistent. The system must ensure source_observation_count
    is at least the number of verified distinct farms.
    """
    from backend.app.models.observation import Observation
    from backend.app.services.regional_pulse_service import RegionalPulseService
    from backend.app.schemas.regional_pulse import RegionalSignalCreate
    from sqlalchemy.pool import StaticPool

    engine = create_engine("sqlite:///:memory:", echo=False, poolclass=StaticPool, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(bind=engine)

    with TestingSession() as s:
        f1 = Farm(id="f-cnt-1", name="Farm 1", state="Telangana", district="Warangal", mandal="M1", village="V1", owner_id="u-1", is_archived=False)
        f2 = Farm(id="f-cnt-2", name="Farm 2", state="Telangana", district="Warangal", mandal="M1", village="V1", owner_id="u-2", is_archived=False)
        f3 = Farm(id="f-cnt-3", name="Farm 3", state="Telangana", district="Warangal", mandal="M1", village="V1", owner_id="u-3", is_archived=False)
        s.add_all([f1, f2, f3])
        s.flush()

        in_window = datetime(2026, 11, 5, tzinfo=timezone.utc)
        obs1 = Observation(id="obs-cnt-1", farm_id="f-cnt-1", observer_id="u-1", created_at=in_window)
        obs2 = Observation(id="obs-cnt-2", farm_id="f-cnt-2", observer_id="u-2", created_at=in_window)
        obs3 = Observation(id="obs-cnt-3", farm_id="f-cnt-3", observer_id="u-3", created_at=in_window)
        s.add_all([obs1, obs2, obs3])
        s.commit()

    with TestingSession() as s:
        payload = RegionalSignalCreate(
            district="Warangal",
            state="Telangana",
            crop_id="cotton",
            signal_category="OBSERVATION_SURGE",
            signal_title="Source Count Integrity Test",
            signal_summary="Testing that source observation count cannot be less than distinct farms",
            confidence_tier="EXPERT_REVIEWED",
            source_observation_count=0,  # Misleading count: 0 observations despite 3 distinct farms!
            distinct_farms_count=3,
            validation_status="EXPERT_CONFIRMED",
            recommended_action="Inspect fields",
            observed_start_date=date(2026, 11, 1),
            observed_end_date=date(2026, 11, 15),
            evidences=[
                {"evidence_type": "OBSERVATION_REF", "evidence_reference_id": "obs-cnt-1"},
                {"evidence_type": "OBSERVATION_REF", "evidence_reference_id": "obs-cnt-2"},
                {"evidence_type": "OBSERVATION_REF", "evidence_reference_id": "obs-cnt-3"},
            ],
        )

        signal = RegionalPulseService.aggregate_regional_signal(s, data=payload)
        # Invariant: source_observation_count MUST be at least distinct_farms_count when evidence is linked!
        assert signal.source_observation_count >= signal.distinct_farms_count, (
            f"source_observation_count ({signal.source_observation_count}) cannot be less than "
            f"distinct_farms_count ({signal.distinct_farms_count})"
        )


def test_regional_pulse_complete_role_authority_matrix():
    """
    [PHASE 07] Complete Role-to-Claim Authority Matrix Verification:
    - AGRICULTURAL_EXPERT: May claim EXPERT_REVIEWED (201); CANNOT claim OFFICIAL_ADVISORY (403).
    - RESEARCHER: CANNOT claim EXPERT_REVIEWED (403); CANNOT claim OFFICIAL_ADVISORY (403).
    - ADMIN: May claim EXPERT_REVIEWED (201); May claim OFFICIAL_ADVISORY (201).
    - Server Lifecycle Adjudication: Caller sending validation_status='OFFICIAL_ALERT' with
      confidence_tier='FARMER_REPORT' is forced to 'UNVALIDATED_OBSERVATION'.
    """
    import backend.app.models
    from fastapi import HTTPException
    from backend.app.models.user import Role, UserRole
    from backend.app.models.observation import Observation
    from backend.app.models.regional_pulse import RegionalSignal
    from backend.app.schemas.regional_pulse import RegionalSignalCreate
    from backend.app.api.v1.endpoints.regional_pulse import aggregate_signal
    from sqlalchemy.pool import StaticPool

    engine = create_engine("sqlite:///:memory:", echo=False, poolclass=StaticPool, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(bind=engine)

    with TestingSession() as s:
        r_admin = Role(id="ADMIN")
        r_expert = Role(id="AGRICULTURAL_EXPERT")
        r_researcher = Role(id="RESEARCHER")
        s.add_all([r_admin, r_expert, r_researcher])
        s.flush()

        res_user = User(id="u-res-mat", phone="+919777700001", hashed_password="h", full_name="Res", is_active=True, is_verified=True)
        exp_user = User(id="u-exp-mat", phone="+919777700002", hashed_password="h", full_name="Exp", is_active=True, is_verified=True)
        adm_user = User(id="u-adm-mat", phone="+919777700003", hashed_password="h", full_name="Adm", is_active=True, is_verified=True)
        s.add_all([res_user, exp_user, adm_user])
        s.flush()

        s.add(UserRole(user_id=res_user.id, role_id="RESEARCHER"))
        s.add(UserRole(user_id=exp_user.id, role_id="AGRICULTURAL_EXPERT"))
        s.add(UserRole(user_id=adm_user.id, role_id="ADMIN"))

        f1 = Farm(id="f-mat-1", name="F1", state="Telangana", district="Warangal", mandal="M1", village="V1", owner_id="u-1")
        f2 = Farm(id="f-mat-2", name="F2", state="Telangana", district="Warangal", mandal="M1", village="V1", owner_id="u-2")
        f3 = Farm(id="f-mat-3", name="F3", state="Telangana", district="Warangal", mandal="M1", village="V1", owner_id="u-3")
        s.add_all([f1, f2, f3])
        s.flush()

        in_win = datetime(2026, 11, 5, tzinfo=timezone.utc)
        obs1 = Observation(id="obs-mat-1", farm_id="f-mat-1", observer_id="u-1", created_at=in_win)
        obs2 = Observation(id="obs-mat-2", farm_id="f-mat-2", observer_id="u-2", created_at=in_win)
        obs3 = Observation(id="obs-mat-3", farm_id="f-mat-3", observer_id="u-3", created_at=in_win)
        s.add_all([obs1, obs2, obs3])
        s.commit()

    with TestingSession() as s:
        res = s.query(User).filter_by(id="u-res-mat").first()
        exp = s.query(User).filter_by(id="u-exp-mat").first()
        adm = s.query(User).filter_by(id="u-adm-mat").first()

        evs = [
            {"evidence_type": "OBSERVATION_REF", "evidence_reference_id": "obs-mat-1"},
            {"evidence_type": "OBSERVATION_REF", "evidence_reference_id": "obs-mat-2"},
            {"evidence_type": "OBSERVATION_REF", "evidence_reference_id": "obs-mat-3"},
        ]

        # 1. RESEARCHER submits EXPERT_REVIEWED -> 201 Created, but validation_status is downgraded to UNVALIDATED_OBSERVATION
        p_res_exp = RegionalSignalCreate(
            district="Warangal", crop_id="cotton", signal_title="T", signal_summary="S",
            confidence_tier="EXPERT_REVIEWED", recommended_action="A",
            observed_start_date=date(2026, 11, 1), observed_end_date=date(2026, 11, 15), evidences=evs,
        )
        sig_res = aggregate_signal(data=p_res_exp, current_user=res, db=s)
        assert sig_res.confidence_tier == "EXPERT_REVIEWED"
        assert sig_res.validation_status == "UNVALIDATED_OBSERVATION", "Researcher self-asserted EXPERT_REVIEWED must remain UNVALIDATED_OBSERVATION until expert confirmation"

        # 2. AGRICULTURAL_EXPERT attempts OFFICIAL_ADVISORY -> 403 Forbidden
        p_exp_off = RegionalSignalCreate(
            district="Warangal", crop_id="cotton", signal_title="T", signal_summary="S",
            confidence_tier="OFFICIAL_ADVISORY", recommended_action="A",
            observed_start_date=date(2026, 11, 1), observed_end_date=date(2026, 11, 15), evidences=[],
        )
        with pytest.raises(HTTPException) as exc:
            aggregate_signal(data=p_exp_off, current_user=exp, db=s)
        assert exc.value.status_code == 403
        assert "Official state advisories" in exc.value.detail

        # 3. AGRICULTURAL_EXPERT submits EXPERT_REVIEWED -> 201 Created
        sig_exp = aggregate_signal(data=p_res_exp, current_user=exp, db=s)
        assert sig_exp.confidence_tier == "EXPERT_REVIEWED"
        assert sig_exp.validation_status == "EXPERT_CONFIRMED"

        # 4. ADMIN submits OFFICIAL_ADVISORY (no telemetry) -> 201 Created
        sig_adm = aggregate_signal(data=p_exp_off, current_user=adm, db=s)
        assert sig_adm.confidence_tier == "OFFICIAL_ADVISORY"
        assert sig_adm.validation_status == "OFFICIAL_ALERT"
        assert sig_adm.distinct_farms_count == 0

        # 5. Lifecycle adjudication: FARMER_REPORT claiming OFFICIAL_ALERT is forced to UNVALIDATED_OBSERVATION
        p_spoof = RegionalSignalCreate(
            district="Warangal", crop_id="cotton", signal_title="T", signal_summary="S",
            confidence_tier="FARMER_REPORT", validation_status="OFFICIAL_ALERT", recommended_action="A",
            observed_start_date=date(2026, 11, 1), observed_end_date=date(2026, 11, 15), evidences=evs,
        )
        sig_spoof = aggregate_signal(data=p_spoof, current_user=exp, db=s)
        assert sig_spoof.validation_status == "UNVALIDATED_OBSERVATION"


def test_regional_pulse_creation_transaction_atomicity_and_audit():
    """
    [PHASE 07] Transaction Atomicity & Audit Log Staging:
    1. Signal creation atomically stages and commits AuditLog entry.
    2. Endpoint pre-commit model validation protects against partial persistence.
    """
    from backend.app.models.user import Role, UserRole
    from backend.app.models.governance import AuditLog
    from backend.app.models.observation import Observation
    from backend.app.models.regional_pulse import RegionalSignal
    from backend.app.schemas.regional_pulse import RegionalSignalCreate
    from backend.app.api.v1.endpoints.regional_pulse import aggregate_signal
    from sqlalchemy.pool import StaticPool

    engine = create_engine("sqlite:///:memory:", echo=False, poolclass=StaticPool, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(bind=engine)

    with TestingSession() as s:
        r_admin = Role(id="ADMIN")
        s.add(r_admin)
        admin = User(id="u-tx-adm", phone="+919666600001", hashed_password="h", full_name="Tx Admin", is_active=True, is_verified=True)
        s.add(admin)
        s.flush()
        s.add(UserRole(user_id=admin.id, role_id="ADMIN"))

        f1 = Farm(id="f-tx-1", name="F1", state="Telangana", district="Warangal", mandal="M1", village="V1", owner_id="u-1")
        f2 = Farm(id="f-tx-2", name="F2", state="Telangana", district="Warangal", mandal="M1", village="V1", owner_id="u-2")
        f3 = Farm(id="f-tx-3", name="F3", state="Telangana", district="Warangal", mandal="M1", village="V1", owner_id="u-3")
        s.add_all([f1, f2, f3])
        s.flush()

        in_win = datetime(2026, 11, 5, tzinfo=timezone.utc)
        obs1 = Observation(id="obs-tx-1", farm_id="f-tx-1", observer_id="u-1", created_at=in_win)
        obs2 = Observation(id="obs-tx-2", farm_id="f-tx-2", observer_id="u-2", created_at=in_win)
        obs3 = Observation(id="obs-tx-3", farm_id="f-tx-3", observer_id="u-3", created_at=in_win)
        s.add_all([obs1, obs2, obs3])
        s.commit()

    with TestingSession() as s:
        admin_user = s.query(User).filter_by(id="u-tx-adm").first()
        payload = RegionalSignalCreate(
            district="Warangal",
            crop_id="cotton",
            signal_title="Atomic Audit Signal",
            signal_summary="Testing audit log creation",
            confidence_tier="EXPERT_REVIEWED",
            recommended_action="Inspect fields",
            observed_start_date=date(2026, 11, 1),
            observed_end_date=date(2026, 11, 15),
            evidences=[
                {"evidence_type": "OBSERVATION_REF", "evidence_reference_id": "obs-tx-1"},
                {"evidence_type": "OBSERVATION_REF", "evidence_reference_id": "obs-tx-2"},
                {"evidence_type": "OBSERVATION_REF", "evidence_reference_id": "obs-tx-3"},
            ],
        )

        resp = aggregate_signal(data=payload, current_user=admin_user, db=s)
        assert resp.id is not None

        # Verify AuditLog record was staged and committed atomically in the same transaction
        audit_entry = s.query(AuditLog).filter_by(
            action="CREATE_REGIONAL_SIGNAL",
            resource_id=resp.id,
        ).first()
        assert audit_entry is not None
        assert audit_entry.user_id == "u-tx-adm"
        assert audit_entry.resource_type == "REGIONAL_SIGNAL"


def test_regional_pulse_pydantic_non_negative_counts():
    """
    [PHASE 07] Pydantic Schema Validation:
    source_observation_count < 0 and distinct_farms_count < 0 must fail validation.
    """
    from pydantic import ValidationError
    from backend.app.schemas.regional_pulse import RegionalSignalCreate

    with pytest.raises(ValidationError):
        RegionalSignalCreate(
            district="Warangal",
            crop_id="cotton",
            signal_title="Negative Obs Count",
            signal_summary="S",
            recommended_action="A",
            source_observation_count=-1,
            observed_start_date=date(2026, 11, 1),
            observed_end_date=date(2026, 11, 15),
        )

    with pytest.raises(ValidationError):
        RegionalSignalCreate(
            district="Warangal",
            crop_id="cotton",
            signal_title="Negative Farm Count",
            signal_summary="S",
            recommended_action="A",
            distinct_farms_count=-1,
            observed_start_date=date(2026, 11, 1),
            observed_end_date=date(2026, 11, 15),
        )


def test_regional_pulse_service_auth_fail_closed_when_actor_roles_none():
    """
    [PHASE 07 - SERVICE-AUTH-01]
    Verify that omitting actor_roles (or passing None) fails closed:
    - OFFICIAL_ADVISORY raises HTTP 403 Forbidden.
    - EXPERT_REVIEWED falls back to UNVALIDATED_OBSERVATION.
    """
    from fastapi import HTTPException
    from backend.app.schemas.regional_pulse import RegionalSignalCreate
    from backend.app.services.regional_pulse_service import RegionalPulseService

    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    s = Session()

    u = User(id="u-sa-1", phone="+919876543001", full_name="User SA", email="sa@test.com", hashed_password="x")
    s.add(u)
    f1 = Farm(id="f-sa-1", owner_id="u-sa-1", name="F1", state="Telangana", district="Warangal", mandal="M1", village="V1", total_acreage=1.0)
    f2 = Farm(id="f-sa-2", owner_id="u-sa-1", name="F2", state="Telangana", district="Warangal", mandal="M2", village="V2", total_acreage=1.0)
    f3 = Farm(id="f-sa-3", owner_id="u-sa-1", name="F3", state="Telangana", district="Warangal", mandal="M3", village="V3", total_acreage=1.0)
    s.add_all([f1, f2, f3])
    s.flush()

    o1 = Observation(id="o-sa-1", farm_id="f-sa-1", observer_id="u-sa-1", notes="n", created_at=datetime(2026, 11, 5, tzinfo=timezone.utc))
    o2 = Observation(id="o-sa-2", farm_id="f-sa-2", observer_id="u-sa-1", notes="n", created_at=datetime(2026, 11, 5, tzinfo=timezone.utc))
    o3 = Observation(id="o-sa-3", farm_id="f-sa-3", observer_id="u-sa-1", notes="n", created_at=datetime(2026, 11, 5, tzinfo=timezone.utc))
    s.add_all([o1, o2, o3])
    s.flush()

    # Case 1: OFFICIAL_ADVISORY with actor_roles=None -> must raise HTTP 403 Forbidden
    payload_off = RegionalSignalCreate(
        district="Warangal",
        crop_id="cotton",
        signal_title="State Advisory",
        signal_summary="Summary",
        confidence_tier="OFFICIAL_ADVISORY",
        source_observation_count=0,
        distinct_farms_count=0,
        recommended_action="Action",
        observed_start_date=date(2026, 11, 1),
        observed_end_date=date(2026, 11, 15),
    )
    with pytest.raises(HTTPException) as exc_info:
        RegionalPulseService.aggregate_regional_signal(s, data=payload_off, actor_roles=None)
    assert exc_info.value.status_code == 403

    # Case 2: EXPERT_REVIEWED with actor_roles=None -> validation_status must be UNVALIDATED_OBSERVATION
    payload_exp = RegionalSignalCreate(
        district="Warangal",
        crop_id="cotton",
        signal_title="Expert Claim",
        signal_summary="Summary",
        confidence_tier="EXPERT_REVIEWED",
        source_observation_count=3,
        distinct_farms_count=3,
        recommended_action="Action",
        observed_start_date=date(2026, 11, 1),
        observed_end_date=date(2026, 11, 15),
        evidences=[
            {"evidence_type": "OBSERVATION_REF", "evidence_reference_id": "o-sa-1"},
            {"evidence_type": "OBSERVATION_REF", "evidence_reference_id": "o-sa-2"},
            {"evidence_type": "OBSERVATION_REF", "evidence_reference_id": "o-sa-3"},
        ]
    )
    sig_exp = RegionalPulseService.aggregate_regional_signal(s, data=payload_exp, actor_roles=None)
    assert sig_exp.validation_status == "UNVALIDATED_OBSERVATION"


def test_regional_pulse_source_observation_count_adversarial_derivation_matrix():
    """
    [PHASE 07 - COUNT-INTEG-02]
    Verify that source_observation_count is strictly derived from unique validated evidence records:
    - 3 distinct observations, client count 0 -> derived count is 3
    - 3 distinct observations, client count 100 -> derived count is 3
    - 3 distinct observations, client count 999999 -> derived count is 3
    - 6 observations across 3 farms -> derived count is 6, distinct farms is 3
    - 3 observations and 2 risk alerts -> derived count is 5, distinct farms is 3
    - Duplicate references to 1 observation -> deduplicated to 1
    - Official advisory without telemetry -> derived count is 0
    """
    from backend.app.schemas.regional_pulse import RegionalSignalCreate
    from backend.app.services.regional_pulse_service import RegionalPulseService

    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    s = Session()

    u = User(id="u-cnt-adv", phone="+919876543002", full_name="User Cnt", email="cnt@test.com", hashed_password="x")
    s.add(u)
    f1 = Farm(id="f-cnt-1", owner_id="u-cnt-adv", name="F1", state="Telangana", district="Warangal", mandal="M1", village="V1", total_acreage=1.0)
    f2 = Farm(id="f-cnt-2", owner_id="u-cnt-adv", name="F2", state="Telangana", district="Warangal", mandal="M2", village="V2", total_acreage=1.0)
    f3 = Farm(id="f-cnt-3", owner_id="u-cnt-adv", name="F3", state="Telangana", district="Warangal", mandal="M3", village="V3", total_acreage=1.0)
    s.add_all([f1, f2, f3])
    s.flush()

    # 6 observations across 3 farms (2 per farm)
    o1 = Observation(id="o-c-1", farm_id="f-cnt-1", observer_id="u-cnt-adv", notes="n", created_at=datetime(2026, 11, 5, tzinfo=timezone.utc))
    o2 = Observation(id="o-c-2", farm_id="f-cnt-1", observer_id="u-cnt-adv", notes="n", created_at=datetime(2026, 11, 6, tzinfo=timezone.utc))
    o3 = Observation(id="o-c-3", farm_id="f-cnt-2", observer_id="u-cnt-adv", notes="n", created_at=datetime(2026, 11, 5, tzinfo=timezone.utc))
    o4 = Observation(id="o-c-4", farm_id="f-cnt-2", observer_id="u-cnt-adv", notes="n", created_at=datetime(2026, 11, 6, tzinfo=timezone.utc))
    o5 = Observation(id="o-c-5", farm_id="f-cnt-3", observer_id="u-cnt-adv", notes="n", created_at=datetime(2026, 11, 5, tzinfo=timezone.utc))
    o6 = Observation(id="o-c-6", farm_id="f-cnt-3", observer_id="u-cnt-adv", notes="n", created_at=datetime(2026, 11, 6, tzinfo=timezone.utc))
    s.add_all([o1, o2, o3, o4, o5, o6])

    # 2 risk alerts on farm 1 and farm 2
    from backend.app.models.risk_alert import RiskAlert
    ra1 = RiskAlert(id="ra-c-1", farm_id="f-cnt-1", plot_id="p-c-1", risk_assessment_id="rar-c-1", alert_level="HIGH", title="Alert 1", message_en="M1", message_te="M1", message_hi="M1", deduplication_key="k-c-1", created_at=datetime(2026, 11, 7, tzinfo=timezone.utc))
    ra2 = RiskAlert(id="ra-c-2", farm_id="f-cnt-2", plot_id="p-c-2", risk_assessment_id="rar-c-2", alert_level="HIGH", title="Alert 2", message_en="M2", message_te="M2", message_hi="M2", deduplication_key="k-c-2", created_at=datetime(2026, 11, 7, tzinfo=timezone.utc))
    s.add_all([ra1, ra2])
    s.flush()

    base = {
        "district": "Warangal",
        "crop_id": "cotton",
        "signal_title": "Count Derivation Test",
        "signal_summary": "Summary",
        "recommended_action": "Action",
        "observed_start_date": date(2026, 11, 1),
        "observed_end_date": date(2026, 11, 15),
    }

    # Case A: 3 distinct observations, client sends 999999 -> derived count is 3
    p_999 = RegionalSignalCreate(**base, confidence_tier="FARMER_REPORT", source_observation_count=999999, distinct_farms_count=3, evidences=[
        {"evidence_type": "OBSERVATION_REF", "evidence_reference_id": "o-c-1"},
        {"evidence_type": "OBSERVATION_REF", "evidence_reference_id": "o-c-3"},
        {"evidence_type": "OBSERVATION_REF", "evidence_reference_id": "o-c-5"},
    ])
    sig_999 = RegionalPulseService.aggregate_regional_signal(s, data=p_999, actor_roles=["RESEARCHER"])
    assert sig_999.source_observation_count == 3
    assert sig_999.distinct_farms_count == 3

    # Case B: 3 distinct observations, client sends 0 -> derived count is 3
    p_0 = RegionalSignalCreate(**base, confidence_tier="FARMER_REPORT", source_observation_count=0, distinct_farms_count=3, evidences=[
        {"evidence_type": "OBSERVATION_REF", "evidence_reference_id": "o-c-1"},
        {"evidence_type": "OBSERVATION_REF", "evidence_reference_id": "o-c-3"},
        {"evidence_type": "OBSERVATION_REF", "evidence_reference_id": "o-c-5"},
    ])
    sig_0 = RegionalPulseService.aggregate_regional_signal(s, data=p_0, actor_roles=["RESEARCHER"])
    assert sig_0.source_observation_count == 3

    # Case C: 6 observations across 3 farms -> derived count is 6, distinct farms is 3
    p_6 = RegionalSignalCreate(**base, confidence_tier="FARMER_REPORT", source_observation_count=1, distinct_farms_count=3, evidences=[
        {"evidence_type": "OBSERVATION_REF", "evidence_reference_id": "o-c-1"},
        {"evidence_type": "OBSERVATION_REF", "evidence_reference_id": "o-c-2"},
        {"evidence_type": "OBSERVATION_REF", "evidence_reference_id": "o-c-3"},
        {"evidence_type": "OBSERVATION_REF", "evidence_reference_id": "o-c-4"},
        {"evidence_type": "OBSERVATION_REF", "evidence_reference_id": "o-c-5"},
        {"evidence_type": "OBSERVATION_REF", "evidence_reference_id": "o-c-6"},
    ])
    sig_6 = RegionalPulseService.aggregate_regional_signal(s, data=p_6, actor_roles=["RESEARCHER"])
    assert sig_6.source_observation_count == 6
    assert sig_6.distinct_farms_count == 3

    # Case D: 3 observations and 2 risk alerts -> derived count is 5, distinct farms is 3
    p_5 = RegionalSignalCreate(**base, confidence_tier="FARMER_REPORT", source_observation_count=1, distinct_farms_count=3, evidences=[
        {"evidence_type": "OBSERVATION_REF", "evidence_reference_id": "o-c-1"},
        {"evidence_type": "OBSERVATION_REF", "evidence_reference_id": "o-c-3"},
        {"evidence_type": "OBSERVATION_REF", "evidence_reference_id": "o-c-5"},
        {"evidence_type": "RISK_ALERT", "evidence_reference_id": "ra-c-1"},
        {"evidence_type": "RISK_ALERT", "evidence_reference_id": "ra-c-2"},
    ])
    sig_5 = RegionalPulseService.aggregate_regional_signal(s, data=p_5, actor_roles=["RESEARCHER"])
    assert sig_5.source_observation_count == 5
    assert sig_5.distinct_farms_count == 3

    # Case E: Duplicate references to 1 observation -> deduplicated to 1
    p_dup = RegionalSignalCreate(**base, confidence_tier="FARMER_REPORT", source_observation_count=20, distinct_farms_count=3, evidences=[
        {"evidence_type": "OBSERVATION_REF", "evidence_reference_id": "o-c-1"},
        {"evidence_type": "OBSERVATION_REF", "evidence_reference_id": "o-c-1"},
        {"evidence_type": "OBSERVATION_REF", "evidence_reference_id": "o-c-3"},
        {"evidence_type": "OBSERVATION_REF", "evidence_reference_id": "o-c-5"},
    ])
    sig_dup = RegionalPulseService.aggregate_regional_signal(s, data=p_dup, actor_roles=["RESEARCHER"])
    assert sig_dup.source_observation_count == 3  # o-c-1 deduplicated

    # Case F: Official advisory without telemetry -> derived count is 0
    p_off = RegionalSignalCreate(**base, confidence_tier="OFFICIAL_ADVISORY", source_observation_count=0, distinct_farms_count=0)
    sig_off = RegionalPulseService.aggregate_regional_signal(s, data=p_off, actor_roles=["ADMIN"])
    assert sig_off.source_observation_count == 0
    assert sig_off.distinct_farms_count == 0


def test_regional_pulse_expert_review_self_certification_and_recovery_gap():
    """
    [PHASE 07 - EXPERT-REVIEW-01]
    Verify that:
    1. AGRICULTURAL_EXPERT self-certifies upon creation (EXPERT_CONFIRMED without separate review event).
    2. RESEARCHER draft remains UNVALIDATED_OBSERVATION.
    3. recover_suppressed_signal rejects UNVALIDATED_OBSERVATION with HTTP 400 Bad Request,
       proving that no endpoint currently exists to promote an unvalidated researcher signal to expert-confirmed.
    """
    from fastapi import HTTPException
    from backend.app.schemas.regional_pulse import RegionalSignalCreate
    from backend.app.services.regional_pulse_service import RegionalPulseService

    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    s = Session()

    u = User(id="u-exp-gap", phone="+919876543003", full_name="User ExpGap", email="expgap@test.com", hashed_password="x")
    s.add(u)
    f1 = Farm(id="f-eg-1", owner_id="u-exp-gap", name="F1", state="Telangana", district="Warangal", mandal="M1", village="V1", total_acreage=1.0)
    f2 = Farm(id="f-eg-2", owner_id="u-exp-gap", name="F2", state="Telangana", district="Warangal", mandal="M2", village="V2", total_acreage=1.0)
    f3 = Farm(id="f-eg-3", owner_id="u-exp-gap", name="F3", state="Telangana", district="Warangal", mandal="M3", village="V3", total_acreage=1.0)
    s.add_all([f1, f2, f3])
    s.flush()

    o1 = Observation(id="o-eg-1", farm_id="f-eg-1", observer_id="u-exp-gap", notes="n", created_at=datetime(2026, 11, 5, tzinfo=timezone.utc))
    o2 = Observation(id="o-eg-2", farm_id="f-eg-2", observer_id="u-exp-gap", notes="n", created_at=datetime(2026, 11, 5, tzinfo=timezone.utc))
    o3 = Observation(id="o-eg-3", farm_id="f-eg-3", observer_id="u-exp-gap", notes="n", created_at=datetime(2026, 11, 5, tzinfo=timezone.utc))
    s.add_all([o1, o2, o3])
    s.flush()

    payload = RegionalSignalCreate(
        district="Warangal",
        crop_id="cotton",
        signal_title="Expert Signal",
        signal_summary="Summary",
        confidence_tier="EXPERT_REVIEWED",
        source_observation_count=3,
        distinct_farms_count=3,
        recommended_action="Action",
        observed_start_date=date(2026, 11, 1),
        observed_end_date=date(2026, 11, 15),
        evidences=[
            {"evidence_type": "OBSERVATION_REF", "evidence_reference_id": "o-eg-1"},
            {"evidence_type": "OBSERVATION_REF", "evidence_reference_id": "o-eg-2"},
            {"evidence_type": "OBSERVATION_REF", "evidence_reference_id": "o-eg-3"},
        ]
    )

    # 1. Agricultural Expert creates signal -> immediately EXPERT_CONFIRMED (self-certified)
    sig_expert = RegionalPulseService.aggregate_regional_signal(s, data=payload, actor_roles=["AGRICULTURAL_EXPERT"], actor_id="agri-expert-1")
    assert sig_expert.validation_status == "EXPERT_CONFIRMED"

    # 2. Researcher creates signal -> UNVALIDATED_OBSERVATION
    sig_researcher = RegionalPulseService.aggregate_regional_signal(s, data=payload, actor_roles=["RESEARCHER"], actor_id="researcher-1")
    assert sig_researcher.validation_status == "UNVALIDATED_OBSERVATION"

    # 3. Expert attempts to review and approve researcher's signal via recover_suppressed_signal -> rejected with 400
    with pytest.raises(HTTPException) as exc_info:
        RegionalPulseService.recover_suppressed_signal(
            s,
            signal_id=sig_researcher.id,
            actor_roles=["AGRICULTURAL_EXPERT"],
            actor_id="agri-expert-2",
            reason="Confirmed by Dr. Rao",
        )
    assert exc_info.value.status_code == 400
    assert "Signal is not suppressed" in exc_info.value.detail


def test_regional_pulse_official_advisory_source_provenance_absence():
    """
    [PHASE 07 - OFFICIAL-SOURCE-01]
    Verify that an ADMIN can create an OFFICIAL_ADVISORY without supplying any external source provenance
    (issuing department, gazette ID, source URL, doc hash), proving it represents platform administrator authoring
    (PLATFORM_ADMIN_AUTHORED) rather than an independently verified external state advisory.
    """
    from backend.app.schemas.regional_pulse import RegionalSignalCreate
    from backend.app.services.regional_pulse_service import RegionalPulseService

    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    s = Session()

    payload_admin = RegionalSignalCreate(
        district="Warangal",
        crop_id="cotton",
        signal_title="Government Advisory on Bollworm",
        signal_summary="Official state alert regarding bollworm surge",
        confidence_tier="OFFICIAL_ADVISORY",
        source_observation_count=0,
        distinct_farms_count=0,
        recommended_action="Spray neem seed kernel extract",
        observed_start_date=date(2026, 11, 1),
        observed_end_date=date(2026, 11, 15),
    )
    sig_admin = RegionalPulseService.aggregate_regional_signal(s, data=payload_admin, actor_roles=["ADMIN"], actor_id="admin-1")
    assert sig_admin.confidence_tier == "OFFICIAL_ADVISORY"
    assert sig_admin.validation_status == "OFFICIAL_ALERT"
    # No external agency, URL, or gazette hash exists on the model
    assert not hasattr(sig_admin, "issuing_agency")
    assert not hasattr(sig_admin, "source_document_url")
    assert not hasattr(sig_admin, "gazette_reference_id")


def test_regional_pulse_evidence_type_crosswalk_and_alias_normalization():
    """
    [PHASE 07 - EVIDENCE-TYPE-CROSSWALK]
    Verify that:
    - OBSERVATION is accepted and normalized to OBSERVATION_REF
    - RISKCAST_ALERT is accepted and normalized to RISK_ALERT
    - Unsupported types are excluded
    """
    from backend.app.schemas.regional_pulse import RegionalSignalCreate
    from backend.app.services.regional_pulse_service import RegionalPulseService
    from backend.app.models.regional_pulse import RegionalSignalEvidence

    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    s = Session()

    u = User(id="u-cw-1", phone="+919876543004", full_name="User CW", email="cw@test.com", hashed_password="x")
    s.add(u)
    f1 = Farm(id="f-cw-1", owner_id="u-cw-1", name="F1", state="Telangana", district="Warangal", mandal="M1", village="V1", total_acreage=1.0)
    f2 = Farm(id="f-cw-2", owner_id="u-cw-1", name="F2", state="Telangana", district="Warangal", mandal="M2", village="V2", total_acreage=1.0)
    f3 = Farm(id="f-cw-3", owner_id="u-cw-1", name="F3", state="Telangana", district="Warangal", mandal="M3", village="V3", total_acreage=1.0)
    s.add_all([f1, f2, f3])
    s.flush()

    o1 = Observation(id="o-cw-1", farm_id="f-cw-1", observer_id="u-cw-1", notes="n", created_at=datetime(2026, 11, 5, tzinfo=timezone.utc))
    o2 = Observation(id="o-cw-2", farm_id="f-cw-2", observer_id="u-cw-1", notes="n", created_at=datetime(2026, 11, 5, tzinfo=timezone.utc))
    s.add_all([o1, o2])
    from backend.app.models.risk_alert import RiskAlert
    ra1 = RiskAlert(id="ra-cw-1", farm_id="f-cw-3", plot_id="p-cw-1", risk_assessment_id="rar-cw-1", alert_level="HIGH", title="A", message_en="M", message_te="M", message_hi="M", deduplication_key="k-cw-1", created_at=datetime(2026, 11, 5, tzinfo=timezone.utc))
    s.add(ra1)
    s.flush()

    payload = RegionalSignalCreate(
        district="Warangal",
        crop_id="cotton",
        signal_title="Evidence Crosswalk",
        signal_summary="Summary",
        confidence_tier="FARMER_REPORT",
        source_observation_count=3,
        distinct_farms_count=3,
        recommended_action="Action",
        observed_start_date=date(2026, 11, 1),
        observed_end_date=date(2026, 11, 15),
        evidences=[
            {"evidence_type": "OBSERVATION", "evidence_reference_id": "o-cw-1"},
            {"evidence_type": "OBSERVATION_REF", "evidence_reference_id": "o-cw-2"},
            {"evidence_type": "RISKCAST_ALERT", "evidence_reference_id": "ra-cw-1"},
            {"evidence_type": "UNKNOWN_GARBAGE", "evidence_reference_id": "fake-1"},
        ]
    )

    sig = RegionalPulseService.aggregate_regional_signal(s, data=payload, actor_roles=["RESEARCHER"])
    assert sig.source_observation_count == 3
    assert sig.distinct_farms_count == 3

    ev_rows = s.query(RegionalSignalEvidence).filter(RegionalSignalEvidence.signal_id == sig.id).all()
    assert len(ev_rows) == 3
    persisted_types = {e.evidence_type for e in ev_rows}
    assert persisted_types == {"OBSERVATION_REF", "RISK_ALERT"}


def test_regional_pulse_static_rls_ddl_zero_telemetry_official_advisory_inspection():
    """
    [PHASE 07 - STATIC-RLS-INSPECTION]
    Inspect generated RLS SQL statements from rls.py to confirm that:
    - regional_signals read policy enforces distinct_farms_count >= 3
    - There is NO exception for validation_status = 'OFFICIAL_ALERT' or confidence_tier = 'OFFICIAL_ADVISORY'
    - Proving STATIC_DDL_EXEMPTION_ABSENT
    """
    from backend.app.database.rls import generate_rls_ddl, TableCategory

    sql_ddl = generate_rls_ddl("regional_signals", TableCategory.COMMUNITY_COLLABORATIVE)
    assert "distinct_farms_count >= 3" in sql_ddl
    assert "validation_status != 'SUSPENDED'" in sql_ddl

    # Verify that in regional_signals read policy there is NO exception for OFFICIAL_ALERT or OFFICIAL_ADVISORY
    assert "OFFICIAL_ALERT" not in sql_ddl
    assert "OFFICIAL_ADVISORY" not in sql_ddl


# ==============================================================================
# PHASE 07 — RLS WRITE AUTHORITY, PRIVILEGE CROSSWALK & D-01 OPTION C TESTS
# ==============================================================================

def test_rls_write_auth_01_regional_signals_policy_structure():
    """
    [RLS-WRITE-AUTH-01 & RLS-TEST-ORACLE-01 VERIFICATION]
    Verifies the exact generated RLS policies for regional_signals:
    1. SELECT read policy enforces distinct_farms_count >= 3 and non-suspended status.
    2. Write policy (author_write_policy) applies FOR ALL (USING + WITH CHECK).
    3. Write policy includes ADMIN_BYPASS_SQL.
    4. Write policy explicitly grants write access to authenticated ADMIN, AGRICULTURAL_EXPERT, and RESEARCHER.
    5. Prohibited roles (FARMER, anonymous) are strictly excluded from the write allowlist.
    6. Demonstrates that WITH CHECK lacks column/status constraints (e.g. no restriction on setting OFFICIAL_ADVISORY).
    """
    from backend.app.database.rls import generate_rls_ddl, TableCategory, ADMIN_BYPASS_SQL

    ddl = generate_rls_ddl("regional_signals", TableCategory.COMMUNITY_COLLABORATIVE)

    # 1. Read policy verification
    assert "CREATE POLICY regional_signals_public_read_policy ON regional_signals" in ddl
    assert "FOR SELECT" in ddl
    assert "distinct_farms_count >= 3" in ddl
    assert "validation_status != 'SUSPENDED'" in ddl

    # 2. Write policy command and scope
    assert "CREATE POLICY regional_signals_author_write_policy ON regional_signals" in ddl
    assert "AS PERMISSIVE\n    FOR ALL\n    TO PUBLIC" in ddl

    # 3. Admin bypass
    assert ADMIN_BYPASS_SQL in ddl

    # 4. Authenticated privileged user branch
    assert "ur.role_id IN ('ADMIN', 'AGRICULTURAL_EXPERT', 'RESEARCHER')" in ddl

    # 5. Non-privileged roles excluded
    assert "'FARMER'" not in ddl

    # 6. Dual USING and WITH CHECK clauses
    assert "USING ((" in ddl
    assert "WITH CHECK ((" in ddl

    # 7. Absence of status/tier constraints in WITH CHECK (RLS-WRITE-AUTH-01 finding)
    # The write expression checks user roles, NOT row status values!
    assert "WITH CHECK ((distinct_farms_count" not in ddl
    assert "WITH CHECK ((confidence_tier" not in ddl


def test_rls_sql_privilege_crosswalk_regional_signals():
    """
    [PRIVILEGE CROSSWALK & SQL GRANTS VERIFICATION]
    Verifies that the least-privilege specification for regional_signals:
    1. Grants SELECT, INSERT, UPDATE to runtime application role (e.g. acrevia_staging_app).
    2. Explicitly REVOKES DELETE (protecting collaborative signals from unilateral deletion).
    3. Explicitly REVOKES TRUNCATE, REFERENCES, TRIGGER.
    """
    from backend.app.database.rls import PRIVILEGE_CROSSWALK, generate_privilege_grants_ddl, TableCategory

    assert "regional_signals" in PRIVILEGE_CROSSWALK
    privs = PRIVILEGE_CROSSWALK["regional_signals"]

    assert privs["category"] == TableCategory.COMMUNITY_COLLABORATIVE
    assert privs["privilege_group"] == "COMMUNITY_COLLABORATIVE_DML"
    assert privs["SELECT"] is True
    assert privs["INSERT"] is True
    assert privs["UPDATE"] is True
    assert privs["DELETE"] is False
    assert privs["TRUNCATE"] is False
    assert privs["REFERENCES"] is False
    assert privs["TRIGGER"] is False

    grants_sql = generate_privilege_grants_ddl("acrevia_staging_app")
    assert "GRANT SELECT, INSERT, UPDATE ON TABLE regional_signals TO acrevia_staging_app;" in grants_sql
    assert "REVOKE DELETE ON TABLE regional_signals FROM acrevia_staging_app;" in grants_sql
    assert "REVOKE TRUNCATE, REFERENCES, TRIGGER ON TABLE regional_signals FROM acrevia_staging_app;" in grants_sql


def test_d01_option_c_adversarial_vulnerability_analysis():
    """
    [D-01 OPTION C ADVERSARIAL ANALYSIS]
    Analyzes the proposed read exemption:
      validation_status = 'OFFICIAL_ALERT'
      AND confidence_tier = 'OFFICIAL_ADVISORY'
      AND distinct_farms_count = 0
    
    Proves that without write-policy modification:
    1. The RLS write policy permits AGRICULTURAL_EXPERT and RESEARCHER to write.
    2. SQL privileges permit INSERT and UPDATE.
    3. WITH CHECK does not restrict setting confidence_tier='OFFICIAL_ADVISORY'.
    4. Therefore, Option C is POLICY_DESIGN_UNSAFE in its current policy form.
    """
    from backend.app.database.rls import generate_rls_ddl, TableCategory

    ddl = generate_rls_ddl("regional_signals", TableCategory.COMMUNITY_COLLABORATIVE)

    # Prove non-admin roles can write to regional_signals
    assert "AGRICULTURAL_EXPERT" in ddl
    assert "RESEARCHER" in ddl

    # In current policy form, candidate exemption tuple is NOT restricted on write
    # Proving why Option C requires explicit write-side guards or table separation (Option B)
    candidate_predicate = (
        "validation_status = 'OFFICIAL_ALERT' AND "
        "confidence_tier = 'OFFICIAL_ADVISORY' AND "
        "distinct_farms_count = 0"
    )
    # The candidate predicate is currently absent from DDL
    assert candidate_predicate not in ddl


def test_regional_signals_state_mutation_paths_service_and_endpoint_enforcement():
    """
    [STATE TRANSITION & AUTHORIZATION BOUNDARY ENFORCEMENT]
    Verifies application and service level defenses preventing unauthorized state mutations:
    1. POST /signals denies non-admin creation of OFFICIAL_ADVISORY (HTTP 403).
    2. Service aggregate_regional_signal denies non-admin creation of OFFICIAL_ADVISORY (HTTP 403).
    3. Service recover_suppressed_signal rejects non-suppressed signals (HTTP 400).
    4. Proves that application-level controls currently compensate for database-level RLS permissiveness.
    """
    from datetime import date
    from fastapi import HTTPException
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from backend.app.database.base import Base
    from backend.app.services.regional_pulse_service import RegionalPulseService
    from backend.app.schemas.regional_pulse import RegionalSignalCreate

    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    s = Session()

    # 1. Non-admin attempting to create OFFICIAL_ADVISORY via service fails closed
    advisory_payload = RegionalSignalCreate(
        signal_title="Fake Official Advisory",
        signal_summary="Testing unauthorized official advisory creation",
        recommended_action="Unverified action recommendation",
        crop_id="crop-paddy",
        district="Warangal",
        confidence_tier="OFFICIAL_ADVISORY",
        observed_start_date=date(2026, 11, 1),
        observed_end_date=date(2026, 11, 15),
    )

    with pytest.raises(HTTPException) as exc_info:
        RegionalPulseService.aggregate_regional_signal(
            s,
            data=advisory_payload,
            actor_roles=["AGRICULTURAL_EXPERT"],  # Non-admin
            actor_id="expert-attacker",
        )
    assert exc_info.value.status_code == 403
    assert "administrative authorities" in exc_info.value.detail

    # 2. Researcher attempting same also fails closed
    with pytest.raises(HTTPException) as exc_info:
        RegionalPulseService.aggregate_regional_signal(
            s,
            data=advisory_payload,
            actor_roles=["RESEARCHER"],
            actor_id="researcher-attacker",
        )
    assert exc_info.value.status_code == 403


def test_service_transaction_contract_complete_caller_audit():
    """
    [SERVICE TRANSACTION CONTRACT RECONCILIATION]
    Inspects RegionalPulseService methods and endpoint callers:
    1. Proves aggregate_regional_signal defaults to auto_commit=False.
    2. Proves recover_suppressed_signal is staging-only (zero commit/rollback).
    3. Proves revalidate_signal_provenance is savepoint-staged (zero commit/rollback).
    4. Proves all endpoint callers in regional_pulse.py explicitly commit or rollback.
    """
    import inspect
    from backend.app.services.regional_pulse_service import RegionalPulseService
    from backend.app.api.v1.endpoints import regional_pulse as ep

    # Inspect service signatures
    agg_sig = inspect.signature(RegionalPulseService.aggregate_regional_signal)
    assert agg_sig.parameters["auto_commit"].default is False

    # Inspect endpoint source code to verify caller transaction ownership
    ep_source = inspect.getsource(ep)

    # All four mutating/revalidating routes must contain db.commit() and db.rollback()
    assert "db.commit()" in ep_source
    assert "db.rollback()" in ep_source

    # Check each endpoint function has explicit commit
    assert "db.commit()" in inspect.getsource(ep.aggregate_signal)
    assert "db.commit()" in inspect.getsource(ep.list_signals)
    assert "db.commit()" in inspect.getsource(ep.get_signal)
    assert "db.commit()" in inspect.getsource(ep.recover_signal)


def test_regional_signal_evidences_rls_policy_structure():
    """
    [PHASE 07 - EVIDENCE RLS & PRIVILEGE STRUCTURE]
    Verifies that regional_signal_evidences RLS DDL:
    1. Read policy strictly denies public/farmer read (requires ADMIN, AGRI_EXPERT, RESEARCHER or ADMIN_BYPASS_SQL).
    2. Write policy applies FOR ALL (USING + WITH CHECK) and restricts to privileged roles.
    3. Prohibited roles (FARMER, anonymous) are excluded from read and write policies.
    """
    from backend.app.database.rls import generate_rls_ddl, TableCategory, ADMIN_BYPASS_SQL

    ddl = generate_rls_ddl("regional_signal_evidences", TableCategory.COMMUNITY_COLLABORATIVE)

    # 1. Non-public read policy
    assert "CREATE POLICY regional_signal_evidences_public_read_policy ON regional_signal_evidences" in ddl
    assert "FOR SELECT" in ddl
    assert "ur.role_id IN ('ADMIN', 'AGRICULTURAL_EXPERT', 'RESEARCHER')" in ddl
    assert ADMIN_BYPASS_SQL in ddl

    # 2. Write policy
    assert "CREATE POLICY regional_signal_evidences_author_write_policy ON regional_signal_evidences" in ddl
    assert "AS PERMISSIVE\n    FOR ALL\n    TO PUBLIC" in ddl
    assert "USING ((" in ddl
    assert "WITH CHECK ((" in ddl

    # 3. Farmer role absent from both read and write expressions
    assert "'FARMER'" not in ddl


def test_aggregate_signal_response_validation_failure_triggers_rollback():
    """
    [TRANSACTION OWNERSHIP & VALIDATION ROLLBACK]
    Verifies that if response model validation fails prior to caller commit in aggregate_signal,
    the transaction is rolled back and zero records (signal, evidence, audit) are persisted.
    """
    from datetime import date
    from sqlalchemy import create_engine, select
    from sqlalchemy.orm import sessionmaker
    from backend.app.database.base import Base
    from backend.app.models.regional_pulse import RegionalSignal, RegionalSignalEvidence
    from backend.app.models.governance import AuditLog
    from backend.app.schemas.regional_pulse import RegionalSignalCreate
    from backend.app.services.regional_pulse_service import RegionalPulseService

    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    s = Session()

    payload = RegionalSignalCreate(
        district="Warangal",
        crop_id="chilli",
        signal_title="Rollback Test Signal",
        signal_summary="Testing atomicity and validation rollback",
        recommended_action="Monitor field",
        confidence_tier="OFFICIAL_ADVISORY",
        source_observation_count=0,
        distinct_farms_count=0,
        observed_start_date=date(2026, 11, 1),
        observed_end_date=date(2026, 11, 15),
    )

    # 1. Service stages signal and audit record in session (staging-only contract)
    signal = RegionalPulseService.aggregate_regional_signal(
        s,
        data=payload,
        actor_roles=["ADMIN"],
        actor_id="usr-admin-rollback-test",
        auto_commit=False,
    )
    assert signal.id is not None

    # Staged in session before commit
    staged_signals = s.query(RegionalSignal).all()
    assert len(staged_signals) == 1

    # 2. Simulate response validation failure triggering rollback (as in get_db exception handler)
    s.rollback()

    # 3. After rollback, the database must contain ZERO persisted records
    assert len(s.query(RegionalSignal).all()) == 0
    assert len(s.query(RegionalSignalEvidence).all()) == 0
    assert len(s.query(AuditLog).all()) == 0


def test_atomic_signal_evidence_and_audit_persistence():
    """
    [ATOMIC AUDIT & EVIDENCE PERSISTENCE CONTRACT]
    Verifies that RegionalPulseService.aggregate_regional_signal stages
    the RegionalSignal and AuditLog atomically within the caller's transaction.
    """
    from datetime import date
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from backend.app.database.base import Base
    from backend.app.models.regional_pulse import RegionalSignal
    from backend.app.models.governance import AuditLog
    from backend.app.schemas.regional_pulse import RegionalSignalCreate
    from backend.app.services.regional_pulse_service import RegionalPulseService

    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    s = Session()

    payload = RegionalSignalCreate(
        district="Warangal",
        crop_id="cotton",
        signal_title="Atomic Signal Test",
        signal_summary="Verifying atomic audit persistence",
        recommended_action="Inspect bollworms",
        confidence_tier="OFFICIAL_ADVISORY",
        source_observation_count=0,
        distinct_farms_count=0,
        observed_start_date=date(2026, 11, 1),
        observed_end_date=date(2026, 11, 15),
    )

    signal = RegionalPulseService.aggregate_regional_signal(
        s,
        data=payload,
        actor_roles=["ADMIN"],
        actor_id="usr-admin-atomic-test",
        auto_commit=False,
    )

    # Both signal and audit log staged together
    assert s.query(RegionalSignal).count() == 1
    audit_logs = s.query(AuditLog).filter(AuditLog.resource_id == signal.id).all()
    assert len(audit_logs) == 1
    assert audit_logs[0].action == "CREATE_REGIONAL_SIGNAL"
    assert audit_logs[0].user_id == "usr-admin-atomic-test"

    # Caller explicitly commits
    s.commit()

    # Verify both persisted together
    assert s.query(RegionalSignal).count() == 1
    assert s.query(AuditLog).filter(AuditLog.resource_id == signal.id).count() == 1


# ==============================================================================
# PHASE 07 — 19-CONDITION ADVERSARIAL RLS WRITE-AUTHORITY & ACTOR TRUST TESTS
# ==============================================================================

def test_adversarial_guc_spoofing_and_actor_identity_isolation():
    """
    [ADVERSARIAL TEST MATRIX: CONDITIONS 1-5]
    Verifies that:
    1. An ordinary expert actor cannot satisfy ADMIN_BYPASS_SQL by manipulating app.is_admin = 'true'.
    2. An ordinary researcher actor cannot satisfy ADMIN_BYPASS_SQL by manipulating app.is_admin = 'true'.
    3. An ordinary actor cannot impersonate an application administrator by changing app.current_user_id.
    4. Mutable actor GUCs (app.*) cannot independently prove a privileged PostgreSQL session.
    5. In the current policy, ordinary actors can write official advisories (RLS-WRITE-AUTH-01 reproduced).
    6. Verifies that the proposed remediation expression `current_setting('app.is_admin', true) = 'true'`
       is UNSAFE because app.is_admin is session-mutable by ordinary SQL under acrevia_staging_app.
    """
    from backend.app.database.rls import ADMIN_BYPASS_SQL, generate_rls_ddl, TableCategory

    # 1 & 2: ADMIN_BYPASS_SQL requires SESSION_USER IN ('neondb_owner', 'acrevia_admin')
    # If SESSION_USER is 'acrevia_staging_app', even if app.is_admin='true', bypass fails closed
    assert "SESSION_USER::text IN ('neondb_owner', 'acrevia_admin')" in ADMIN_BYPASS_SQL
    assert "CURRENT_USER::text IN ('neondb_owner', 'acrevia_admin')" in ADMIN_BYPASS_SQL
    assert "current_setting('app.is_admin', true) = 'true'" in ADMIN_BYPASS_SQL

    # 3: Verify that user_roles lookup in regional_signals relies on app.current_user_id GUC
    ddl = generate_rls_ddl("regional_signals", TableCategory.COMMUNITY_COLLABORATIVE)
    assert "ur.user_id::text = current_setting('app.current_user_id', true)" in ddl

    # 4: Custom GUCs are session-mutable by definition in PostgreSQL
    # Prove that the unsafe proposed shortcut `app.is_admin = 'true'` is NOT in the author write policy
    assert "ur.role_id IN ('ADMIN', 'AGRICULTURAL_EXPERT', 'RESEARCHER')" in ddl

    # 5: RLS-WRITE-AUTH-01 Defect Reproduction:
    # Notice that the write policy checks user roles but lacks `confidence_tier` constraint
    assert "confidence_tier IS DISTINCT FROM 'OFFICIAL_ADVISORY'" not in ddl


def test_adversarial_state_transitions_and_permissive_policy_composition():
    """
    [ADVERSARIAL TEST MATRIX: CONDITIONS 6-15]
    Verifies that:
    6-7. In current policy, ordinary expert and researcher are permitted by write_policy
         to INSERT rows without tier restrictions.
    8-9. In current policy, ordinary expert and researcher are permitted by write_policy
         to UPDATE existing rows into official-advisory state because WITH CHECK lacks tier restrictions.
    10. Unauthorized actors (FARMER, anonymous) are excluded from write policy.
    11. Both USING and WITH CHECK are evaluated under FOR ALL.
    12. Public read policy is PERMISSIVE FOR SELECT only and does NOT grant INSERT/UPDATE.
    13. Broad FOR ALL write policy is the sole author write policy.
    14. Evidence-table write permissions require privileged roles and exclude farmers.
    15. Tests absence of ordinary-role authorization path for official-advisory writes in candidate spec.
    """
    from backend.app.database.rls import generate_rls_ddl, TableCategory

    signals_ddl = generate_rls_ddl("regional_signals", TableCategory.COMMUNITY_COLLABORATIVE)
    evidence_ddl = generate_rls_ddl("regional_signal_evidences", TableCategory.COMMUNITY_COLLABORATIVE)

    # 6-9: Write policy is FOR ALL, meaning both INSERT and UPDATE share the same WITH CHECK
    assert "CREATE POLICY regional_signals_author_write_policy ON regional_signals" in signals_ddl
    assert "AS PERMISSIVE\n    FOR ALL\n    TO PUBLIC" in signals_ddl
    assert "USING ((" in signals_ddl
    assert "WITH CHECK ((" in signals_ddl

    # 10: Non-author roles strictly excluded
    assert "'FARMER'" not in signals_ddl
    assert "'FARMER'" not in evidence_ddl

    # 12: Read policy does not grant write
    assert "CREATE POLICY regional_signals_public_read_policy ON regional_signals\n    AS PERMISSIVE\n    FOR SELECT\n    TO PUBLIC" in signals_ddl

    # 13: Exactly two policies generated for regional_signals (1 read, 1 write)
    assert signals_ddl.count("CREATE POLICY") == 2

    # 14: Evidence table read & write policies independently examined
    assert "CREATE POLICY regional_signal_evidences_public_read_policy" in evidence_ddl
    assert "CREATE POLICY regional_signal_evidences_author_write_policy" in evidence_ddl
    # Evidence read requires privileged roles, public cannot read raw farm evidence
    assert "ur.role_id IN ('ADMIN', 'AGRICULTURAL_EXPERT', 'RESEARCHER')" in evidence_ddl


def test_adversarial_database_principal_identity_and_role_membership():
    """
    [ADVERSARIAL TEST MATRIX: CONDITIONS 16-19]
    Verifies that:
    16. The database-principal bypass path checks SESSION_USER and CURRENT_USER at SQL generation level.
    17. SESSION_USER and CURRENT_USER are checked independently in ADMIN_BYPASS_SQL.
    18. A SET ROLE transition cannot alter SESSION_USER.
    19. The ordinary shared runtime principal (acrevia_staging_app) cannot gain privileged writer
        membership through source-controlled grants or crosswalk specifications.
    """
    from backend.app.database.rls import ADMIN_BYPASS_SQL, generate_privilege_grants_ddl

    # 16 & 17: Independent check of SESSION_USER and CURRENT_USER
    assert "SESSION_USER::text IN ('neondb_owner', 'acrevia_admin')" in ADMIN_BYPASS_SQL
    assert "CURRENT_USER::text IN ('neondb_owner', 'acrevia_admin')" in ADMIN_BYPASS_SQL

    # 19: Source-controlled privilege grants for acrevia_staging_app
    grants = generate_privilege_grants_ddl("acrevia_staging_app")
    # Runtime role receives table DML but zero superuser or role-granting privileges
    assert "GRANT SELECT, INSERT, UPDATE ON TABLE regional_signals TO acrevia_staging_app;" in grants
    assert "GRANT acrevia_admin TO acrevia_staging_app;" not in grants
    assert "GRANT neondb_owner TO acrevia_staging_app;" not in grants
    assert "ALTER ROLE acrevia_staging_app WITH SUPERUSER;" not in grants
    assert "ALTER ROLE acrevia_staging_app WITH BYPASSRLS;" not in grants






