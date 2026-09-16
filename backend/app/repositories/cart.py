from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.carts import Cart
from app.database.models.guests import Guest
from app.database.models.users import User


class CartRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_user_id(self, user_id: UUID) -> Cart | None:
        query = (
            select(Cart)
            .join(User, User.cart_id == Cart.id)
            .where(User.id == user_id)
        )
        return await self.session.scalar(query)

    async def get_by_guest_id(self, guest_id: UUID) -> Cart | None:
        query = (
            select(Cart)
            .join(Guest, Guest.cart_id == Cart.id)
            .where(Guest.id == guest_id)
        )
        return await self.session.scalar(query)

    async def create(self, cart: Cart) -> Cart:
        self.session.add(cart)
        await self.session.commit()
        await self.session.refresh(cart)
        return cart

    async def update(self, cart: Cart) -> Cart:
        self.session.add(cart)
        await self.session.commit()
        await self.session.refresh(cart)
        return cart
