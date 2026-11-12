"""
ACREVIA - PostgreSQL Row-Level Security (RLS) Tenant Isolation Architecture.
Defines tenant isolation policies, table classifications across all 132 tables,
transaction-local session context lifecycle, and SQL policy generators.
"""

from enum import Enum
from typing import Dict, Optional, Any
import sqlalchemy as sa
from sqlalchemy.orm import Session
from sqlalchemy import event

from backend.app.core.logging import logger


# PostgreSQL administrative role whitelist for RLS bypass.
# Enforces dual boundary: both the authenticated session user (SESSION_USER)
# and the effective execution context (CURRENT_USER) must be in the allowlist,
# AND the transaction-scoped 'app.is_admin' GUC must be true.
# This structurally eliminates privilege escalation via SECURITY DEFINER functions,
# role-switching, or unprivileged GUC self-escalation by runtime roles (e.g. acrevia_staging_app).
ADMIN_ROLES = ("neondb_owner", "acrevia_admin")
ADMIN_BYPASS_SQL = (
    "(SESSION_USER::text IN ('neondb_owner', 'acrevia_admin') "
    "AND CURRENT_USER::text IN ('neondb_owner', 'acrevia_admin') "
    "AND current_setting('app.is_admin', true) = 'true')"
)


class TableCategory(str, Enum):
    TENANT_DIRECT = "tenant_direct"          # Direct farm_id or tenant_id column
    TENANT_INDIRECT = "tenant_indirect"      # Child of plot, season, farm, or observation
    USER_OWNED = "user_owned"                # Owned directly by user_id or owner_id
    SHARED_REFERENCE = "shared_reference"    # Public / reference lookup tables
    COMMUNITY_COLLABORATIVE = "community"    # Community posts, comments, contributions
    SYSTEM_INFRASTRUCTURE = "system"        # System, alembic, background worker tables


