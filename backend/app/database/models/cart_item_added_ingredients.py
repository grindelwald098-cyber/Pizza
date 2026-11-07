from decimal import Decimal
from sqlalchemy import UUID, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.database import Base
import uuid


class CartItemAddedIngredient(Base):
    __tablename__ = "cart_item_added_ingredients"

    cart_item_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cart_items.id"), nullable=False
    )
    ingredient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ingredients.id"), nullable=False
    )
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=Decimal("0.00"))

    cart_item: Mapped["CartItem"] = relationship("CartItem", back_populates="added_ingredients")
    ingredient: Mapped["Ingredient"] = relationship("Ingredient")
