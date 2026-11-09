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
    "expert_reviews": {"category": TableCategory.TENANT_INDIRECT, "parent_table": "predictions", "fk": "prediction_id"},
    "expert_assessments": {"category": TableCategory.TENANT_INDIRECT, "parent_table": "expert_review_cases", "fk": "case_id"},
    "expert_assessment_revisions": {"category": TableCategory.TENANT_INDIRECT, "parent_table": "expert_assessments", "fk": "assessment_id"},
    "outcome_observations": {"category": TableCategory.TENANT_INDIRECT, "parent_table": "intervention_records", "fk": "intervention_id"},
    "farm_operations": {"category": TableCategory.TENANT_INDIRECT, "parent_table": "plots", "fk": "plot_id"},
    "observation_media": {"category": TableCategory.TENANT_INDIRECT, "parent_table": "observations", "fk": "observation_id"},
    "image_quality_assessments": {"category": TableCategory.TENANT_INDIRECT, "parent_table": "observation_media", "fk": "media_id"},
    "sensor_measurements": {"category": TableCategory.TENANT_INDIRECT, "parent_table": "plots", "fk": "plot_id"},
    "sensor_calibrations": {"category": TableCategory.TENANT_INDIRECT, "parent_table": "sensor_devices", "fk": "device_id"},
    "satellite_observations": {"category": TableCategory.TENANT_INDIRECT, "parent_table": "plots", "fk": "plot_id"},
    "fusion_explanations": {"category": TableCategory.TENANT_INDIRECT, "parent_table": "observations", "fk": "observation_id"},
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
    "harvest_sessions": {"category": TableCategory.TENANT_INDIRECT, "parent_table": "harvest_plans", "fk": "plan_id"},
    "lot_movements": {"category": TableCategory.TENANT_INDIRECT, "parent_table": "produce_lots", "fk": "lot_id"},
    "produce_quality_profiles": {"category": TableCategory.TENANT_INDIRECT, "parent_table": "produce_lots", "fk": "lot_id"},
    "quality_measurements": {"category": TableCategory.TENANT_INDIRECT, "parent_table": "produce_quality_profiles", "fk": "profile_id"},
    "storage_lots": {"category": TableCategory.TENANT_INDIRECT, "parent_table": "produce_lots", "fk": "lot_id"},
    "soil_profiles": {"category": TableCategory.TENANT_INDIRECT, "parent_table": "plots", "fk": "plot_id"},
    "soil_samples": {"category": TableCategory.TENANT_INDIRECT, "parent_table": "plots", "fk": "plot_id"},
    "soil_test_results": {"category": TableCategory.TENANT_INDIRECT, "parent_table": "soil_samples", "fk": "soil_sample_id"},
    "water_balance_snapshots": {"category": TableCategory.TENANT_INDIRECT, "parent_table": "plots", "fk": "plot_id"},
    "irrigation_events": {"category": TableCategory.TENANT_INDIRECT, "parent_table": "plots", "fk": "plot_id"},
    "soil_moisture_observations": {"category": TableCategory.TENANT_INDIRECT, "parent_table": "plots", "fk": "plot_id"},
    "climate_exposure_assessments": {"category": TableCategory.TENANT_INDIRECT, "parent_table": "plots", "fk": "plot_id"},
    "climate_adaptation_scenarios": {"category": TableCategory.TENANT_INDIRECT, "parent_table": "climate_exposure_assessments", "fk": "assessment_id"},
    "nutrient_assessments": {"category": TableCategory.TENANT_INDIRECT, "parent_table": "plots", "fk": "plot_id"},
    "nutrient_expert_reviews": {"category": TableCategory.TENANT_INDIRECT, "parent_table": "nutrient_assessments", "fk": "assessment_id"},
    "farm_practice_records": {"category": TableCategory.TENANT_INDIRECT, "parent_table": "plots", "fk": "plot_id"},
    "soil_carbon_measurements": {"category": TableCategory.TENANT_INDIRECT, "parent_table": "plots", "fk": "plot_id"},
    "environmental_accounting_estimates": {"category": TableCategory.TENANT_INDIRECT, "parent_table": "plots", "fk": "plot_id"},
    "resilience_assessments": {"category": TableCategory.TENANT_INDIRECT, "parent_table": "plots", "fk": "plot_id"},
    "resilience_scenario_simulations": {"category": TableCategory.TENANT_INDIRECT, "parent_table": "resilience_assessments", "fk": "resilience_assessment_id"},
    "decision_records": {"category": TableCategory.TENANT_INDIRECT, "parent_table": "plots", "fk": "plot_id"},
    "decision_feedbacks": {"category": TableCategory.TENANT_INDIRECT, "parent_table": "decision_records", "fk": "decision_record_id"},
    "api_credentials": {"category": TableCategory.TENANT_INDIRECT, "parent_table": "api_applications", "fk": "application_id"},
    "webhook_deliveries": {"category": TableCategory.TENANT_INDIRECT, "parent_table": "webhook_endpoints", "fk": "endpoint_id"},

    # 4. Shared Reference / Knowledge Catalogs (26 tables)
    "roles": {"category": TableCategory.SHARED_REFERENCE},
    "crops": {"category": TableCategory.SHARED_REFERENCE},
    "crop_varieties": {"category": TableCategory.SHARED_REFERENCE},
    "crop_calendar_definitions": {"category": TableCategory.SHARED_REFERENCE},
    "agricultural_practice_definitions": {"category": TableCategory.SHARED_REFERENCE},
    "market_commodities": {"category": TableCategory.SHARED_REFERENCE},
    "market_locations": {"category": TableCategory.SHARED_REFERENCE},
    "market_price_observations": {"category": TableCategory.SHARED_REFERENCE},
    "satellite_sources": {"category": TableCategory.SHARED_REFERENCE},
    "climate_baselines": {"category": TableCategory.SHARED_REFERENCE},
    "risk_rules": {"category": TableCategory.SHARED_REFERENCE},
    "integration_partners": {"category": TableCategory.SHARED_REFERENCE},
    "partner_integrations": {"category": TableCategory.SHARED_REFERENCE},
    "knowledge_sources": {"category": TableCategory.SHARED_REFERENCE},
    "knowledge_documents": {"category": TableCategory.SHARED_REFERENCE},
    "knowledge_document_versions": {"category": TableCategory.SHARED_REFERENCE},
    "knowledge_chunks": {"category": TableCategory.SHARED_REFERENCE},
    "knowledge_embeddings": {"category": TableCategory.SHARED_REFERENCE},
    "knowledge_entities": {"category": TableCategory.SHARED_REFERENCE},
    "knowledge_relationships": {"category": TableCategory.SHARED_REFERENCE},
    "ingestion_jobs": {"category": TableCategory.SHARED_REFERENCE},
    "learning_resources": {"category": TableCategory.SHARED_REFERENCE},
    "training_events": {"category": TableCategory.SHARED_REFERENCE},
    "satellite_acquisitions": {"category": TableCategory.SHARED_REFERENCE},

    # 5. Community & Collaborative Hub (18 tables)
    "communities": {"category": TableCategory.COMMUNITY_COLLABORATIVE},
    "community_posts": {"category": TableCategory.COMMUNITY_COLLABORATIVE},
    "community_comments": {"category": TableCategory.COMMUNITY_COLLABORATIVE},
    "community_reports": {"category": TableCategory.COMMUNITY_COLLABORATIVE},
    "knowledge_contributions": {"category": TableCategory.COMMUNITY_COLLABORATIVE},
    "contribution_reviews": {"category": TableCategory.COMMUNITY_COLLABORATIVE},
    "translation_versions": {"category": TableCategory.COMMUNITY_COLLABORATIVE},
    "agricultural_organizations": {"category": TableCategory.COMMUNITY_COLLABORATIVE},
    "collective_activities": {"category": TableCategory.COMMUNITY_COLLABORATIVE},
    "research_projects": {"category": TableCategory.COMMUNITY_COLLABORATIVE},
    "research_consents": {"category": TableCategory.COMMUNITY_COLLABORATIVE},
    "dataset_contributions": {"category": TableCategory.COMMUNITY_COLLABORATIVE},
    "annotation_tasks": {"category": TableCategory.COMMUNITY_COLLABORATIVE},
    "annotation_records": {"category": TableCategory.COMMUNITY_COLLABORATIVE},
    "regional_signals": {"category": TableCategory.COMMUNITY_COLLABORATIVE},
    "regional_signal_evidences": {"category": TableCategory.COMMUNITY_COLLABORATIVE},
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
        logger.warning(f"Could not apply PostgreSQL RLS runtime configuration: {exc}")


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
    """
    if category == TableCategory.TENANT_DIRECT:
        return f"""
