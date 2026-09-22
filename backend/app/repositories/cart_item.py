from typing import Any


from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database.models.cart_items import CartItem


class CartItemRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, cart_item: CartItem) -> CartItem:
        self.session.add(cart_item)
        await self.session.commit()
        await self.session.refresh(cart_item)
        return cart_item

    async def update(self, cart_item: CartItem) -> CartItem:
        self.session.add(cart_item)
        await self.session.commit()
        await self.session.refresh(cart_item)
        return cart_item

    async def find_matching(
        self,
        cart_id: UUID,
        product_id: UUID,
        size_id: UUID | None,
        dough_type_id: UUID | None,
        extra_ingredient_ids: list[UUID],
    ) -> CartItem | None:
        query = (
            select(CartItem)
            .where(
                CartItem.cart_id == cart_id,
                CartItem.product_id == product_id,
                CartItem.size_id == size_id,
                CartItem.dough_type_id == dough_type_id,
            )
            .options(selectinload(CartItem.added_ingredients))
        )
        items = list[Any](await self.session.scalars(query))
        wanted = set[UUID](extra_ingredient_ids)
        for item in items:
            current = {extra.ingredient_id for extra in item.added_ingredients}
            if current == wanted:
                return item
        return None
