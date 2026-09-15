"""invert cart ownership to users/guests.cart_id

Revision ID: f0a1b2c3d4e5
Revises: e9f0a1b2c3d4
Create Date: 2026-09-15 13:50:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "f0a1b2c3d4e5"
down_revision: Union[str, Sequence[str], None] = "e9f0a1b2c3d4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _drop_fk(table: str, column: str) -> None:
    conn = op.get_bind()
    name = conn.execute(
        sa.text(
            """
            SELECT tc.constraint_name
            FROM information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
              ON tc.constraint_name = kcu.constraint_name
             AND tc.table_schema = kcu.table_schema
            WHERE tc.table_schema = 'public'
              AND tc.table_name = :table
              AND tc.constraint_type = 'FOREIGN KEY'
              AND kcu.column_name = :column
            """
        ),
        {"table": table, "column": column},
    ).scalar()
    if name:
        op.drop_constraint(name, table, type_="foreignkey")


def _drop_unique(table: str, column: str) -> None:
    conn = op.get_bind()
    name = conn.execute(
        sa.text(
            """
            SELECT tc.constraint_name
            FROM information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
              ON tc.constraint_name = kcu.constraint_name
             AND tc.table_schema = kcu.table_schema
            WHERE tc.table_schema = 'public'
              AND tc.table_name = :table
              AND tc.constraint_type = 'UNIQUE'
              AND kcu.column_name = :column
            """
        ),
        {"table": table, "column": column},
    ).scalar()
    if name:
        op.drop_constraint(name, table, type_="unique")


def upgrade() -> None:
    op.add_column("users", sa.Column("cart_id", sa.UUID(), nullable=True))
    op.add_column("guests", sa.Column("cart_id", sa.UUID(), nullable=True))

    # Если у корзины заполнены оба FK — отдаём пользователю (guest pointer не ставим).
    op.execute(
        """
        UPDATE users AS u
        SET cart_id = c.id
        FROM carts AS c
        WHERE c.user_id = u.id
        """
    )
    op.execute(
        """
        UPDATE guests AS g
        SET cart_id = c.id
        FROM carts AS c
        WHERE c.guest_id = g.id
          AND c.user_id IS NULL
        """
    )

    op.create_unique_constraint("uq_users_cart_id", "users", ["cart_id"])
    op.create_unique_constraint("uq_guests_cart_id", "guests", ["cart_id"])
    op.create_foreign_key(
        "fk_users_cart_id",
        "users",
        "carts",
        ["cart_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        "fk_guests_cart_id",
        "guests",
        "carts",
        ["cart_id"],
        ["id"],
        ondelete="SET NULL",
    )

    _drop_fk("carts", "user_id")
    _drop_unique("carts", "user_id")
    op.drop_column("carts", "user_id")

    _drop_fk("carts", "guest_id")
    _drop_unique("carts", "guest_id")
    op.drop_column("carts", "guest_id")


def downgrade() -> None:
    op.add_column("carts", sa.Column("user_id", sa.UUID(), nullable=True))
    op.add_column("carts", sa.Column("guest_id", sa.UUID(), nullable=True))

    op.execute(
        """
        UPDATE carts AS c
        SET user_id = u.id
        FROM users AS u
        WHERE u.cart_id = c.id
        """
    )
    op.execute(
        """
        UPDATE carts AS c
        SET guest_id = g.id
        FROM guests AS g
        WHERE g.cart_id = c.id
        """
    )

    op.create_unique_constraint("carts_user_id_key", "carts", ["user_id"])
    op.create_foreign_key("carts_user_id_fkey", "carts", "users", ["user_id"], ["id"])
    op.create_unique_constraint("uq_carts_guest_id", "carts", ["guest_id"])
    op.create_foreign_key("fk_carts_guest_id", "carts", "guests", ["guest_id"], ["id"])

    op.drop_constraint("fk_guests_cart_id", "guests", type_="foreignkey")
    op.drop_constraint("uq_guests_cart_id", "guests", type_="unique")
    op.drop_column("guests", "cart_id")

    op.drop_constraint("fk_users_cart_id", "users", type_="foreignkey")
    op.drop_constraint("uq_users_cart_id", "users", type_="unique")
    op.drop_column("users", "cart_id")
