from app.database.models.users import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    model = User

    async def get_by_email(self, email: str) -> User | None:
        return await self.get_one_by(email=email)

    async def get_by_phone(self, phone: str) -> User | None:
        return await self.get_one_by(phone=phone)
