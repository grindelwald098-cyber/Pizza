from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import get_session
from app.schemas.user import UserCreate, UserLogin, UserResponse, TokenResponse
from app.services.auth import AuthService

router = APIRouter(
    tags=["Auth"],
)


@router.post("/login", response_model=TokenResponse)
async def login(
    user: UserLogin, session: AsyncSession = Depends(get_session)
) -> TokenResponse:
    service = AuthService(session)
    return await service.login(user)


@router.post("/register", response_model=UserResponse)
async def register(
    user: UserCreate, session: AsyncSession = Depends(get_session)
) -> UserResponse:
    service = AuthService(session)
    return await service.register(user)
