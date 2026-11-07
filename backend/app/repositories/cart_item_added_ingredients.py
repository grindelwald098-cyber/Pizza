from app.database.models.cart_item_added_ingredients import (
    CartItemAddedIngredient,
)
from app.repositories.base import BaseRepository


class CartItemAddedIngredientRepository(
    BaseRepository[CartItemAddedIngredient],
):
    model = CartItemAddedIngredient
