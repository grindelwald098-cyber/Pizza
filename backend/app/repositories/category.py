from sqlalchemy.orm import Session
from sqlalchemy import select
from uuid import UUID

from app.database.models.category import Category


class CategoryRepository:

    def __init__(self, session: Session):
        self.session = session

    def get_all(self) -> list[Category]:
        query = select(Category)
        return self.session.scalars(query).all()

    def get_by_id(self, id: UUID) -> Product | None:
        query = select(Category).where(Category.id == id)
        return self.session.scalar(query)

    def create(self, category: Category) -> Category:
        self.session.add(category)
        self.session.commit()
        self.session.refresh(category)
        return category
        