"""require one default size and dough per product

Revision ID: d5e6f7a8b9c0
Revises: c4d5e6f7a8b9
Create Date: 2026-10-19 17:20:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "d5e6f7a8b9c0"
down_revision: Union[str, Sequence[str], None] = "c4d5e6f7a8b9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "product_sizes",
        sa.Column(
            "is_default",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )

    op.execute(
        """
        DELETE FROM product_sizes AS extra
        USING product_sizes AS kept
        WHERE extra.product_id = kept.product_id
          AND extra.size_id = kept.size_id
          AND extra.id > kept.id
        """
    )
    op.execute(
        """
        DELETE FROM product_doughs AS extra
        USING product_doughs AS kept
        WHERE extra.product_id = kept.product_id
          AND extra.dough_type_id = kept.dough_type_id
          AND extra.id > kept.id
        """
    )
    op.execute(
        """
        WITH ranked AS (
            SELECT
                ps.id,
                ROW_NUMBER() OVER (
                    PARTITION BY ps.product_id
                    ORDER BY ps.is_available DESC, COALESCE(s.sort_order, 0) ASC, ps.id ASC
                ) AS rn
            FROM product_sizes AS ps
            LEFT JOIN sizes AS s ON s.id = ps.size_id
        )
        UPDATE product_sizes AS ps
        SET is_default = (ranked.rn = 1)
        FROM ranked
        WHERE ps.id = ranked.id
        """
    )
    op.execute(
        """
        WITH ranked AS (
            SELECT
                pd.id,
                ROW_NUMBER() OVER (
                    PARTITION BY pd.product_id
                    ORDER BY pd.is_default DESC, COALESCE(dt.sort_order, 0) ASC, pd.id ASC
                ) AS rn
            FROM product_doughs AS pd
            LEFT JOIN dough_types AS dt ON dt.id = pd.dough_type_id
        )
        UPDATE product_doughs AS pd
        SET is_default = (ranked.rn = 1)
        FROM ranked
        WHERE pd.id = ranked.id
        """
    )

    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1
                FROM product_sizes
                GROUP BY product_id
                HAVING COUNT(*) FILTER (WHERE is_default) <> 1
            ) THEN
                RAISE EXCEPTION 'product_sizes must contain exactly one default per product';
            END IF;

            IF EXISTS (
                SELECT 1
                FROM product_doughs
                GROUP BY product_id
                HAVING COUNT(*) FILTER (WHERE is_default) <> 1
            ) THEN
                RAISE EXCEPTION 'product_doughs must contain exactly one default per product';
            END IF;
        END $$
        """
    )
    op.alter_column("product_sizes", "is_default", server_default=None)
    op.create_unique_constraint(
        "uq_product_sizes_product_id_size_id",
        "product_sizes",
        ["product_id", "size_id"],
    )
    op.create_unique_constraint(
        "uq_product_doughs_product_id_dough_type_id",
        "product_doughs",
        ["product_id", "dough_type_id"],
    )

    op.execute("CREATE EXTENSION IF NOT EXISTS btree_gist")
    op.execute(
        """
        ALTER TABLE product_sizes
        ADD CONSTRAINT uq_product_sizes_one_default
        EXCLUDE USING gist (product_id WITH =) WHERE (is_default)
        DEFERRABLE INITIALLY DEFERRED
        """
    )
    op.execute(
        """
        ALTER TABLE product_doughs
        ADD CONSTRAINT uq_product_doughs_one_default
        EXCLUDE USING gist (product_id WITH =) WHERE (is_default)
        DEFERRABLE INITIALLY DEFERRED
        """
    )
    op.execute(
        """
        CREATE OR REPLACE FUNCTION enforce_product_option_default()
        RETURNS trigger
        LANGUAGE plpgsql
        AS $$
        DECLARE
            product_ids uuid[];
            product uuid;
            total_count integer;
            default_count integer;
        BEGIN
            IF TG_OP = 'DELETE' THEN
                product_ids := ARRAY[OLD.product_id];
            ELSIF TG_OP = 'UPDATE' AND OLD.product_id IS DISTINCT FROM NEW.product_id THEN
                product_ids := ARRAY[OLD.product_id, NEW.product_id];
            ELSE
                product_ids := ARRAY[NEW.product_id];
            END IF;

            FOREACH product IN ARRAY product_ids
            LOOP
                IF TG_TABLE_NAME = 'product_sizes' THEN
                    SELECT COUNT(*), COUNT(*) FILTER (WHERE is_default)
                    INTO total_count, default_count
                    FROM product_sizes
                    WHERE product_id = product;
                ELSE
                    SELECT COUNT(*), COUNT(*) FILTER (WHERE is_default)
                    INTO total_count, default_count
                    FROM product_doughs
                    WHERE product_id = product;
                END IF;

                IF total_count > 0 AND default_count <> 1 THEN
                    RAISE EXCEPTION
                        '% for product % must contain exactly one default',
                        TG_TABLE_NAME, product
                        USING ERRCODE = '23514';
                END IF;
            END LOOP;

            RETURN NULL;
        END;
        $$
        """
    )
    op.execute(
        """
        CREATE CONSTRAINT TRIGGER product_sizes_one_default
        AFTER INSERT OR UPDATE OR DELETE ON product_sizes
        DEFERRABLE INITIALLY DEFERRED
        FOR EACH ROW
        EXECUTE FUNCTION enforce_product_option_default()
        """
    )
    op.execute(
        """
        CREATE CONSTRAINT TRIGGER product_doughs_one_default
        AFTER INSERT OR UPDATE OR DELETE ON product_doughs
        DEFERRABLE INITIALLY DEFERRED
        FOR EACH ROW
        EXECUTE FUNCTION enforce_product_option_default()
        """
    )


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS product_doughs_one_default ON product_doughs")
    op.execute("DROP TRIGGER IF EXISTS product_sizes_one_default ON product_sizes")
    op.execute("DROP FUNCTION IF EXISTS enforce_product_option_default()")
    op.execute(
        "ALTER TABLE product_doughs DROP CONSTRAINT IF EXISTS uq_product_doughs_one_default"
    )
    op.execute(
        "ALTER TABLE product_sizes DROP CONSTRAINT IF EXISTS uq_product_sizes_one_default"
    )
    op.drop_constraint(
        "uq_product_doughs_product_id_dough_type_id",
        "product_doughs",
        type_="unique",
    )
    op.drop_constraint(
        "uq_product_sizes_product_id_size_id",
        "product_sizes",
        type_="unique",
    )
    op.drop_column("product_sizes", "is_default")
