"""stage13_climate_resilient_sustainability

Revision ID: e3894a11c87d
Revises: d2894a11c87d
Create Date: 2026-11-08 12:05:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from backend.app.database.base import Base
import backend.app.models  # Registers Stage 13 entities (soil_profiles, soil_samples, soil_test_results, water_sources, irrigation_events, soil_moisture_observations, water_balance_snapshots, climate_baselines, climate_exposure_assessments, climate_adaptation_scenarios, nutrient_assessments, nutrient_expert_reviews, agricultural_practice_definitions, farm_practice_records, soil_carbon_measurements, environmental_accounting_estimates, resilience_assessments, resilience_scenario_simulations)


# revision identifiers, used by Alembic.
revision: str = 'e3894a11c87d'
down_revision: Union[str, None] = 'd2894a11c87d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    # Idempotently creates Stage 13 tables across Soil, Water, Climate, Nutrient, Sustain, and Resilience
    Base.metadata.create_all(bind=bind)


def downgrade() -> None:
    pass
