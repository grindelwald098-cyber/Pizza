from decimal import Decimal
from sqlalchemy import UUID, Boolean, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.database import Base
import uuid


class ProductSize(Base):
    def __repr__(self) -> str:
        return (
            f"<ProductSize id={self.id} product_id={self.product_id} "
            f"size_id={self.size_id} price={self.price} "
            f"is_available={self.is_available} is_default={self.is_default}>"
        )

    __tablename__ = "product_sizes"

    product_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    size_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("sizes.id"), nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=Decimal("0.00"))
    is_available: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    is_default: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    product: Mapped["Product"] = relationship("Product", back_populates="sizes")
    size: Mapped["Size"] = relationship("Size")