# Classification of all 132 ACREVIA entities
TABLE_CLASSIFICATION: Dict[str, Dict[str, Any]] = {
    # 1. Direct Tenant Tables (24 tables with direct farm_id or tenant_id)
    "farms": {"category": TableCategory.TENANT_DIRECT, "column": "id", "owner_column": "owner_id"},
    "audit_logs": {"category": TableCategory.TENANT_DIRECT, "column": "farm_id"},
    "crop_loss_evidence_packages": {"category": TableCategory.TENANT_DIRECT, "column": "farm_id"},
    "data_exchange_jobs": {"category": TableCategory.TENANT_DIRECT, "column": "farm_id"},
    "data_sharing_grants": {"category": TableCategory.TENANT_DIRECT, "column": "farm_id"},
    "expert_review_cases": {"category": TableCategory.TENANT_DIRECT, "column": "farm_id"},
    "farm_expenses": {"category": TableCategory.TENANT_DIRECT, "column": "farm_id"},
    "farm_memberships": {"category": TableCategory.TENANT_DIRECT, "column": "farm_id"},
    "farm_twins": {"category": TableCategory.TENANT_DIRECT, "column": "farm_id"},
    "intervention_records": {"category": TableCategory.TENANT_DIRECT, "column": "farm_id"},
    "location_permissions": {"category": TableCategory.TENANT_DIRECT, "column": "farm_id"},
    "observations": {"category": TableCategory.TENANT_DIRECT, "column": "farm_id"},
    "optimization_problems": {"category": TableCategory.TENANT_DIRECT, "column": "farm_id"},
    "plots": {"category": TableCategory.TENANT_DIRECT, "column": "farm_id"},
    "produce_lots": {"category": TableCategory.TENANT_DIRECT, "column": "farm_id"},
    "risk_alerts": {"category": TableCategory.TENANT_DIRECT, "column": "farm_id"},
    "risk_assessment_records": {"category": TableCategory.TENANT_DIRECT, "column": "farm_id"},
    "risk_assessments": {"category": TableCategory.TENANT_DIRECT, "column": "farm_id"},
    "sensor_devices": {"category": TableCategory.TENANT_DIRECT, "column": "farm_id"},
    "storage_locations": {"category": TableCategory.TENANT_DIRECT, "column": "farm_id"},
    "twin_snapshots": {"category": TableCategory.TENANT_DIRECT, "column": "farm_id"},
    "water_sources": {"category": TableCategory.TENANT_DIRECT, "column": "farm_id"},
    "weather_data": {"category": TableCategory.TENANT_DIRECT, "column": "farm_id"},
    "weather_observations": {"category": TableCategory.TENANT_DIRECT, "column": "farm_id"},
    "webhook_events": {"category": TableCategory.TENANT_DIRECT, "column": "tenant_id"},

    # 2. User-Owned Tables (13 tables)
    "users": {"category": TableCategory.USER_OWNED, "column": "id"},
    "session_tokens": {"category": TableCategory.USER_OWNED, "column": "user_id"},
    "user_roles": {"category": TableCategory.USER_OWNED, "column": "user_id"},
    "consent_records": {"category": TableCategory.USER_OWNED, "column": "user_id"},
    "api_applications": {"category": TableCategory.USER_OWNED, "column": "user_id"},
    "webhook_endpoints": {"category": TableCategory.USER_OWNED, "column": "user_id"},
    "data_mapping_profiles": {"category": TableCategory.USER_OWNED, "column": "user_id"},
    "expert_profiles": {"category": TableCategory.USER_OWNED, "column": "user_id"},
    "community_memberships": {"category": TableCategory.USER_OWNED, "column": "user_id"},
    "organization_memberships": {"category": TableCategory.USER_OWNED, "column": "user_id"},
    "event_registrations": {"category": TableCategory.USER_OWNED, "column": "user_id"},
    "knowledge_feedback": {"category": TableCategory.USER_OWNED, "column": "user_id"},
    "learning_feedback": {"category": TableCategory.USER_OWNED, "column": "user_id"},

    # 3. Indirect Tenant Tables (51 child tables linked to plot, season, farm, or observation)
    "plants": {"category": TableCategory.TENANT_INDIRECT, "parent_table": "plots", "fk": "plot_id"},
    "plot_geometries": {"category": TableCategory.TENANT_INDIRECT, "parent_table": "plots", "fk": "plot_id"},
    "crop_seasons": {"category": TableCategory.TENANT_INDIRECT, "parent_table": "plots", "fk": "plot_id"},
    "crop_stage_events": {"category": TableCategory.TENANT_INDIRECT, "parent_table": "crop_seasons", "fk": "crop_season_id"},
    "crop_tasks": {"category": TableCategory.TENANT_INDIRECT, "parent_table": "plots", "fk": "plot_id"},
    "crop_season_economics": {"category": TableCategory.TENANT_INDIRECT, "parent_table": "crop_seasons", "fk": "crop_season_id"},
    "diagnosis_requests": {"category": TableCategory.TENANT_INDIRECT, "parent_table": "observations", "fk": "observation_id"},
    "predictions": {"category": TableCategory.TENANT_INDIRECT, "parent_table": "diagnosis_requests", "fk": "diagnosis_request_id"},
    "prediction_candidates": {"category": TableCategory.TENANT_INDIRECT, "parent_table": "predictions", "fk": "prediction_id"},
    "expert_reviews": {"category": TableCategory.TENANT_INDIRECT, "parent_table": "diagnosis_requests", "fk": "diagnosis_request_id"},
    "expert_assessments": {"category": TableCategory.TENANT_INDIRECT, "parent_table": "expert_review_cases", "fk": "case_id"},
    "expert_assessment_revisions": {"category": TableCategory.TENANT_INDIRECT, "parent_table": "expert_assessments", "fk": "assessment_id"},
    "outcome_observations": {"category": TableCategory.TENANT_INDIRECT, "parent_table": "intervention_records", "fk": "intervention_id"},
    "farm_operations": {"category": TableCategory.TENANT_INDIRECT, "parent_table": "plots", "fk": "plot_id"},
    "observation_media": {"category": TableCategory.TENANT_INDIRECT, "parent_table": "observations", "fk": "observation_id"},
    "image_quality_assessments": {"category": TableCategory.TENANT_INDIRECT, "parent_table": "observation_media", "fk": "media_id"},
    "sensor_measurements": {"category": TableCategory.TENANT_INDIRECT, "parent_table": "plots", "fk": "plot_id"},
    "sensor_calibrations": {"category": TableCategory.TENANT_INDIRECT, "parent_table": "sensor_devices", "fk": "device_id"},
    "satellite_observations": {"category": TableCategory.TENANT_INDIRECT, "parent_table": "plots", "fk": "plot_id"},
    "fusion_explanations": {"category": TableCategory.TENANT_INDIRECT, "parent_table": "plots", "fk": "plot_id"},
    "yield_forecast_records": {"category": TableCategory.TENANT_INDIRECT, "parent_table": "plots", "fk": "plot_id"},
    "harvest_measurements": {"category": TableCategory.TENANT_INDIRECT, "parent_table": "plots", "fk": "plot_id"},
    "twin_state_records": {"category": TableCategory.TENANT_INDIRECT, "parent_table": "twin_snapshots", "fk": "snapshot_id"},
    "twin_synchronization_events": {"category": TableCategory.TENANT_INDIRECT, "parent_table": "farm_twins", "fk": "twin_id"},
    "simulation_scenarios": {"category": TableCategory.TENANT_INDIRECT, "parent_table": "plots", "fk": "plot_id"},
    "simulation_results": {"category": TableCategory.TENANT_INDIRECT, "parent_table": "simulation_scenarios", "fk": "scenario_id"},
    "optimization_results": {"category": TableCategory.TENANT_INDIRECT, "parent_table": "optimization_problems", "fk": "problem_id"},
    "financial_corrections": {"category": TableCategory.TENANT_INDIRECT, "parent_table": "farm_expenses", "fk": "expense_id"},
    "sale_transactions": {"category": TableCategory.TENANT_INDIRECT, "parent_table": "produce_lots", "fk": "lot_id"},
    "harvest_plans": {"category": TableCategory.TENANT_INDIRECT, "parent_table": "plots", "fk": "plot_id"},
    "harvest_sessions": {"category": TableCategory.TENANT_INDIRECT, "parent_table": "harvest_plans", "fk": "harvest_plan_id"},
    "lot_movements": {"category": TableCategory.TENANT_INDIRECT, "parent_table": "produce_lots", "fk": "lot_id"},
    "quality_measurements": {"category": TableCategory.TENANT_INDIRECT, "parent_table": "produce_lots", "fk": "lot_id"},
    "storage_lots": {"category": TableCategory.TENANT_INDIRECT, "parent_table": "produce_lots", "fk": "lot_id"},
    "soil_profiles": {"category": TableCategory.TENANT_INDIRECT, "parent_table": "plots", "fk": "plot_id"},
    "soil_samples": {"category": TableCategory.TENANT_INDIRECT, "parent_table": "plots", "fk": "plot_id"},
    "soil_test_results": {"category": TableCategory.TENANT_INDIRECT, "parent_table": "soil_samples", "fk": "soil_sample_id"},
    "water_balance_snapshots": {"category": TableCategory.TENANT_INDIRECT, "parent_table": "plots", "fk": "plot_id"},
    "irrigation_events": {"category": TableCategory.TENANT_INDIRECT, "parent_table": "plots", "fk": "plot_id"},
    "soil_moisture_observations": {"category": TableCategory.TENANT_INDIRECT, "parent_table": "plots", "fk": "plot_id"},
    "climate_exposure_assessments": {"category": TableCategory.TENANT_INDIRECT, "parent_table": "plots", "fk": "plot_id"},
    "climate_adaptation_scenarios": {"category": TableCategory.TENANT_INDIRECT, "parent_table": "climate_exposure_assessments", "fk": "assessment_id"},
    "nutrient_assessments": {"category": TableCategory.TENANT_INDIRECT, "parent_table": "soil_test_results", "fk": "soil_test_result_id"},
    "nutrient_expert_reviews": {"category": TableCategory.TENANT_INDIRECT, "parent_table": "nutrient_assessments", "fk": "nutrient_assessment_id"},
    "farm_practice_records": {"category": TableCategory.TENANT_INDIRECT, "parent_table": "plots", "fk": "plot_id"},
    "soil_carbon_measurements": {"category": TableCategory.TENANT_INDIRECT, "parent_table": "plots", "fk": "plot_id"},
    "environmental_accounting_estimates": {"category": TableCategory.TENANT_INDIRECT, "parent_table": "plots", "fk": "plot_id"},
    "resilience_assessments": {"category": TableCategory.TENANT_INDIRECT, "parent_table": "plots", "fk": "plot_id"},
    "resilience_scenario_simulations": {"category": TableCategory.TENANT_INDIRECT, "parent_table": "resilience_assessments", "fk": "assessment_id"},
    "decision_records": {"category": TableCategory.TENANT_INDIRECT, "parent_table": "plots", "fk": "plot_id"},
    "decision_feedbacks": {"category": TableCategory.TENANT_INDIRECT, "parent_table": "decision_records", "fk": "decision_id"},
    "api_credentials": {"category": TableCategory.TENANT_INDIRECT, "parent_table": "api_applications", "fk": "application_id"},
    "webhook_deliveries": {"category": TableCategory.TENANT_INDIRECT, "parent_table": "webhook_endpoints", "fk": "endpoint_id"},

    # 4. Shared Reference / Knowledge Catalogs (25 tables)
    "roles": {"category": TableCategory.SHARED_REFERENCE, "access_type": "PUBLIC_REFERENCE"},
    "crops": {"category": TableCategory.SHARED_REFERENCE, "access_type": "PUBLIC_REFERENCE"},
    "crop_varieties": {"category": TableCategory.SHARED_REFERENCE, "access_type": "PUBLIC_REFERENCE"},
    "crop_calendar_definitions": {"category": TableCategory.SHARED_REFERENCE, "access_type": "PUBLIC_REFERENCE"},
    "agricultural_practice_definitions": {"category": TableCategory.SHARED_REFERENCE, "access_type": "PUBLIC_REFERENCE"},
    "market_commodities": {"category": TableCategory.SHARED_REFERENCE, "access_type": "PUBLIC_REFERENCE"},
    "market_locations": {"category": TableCategory.SHARED_REFERENCE, "access_type": "PUBLIC_REFERENCE"},
    "market_price_observations": {"category": TableCategory.SHARED_REFERENCE, "access_type": "PUBLIC_REFERENCE"},
    "satellite_sources": {"category": TableCategory.SHARED_REFERENCE, "access_type": "PUBLIC_REFERENCE"},
    "climate_baselines": {"category": TableCategory.SHARED_REFERENCE, "access_type": "PUBLIC_REFERENCE"},
    "risk_rules": {"category": TableCategory.SHARED_REFERENCE, "access_type": "PUBLIC_REFERENCE"},
    "produce_quality_profiles": {"category": TableCategory.SHARED_REFERENCE, "access_type": "PUBLIC_REFERENCE"},
    "learning_resources": {"category": TableCategory.SHARED_REFERENCE, "access_type": "PUBLIC_REFERENCE"},
    "training_events": {"category": TableCategory.SHARED_REFERENCE, "access_type": "PUBLIC_REFERENCE"},
    "knowledge_sources": {"category": TableCategory.SHARED_REFERENCE, "access_type": "PUBLIC_REFERENCE"},
    "knowledge_documents": {"category": TableCategory.SHARED_REFERENCE, "access_type": "PUBLIC_REFERENCE"},
    "knowledge_document_versions": {"category": TableCategory.SHARED_REFERENCE, "access_type": "PUBLIC_REFERENCE"},
    "knowledge_chunks": {"category": TableCategory.SHARED_REFERENCE, "access_type": "PUBLIC_REFERENCE"},
    "knowledge_embeddings": {"category": TableCategory.SHARED_REFERENCE, "access_type": "PUBLIC_REFERENCE"},
    "knowledge_entities": {"category": TableCategory.SHARED_REFERENCE, "access_type": "PUBLIC_REFERENCE"},
    "knowledge_relationships": {"category": TableCategory.SHARED_REFERENCE, "access_type": "PUBLIC_REFERENCE"},
    "satellite_acquisitions": {"category": TableCategory.SHARED_REFERENCE, "access_type": "PUBLIC_REFERENCE"},
    # Sensitive Operational and Integration Catalogs (Restricted to Database Admin / Ingestion Workers)
    "ingestion_jobs": {"category": TableCategory.SHARED_REFERENCE, "access_type": "PRIVATE_OPERATIONAL"},
    "partner_integrations": {"category": TableCategory.SHARED_REFERENCE, "access_type": "ADMINISTRATIVE"},
    "integration_partners": {"category": TableCategory.SHARED_REFERENCE, "access_type": "ADMINISTRATIVE"},

    # 5. Community & Collaborative Hub (16 tables)
    "communities": {
        "category": TableCategory.COMMUNITY_COLLABORATIVE,
        "author_column": "created_by_user_id",
        "public_read": True,
    },
    "community_posts": {
        "category": TableCategory.COMMUNITY_COLLABORATIVE,
        "author_column": "author_id",
        "public_read": True,
        "read_filter": "moderation_status = 'APPROVED' AND visibility = 'COMMUNITY_PUBLIC'",
    },
    "community_comments": {
        "category": TableCategory.COMMUNITY_COLLABORATIVE,
        "author_column": "author_id",
        "public_read": True,
        "read_filter": "moderation_status = 'APPROVED'",
    },
    "community_reports": {
        "category": TableCategory.COMMUNITY_COLLABORATIVE,
        "author_column": "reported_by_user_id",
        "public_read": False,  # Private: reporter or admin only
    },
    "knowledge_contributions": {
        "category": TableCategory.COMMUNITY_COLLABORATIVE,
        "author_column": "contributor_id",
        "public_read": True,
        "read_filter": "status IN ('APPROVED', 'PUBLISHED')",
    },
    "contribution_reviews": {
        "category": TableCategory.COMMUNITY_COLLABORATIVE,
        "author_column": "reviewer_id",
        "public_read": True,
    },
    "translation_versions": {
        "category": TableCategory.COMMUNITY_COLLABORATIVE,
        "parent_table": "knowledge_contributions",
        "fk": "contribution_id",
    },
    "agricultural_organizations": {
        "category": TableCategory.COMMUNITY_COLLABORATIVE,
        "public_read": True,
        "read_filter": "verification_status = 'APPROVED'",
    },
    "collective_activities": {
        "category": TableCategory.COMMUNITY_COLLABORATIVE,
        "author_column": "created_by_user_id",
        "public_read": True,
    },
    "research_projects": {
        "category": TableCategory.COMMUNITY_COLLABORATIVE,
        "author_column": "lead_researcher_id",
        "public_read": True,
        "read_filter": "project_status = 'ACTIVE'",
    },
    "research_consents": {
        "category": TableCategory.COMMUNITY_COLLABORATIVE,
        "author_column": "farmer_id",
        "public_read": False,  # Private: farmer or admin only
    },
    "dataset_contributions": {
        "category": TableCategory.COMMUNITY_COLLABORATIVE,
        "author_column": "contributor_id",
        "public_read": True,
        "read_filter": "status = 'PUBLISHED'",
    },
    "annotation_tasks": {
        "category": TableCategory.COMMUNITY_COLLABORATIVE,
        "author_column": "assigned_expert_id",
        "public_read": True,
    },
    "annotation_records": {
        "category": TableCategory.COMMUNITY_COLLABORATIVE,
        "author_column": "annotator_id",
        "public_read": True,
    },
    "regional_signals": {
        "category": TableCategory.COMMUNITY_COLLABORATIVE,
        "public_read": True,
    },
    "regional_signal_evidences": {
        "category": TableCategory.COMMUNITY_COLLABORATIVE,
        "public_read": False,
    },
}


