from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database.models.product import Product
from app.database.models.product_dough import ProductDough
from app.database.models.product_ingredients import ProductIngredient
from app.database.models.product_sizes import ProductSize


class ProductRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    @staticmethod
    def _load_options():
        return (
            selectinload(Product.category),
            selectinload(Product.sizes).selectinload(ProductSize.size),
            selectinload(Product.doughs).selectinload(ProductDough.dough_type),
            selectinload(Product.ingredients).selectinload(ProductIngredient.ingredient),
        )

    async def get_all(self) -> list[Product]:
        query = (
            select(Product)
            .where(Product.is_active.is_(True))
            .options(*self._load_options())
        )

        result = await self.session.scalars(query)

        return list(result.all())

    async def get_by_id(self, id: UUID) -> Product | None:
        query = (
            select(Product)
            .where(Product.id == id, Product.is_active.is_(True))
            .options(*self._load_options())
        )

        return await self.session.scalar(query)

    async def create(self, product: Product) -> Product:
        self.session.add(product)

        await self.session.commit()
        await self.session.refresh(product)

        return product

    async def update(self, product: Product) -> Product:
        self.session.add(product)

        await self.session.commit()
        await self.session.refresh(product)

        return product

    async def delete(self, product: Product) -> None:
        try:
            self.session.add(product)
            await self.session.commit()

        except Exception:
            await self.session.rollback()
            raise
