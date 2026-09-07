"""update sizes structure

Revision ID: 8bf8674cdd61
Revises: a1b2c3d4e5f6
Create Date: 2026-09-07 10:56:43.923407

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8bf8674cdd61'
down_revision: Union[str, Sequence[str], None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Добавляем новые поля временно nullable
    op.add_column(
        "sizes",
        sa.Column("value", sa.Integer(), nullable=True),
    )
    op.add_column(
        "sizes",
        sa.Column("unit", sa.String(length=10), nullable=True),
    )

    # 2. Переносим старые данные
    op.execute(
        """
        UPDATE sizes
        SET value = diameter,
            unit = 'cm'
        """
    )

    # 3. Теперь данные заполнены — запрещаем NULL
    op.alter_column(
        "sizes",
        "value",
        existing_type=sa.Integer(),
        nullable=False,
    )
    op.alter_column(
        "sizes",
        "unit",
        existing_type=sa.String(length=10),
        nullable=False,
    )

    # 4. Удаляем старое поле
    op.drop_column("sizes", "diameter")


def downgrade() -> None:
    op.add_column(
        "sizes",
        sa.Column("diameter", sa.Integer(), nullable=True),
    )

    op.execute(
        """
        UPDATE sizes
        SET diameter = value
        """
    )

    op.alter_column(
        "sizes",
        "diameter",
        existing_type=sa.Integer(),
        nullable=False,
    )

    op.drop_column("sizes", "unit")
    op.drop_column("sizes", "value")
