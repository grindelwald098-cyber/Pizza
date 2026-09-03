from decimal import Decimal
from sqlalchemy import UUID, Integer, String, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.database import Base
import uuid


class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("orders.id"), nullable=False)
    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("products.id"), nullable=False
    )
    size_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("sizes.id"), nullable=True
    )
    dough_type_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("dough_types.id"), nullable=True
    )
    # Snapshot на момент покупки — история не ломается при смене каталога
    product_name: Mapped[str] = mapped_column(String(255), nullable=False)
    size_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    dough_type_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=Decimal("0.00"))
    total_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=Decimal("0.00"))

    order: Mapped["Order"] = relationship("Order", back_populates="items")
    product: Mapped["Product"] = relationship("Product")
    size: Mapped["Size | None"] = relationship("Size")
    dough_type: Mapped["DoughType | None"] = relationship("DoughType")
    added_ingredients: Mapped[list["OrderItemAddedIngredient"]] = relationship(
        "OrderItemAddedIngredient", back_populates="order_item"
    )
