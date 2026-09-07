from sqlalchemy.orm import Session
from sqlalchemy import select
from app.database.models.ingredient import Ingredient

from uuid import UUID   

class IngredientsRepository: 

    def __init__(self, session: Session):
        self.session = session

    def get_all(self) -> list[Ingredient]:
        query = select(Ingredient)
        return self.session.scalars(query).all()

    def get_by_id(self, id: UUID) -> Ingredient | None:
        query = select(Ingredient).where(Ingredient.id == id)
        return self.session.scalar(query)

    def create(self, ingredient: Ingredient) -> Ingredient:
        self.session.add(ingredient)
        self.session.commit()
        self.session.refresh(ingredient)
        return ingredient

    def create_many(self, ingredients: list[Ingredient]) -> list[Ingredient]:
        self.session.add_all(ingredients)
        self.session.commit()
        for ingredient in ingredients:
            self.session.refresh(ingredient)
        return ingredients

    def delete(self, id: UUID) -> None:
        query = select(Ingredient).where(Ingredient.id == id)
        self.session.delete(self.session.scalar(query))
        self.session.commit()