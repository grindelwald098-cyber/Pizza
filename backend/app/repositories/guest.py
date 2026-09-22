from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database.models.guests import Guest
from app.repositories.cart import CartRepository


class GuestRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, id: UUID) -> Guest | None:
        query = (
            select(Guest)
            .where(Guest.id == id)
            .options(selectinload(Guest.cart).options(*CartRepository._load_options()))
        )
        return await self.session.scalar(query)

    async def create(self, guest: Guest) -> Guest:
        self.session.add(guest)
        await self.session.commit()
        await self.session.refresh(guest, attribute_names=["cart"])
        return guest

    async def update(self, guest: Guest) -> Guest:
        self.session.add(guest)
        await self.session.commit()
        await self.session.refresh(guest, attribute_names=["cart"])
        return guest
