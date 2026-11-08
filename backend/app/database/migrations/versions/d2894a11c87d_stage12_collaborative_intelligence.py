"""stage12_collaborative_intelligence

Revision ID: d2894a11c87d
Revises: c1894a11c87d
Create Date: 2026-11-08 11:35:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from backend.app.database.base import Base
import backend.app.models  # Registers Stage 12 entities (communities, posts, comments, reports, knowledge_contributions, reviews, translations, organizations, memberships, collective_activities, research_projects, consents, datasets, annotation_tasks, annotation_records, learning_resources, training_events, event_registrations, learning_feedback, regional_signals, regional_signal_evidences)


# revision identifiers, used by Alembic.
revision: str = 'd2894a11c87d'
down_revision: Union[str, None] = 'c1894a11c87d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    # Idempotently creates Stage 12 tables across Connect, Commons, Collectives, Research, Extension, and Regional Pulse
    Base.metadata.create_all(bind=bind)


def downgrade() -> None:
    pass
