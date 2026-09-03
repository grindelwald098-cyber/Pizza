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

    def delete(self, id: UUID) -> None:
        return self.repository.delete(id)