def set_tenant_context(
    session: Session,
    tenant_id: Optional[str] = None,
    user_id: Optional[str] = None,
    is_admin: bool = False
) -> None:
    """
    Sets the runtime tenant isolation session context.
    On PostgreSQL: executes transaction-local set_config parameters (`is_local=true`),
    ensuring parameters are automatically reset when the transaction terminates.
    On SQLite / test dialects: stores context in `session.info['tenant_context']`.
    """
    # Always track in session.info for application layer introspection
    session.info["tenant_context"] = {
        "tenant_id": str(tenant_id) if tenant_id else None,
        "user_id": str(user_id) if user_id else None,
        "is_admin": is_admin
    }

    try:
        bind = session.get_bind()
        if bind and bind.dialect.name == "postgresql":
            # PostgreSQL runtime configuration with is_local=true (transaction-scoped)
            tenant_val = str(tenant_id) if tenant_id else ""
            user_val = str(user_id) if user_id else ""
            admin_val = "true" if is_admin else "false"

            session.execute(
                sa.text("SELECT set_config('app.current_tenant_id', :val, true)"),
                {"val": tenant_val}
            )
            session.execute(
                sa.text("SELECT set_config('app.current_user_id', :val, true)"),
                {"val": user_val}
            )
            session.execute(
                sa.text("SELECT set_config('app.is_admin', :val, true)"),
                {"val": admin_val}
            )
    except Exception as exc:
        logger.error(f"Failed to set PostgreSQL RLS tenant context: {exc}")
        # On PostgreSQL, failing to establish security context must not be silently swallowed
        bind = None
        try:
            bind = session.get_bind()
        except Exception:
            pass
        if bind and bind.dialect.name == "postgresql":
            session.rollback()
            raise RuntimeError(f"Database security error: Failed to establish tenant context: {exc}") from exc


