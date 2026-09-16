"""drop guests.token (JWT auth uses guest id)

Revision ID: a2b3c4d5e6f7
Revises: f0a1b2c3d4e5
Create Date: 2026-09-15 17:36:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a2b3c4d5e6f7"
down_revision: Union[str, Sequence[str], None] = "f0a1b2c3d4e5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint("uq_guests_token", "guests", type_="unique")
    op.drop_column("guests", "token")


def downgrade() -> None:
    op.add_column("guests", sa.Column("token", sa.String(length=64), nullable=True))
    op.execute(
        """
        UPDATE guests
        SET token = replace(id::text, '-', '')
        WHERE token IS NULL
        """
    )
    op.alter_column("guests", "token", nullable=False)
    op.create_unique_constraint("uq_guests_token", "guests", ["token"])
