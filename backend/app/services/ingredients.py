from app.database.models.ingredient import Ingredient
from app.repositories.ingredients import IngredientsRepository
from app.schemas.ingredients import IngredientCreate
from app.services.crud import CrudService


class IngredientsService(CrudService[Ingredient, IngredientCreate]):
    repository_cls = IngredientsRepository
    not_found_detail = "Ingredient not found"

    def build(self, data: IngredientCreate) -> Ingredient:
        return Ingredient(
            name=data.name,
            description=data.description,
            price=data.price,
            image_url=data.image_url,
            is_available=data.is_available,
        )

    async def create_many(self, data: list[IngredientCreate]) -> list[Ingredient]:
        return await self.repository.create_many([self.build(item) for item in data])
