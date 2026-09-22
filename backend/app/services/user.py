from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.database.models.users import User
from app.repositories.user import UserRepository
from app.schemas.user import UserResponse
from app.services.cart import to_cart_response
from app.utils.principals import Principal, UserPrincipal


def to_user_response(user: User) -> UserResponse:
    return UserResponse(
        id=user.id,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        phone=user.phone,
        created_at=user.created_at,
        updated_at=user.updated_at,
        cart=to_cart_response(user.cart) if user.cart is not None else None,
    )


class UserService:
    def __init__(self, session: AsyncSession):
        self.user_repository = UserRepository(session)

    async def get_user_by_principal(self, principal: Principal) -> UserResponse:
        if isinstance(principal, UserPrincipal):
            user = await self.user_repository.get_by_id(principal.id)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            return to_user_response(user)
        raise HTTPException(
            status_code=403,
            detail="Guest principal is not allowed to access this resource",
        )
