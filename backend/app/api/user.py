from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import get_current_principal
from app.database.database import get_session
from app.schemas.user import UserResponse
from app.services.user import UserService
from app.utils.principals import Principal

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)

@router.get("/me", response_model=UserResponse)
async def get_me(
    principal: Principal = Depends(get_current_principal),
    session: AsyncSession = Depends(get_session),
) -> UserResponse:
    service = UserService(session)
    return await service.get_user_by_principal(principal)

