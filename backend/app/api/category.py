from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import get_session
from app.database.models.category import Category
from app.schemas.category import CategoryCreate, CategoryResponse
from app.services.category import CategoryService

router = APIRouter(
    prefix="/categories",
    tags=["Categories"],
)


@router.post("/", response_model=CategoryResponse)
async def create_category(
    data: CategoryCreate, session: AsyncSession = Depends(get_session)
) -> Category:
    service = CategoryService(session)
    return await service.create(data)
