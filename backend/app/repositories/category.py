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

    def get_by_id(self, id: UUID) -> Category | None:
        query = select(Category).where(Category.id == id)
        return self.session.scalar(query)

    def get_existing_ids(self, ids: list[UUID]) -> set[UUID]:
        if not ids:
            return set()
        query = select(Category.id).where(Category.id.in_(ids))
        return set(self.session.scalars(query).all())

    def create(self, category: Category) -> Category:
        self.session.add(category)
        self.session.commit()
        self.session.refresh(category)
        return category
        