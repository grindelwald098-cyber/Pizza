from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database.models.cart_item_added_ingredients import CartItemAddedIngredient
from app.database.models.cart_items import CartItem
from app.database.models.carts import Cart
from app.database.models.guests import Guest
from app.database.models.users import User
from app.repositories.product import ProductRepository


class CartRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    @staticmethod
    def _load_options():
        # selectinload = заранее подтянуть связи отдельным SELECT IN (...),
        # чтобы потом не было lazy-load и MissingGreenlet в async.
        return (
            selectinload(Cart.items)
            .selectinload(CartItem.added_ingredients)
            .selectinload(CartItemAddedIngredient.ingredient),
            selectinload(Cart.items)
            .selectinload(CartItem.product)
            .options(*ProductRepository._load_options()),
        )

    async def get_by_id(self, cart_id: UUID) -> Cart | None:
        query = select(Cart).where(Cart.id == cart_id).options(*self._load_options())
        return await self.session.scalar(query)

    async def get_by_user_id(self, user_id: UUID) -> Cart | None:
        query = (
            select(Cart)
            .join(User, User.cart_id == Cart.id)
            .where(User.id == user_id)
            .options(*self._load_options())
        )
        return await self.session.scalar(query)

    async def get_by_guest_id(self, guest_id: UUID) -> Cart | None:
        query = (
            select(Cart)
            .join(Guest, Guest.cart_id == Cart.id)
            .where(Guest.id == guest_id)
            .options(*self._load_options())
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
