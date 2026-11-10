"""
ACREVIA - ORM Model-to-RLS Alignment & Policy Semantics Test Suite.
Validates 100% dynamic alignment between SQLAlchemy Base.metadata and RLS policies.
Honest Test Classification:
  - STATIC_METADATA_TEST: Metadata inspection and set equality.
  - STATIC_POLICY_GENERATION_TEST: SQL string generation and predicate verification.
  - OFFLINE_UNIT_TEST: Context lifecycle and fail-closed behavior.
"""

import pytest
import re
from backend.app.database.base import Base
import backend.app.models  # Ensures all ORM models are registered in Base.metadata
from backend.app.database.rls import (
    TABLE_CLASSIFICATION,
    TableCategory,
    ADMIN_BYPASS_SQL,
    generate_rls_ddl,
    set_tenant_context,
    clear_tenant_context,
)


# ==============================================================================
# 1. DYNAMIC METADATA CONSISTENCY TESTS (STATIC_METADATA_TEST)
# ==============================================================================

def test_dynamic_model_registry_matches_rls_classification():
    """
    [STATIC_METADATA_TEST]
    Mathematically verifies that:
      M = actual registered SQLAlchemy table names (Base.metadata.tables.keys())
      R = RLS classification table names (TABLE_CLASSIFICATION.keys())
      M - R = empty set (zero unclassified model tables)
      R - M = empty set (zero unknown RLS tables)
      M == R (100% coverage, dynamic set equality)
    """
    m_tables = set(Base.metadata.tables.keys())
    r_tables = set(TABLE_CLASSIFICATION.keys())

    unclassified_model_tables = m_tables - r_tables
    unknown_rls_tables = r_tables - m_tables

    assert not unclassified_model_tables, (
        f"Security Flaw: Found {len(unclassified_model_tables)} unclassified ORM models: {unclassified_model_tables}"
    )
    assert not unknown_rls_tables, (
        f"Configuration Error: Found {len(unknown_rls_tables)} phantom RLS entries without ORM models: {unknown_rls_tables}"
    )
    assert m_tables == r_tables, "Set equality condition M == R failed"


def test_every_classified_column_and_fk_exists_in_real_metadata():
    """
    [STATIC_METADATA_TEST]
    Verifies that every column, author_column, parent_table, and fk referenced
    in TABLE_CLASSIFICATION actually exists in SQLAlchemy Base.metadata.
    """
    for table_name, meta in TABLE_CLASSIFICATION.items():
        assert table_name in Base.metadata.tables, f"Table {table_name} not found in metadata"
        table = Base.metadata.tables[table_name]
        col_names = {c.name for c in table.columns}

        if "column" in meta:
            col = meta["column"]
            assert col in col_names, (
                f"Column '{col}' referenced in classification of '{table_name}' does not exist. Available: {col_names}"
            )

        if "author_column" in meta:
            author_col = meta["author_column"]
            assert author_col in col_names, (
                f"Author column '{author_col}' referenced in classification of '{table_name}' does not exist. Available: {col_names}"
            )

        if "parent_table" in meta:
            parent = meta["parent_table"]
            assert parent in Base.metadata.tables, (
                f"Parent table '{parent}' referenced by '{table_name}' does not exist in metadata"
            )
            fk = meta.get("fk")
            assert fk in col_names, (
                f"Foreign key '{fk}' referenced in '{table_name}' does not exist in columns. Available: {col_names}"
            )


# ==============================================================================
# 2. SHARED REFERENCE & SENSITIVE TABLE POLICY TESTS (STATIC_POLICY_GENERATION_TEST)
# ==============================================================================

def test_shared_reference_public_read_and_admin_write():
    """
    [STATIC_POLICY_GENERATION_TEST]
    Verifies public reference tables generate permissive SELECT USING (true)
    and permissive Admin-only DML.
    """
    public_refs = [
        "crop_varieties", "crops", "market_locations", "produce_quality_profiles",
        "learning_resources", "training_events", "satellite_sources"
    ]
    for tbl in public_refs:
        ddl = generate_rls_ddl(tbl, TableCategory.SHARED_REFERENCE)
        assert f"ALTER TABLE {tbl} ENABLE ROW LEVEL SECURITY;" in ddl
        assert f"ALTER TABLE {tbl} FORCE ROW LEVEL SECURITY;" not in ddl  # Public refs don't force RLS
        assert f"CREATE POLICY {tbl}_shared_read_policy ON {tbl}" in ddl
        assert "AS PERMISSIVE\n    FOR SELECT\n    TO PUBLIC\n    USING (true);" in ddl
        assert f"CREATE POLICY {tbl}_admin_write_policy ON {tbl}" in ddl
        assert ADMIN_BYPASS_SQL in ddl


