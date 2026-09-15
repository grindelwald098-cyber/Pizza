from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.ingredient import Ingredient


class IngredientsRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self) -> list[Ingredient]:
        query = select(Ingredient)

        result = await self.session.scalars(query)

        return list(result.all())

    async def get_by_id(self, id: UUID) -> Ingredient | None:
        query = select(Ingredient).where(Ingredient.id == id)

        return await self.session.scalar(query)

    async def get_existing_ids(self, ids: list[UUID]) -> set[UUID]:
        if not ids:
            return set()

        query = select(Ingredient.id).where(Ingredient.id.in_(ids))

        result = await self.session.scalars(query)

        return set(result.all())

    async def create(self, ingredient: Ingredient) -> Ingredient:
        self.session.add(ingredient)

        await self.session.commit()
        await self.session.refresh(ingredient)

        return ingredient

    async def create_many(self, ingredients: list[Ingredient]) -> list[Ingredient]:
        self.session.add_all(ingredients)

        await self.session.commit()

        for ingredient in ingredients:
            await self.session.refresh(ingredient)

        return ingredients

    async def delete(self, ingredient: Ingredient) -> None:
        try:
            await self.session.delete(ingredient)
            await self.session.commit()

        except Exception:
            await self.session.rollback()
            raise
