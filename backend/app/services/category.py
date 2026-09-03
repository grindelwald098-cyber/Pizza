from app.repositories.category import CategoryRepository
from sqlalchemy.orm import Session
from app.schemas.category import CategoryCreate
from app.database.models.category import Category
from uuid import UUID

class CategoryService:
    def __init__(self, session: Session):
        self.repository = CategoryRepository(session)

    def get_category_by_id(self, id: UUID) -> Category | None:
        return self.repository.get_by_id(id)

    def get_all_categories(self) -> list[Category]:
        return self.repository.get_all()

    def create_category(self, data: CategoryCreate) -> Category:
        category = Category(
            name=data.name,
            slug=data.slug,
            description=data.description,
            image_url=data.image_url,
            is_active=data.is_active,
        )
        return self.repository.create(category)