from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models.cart_item_added_ingredients import CartItemAddedIngredient

class CartItemAddedIngredientRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, cart_item_added_ingredient: CartItemAddedIngredient) -> CartItemAddedIngredient:
        self.session.add(cart_item_added_ingredient)
        await self.session.commit()
        await self.session.refresh(cart_item_added_ingredient)
        return cart_item_added_ingredient