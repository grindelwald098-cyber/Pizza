from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.category import Category


class CategoryRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self) -> list[Category]:
        query = select(Category)

        result = await self.session.scalars(query)

        return list(result.all())

    async def get_by_id(self, id: UUID) -> Category | None:
        query = select(Category).where(Category.id == id)

        return await self.session.scalar(query)

    async def get_existing_ids(self, ids: list[UUID]) -> set[UUID]:
        if not ids:
            return set()

        query = select(Category.id).where(Category.id.in_(ids))

        result = await self.session.scalars(query)

        return set(result.all())

    async def create(self, category: Category) -> Category:
        self.session.add(category)

        await self.session.commit()
        await self.session.refresh(category)

        return category

    async def delete(self, category: Category) -> None:
        try:
            await self.session.delete(category)
            await self.session.commit()

        except Exception:
            await self.session.rollback()
            raise
