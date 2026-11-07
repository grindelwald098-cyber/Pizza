from app.database.models.ingredient import Ingredient
from app.repositories.base import BaseRepository


class IngredientsRepository(BaseRepository[Ingredient]):
    model = Ingredient
