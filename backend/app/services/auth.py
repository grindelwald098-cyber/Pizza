from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.schemas.user import UserLogin, UserResponse, UserCreate, TokenResponse
from app.repositories.user import UserRepository
from app.utils.password import check_password_hash, hash_password
from app.utils.jwt import create_access_token
from app.database.models.users import User


class AuthService:

    def __init__(self, session: AsyncSession):
        self.repository = UserRepository(session)

    async def login(self, data: UserLogin) -> TokenResponse:
        user = await self.repository.get_by_email(data.email)

        if not user or not check_password_hash(data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        return TokenResponse(
            access_token=create_access_token(user.id),
            user=UserResponse.model_validate(user, from_attributes=True),
        )

    async def register(self, data: UserCreate) -> UserResponse:
        existing = await self.repository.get_by_email(data.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this email already exists",
            )

        user = User(
            email=data.email,
            first_name=data.first_name,
            last_name=data.last_name,
            password_hash=hash_password(data.password),
            phone=data.phone,
            is_active=True,
        )
        created = await self.repository.create(user)

        return UserResponse.model_validate(created, from_attributes=True)
