"""enable_postgresql_rls_tenant_isolation

Revision ID: a1089411c87d
Revises: f4894a11c87d
Create Date: 2026-11-09 16:30:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

from backend.app.database.rls import TABLE_CLASSIFICATION, TableCategory, generate_rls_ddl


# revision identifiers, used by Alembic.
revision: str = 'a1089411c87d'
down_revision: Union[str, None] = 'f4894a11c87d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        # Safe dialect guard: RLS policies are PostgreSQL-specific
        print(f"[RLS Migration] Current dialect is '{bind.dialect.name}'. Skipping PostgreSQL RLS DDL execution.")
        return

    print("[RLS Migration] Enabling PostgreSQL Row-Level Security across classified tables...")
    for table_name, meta in TABLE_CLASSIFICATION.items():
        category = meta.get("category")
        col = meta.get("column", "farm_id")
        if category in (TableCategory.TENANT_DIRECT, TableCategory.USER_OWNED, TableCategory.SHARED_REFERENCE):
            ddl = generate_rls_ddl(table_name, category, col)
            if ddl.strip():
                for stmt in ddl.strip().split(";"):
                    cleaned = stmt.strip()
                    if cleaned:
                        op.execute(sa.text(cleaned))


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        return

    print("[RLS Migration] Disabling PostgreSQL Row-Level Security across classified tables...")
    for table_name, meta in TABLE_CLASSIFICATION.items():
        category = meta.get("category")
        if category in (TableCategory.TENANT_DIRECT, TableCategory.USER_OWNED, TableCategory.SHARED_REFERENCE):
            op.execute(sa.text(f"ALTER TABLE {table_name} NO FORCE ROW LEVEL SECURITY;"))
            op.execute(sa.text(f"ALTER TABLE {table_name} DISABLE ROW LEVEL SECURITY;"))
