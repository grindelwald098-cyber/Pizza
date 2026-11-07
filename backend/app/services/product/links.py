"""Связи товара: одна синхронизация и отдельная политика на каждый тип строки."""

from abc import ABC, abstractmethod
from typing import ClassVar, Generic, TypeVar
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.product_dough import ProductDough
from app.database.models.product_ingredients import ProductIngredient
from app.database.models.product_sizes import ProductSize
from app.schemas.product_dough_types import ProductDoughTypeCreate
from app.schemas.product_ingredients import ProductIngredientCreate
from app.schemas.product_sizes import ProductSizeCreate

RowT = TypeVar("RowT")
SpecT = TypeVar("SpecT")


class ProductLink(ABC, Generic[RowT, SpecT]):
    """Как собрать, обновить и снять строку связи."""

    label: ClassVar[str]
    unique_label: ClassVar[str]

    @abstractmethod
    def item_id(self, spec: SpecT) -> UUID:
        """Идентификатор справочника в запросе."""

    @abstractmethod
    def row_id(self, row: RowT) -> UUID:
        """Идентификатор справочника у уже сохранённой строки."""

    @abstractmethod
    def build(self, spec: SpecT) -> RowT:
        """Новая строка связи."""

    @abstractmethod
    def apply(self, row: RowT, spec: SpecT) -> None:
        """Перенести поля запроса в существующую строку."""

    @abstractmethod
    def retire(self, row: RowT) -> bool:
        """True — строку нужно удалить. False — связь уже скрыта на самой строке."""


class SizeLink(ProductLink[ProductSize, ProductSizeCreate]):
    label = "size"
    unique_label = "size"

    def item_id(self, spec: ProductSizeCreate) -> UUID:
        return spec.size_id

    def row_id(self, row: ProductSize) -> UUID:
        return row.size_id

    def build(self, spec: ProductSizeCreate) -> ProductSize:
        return ProductSize(
            size_id=spec.size_id,
            price=spec.price,
            is_available=spec.is_available,
            is_default=spec.is_default,
        )

    def apply(self, row: ProductSize, spec: ProductSizeCreate) -> None:
        row.price = spec.price
        row.is_available = spec.is_available
        row.is_default = spec.is_default

    def retire(self, row: ProductSize) -> bool:
        row.is_available = False
        row.is_default = False
        return False


class DoughLink(ProductLink[ProductDough, ProductDoughTypeCreate]):
    label = "dough_type"
    unique_label = "dough type"

    def item_id(self, spec: ProductDoughTypeCreate) -> UUID:
        return spec.dough_type_id

    def row_id(self, row: ProductDough) -> UUID:
        return row.dough_type_id

    def build(self, spec: ProductDoughTypeCreate) -> ProductDough:
        return ProductDough(
            dough_type_id=spec.dough_type_id,
            is_default=bool(spec.is_default),
        )

    def apply(self, row: ProductDough, spec: ProductDoughTypeCreate) -> None:
        row.is_default = bool(spec.is_default)

    def retire(self, row: ProductDough) -> bool:
        return True


class IngredientLink(ProductLink[ProductIngredient, ProductIngredientCreate]):
    label = "ingredient"
    unique_label = "ingredient"

    def item_id(self, spec: ProductIngredientCreate) -> UUID:
        return spec.ingredient_id

    def row_id(self, row: ProductIngredient) -> UUID:
        return row.ingredient_id

    def build(self, spec: ProductIngredientCreate) -> ProductIngredient:
        return ProductIngredient(
            ingredient_id=spec.ingredient_id,
            quantity=spec.quantity,
            is_default=spec.is_default,
        )

    def apply(self, row: ProductIngredient, spec: ProductIngredientCreate) -> None:
        row.quantity = spec.quantity
        row.is_default = spec.is_default
        row.is_active = True

    def retire(self, row: ProductIngredient) -> bool:
        row.is_active = False
        return False


size_link = SizeLink()
dough_link = DoughLink()
ingredient_link = IngredientLink()


async def sync_rows(
    session: AsyncSession,
    rows: list[RowT],
    incoming: list[SpecT],
    link: ProductLink[RowT, SpecT],
) -> None:
    current = {link.row_id(row): row for row in rows}
    incoming_ids = {link.item_id(item) for item in incoming}

    for row in list(rows):
        if link.row_id(row) in incoming_ids:
            continue
        if link.retire(row):
            rows.remove(row)
            await session.delete(row)

    for item in incoming:
        row = current.get(link.item_id(item))
        if row is None:
            rows.append(link.build(item))
        else:
            link.apply(row, item)