def clear_tenant_context(session: Session) -> None:
    """
    Explicitly resets tenant context in session and clears PostgreSQL session parameters.
    """
    session.info["tenant_context"] = {
        "tenant_id": None,
        "user_id": None,
        "is_admin": False
    }

    try:
        bind = session.get_bind()
        if bind and bind.dialect.name == "postgresql":
            session.execute(sa.text("SELECT set_config('app.current_tenant_id', '', true)"))
            session.execute(sa.text("SELECT set_config('app.current_user_id', '', true)"))
            session.execute(sa.text("SELECT set_config('app.is_admin', 'false', true)"))
    except Exception:
        pass


def generate_rls_ddl(table_name: str, category: TableCategory, column_name: str = "farm_id") -> str:
    """
    Generates standard PostgreSQL DDL for enabling Row-Level Security
    and establishing strict isolation policies.

    Combines a base PERMISSIVE policy with a RESTRICTIVE tenant isolation policy.
    In PostgreSQL RLS architecture:
      - At least one PERMISSIVE policy must grant access for an operation.
      - RESTRICTIVE policies combine via AND to strictly enforce tenant boundary constraints.
    """
    if category == TableCategory.TENANT_DIRECT:
        return f"""
-- Table: {table_name} (Direct Tenant Isolation)
ALTER TABLE {table_name} ENABLE ROW LEVEL SECURITY;
ALTER TABLE {table_name} FORCE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS {table_name}_base_access_policy ON {table_name};
CREATE POLICY {table_name}_base_access_policy ON {table_name}
    AS PERMISSIVE
    FOR ALL
    TO PUBLIC
    USING (true)
    WITH CHECK (true);

DROP POLICY IF EXISTS {table_name}_tenant_isolation_policy ON {table_name};
CREATE POLICY {table_name}_tenant_isolation_policy ON {table_name}
    AS RESTRICTIVE
    FOR ALL
    TO PUBLIC
    USING (
        {ADMIN_BYPASS_SQL}
        OR {column_name}::text = current_setting('app.current_tenant_id', true)
    )
    WITH CHECK (
        {ADMIN_BYPASS_SQL}
        OR {column_name}::text = current_setting('app.current_tenant_id', true)
    );
"""
    elif category == TableCategory.USER_OWNED:
        return f"""
-- Table: {table_name} (User-Owned Isolation)
ALTER TABLE {table_name} ENABLE ROW LEVEL SECURITY;
ALTER TABLE {table_name} FORCE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS {table_name}_base_access_policy ON {table_name};
CREATE POLICY {table_name}_base_access_policy ON {table_name}
    AS PERMISSIVE
    FOR ALL
    TO PUBLIC
    USING (true)
    WITH CHECK (true);

DROP POLICY IF EXISTS {table_name}_user_isolation_policy ON {table_name};
CREATE POLICY {table_name}_user_isolation_policy ON {table_name}
    AS RESTRICTIVE
    FOR ALL
    TO PUBLIC
    USING (
        {ADMIN_BYPASS_SQL}
        OR {column_name}::text = current_setting('app.current_user_id', true)
    )
    WITH CHECK (
        {ADMIN_BYPASS_SQL}
        OR {column_name}::text = current_setting('app.current_user_id', true)
    );
"""
    elif category == TableCategory.SHARED_REFERENCE:
        meta = TABLE_CLASSIFICATION.get(table_name, {})
        access_type = meta.get("access_type", "PUBLIC_REFERENCE")

        if access_type in ("ADMINISTRATIVE", "PRIVATE_OPERATIONAL"):
            # Private operational / Administrative internal table: ZERO public read!
            if table_name == "ingestion_jobs":
                # Ingestion jobs: Authorized Agronomists/Researchers/Admins or Database Admin
                auth_expr = f"""(
        {ADMIN_BYPASS_SQL}
        OR (
            current_setting('app.current_user_id', true) != ''
            AND EXISTS (
                SELECT 1 FROM user_roles ur
                WHERE ur.user_id::text = current_setting('app.current_user_id', true)
                AND ur.role_id IN ('ADMIN', 'AGRICULTURAL_EXPERT', 'RESEARCHER')
            )
        )
    )"""
                return f"""
-- Table: {table_name} (Private Operational Reference - Ingestion Worker / Admin Scoped)
ALTER TABLE {table_name} ENABLE ROW LEVEL SECURITY;
ALTER TABLE {table_name} FORCE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS {table_name}_shared_read_policy ON {table_name};
DROP POLICY IF EXISTS {table_name}_admin_write_policy ON {table_name};
CREATE POLICY {table_name}_admin_write_policy ON {table_name}
    AS PERMISSIVE
    FOR ALL
    TO PUBLIC
    USING ({auth_expr})
    WITH CHECK ({auth_expr});
"""
            return f"""
-- Table: {table_name} (Private Operational / Administrative Reference - Admin Only)
ALTER TABLE {table_name} ENABLE ROW LEVEL SECURITY;
ALTER TABLE {table_name} FORCE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS {table_name}_shared_read_policy ON {table_name};
DROP POLICY IF EXISTS {table_name}_admin_write_policy ON {table_name};
CREATE POLICY {table_name}_admin_write_policy ON {table_name}
    AS PERMISSIVE
    FOR ALL
    TO PUBLIC
    USING ({ADMIN_BYPASS_SQL})
    WITH CHECK ({ADMIN_BYPASS_SQL});
"""
        elif access_type == "AUTHENTICATED_SHARED":
            # Authenticated read, administrative write
            return f"""
-- Table: {table_name} (Authenticated Shared Reference - Authenticated Read, Admin Write)
ALTER TABLE {table_name} ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS {table_name}_shared_read_policy ON {table_name};
CREATE POLICY {table_name}_shared_read_policy ON {table_name}
    AS PERMISSIVE
    FOR SELECT
    TO PUBLIC
    USING (
        {ADMIN_BYPASS_SQL}
        OR current_setting('app.current_user_id', true) != ''
    );

DROP POLICY IF EXISTS {table_name}_admin_write_policy ON {table_name};
CREATE POLICY {table_name}_admin_write_policy ON {table_name}
    AS PERMISSIVE
    FOR ALL
    TO PUBLIC
    USING ({ADMIN_BYPASS_SQL})
    WITH CHECK ({ADMIN_BYPASS_SQL});
"""
        else:
            # PUBLIC_REFERENCE: Public Read, Admin Write (both PERMISSIVE)
            return f"""
-- Table: {table_name} (Shared Reference - Public Read, Admin Write)
ALTER TABLE {table_name} ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS {table_name}_shared_read_policy ON {table_name};
CREATE POLICY {table_name}_shared_read_policy ON {table_name}
    AS PERMISSIVE
    FOR SELECT
    TO PUBLIC
    USING (true);

DROP POLICY IF EXISTS {table_name}_admin_write_policy ON {table_name};
CREATE POLICY {table_name}_admin_write_policy ON {table_name}
    AS PERMISSIVE
    FOR ALL
    TO PUBLIC
    USING ({ADMIN_BYPASS_SQL})
    WITH CHECK ({ADMIN_BYPASS_SQL});
"""
    elif category == TableCategory.TENANT_INDIRECT:
        parent = TABLE_CLASSIFICATION.get(table_name, {}).get("parent_table", "plots")
        fk = TABLE_CLASSIFICATION.get(table_name, {}).get("fk", "plot_id")
        return f"""
-- Table: {table_name} (Indirect Tenant Child Table linked to {parent})
ALTER TABLE {table_name} ENABLE ROW LEVEL SECURITY;
ALTER TABLE {table_name} FORCE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS {table_name}_base_access_policy ON {table_name};
CREATE POLICY {table_name}_base_access_policy ON {table_name}
    AS PERMISSIVE
    FOR ALL
    TO PUBLIC
    USING (true)
    WITH CHECK (true);

DROP POLICY IF EXISTS {table_name}_child_isolation_policy ON {table_name};
CREATE POLICY {table_name}_child_isolation_policy ON {table_name}
    AS RESTRICTIVE
    FOR ALL
    TO PUBLIC
    USING (
        {ADMIN_BYPASS_SQL}
        OR EXISTS (
            SELECT 1 FROM {parent}
            WHERE {parent}.id = {table_name}.{fk}
            AND (
                {parent}.id::text = current_setting('app.current_tenant_id', true)
                OR (
                    EXISTS (
                        SELECT 1 FROM information_schema.columns
                        WHERE table_name = '{parent}' AND column_name = 'farm_id'
                    )
                    AND ({parent}.farm_id::text = current_setting('app.current_tenant_id', true))
                )
                OR (
                    EXISTS (
                        SELECT 1 FROM information_schema.columns
                        WHERE table_name = '{parent}' AND column_name = 'user_id'
                    )
                    AND ({parent}.user_id::text = current_setting('app.current_user_id', true))
                )
            )
        )
    )
    WITH CHECK (
        {ADMIN_BYPASS_SQL}
        OR EXISTS (
            SELECT 1 FROM {parent}
            WHERE {parent}.id = {table_name}.{fk}
            AND (
                {parent}.id::text = current_setting('app.current_tenant_id', true)
                OR (
                    EXISTS (
                        SELECT 1 FROM information_schema.columns
                        WHERE table_name = '{parent}' AND column_name = 'farm_id'
                    )
                    AND ({parent}.farm_id::text = current_setting('app.current_tenant_id', true))
                )
                OR (
                    EXISTS (
                        SELECT 1 FROM information_schema.columns
                        WHERE table_name = '{parent}' AND column_name = 'user_id'
                    )
                    AND ({parent}.user_id::text = current_setting('app.current_user_id', true))
                )
            )
        )
    );
"""
    elif category == TableCategory.COMMUNITY_COLLABORATIVE:
        meta = TABLE_CLASSIFICATION.get(table_name, {})

        if table_name == "community_posts":
            read_expr = f"""(
        {ADMIN_BYPASS_SQL}
        OR author_id::text = current_setting('app.current_user_id', true)
        OR EXISTS (
            SELECT 1 FROM community_memberships cm
            WHERE cm.community_id = community_posts.community_id
            AND cm.user_id::text = current_setting('app.current_user_id', true)
            AND cm.role = 'MODERATOR'
        )
        OR (
            moderation_status = 'APPROVED'
            AND (
                visibility = 'COMMUNITY_PUBLIC'
                OR (
                    visibility = 'RESTRICTED_MEMBERS'
                    AND EXISTS (
                        SELECT 1 FROM community_memberships cm
                        WHERE cm.community_id = community_posts.community_id
                        AND cm.user_id::text = current_setting('app.current_user_id', true)
                    )
                )
                OR (
                    visibility = 'EXPERT_ONLY'
                    AND (
                        EXISTS (
                            SELECT 1 FROM community_memberships cm
                            WHERE cm.community_id = community_posts.community_id
                            AND cm.user_id::text = current_setting('app.current_user_id', true)
                            AND cm.role IN ('EXPERT_ADVISOR', 'MODERATOR')
                        )
                        OR EXISTS (
                            SELECT 1 FROM user_roles ur
                            WHERE ur.user_id::text = current_setting('app.current_user_id', true)
                            AND ur.role_id IN ('AGRICULTURAL_EXPERT', 'RESEARCHER', 'ADMIN')
                        )
                    )
                )
            )
        )
    )"""
            write_expr = f"""(
        {ADMIN_BYPASS_SQL}
        OR (
            current_setting('app.current_user_id', true) != ''
            AND author_id::text = current_setting('app.current_user_id', true)
        )
        OR EXISTS (
            SELECT 1 FROM community_memberships cm
            WHERE cm.community_id = community_posts.community_id
            AND cm.user_id::text = current_setting('app.current_user_id', true)
            AND cm.role = 'MODERATOR'
        )
    )"""
        elif table_name == "community_comments":
            read_expr = f"""(
        {ADMIN_BYPASS_SQL}
        OR author_id::text = current_setting('app.current_user_id', true)
        OR (
            moderation_status = 'APPROVED'
            AND EXISTS (
                SELECT 1 FROM community_posts cp
                WHERE cp.id = community_comments.post_id
                AND (
                    cp.author_id::text = current_setting('app.current_user_id', true)
                    OR EXISTS (
                        SELECT 1 FROM community_memberships cm
                        WHERE cm.community_id = cp.community_id
                        AND cm.user_id::text = current_setting('app.current_user_id', true)
                        AND cm.role = 'MODERATOR'
                    )
                    OR (
                        cp.moderation_status = 'APPROVED'
                        AND (
                            cp.visibility = 'COMMUNITY_PUBLIC'
                            OR (
                                cp.visibility = 'RESTRICTED_MEMBERS'
                                AND EXISTS (
                                    SELECT 1 FROM community_memberships cm
                                    WHERE cm.community_id = cp.community_id
                                    AND cm.user_id::text = current_setting('app.current_user_id', true)
                                )
                            )
                            OR (
                                cp.visibility = 'EXPERT_ONLY'
                                AND (
                                    EXISTS (
                                        SELECT 1 FROM community_memberships cm
                                        WHERE cm.community_id = cp.community_id
                                        AND cm.user_id::text = current_setting('app.current_user_id', true)
                                        AND cm.role IN ('EXPERT_ADVISOR', 'MODERATOR')
                                    )
                                    OR EXISTS (
                                        SELECT 1 FROM user_roles ur
                                        WHERE ur.user_id::text = current_setting('app.current_user_id', true)
                                        AND ur.role_id IN ('AGRICULTURAL_EXPERT', 'RESEARCHER', 'ADMIN')
                                    )
                                )
                            )
                        )
                    )
                )
            )
        )
    )"""
            write_expr = f"""(
        {ADMIN_BYPASS_SQL}
        OR (
            current_setting('app.current_user_id', true) != ''
            AND author_id::text = current_setting('app.current_user_id', true)
        )
    )"""
        elif table_name == "community_reports":
            read_expr = f"""(
        {ADMIN_BYPASS_SQL}
        OR reported_by_user_id::text = current_setting('app.current_user_id', true)
        OR EXISTS (
            SELECT 1 FROM community_posts cp
            JOIN community_memberships cm ON cm.community_id = cp.community_id
            WHERE (
                cp.id = community_reports.post_id
                OR cp.id IN (SELECT cc.post_id FROM community_comments cc WHERE cc.id = community_reports.comment_id)
            )
            AND cm.user_id::text = current_setting('app.current_user_id', true)
            AND cm.role = 'MODERATOR'
        )
    )"""
            write_expr = f"""(
        {ADMIN_BYPASS_SQL}
        OR (
            current_setting('app.current_user_id', true) != ''
            AND reported_by_user_id::text = current_setting('app.current_user_id', true)
        )
    )"""
        elif table_name == "knowledge_contributions":
            read_expr = f"""(
        {ADMIN_BYPASS_SQL}
        OR contributor_id::text = current_setting('app.current_user_id', true)
        OR assigned_expert_id::text = current_setting('app.current_user_id', true)
        OR status IN ('APPROVED', 'PUBLISHED')
        OR EXISTS (
            SELECT 1 FROM user_roles ur
            WHERE ur.user_id::text = current_setting('app.current_user_id', true)
            AND ur.role_id IN ('AGRICULTURAL_EXPERT', 'RESEARCHER', 'ADMIN')
        )
    )"""
            write_expr = f"""(
        {ADMIN_BYPASS_SQL}
        OR (
            current_setting('app.current_user_id', true) != ''
            AND contributor_id::text = current_setting('app.current_user_id', true)
        )
    )"""
        elif table_name == "contribution_reviews":
            read_expr = f"""(
        {ADMIN_BYPASS_SQL}
        OR reviewer_id::text = current_setting('app.current_user_id', true)
        OR EXISTS (
            SELECT 1 FROM knowledge_contributions kc
            WHERE kc.id = contribution_reviews.contribution_id
            AND (
                kc.contributor_id::text = current_setting('app.current_user_id', true)
                OR kc.status IN ('APPROVED', 'PUBLISHED')
            )
        )
        OR EXISTS (
            SELECT 1 FROM user_roles ur
            WHERE ur.user_id::text = current_setting('app.current_user_id', true)
            AND ur.role_id IN ('AGRICULTURAL_EXPERT', 'RESEARCHER', 'ADMIN')
        )
    )"""
            write_expr = f"""(
        {ADMIN_BYPASS_SQL}
        OR (
            current_setting('app.current_user_id', true) != ''
            AND reviewer_id::text = current_setting('app.current_user_id', true)
        )
    )"""
        elif table_name == "translation_versions":
            read_expr = f"""(
        {ADMIN_BYPASS_SQL}
        OR reviewer_id::text = current_setting('app.current_user_id', true)
        OR EXISTS (
            SELECT 1 FROM knowledge_contributions kc
            WHERE kc.id = translation_versions.contribution_id
            AND (
                kc.contributor_id::text = current_setting('app.current_user_id', true)
                OR (
                    kc.status IN ('APPROVED', 'PUBLISHED')
                    AND translation_versions.is_native_reviewed = true
                )
            )
        )
    )"""
            write_expr = f"""(
        {ADMIN_BYPASS_SQL}
        OR (
            current_setting('app.current_user_id', true) != ''
            AND (
                reviewer_id::text = current_setting('app.current_user_id', true)
                OR EXISTS (
                    SELECT 1 FROM knowledge_contributions kc
                    WHERE kc.id = translation_versions.contribution_id
                    AND kc.contributor_id::text = current_setting('app.current_user_id', true)
                )
            )
        )
    )"""
        elif table_name == "agricultural_organizations":
            read_expr = f"""(
        {ADMIN_BYPASS_SQL}
        OR verification_status = 'APPROVED'
        OR EXISTS (
            SELECT 1 FROM organization_memberships om
            WHERE om.organization_id = agricultural_organizations.id
            AND om.user_id::text = current_setting('app.current_user_id', true)
            AND om.is_active = true
        )
    )"""
            write_expr = f"""(
        {ADMIN_BYPASS_SQL}
        OR EXISTS (
            SELECT 1 FROM organization_memberships om
            WHERE om.organization_id = agricultural_organizations.id
            AND om.user_id::text = current_setting('app.current_user_id', true)
            AND om.org_role = 'ORGANIZATION_ADMIN'
            AND om.is_active = true
        )
    )"""
        elif table_name == "collective_activities":
            read_expr = f"""(
        {ADMIN_BYPASS_SQL}
        OR created_by_user_id::text = current_setting('app.current_user_id', true)
        OR EXISTS (
            SELECT 1 FROM organization_memberships om
            WHERE om.organization_id = collective_activities.organization_id
            AND om.user_id::text = current_setting('app.current_user_id', true)
            AND om.is_active = true
        )
    )"""
            write_expr = f"""(
        {ADMIN_BYPASS_SQL}
        OR (
            created_by_user_id::text = current_setting('app.current_user_id', true)
            AND EXISTS (
                SELECT 1 FROM organization_memberships om
                WHERE om.organization_id = collective_activities.organization_id
                AND om.user_id::text = current_setting('app.current_user_id', true)
                AND om.is_active = true
                AND om.org_role IN ('ORGANIZATION_ADMIN', 'GROUP_COORDINATOR')
            )
        )
    )"""
        elif table_name == "research_projects":
            read_expr = f"""(
        {ADMIN_BYPASS_SQL}
        OR lead_researcher_id::text = current_setting('app.current_user_id', true)
        OR project_status = 'ACTIVE'
    )"""
            write_expr = f"""(
        {ADMIN_BYPASS_SQL}
        OR (
            current_setting('app.current_user_id', true) != ''
            AND lead_researcher_id::text = current_setting('app.current_user_id', true)
        )
    )"""
        elif table_name == "research_consents":
            read_expr = f"""(
        {ADMIN_BYPASS_SQL}
        OR farmer_id::text = current_setting('app.current_user_id', true)
        OR EXISTS (
            SELECT 1 FROM research_projects rp
            WHERE rp.id = research_consents.project_id
            AND rp.lead_researcher_id::text = current_setting('app.current_user_id', true)
        )
    )"""
            write_expr = f"""(
        {ADMIN_BYPASS_SQL}
        OR (
            current_setting('app.current_user_id', true) != ''
            AND farmer_id::text = current_setting('app.current_user_id', true)
        )
    )"""
        elif table_name == "dataset_contributions":
            read_expr = f"""(
        {ADMIN_BYPASS_SQL}
        OR contributor_id::text = current_setting('app.current_user_id', true)
        OR EXISTS (
            SELECT 1 FROM research_projects rp
            WHERE rp.id = dataset_contributions.project_id
            AND rp.lead_researcher_id::text = current_setting('app.current_user_id', true)
        )
        OR status = 'PUBLISHED'
    )"""
            write_expr = f"""(
        {ADMIN_BYPASS_SQL}
        OR (
            current_setting('app.current_user_id', true) != ''
            AND contributor_id::text = current_setting('app.current_user_id', true)
        )
    )"""
        elif table_name == "annotation_tasks":
            read_expr = f"""(
        {ADMIN_BYPASS_SQL}
        OR assigned_expert_id::text = current_setting('app.current_user_id', true)
        OR EXISTS (
            SELECT 1 FROM research_projects rp
            WHERE rp.id = annotation_tasks.project_id
            AND rp.lead_researcher_id::text = current_setting('app.current_user_id', true)
        )
    )"""
            write_expr = f"""(
        {ADMIN_BYPASS_SQL}
        OR EXISTS (
            SELECT 1 FROM research_projects rp
            WHERE rp.id = annotation_tasks.project_id
            AND rp.lead_researcher_id::text = current_setting('app.current_user_id', true)
        )
    )"""
        elif table_name == "annotation_records":
            read_expr = f"""(
        {ADMIN_BYPASS_SQL}
        OR annotator_id::text = current_setting('app.current_user_id', true)
        OR EXISTS (
            SELECT 1 FROM annotation_tasks at
            WHERE at.id = annotation_records.task_id
            AND (
                at.assigned_expert_id::text = current_setting('app.current_user_id', true)
                OR EXISTS (
                    SELECT 1 FROM research_projects rp
                    WHERE rp.id = at.project_id
                    AND rp.lead_researcher_id::text = current_setting('app.current_user_id', true)
                )
            )
        )
    )"""
            write_expr = f"""(
        {ADMIN_BYPASS_SQL}
        OR (
            current_setting('app.current_user_id', true) != ''
            AND annotator_id::text = current_setting('app.current_user_id', true)
        )
    )"""
        elif table_name in ("regional_signals", "regional_signal_evidences"):
            if table_name == "regional_signals":
                read_expr = f"""(
        {ADMIN_BYPASS_SQL}
        OR (
            distinct_farms_count >= 3
            AND validation_status != 'SUSPENDED'
        )
    )"""
            else:
                # Evidence table: Restricted to Admin, Agricultural Expert, and Researcher to protect farmer anonymity
                read_expr = f"""(
        {ADMIN_BYPASS_SQL}
        OR (
            current_setting('app.current_user_id', true) != ''
            AND EXISTS (
                SELECT 1 FROM user_roles ur
                WHERE ur.user_id::text = current_setting('app.current_user_id', true)
                AND ur.role_id IN ('ADMIN', 'AGRICULTURAL_EXPERT', 'RESEARCHER')
            )
        )
    )"""
            write_expr = f"""(
        {ADMIN_BYPASS_SQL}
        OR (
            current_setting('app.current_user_id', true) != ''
            AND EXISTS (
                SELECT 1 FROM user_roles ur
                WHERE ur.user_id::text = current_setting('app.current_user_id', true)
                AND ur.role_id IN ('ADMIN', 'AGRICULTURAL_EXPERT', 'RESEARCHER')
            )
        )
    )"""
        elif table_name == "communities":
            read_expr = "true"
            write_expr = f"""(
        {ADMIN_BYPASS_SQL}
        OR (
            current_setting('app.current_user_id', true) != ''
            AND created_by_user_id::text = current_setting('app.current_user_id', true)
        )
    )"""
        else:
            author_col = meta.get("author_column")
            if author_col:
                read_expr = f"({ADMIN_BYPASS_SQL} OR {author_col}::text = current_setting('app.current_user_id', true))"
                write_expr = f"({ADMIN_BYPASS_SQL} OR (current_setting('app.current_user_id', true) != '' AND {author_col}::text = current_setting('app.current_user_id', true)))"
            else:
                read_expr = f"({ADMIN_BYPASS_SQL})"
                write_expr = f"({ADMIN_BYPASS_SQL})"

        return f"""
-- Table: {table_name} (Collaborative Table with Scoped Security)
ALTER TABLE {table_name} ENABLE ROW LEVEL SECURITY;
ALTER TABLE {table_name} FORCE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS {table_name}_public_read_policy ON {table_name};
CREATE POLICY {table_name}_public_read_policy ON {table_name}
    AS PERMISSIVE
    FOR SELECT
    TO PUBLIC
    USING ({read_expr});

DROP POLICY IF EXISTS {table_name}_author_write_policy ON {table_name};
CREATE POLICY {table_name}_author_write_policy ON {table_name}
    AS PERMISSIVE
    FOR ALL
    TO PUBLIC
    USING ({write_expr})
    WITH CHECK ({write_expr});
"""
    return ""


