"""stage14_interoperability_ecosystem

Revision ID: f4894a11c87d
Revises: e3894a11c87d
Create Date: 2026-11-08 13:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from backend.app.database.base import Base
import backend.app.models  # Registers Stage 14 entities (integration_partners, partner_integrations, api_applications, api_credentials, data_sharing_grants, webhook_endpoints, webhook_events, webhook_deliveries, data_exchange_jobs, data_mapping_profiles)


# revision identifiers, used by Alembic.
revision: str = 'f4894a11c87d'
down_revision: Union[str, None] = 'e3894a11c87d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    # Idempotently creates Stage 14 tables across Partners, Integrations, Developer API Apps, Grants, Webhooks, and Data Exchange
    Base.metadata.create_all(bind=bind)


def downgrade() -> None:
    pass
