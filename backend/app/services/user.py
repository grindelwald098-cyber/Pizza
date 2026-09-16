from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.user import UserRepository
from app.schemas.user import UserResponse
from app.utils.principals import Principal, UserPrincipal

class UserService:
    def __init__(self, session: AsyncSession):
        self.user_repository = UserRepository(session)

    async def get_user_by_principal(self, principal: Principal) -> UserResponse:
        if isinstance(principal, UserPrincipal):
            user = await self.user_repository.get_by_id(principal.id)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            return UserResponse.model_validate(user, from_attributes=True)
        raise HTTPException(status_code=400, detail="Invalid principal type")