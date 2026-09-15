"""align roles and permissions schema

Revision ID: c7d8e9f0a1b2
Revises: 5b3a44856af7
Create Date: 2026-09-10 19:55:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c7d8e9f0a1b2"
down_revision: Union[str, Sequence[str], None] = "5b3a44856af7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column("roles", "is_active")
    op.drop_column("roles", "updated_at")
    op.create_unique_constraint("uq_roles_name", "roles", ["name"])
    op.create_unique_constraint("uq_permissions_name", "permissions", ["name"])


def downgrade() -> None:
    op.drop_constraint("uq_permissions_name", "permissions", type_="unique")
    op.drop_constraint("uq_roles_name", "roles", type_="unique")
    op.add_column(
        "roles",
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.add_column(
        "roles",
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    op.alter_column("roles", "updated_at", server_default=None)
    op.alter_column("roles", "is_active", server_default=None)