# ==============================================================================
# AUTHORITATIVE 132-TABLE PRIVILEGE CROSSWALK (LEAST PRIVILEGE SPECIFICATION)
# ==============================================================================

PRIVILEGE_CROSSWALK: Dict[str, Dict[str, Any]] = {}
for tbl_name, tbl_meta in TABLE_CLASSIFICATION.items():
    cat = tbl_meta.get("category")
    acc = tbl_meta.get("access_type")

    # Determine least-privilege rights for runtime application role (e.g. acrevia_staging_app)
    can_select = True
    can_insert = False
    can_update = False
    can_delete = False
    can_truncate = False
    can_references = False
    can_trigger = False

    if tbl_name == "audit_logs":
        # Strictly append-only audit trail under DPDPA 2023 least-privilege specification
        can_insert = True
        can_update = False
        can_delete = False
        priv_group = "TENANT_DIRECT_APPEND_ONLY"
    elif cat in (TableCategory.TENANT_DIRECT, TableCategory.USER_OWNED, TableCategory.TENANT_INDIRECT):
        can_insert = True
        can_update = True
        can_delete = True
        priv_group = f"{cat.value.upper()}_DML"
    elif cat == TableCategory.COMMUNITY_COLLABORATIVE:
        can_insert = True
        can_update = True
        can_delete = False  # Denied to protect collaborative records from unilateral deletion
        priv_group = "COMMUNITY_COLLABORATIVE_DML"
    elif cat == TableCategory.SHARED_REFERENCE:
        if acc == "PRIVATE_OPERATIONAL":
            can_insert = True
            can_update = True
            can_delete = False
            priv_group = "PRIVATE_OPERATIONAL_REF"
        elif acc == "ADMINISTRATIVE":
            can_insert = False
            can_update = False
            can_delete = False
            priv_group = "ADMIN_INTEGRATION_REF"
        else:
            can_insert = False
            can_update = False
            can_delete = False
            priv_group = "PUBLIC_SHARED_REF"
    else:
        priv_group = "UNCLASSIFIED"

    PRIVILEGE_CROSSWALK[tbl_name] = {
        "table_name": tbl_name,
        "category": cat,
        "privilege_group": priv_group,
        "SELECT": can_select,
        "INSERT": can_insert,
        "UPDATE": can_update,
        "DELETE": can_delete,
        "TRUNCATE": can_truncate,
        "REFERENCES": can_references,
        "TRIGGER": can_trigger,
    }


