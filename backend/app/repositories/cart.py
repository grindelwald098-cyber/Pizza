from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database.models.cart_item_added_ingredients import (
    CartItemAddedIngredient,
)
from app.database.models.cart_items import CartItem
from app.database.models.carts import Cart
from app.database.models.guests import Guest
from app.database.models.users import User
from app.repositories.base import BaseRepository


class CartRepository(BaseRepository[Cart]):
    model = Cart

    @staticmethod
    def _load_options() -> tuple[Any, ...]:
        # Снимок строки: продукт (карточка), выбранные size/dough, допы.
        return (
            selectinload(Cart.items)
            .selectinload(CartItem.added_ingredients)
            .selectinload(CartItemAddedIngredient.ingredient),
            selectinload(Cart.items).selectinload(CartItem.product),
            selectinload(Cart.items).selectinload(CartItem.size),
            selectinload(Cart.items).selectinload(CartItem.dough_type),
        )

    async def get_by_user_id(self, user_id: UUID) -> Cart | None:
        statement = (
            select(Cart)
            .join(User, User.cart_id == Cart.id)
            .where(User.id == user_id)
            .options(*self._load_options())
        )
        return await self.session.scalar(statement)

    async def get_by_guest_id(self, guest_id: UUID) -> Cart | None:
        statement = (
            select(Cart)
            .join(Guest, Guest.cart_id == Cart.id)
            .where(Guest.id == guest_id)
            .options(*self._load_options())
        )
        return await self.session.scalar(statement)