-- Table: {table_name} (Direct Tenant Isolation)
ALTER TABLE {table_name} ENABLE ROW LEVEL SECURITY;
ALTER TABLE {table_name} FORCE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS {table_name}_tenant_isolation_policy ON {table_name};
CREATE POLICY {table_name}_tenant_isolation_policy ON {table_name}
    AS RESTRICTIVE
    FOR ALL
    TO PUBLIC
    USING (
        current_setting('app.is_admin', true) = 'true'
        OR {column_name}::text = current_setting('app.current_tenant_id', true)
    )
    WITH CHECK (
        current_setting('app.is_admin', true) = 'true'
        OR {column_name}::text = current_setting('app.current_tenant_id', true)
    );
"""
    elif category == TableCategory.USER_OWNED:
        return f"""
-- Table: {table_name} (User-Owned Isolation)
ALTER TABLE {table_name} ENABLE ROW LEVEL SECURITY;
ALTER TABLE {table_name} FORCE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS {table_name}_user_isolation_policy ON {table_name};
CREATE POLICY {table_name}_user_isolation_policy ON {table_name}
    AS RESTRICTIVE
    FOR ALL
    TO PUBLIC
    USING (
        current_setting('app.is_admin', true) = 'true'
        OR {column_name}::text = current_setting('app.current_user_id', true)
    )
    WITH CHECK (
        current_setting('app.is_admin', true) = 'true'
        OR {column_name}::text = current_setting('app.current_user_id', true)
    );
"""
    elif category == TableCategory.SHARED_REFERENCE:
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
    AS RESTRICTIVE
    FOR ALL
    TO PUBLIC
    USING (current_setting('app.is_admin', true) = 'true')
    WITH CHECK (current_setting('app.is_admin', true) = 'true');
"""
    return ""
