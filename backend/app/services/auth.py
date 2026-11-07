from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.carts import Cart
from app.database.models.users import User
from app.exceptions import ConflictError, UnauthorizedError
from app.repositories.user import UserRepository
from app.schemas.user import UserCreate, UserLogin, UserTokenResponse
from app.services.user import to_user_response
from app.utils.jwt import create_access_token
from app.utils.password import check_password_hash, hash_password
from app.services.cart import CartService
from uuid import UUID

class AuthService:

    def __init__(self, session: AsyncSession):
        self.repository = UserRepository(session)

    async def login(self, data: UserLogin, guest_id: UUID | None) -> UserTokenResponse:
        user = await self.repository.get_by_email(data.email)

        if not user or not check_password_hash(data.password, user.password_hash):
            raise UnauthorizedError("Invalid email or password")

        if guest_id is not None:
            await CartService(self.repository.session).merge_guest_cart(guest_id, user.id)

        return UserTokenResponse(
            access_token=create_access_token(user.id, "user"),
            user=to_user_response(user),
        )

    async def register(self, data: UserCreate) -> UserTokenResponse:
        existing = await self.repository.get_by_email(data.email)
        if existing:
            raise ConflictError("User with this email already exists")

        user = User(
            email=data.email,
            first_name=data.first_name,
            last_name=data.last_name,
            password_hash=hash_password(data.password),
            phone=data.phone,
            is_active=True,
            cart=Cart(),
        )
        created_user = await self.repository.create(user)

        return UserTokenResponse(
            access_token=create_access_token(created_user.id, "user"),
            user=to_user_response(created_user),
        )
