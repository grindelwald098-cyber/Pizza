from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.ingredient import Ingredient
from app.repositories.ingredients import IngredientsRepository
from app.schemas.ingredients import IngredientCreate


class IngredientsService:

    def __init__(self, session: AsyncSession):
        self.repository = IngredientsRepository(session)

    async def get_all(self) -> list[Ingredient]:
        return await self.repository.get_all()

    async def get_by_id(self, id: UUID) -> Ingredient:
        ingredient = await self.repository.get_by_id(id)

        if not ingredient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ingredient not found",
            )

        return ingredient

    async def create(self, data: IngredientCreate) -> Ingredient:
        ingredient = Ingredient(
            name=data.name,
            description=data.description,
            price=data.price,
            image_url=data.image_url,
            is_available=data.is_available,
        )

        return await self.repository.create(ingredient)

    async def create_many(self, data: list[IngredientCreate]) -> list[Ingredient]:
        ingredients = [
            Ingredient(
                name=item.name,
                description=item.description,
                price=item.price,
                image_url=item.image_url,
                is_available=item.is_available,
            )
            for item in data
        ]

        return await self.repository.create_many(ingredients)

    async def delete(self, id: UUID) -> None:
        ingredient = await self.get_by_id(id)
        await self.repository.delete(ingredient)
