from decimal import Decimal
from sqlalchemy import UUID, Boolean, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.database import Base
import uuid


class ProductSize(Base):
    def __repr__(self) -> str:
        return f"<ProductSize id={self.id} product_id={self.product_id} size_id={self.size_id} price={self.price} is_available={self.is_available}>"

    __tablename__ = "product_sizes"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    size_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("sizes.id"), nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=Decimal("0.00"))
    is_available: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    product: Mapped["Product"] = relationship("Product", back_populates="sizes")
    size: Mapped["Size"] = relationship("Size")
