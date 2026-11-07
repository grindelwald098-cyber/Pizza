from app.database.models.category import Category
from app.repositories.category import CategoryRepository
from app.schemas.category import CategoryCreate
from app.services.crud import CrudService


class CategoryService(CrudService[Category, CategoryCreate]):
    repository_cls = CategoryRepository
    not_found_detail = "Category not found"

    def build(self, data: CategoryCreate) -> Category:
        return Category(
            name=data.name,
            slug=data.slug,
            description=data.description,
            image_url=data.image_url,
            is_active=data.is_active,
        )
