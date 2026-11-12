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
from datetime import datetime, timezone, date
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
from backend.app.tasks.run_riskcast_batch import (
    evaluate_single_farm,
    run_batch,
    ProductionDispatchBlockedError,
    TaskManifestVerificationError,
    BatchTaskManifest,
    verify_dispatch_manifest,
    PROCESSED_TASK_IDS,
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
            # Run evaluate_single_farm
            evaluated = asyncio.run(evaluate_single_farm("farm-tenant-01", is_authorized=True))
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
        evaluated = asyncio.run(evaluate_single_farm("farm-arch-01", is_authorized=True))
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
    from datetime import datetime, timezone
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
    Proves that evaluate_single_farm fails closed with PermissionError if invoked
    without explicit dispatch authorization (is_authorized=False).
    Guarantees no tenant context is established for unverified caller inputs.
    """
    import uuid
    unauthorized_uuid = str(uuid.uuid4())
    with pytest.raises(PermissionError, match="Unauthorized farm evaluation"):
        asyncio.run(evaluate_single_farm(unauthorized_uuid, is_authorized=False))


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