def generate_privilege_grants_ddl(role_name: str = "acrevia_staging_app") -> str:
    """
    Generates exact least-privilege PostgreSQL GRANT and REVOKE statements
    for the runtime application role across all 132 database entities.
    
    LEAST-PRIVILEGE INVARIANTS:
    1. Zero blanket grants. Shared reference tables receive SELECT only.
    2. Zero TRUNCATE permissions granted to any runtime role (RLS bypass mitigation).
    3. Zero REFERENCES permissions granted to prevent foreign key schema constraints.
    4. Zero TRIGGER permissions granted to prevent unauthorized trigger execution.
    5. Audit log table (audit_logs) receives SELECT, INSERT, with explicit REVOKE UPDATE, DELETE for idempotency.
    6. Community collaborative tables receive SELECT, INSERT, UPDATE, with explicit REVOKE DELETE.
    """
    lines = [
        f"-- Least-Privilege Grants for Runtime Role: {role_name}",
        f"REVOKE ALL ON SCHEMA public FROM {role_name};",
        f"GRANT USAGE ON SCHEMA public TO {role_name};",
        f"GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO {role_name};",
        "",
    ]
    for tbl_name, privs in PRIVILEGE_CROSSWALK.items():
        # First, explicitly revoke disallowed DML permissions for idempotency
        disallowed_dml = []
        for p in ["INSERT", "UPDATE", "DELETE"]:
            if not privs[p]:
                disallowed_dml.append(p)
        if disallowed_dml:
            lines.append(f"REVOKE {', '.join(disallowed_dml)} ON TABLE {tbl_name} FROM {role_name};")

        grants = []
        if privs["SELECT"]:
            grants.append("SELECT")
        if privs["INSERT"]:
            grants.append("INSERT")
        if privs["UPDATE"]:
            grants.append("UPDATE")
        if privs["DELETE"]:
            grants.append("DELETE")

        if grants:
            lines.append(f"GRANT {', '.join(grants)} ON TABLE {tbl_name} TO {role_name};")
        # Explicit defensive revokes for dangerous schema/system privileges
        lines.append(f"REVOKE TRUNCATE, REFERENCES, TRIGGER ON TABLE {tbl_name} FROM {role_name};")

    return "\n".join(lines)

