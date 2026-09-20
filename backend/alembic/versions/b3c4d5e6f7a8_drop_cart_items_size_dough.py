"""drop size_id and dough_type_id from cart_items

Revision ID: b3c4d5e6f7a8
Revises: a2b3c4d5e6f7
Create Date: 2026-09-17 13:20:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b3c4d5e6f7a8"
down_revision: Union[str, Sequence[str], None] = "a2b3c4d5e6f7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint("fk_cart_items_dough_type_id", "cart_items", type_="foreignkey")
    op.drop_constraint("fk_cart_items_size_id", "cart_items", type_="foreignkey")
    op.drop_column("cart_items", "dough_type_id")
    op.drop_column("cart_items", "size_id")


def downgrade() -> None:
    op.add_column("cart_items", sa.Column("size_id", sa.UUID(), nullable=True))
    op.add_column("cart_items", sa.Column("dough_type_id", sa.UUID(), nullable=True))
    op.create_foreign_key("fk_cart_items_size_id", "cart_items", "sizes", ["size_id"], ["id"])
    op.create_foreign_key(
        "fk_cart_items_dough_type_id", "cart_items", "dough_types", ["dough_type_id"], ["id"]
    )
