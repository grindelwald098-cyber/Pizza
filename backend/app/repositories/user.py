from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.users import User


class UserRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, id: UUID) -> User | None:
        query = select(User).where(User.id == id)

        return await self.session.scalar(query)

    async def get_by_email(self, email: str) -> User | None:
        query = select(User).where(User.email == email)

        return await self.session.scalar(query)

    async def get_by_phone(self, phone: str) -> User | None:
        query = select(User).where(User.phone == phone)

        return await self.session.scalar(query)

    async def create(self, user: User) -> User:
        self.session.add(user)

        await self.session.commit()
        await self.session.refresh(user)

        return user

    async def update(self, user: User) -> User:
        self.session.add(user)

        await self.session.commit()
        await self.session.refresh(user)

        return user

    async def delete(self, user: User) -> None:
        try:
            await self.session.delete(user)
            await self.session.commit()

        except Exception:
            await self.session.rollback()
            raise
