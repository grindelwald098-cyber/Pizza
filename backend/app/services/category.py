from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.category import Category
from app.repositories.category import CategoryRepository
from app.schemas.category import CategoryCreate


class CategoryService:

    def __init__(self, session: AsyncSession):
        self.repository = CategoryRepository(session)

    async def get_category_by_id(self, id: UUID) -> Category:
        category = await self.repository.get_by_id(id)

        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found",
            )

        return category

    async def get_all_categories(self) -> list[Category]:
        return await self.repository.get_all()

    async def create_category(self, data: CategoryCreate) -> Category:
        category = Category(
            name=data.name,
            slug=data.slug,
            description=data.description,
            image_url=data.image_url,
            is_active=data.is_active,
        )

        return await self.repository.create(category)