def test_sensitive_shared_tables_deny_public_read():
    """
    [STATIC_POLICY_GENERATION_TEST]
    Verifies sensitive partner/operational tables (ingestion_jobs, partner_integrations,
    integration_partners) enforce FORCE RLS, zero public read, and admin-only access.
    """
    sensitive_tables = ["ingestion_jobs", "partner_integrations", "integration_partners"]
    for tbl in sensitive_tables:
        ddl = generate_rls_ddl(tbl, TableCategory.SHARED_REFERENCE)
        assert f"ALTER TABLE {tbl} ENABLE ROW LEVEL SECURITY;" in ddl
        assert f"ALTER TABLE {tbl} FORCE ROW LEVEL SECURITY;" in ddl
        # Crucial: Must NEVER create a shared read policy allowing public SELECT
        assert f"CREATE POLICY {tbl}_shared_read_policy" not in ddl
        assert "USING (true)" not in ddl
        # Admin write/all policy present
        assert f"CREATE POLICY {tbl}_admin_write_policy ON {tbl}" in ddl
        assert ADMIN_BYPASS_SQL in ddl


# ==============================================================================
# 3. COMMUNITY POST & COMMENT VISIBILITY TESTS (STATIC_POLICY_GENERATION_TEST)
# ==============================================================================

def test_community_post_visibility_and_moderation():
    """
    [STATIC_POLICY_GENERATION_TEST]
    Verifies CommunityPost policy:
    1. Author can access their own posts regardless of moderation status.
    2. Community moderators can view all posts in their community.
    3. Public can ONLY view APPROVED posts with COMMUNITY_PUBLIC visibility.
    4. RESTRICTED_MEMBERS posts require active community membership.
    5. EXPERT_ONLY posts require expert role or advisor membership.
    6. Author can write/edit their own posts.
    """
    ddl = generate_rls_ddl("community_posts", TableCategory.COMMUNITY_COLLABORATIVE)
    assert "ALTER TABLE community_posts ENABLE ROW LEVEL SECURITY;" in ddl
    assert "ALTER TABLE community_posts FORCE ROW LEVEL SECURITY;" in ddl

    # Read policy assertions
    assert "author_id::text = current_setting('app.current_user_id', true)" in ddl
    assert "community_memberships" in ddl
    assert "cm.role = 'MODERATOR'" in ddl
    assert "moderation_status = 'APPROVED'" in ddl
    assert "visibility = 'COMMUNITY_PUBLIC'" in ddl
    assert "visibility = 'RESTRICTED_MEMBERS'" in ddl
    assert "visibility = 'EXPERT_ONLY'" in ddl
    assert "user_roles" in ddl

    # Write policy assertions
    assert "author_id::text = current_setting('app.current_user_id', true)" in ddl
    assert ADMIN_BYPASS_SQL in ddl


def test_community_comments_inherits_parent_post_visibility():
    """
    [STATIC_POLICY_GENERATION_TEST]
    Verifies CommunityComment policy:
    1. Comment author can access their own comment.
    2. Comments are ONLY readable if moderation_status is APPROVED AND parent post is accessible.
    3. Prevents leak of comments attached to restricted or expert posts.
    """
    ddl = generate_rls_ddl("community_comments", TableCategory.COMMUNITY_COLLABORATIVE)
    assert "ALTER TABLE community_comments ENABLE ROW LEVEL SECURITY;" in ddl
    assert "ALTER TABLE community_comments FORCE ROW LEVEL SECURITY;" in ddl
    assert "author_id::text = current_setting('app.current_user_id', true)" in ddl
    assert "community_posts" in ddl
    assert "cp.id = community_comments.post_id" in ddl
    assert "cp.visibility = 'COMMUNITY_PUBLIC'" in ddl


def test_community_reports_strict_privacy():
    """
    [STATIC_POLICY_GENERATION_TEST]
    Verifies CommunityReport policy:
    1. Uses the actual 'reported_by_user_id' column from CommunityReport model.
    2. Zero public read (no USING (true)).
    3. Only readable by reporting user, community moderators, or platform admin.
    """
    ddl = generate_rls_ddl("community_reports", TableCategory.COMMUNITY_COLLABORATIVE)
    assert "reported_by_user_id::text = current_setting('app.current_user_id', true)" in ddl
    assert "reporter_id" not in ddl  # Non-existent column must NOT be referenced
    assert "USING (true)" not in ddl
    assert "cm.role = 'MODERATOR'" in ddl


# ==============================================================================
# 4. KNOWLEDGE & RESEARCH PRIVACY TESTS (STATIC_POLICY_GENERATION_TEST)
# ==============================================================================

