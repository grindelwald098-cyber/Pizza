"""add guests table and link carts 1:1

Revision ID: e9f0a1b2c3d4
Revises: d8e9f0a1b2c3
Create Date: 2026-09-11 15:50:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "e9f0a1b2c3d4"
down_revision: Union[str, Sequence[str], None] = "d8e9f0a1b2c3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "guests",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("token", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("token", name="uq_guests_token"),
    )

    op.add_column("carts", sa.Column("guest_id", sa.UUID(), nullable=True))
    op.create_unique_constraint("uq_carts_guest_id", "carts", ["guest_id"])
    op.create_foreign_key("fk_carts_guest_id", "carts", "guests", ["guest_id"], ["id"])

    # Перенос существующих гостевых корзин: guest_token → guests.token + carts.guest_id
    op.execute(
        """
        INSERT INTO guests (id, token, created_at, updated_at)
        SELECT gen_random_uuid(), guest_token, created_at, updated_at
        FROM carts
        WHERE guest_token IS NOT NULL
        """
    )
    op.execute(
        """
        UPDATE carts AS c
        SET guest_id = g.id
        FROM guests AS g
        WHERE c.guest_token = g.token
        """
    )

    op.drop_constraint("uq_carts_guest_token", "carts", type_="unique")
    op.drop_column("carts", "guest_token")


def downgrade() -> None:
    op.add_column("carts", sa.Column("guest_token", sa.String(length=64), nullable=True))
    op.create_unique_constraint("uq_carts_guest_token", "carts", ["guest_token"])

    op.execute(
        """
        UPDATE carts AS c
        SET guest_token = g.token
        FROM guests AS g
        WHERE c.guest_id = g.id
        """
    )

    op.drop_constraint("fk_carts_guest_id", "carts", type_="foreignkey")
    op.drop_constraint("uq_carts_guest_id", "carts", type_="unique")
    op.drop_column("carts", "guest_id")
    op.drop_table("guests")
