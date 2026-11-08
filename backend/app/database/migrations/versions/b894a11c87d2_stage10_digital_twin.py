"""stage10_digital_twin

Revision ID: b894a11c87d2
Revises: e738192a54b1
Create Date: 2026-11-08 10:42:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from backend.app.database.base import Base
import backend.app.models  # Registers Stage 10 entities


# revision identifiers, used by Alembic.
revision: str = 'b894a11c87d2'
down_revision: Union[str, None] = 'e738192a54b1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    # Idempotently creates Stage 10 tables (farm_twins, simulation_scenarios, optimization_problems, crop_tasks, decision_records, etc.)
    Base.metadata.create_all(bind=bind)


def downgrade() -> None:
    pass
