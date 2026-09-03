from decimal import Decimal
from sqlalchemy import UUID, Boolean, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.database import Base
import uuid


class ProductAddon(Base):
    __tablename__ = "product_addons"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    ingredient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ingredients.id"), nullable=False
    )
    is_available: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    additional_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=Decimal("0.00"))

    product: Mapped["Product"] = relationship("Product", back_populates="addons")
    ingredient: Mapped["Ingredient"] = relationship("Ingredient")
