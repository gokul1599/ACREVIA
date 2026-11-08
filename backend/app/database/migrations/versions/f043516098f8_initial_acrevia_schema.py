"""initial_acrevia_schema

Revision ID: f043516098f8
Revises: 
Create Date: 2026-11-08 09:41:40.484426

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from backend.app.database.base import Base
import backend.app.models  # Registers all 32 entities


# revision identifiers, used by Alembic.
revision: str = 'f043516098f8'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    # Create all domain tables if they do not already exist (idempotent for fresh Neon PostgreSQL setups)
    Base.metadata.create_all(bind=bind)


def downgrade() -> None:
    bind = op.get_bind()
    Base.metadata.drop_all(bind=bind)

