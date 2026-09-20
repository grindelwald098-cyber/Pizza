from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.database.models.carts import CartItem


class CartItemRepository:
    def __init__(self, session: AsyncSession):
        self.session = session


    async def add_product_to_cart(self, cart_id: UUID, product_id: UUID, quantity: int) -> CartItem:
        cart_item = CartItem(cart_id=cart_id, product_id=product_id, quantity=quantity)
        self.session.add(cart_item)
        await self.session.commit()
        return cart_item