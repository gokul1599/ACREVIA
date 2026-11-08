"""stage11_agricultural_economics

Revision ID: c1894a11c87d
Revises: b894a11c87d2
Create Date: 2026-11-08 11:15:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from backend.app.database.base import Base
import backend.app.models  # Registers Stage 11 entities (farm_expenses, sale_transactions, market_locations, harvest_sessions, produce_lots, crop_season_economics, etc.)


# revision identifiers, used by Alembic.
revision: str = 'c1894a11c87d'
down_revision: Union[str, None] = 'b894a11c87d2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    # Idempotently creates Stage 11 tables (farm_expenses, financial_corrections, sale_transactions,
    # market_locations, market_commodities, market_price_observations, harvest_plans, harvest_sessions,
    # produce_quality_profiles, quality_measurements, storage_locations, storage_lots, produce_lots,
    # lot_movements, crop_season_economics, crop_loss_evidence_packages)
    Base.metadata.create_all(bind=bind)


def downgrade() -> None:
    pass
