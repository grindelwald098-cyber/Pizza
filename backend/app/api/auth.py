from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import get_session
from app.schemas.user import UserCreate, UserLogin, UserTokenResponse
from app.services.auth import AuthService
from app.api.dependencies.auth import get_optional_guest_id
from uuid import UUID

router = APIRouter(
    tags=["Auth"],
)


@router.post("/login", response_model=UserTokenResponse)
async def login(
    user: UserLogin, 
    session: AsyncSession = Depends(get_session),
    guest_id: UUID | None = Depends(get_optional_guest_id)    
) -> UserTokenResponse:
    service = AuthService(session)
    return await service.login(user, guest_id)


@router.post("/register", response_model=UserTokenResponse)
async def register(
    user: UserCreate, session: AsyncSession = Depends(get_session)
) -> UserTokenResponse:
    service = AuthService(session)
    return await service.register(user)
