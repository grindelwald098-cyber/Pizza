from decimal import Decimal
from sqlalchemy import UUID, String, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.database import Base
import uuid


class OrderItemAddedIngredient(Base):
    __tablename__ = "order_item_added_ingredients"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_item_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("order_items.id"), nullable=False
    )
    ingredient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ingredients.id"), nullable=False
    )
    # Snapshot названия и цены допа на момент заказа
    ingredient_name: Mapped[str] = mapped_column(String(255), nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=Decimal("0.00"))

    order_item: Mapped["OrderItem"] = relationship("OrderItem", back_populates="added_ingredients")
    ingredient: Mapped["Ingredient"] = relationship("Ingredient")