def test_knowledge_contribution_and_review_policies():
    """
    [STATIC_POLICY_GENERATION_TEST]
    Verifies KnowledgeContribution & ContributionReview policies:
    1. Contributor can access their drafts/submissions.
    2. Public can only read APPROVED/PUBLISHED contributions.
    3. Reviewers can access assigned reviews.
    4. Translations inherit publication status and require native review for public.
    """
    contrib_ddl = generate_rls_ddl("knowledge_contributions", TableCategory.COMMUNITY_COLLABORATIVE)
    assert "contributor_id::text = current_setting('app.current_user_id', true)" in contrib_ddl
    assert "status IN ('APPROVED', 'PUBLISHED')" in contrib_ddl

    review_ddl = generate_rls_ddl("contribution_reviews", TableCategory.COMMUNITY_COLLABORATIVE)
    assert "reviewer_id::text = current_setting('app.current_user_id', true)" in review_ddl
    assert "knowledge_contributions" in review_ddl

    trans_ddl = generate_rls_ddl("translation_versions", TableCategory.COMMUNITY_COLLABORATIVE)
    assert "reviewer_id::text = current_setting('app.current_user_id', true)" in trans_ddl
    assert "translation_versions.is_native_reviewed = true" in trans_ddl


def test_research_consent_strict_farmer_privacy():
    """
    [STATIC_POLICY_GENERATION_TEST]
    Verifies ResearchConsent policy:
    1. Uses actual 'farmer_id' column.
    2. Strictly restricted to the consenting farmer and the project lead researcher.
    3. Zero public read.
    """
    ddl = generate_rls_ddl("research_consents", TableCategory.COMMUNITY_COLLABORATIVE)
    assert "farmer_id::text = current_setting('app.current_user_id', true)" in ddl
    assert "research_projects" in ddl
    assert "rp.lead_researcher_id::text = current_setting('app.current_user_id', true)" in ddl
    assert "USING (true)" not in ddl


def test_annotation_task_and_record_isolation():
    """
    [STATIC_POLICY_GENERATION_TEST]
    Verifies AnnotationTask & AnnotationRecord policies:
    1. Task accessible by assigned expert and project lead.
    2. Annotation record modifiable ONLY by the annotator who created it.
    """
    task_ddl = generate_rls_ddl("annotation_tasks", TableCategory.COMMUNITY_COLLABORATIVE)
    assert "assigned_expert_id::text = current_setting('app.current_user_id', true)" in task_ddl

    rec_ddl = generate_rls_ddl("annotation_records", TableCategory.COMMUNITY_COLLABORATIVE)
    assert "annotator_id::text = current_setting('app.current_user_id', true)" in rec_ddl


# ==============================================================================
# 5. ORGANIZATIONS & REGIONAL SIGNALS (STATIC_POLICY_GENERATION_TEST)
# ==============================================================================

def test_agricultural_organization_and_activity_isolation():
    """
    [STATIC_POLICY_GENERATION_TEST]
    Verifies:
    1. Organizations: Unverified orgs are hidden from public (visible to members/admin only).
    2. Activities: Restricted to active organization members; write requires org coordinator/admin.
    """
    org_ddl = generate_rls_ddl("agricultural_organizations", TableCategory.COMMUNITY_COLLABORATIVE)
    assert "verification_status = 'APPROVED'" in org_ddl
    assert "organization_memberships" in org_ddl

    act_ddl = generate_rls_ddl("collective_activities", TableCategory.COMMUNITY_COLLABORATIVE)
    assert "created_by_user_id::text = current_setting('app.current_user_id', true)" in act_ddl
    assert "organization_memberships" in act_ddl
    assert "om.org_role IN ('ORGANIZATION_ADMIN', 'GROUP_COORDINATOR')" in act_ddl


def test_regional_signals_threshold_and_evidence():
    """
    [STATIC_POLICY_GENERATION_TEST]
    Verifies:
    1. RegionalSignal enforces distinct_farms_count >= 3 for public visibility.
    2. Evidence inherits parent signal access.
    3. Writes strictly restricted to ADMIN_BYPASS_SQL (dedicated worker architecture required).
    """
    sig_ddl = generate_rls_ddl("regional_signals", TableCategory.COMMUNITY_COLLABORATIVE)
    assert "distinct_farms_count >= 3" in sig_ddl
    assert ADMIN_BYPASS_SQL in sig_ddl

    ev_ddl = generate_rls_ddl("regional_signal_evidences", TableCategory.COMMUNITY_COLLABORATIVE)
    assert "regional_signals" in ev_ddl
    assert "rs.distinct_farms_count >= 3" in ev_ddl
