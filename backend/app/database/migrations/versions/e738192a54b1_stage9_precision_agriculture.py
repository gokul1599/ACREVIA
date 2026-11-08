"""stage9_precision_agriculture

Revision ID: e738192a54b1
Revises: f043516098f8
Create Date: 2026-11-08 10:18:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from backend.app.database.base import Base
import backend.app.models  # Registers Stage 9 entities


# revision identifiers, used by Alembic.
revision: str = 'e738192a54b1'
down_revision: Union[str, None] = 'f043516098f8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    # Idempotently creates Stage 9 tables (plot_geometries, satellite_observations, sensor_devices, etc.)
    Base.metadata.create_all(bind=bind)


def downgrade() -> None:
    pass
