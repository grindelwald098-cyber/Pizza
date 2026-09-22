from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database.models.users import User
from app.repositories.cart import CartRepository


class UserRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    def _with_cart(self):
        return selectinload(User.cart).options(*CartRepository._load_options())

    async def get_by_id(self, id: UUID) -> User | None:
        query = select(User).where(User.id == id).options(self._with_cart())
        return await self.session.scalar(query)

    async def get_by_email(self, email: str) -> User | None:
        query = select(User).where(User.email == email).options(self._with_cart())
        return await self.session.scalar(query)

    async def get_by_phone(self, phone: str) -> User | None:
        query = select(User).where(User.phone == phone).options(self._with_cart())
        return await self.session.scalar(query)

    async def create(self, user: User) -> User:
        self.session.add(user)
        await self.session.flush()
        user_id = user.id
        await self.session.commit()
        created = await self.get_by_id(user_id)
        if created is None:
            raise RuntimeError("User was not found after create")
        return created

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
