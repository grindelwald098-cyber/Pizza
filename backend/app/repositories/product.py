from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from app.database.models.product import Product
from app.database.models.product_addons import ProductAddon
from app.database.models.product_dough import ProductDough
from app.database.models.product_ingredients import ProductIngredient
from app.database.models.product_sizes import ProductSize
from app.exceptions import InternalError
from app.repositories.base import SoftDeleteRepository


class ProductRepository(SoftDeleteRepository[Product]):
    model = Product

    @staticmethod
    def _load_options() -> tuple[Any, ...]:
        return (
            selectinload(Product.category),
            selectinload(Product.sizes).selectinload(ProductSize.size),
            selectinload(Product.doughs).selectinload(ProductDough.dough_type),
            selectinload(Product.ingredients).selectinload(
                ProductIngredient.ingredient
            ),
            selectinload(Product.addons).selectinload(ProductAddon.ingredient),
        )

    @staticmethod
    def _cart_config_options() -> tuple[Any, ...]:
        return (
            selectinload(Product.sizes).selectinload(ProductSize.size),
            selectinload(Product.doughs).selectinload(ProductDough.dough_type),
            selectinload(Product.addons).selectinload(ProductAddon.ingredient),
        )

    async def list_page(
        self,
        *,
        category_id: UUID | None,
        limit: int,
        offset: int,
    ) -> tuple[list[Product], int]:
        filters = [Product.is_active.is_(True)]
        if category_id is not None:
            filters.append(Product.category_id == category_id)

        total = await self.session.scalar(
            select(func.count()).select_from(Product).where(*filters)
        )
        statement = (
            select(Product)
            .where(*filters)
            .order_by(Product.name)
            .limit(limit)
            .offset(offset)
            .options(*self._load_options())
        )
        products = await self._list(statement)
        return products, int(total or 0)

    async def get_by_id(self, entity_id: UUID) -> Product | None:
        statement = self._select().where(
            Product.id == entity_id,
            Product.is_active.is_(True),
        )
        return await self.session.scalar(statement)

    async def get_by_id_for_cart(self, entity_id: UUID) -> Product | None:
        statement = (
            select(Product)
            .where(Product.id == entity_id, Product.is_active.is_(True))
            .options(*self._cart_config_options())
        )
        return await self.session.scalar(statement)

    async def create(self, product: Product) -> Product:
        await self._persist(product)
        loaded = await self.get_by_id(product.id)
        if loaded is None:
            raise InternalError("Product was created but could not be loaded")
        return loaded
