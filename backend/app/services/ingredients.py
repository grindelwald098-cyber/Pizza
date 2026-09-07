from app.repositories.ingredients import IngredientsRepository
from sqlalchemy.orm import Session
from app.schemas.ingredients import IngredientCreate, IngredientResponse
from app.database.models.ingredient import Ingredient
from uuid import UUID

class IngredientsService:
    def __init__(self, session: Session):
        self.repository = IngredientsRepository(session)

    def get_all(self) -> list[Ingredient]:
        return self.repository.get_all()

    def get_by_id(self, id: UUID) -> Ingredient | None:
        return self.repository.get_by_id(id)

    def create(self, data: IngredientCreate) -> Ingredient:
        return self.repository.create(data)

    def create_many(self, data: list[IngredientCreate]) -> list[Ingredient]:
        ingredients = [Ingredient(
            name=item.name,
            description=item.description,
            price=item.price,
            image_url=item.image_url,
            is_available=item.is_available
        ) for item in data]
        return self.repository.create_many(ingredients)

    def delete(self, id: UUID) -> None:
        return self.repository.delete(id)