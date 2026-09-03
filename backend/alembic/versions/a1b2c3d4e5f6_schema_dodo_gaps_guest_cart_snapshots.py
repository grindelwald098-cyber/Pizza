"""schema dodo gaps: guest cart, snapshots, FKs, order status seed

Revision ID: a1b2c3d4e5f6
Revises: 7820a7fcf215
Create Date: 2026-08-30 16:10:00.000000

"""
from typing import Sequence, Union
import uuid as uuid_mod

from alembic import op
import sqlalchemy as sa


revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, Sequence[str], None] = "7820a7fcf215"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


ORDER_STATUSES = [
    ("new", "Новый", "Заказ создан"),
    ("confirmed", "Подтверждён", "Заказ подтверждён"),
    ("cooking", "Готовится", "Заказ на кухне"),
    ("ready", "Готов", "Заказ готов к выдаче или доставке"),
    ("delivering", "В пути", "Курьер везёт заказ"),
    ("completed", "Выполнен", "Заказ доставлен или выдан"),
    ("cancelled", "Отменён", "Заказ отменён"),
]


def upgrade() -> None:
    # --- carts: гостевая корзина ---
    op.add_column("carts", sa.Column("guest_token", sa.String(length=64), nullable=True))
    op.create_unique_constraint("uq_carts_guest_token", "carts", ["guest_token"])
    op.alter_column("carts", "user_id", existing_type=sa.UUID(), nullable=True)

    # --- cart_items: размер и тесто ---
    op.add_column("cart_items", sa.Column("size_id", sa.UUID(), nullable=True))
    op.add_column("cart_items", sa.Column("dough_type_id", sa.UUID(), nullable=True))
    op.create_foreign_key("fk_cart_items_size_id", "cart_items", "sizes", ["size_id"], ["id"])
    op.create_foreign_key(
        "fk_cart_items_dough_type_id", "cart_items", "dough_types", ["dough_type_id"], ["id"]
    )

    # --- order_items: размер, тесто, snapshot названий ---
    op.add_column("order_items", sa.Column("size_id", sa.UUID(), nullable=True))
    op.add_column("order_items", sa.Column("dough_type_id", sa.UUID(), nullable=True))
    op.add_column(
        "order_items",
        sa.Column("product_name", sa.String(length=255), nullable=False, server_default=""),
    )
    op.add_column("order_items", sa.Column("size_name", sa.String(length=255), nullable=True))
    op.add_column("order_items", sa.Column("dough_type_name", sa.String(length=255), nullable=True))
    op.create_foreign_key("fk_order_items_size_id", "order_items", "sizes", ["size_id"], ["id"])
    op.create_foreign_key(
        "fk_order_items_dough_type_id", "order_items", "dough_types", ["dough_type_id"], ["id"]
    )
    op.alter_column("order_items", "product_name", server_default=None)

    # --- snapshot допов в заказе ---
    op.create_table(
        "order_item_added_ingredients",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("order_item_id", sa.UUID(), nullable=False),
        sa.Column("ingredient_id", sa.UUID(), nullable=False),
        sa.Column("ingredient_name", sa.String(length=255), nullable=False),
        sa.Column("price", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.ForeignKeyConstraint(["ingredient_id"], ["ingredients.id"]),
        sa.ForeignKeyConstraint(["order_item_id"], ["order_items.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    # --- addresses.is_default ---
    op.add_column(
        "addresses",
        sa.Column("is_default", sa.Boolean(), nullable=False, server_default=sa.text("false")),
    )
    op.alter_column("addresses", "is_default", server_default=None)

    # --- favorites / reviews / notifications (ранее миграция была пустой) ---
    op.create_table(
        "favorites",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("product_id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "product_id", name="uq_favorites_user_product"),
    )
    op.create_table(
        "reviews",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("product_id", sa.UUID(), nullable=False),
        sa.Column("rating", sa.Integer(), nullable=False),
        sa.Column("comment", sa.Text(), nullable=False),
        sa.Column("is_published", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "notifications",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("type", sa.String(length=255), nullable=False),
        sa.Column("is_read", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("read_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    # --- promocode_usages: FK ---
    op.create_foreign_key(
        "fk_promocode_usages_promocode_id", "promocode_usages", "promocodes", ["promocode_id"], ["id"]
    )
    op.create_foreign_key(
        "fk_promocode_usages_user_id", "promocode_usages", "users", ["user_id"], ["id"]
    )
    op.create_foreign_key(
        "fk_promocode_usages_order_id", "promocode_usages", "orders", ["order_id"], ["id"]
    )

    # --- seed order statuses (не дублируем, если уже есть) ---
    order_statuses = sa.table(
        "order_statuses",
        sa.column("id", sa.UUID()),
        sa.column("name", sa.String()),
        sa.column("code", sa.String()),
        sa.column("description", sa.Text()),
        sa.column("is_active", sa.Boolean()),
    )
    conn = op.get_bind()
    existing = {
        row[0]
        for row in conn.execute(sa.text("SELECT code FROM order_statuses")).fetchall()
    }
    rows = [
        {
            "id": str(uuid_mod.uuid4()),
            "name": name,
            "code": code,
            "description": description,
            "is_active": True,
        }
        for code, name, description in ORDER_STATUSES
        if code not in existing
    ]
    if rows:
        op.bulk_insert(order_statuses, rows)


def downgrade() -> None:
    op.execute(
        sa.text(
            "DELETE FROM order_statuses WHERE code IN "
            "('new', 'confirmed', 'cooking', 'ready', 'delivering', 'completed', 'cancelled')"
        )
    )

    op.drop_constraint("fk_promocode_usages_order_id", "promocode_usages", type_="foreignkey")
    op.drop_constraint("fk_promocode_usages_user_id", "promocode_usages", type_="foreignkey")
    op.drop_constraint("fk_promocode_usages_promocode_id", "promocode_usages", type_="foreignkey")

    op.drop_table("notifications")
    op.drop_table("reviews")
    op.drop_table("favorites")

    op.drop_column("addresses", "is_default")

    op.drop_table("order_item_added_ingredients")

    op.drop_constraint("fk_order_items_dough_type_id", "order_items", type_="foreignkey")
    op.drop_constraint("fk_order_items_size_id", "order_items", type_="foreignkey")
    op.drop_column("order_items", "dough_type_name")
    op.drop_column("order_items", "size_name")
    op.drop_column("order_items", "product_name")
    op.drop_column("order_items", "dough_type_id")
    op.drop_column("order_items", "size_id")

    op.drop_constraint("fk_cart_items_dough_type_id", "cart_items", type_="foreignkey")
    op.drop_constraint("fk_cart_items_size_id", "cart_items", type_="foreignkey")
    op.drop_column("cart_items", "dough_type_id")
    op.drop_column("cart_items", "size_id")

    op.alter_column("carts", "user_id", existing_type=sa.UUID(), nullable=False)
    op.drop_constraint("uq_carts_guest_token", "carts", type_="unique")
    op.drop_column("carts", "guest_token")
