from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from uuid import UUID
from app.schemas.category import CategoryCreate
from app.database.models.category import Category
from app.services.category import CategoryService
from app.database.database import get_session
from app.schemas.category import CategoryResponse

router = APIRouter(
    prefix="/categories",
    tags=["Categories"],
)

@router.post("/", response_model=CategoryResponse)
def create_category(data: CategoryCreate, session: Session = Depends(get_session)) -> Category:
    service = CategoryService(session)
    return service.create_category(data)