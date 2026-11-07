from decimal import Decimal
from sqlalchemy import UUID, String, Text, Boolean, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.database import Base
import uuid


class Product(Base):
    __tablename__ = "products"

    category_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("categories.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    image_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
    base_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=Decimal("0.00"))
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    is_available: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    category: Mapped["Category"] = relationship("Category")
    sizes: Mapped[list["ProductSize"]] = relationship("ProductSize", back_populates="product")
    doughs: Mapped[list["ProductDough"]] = relationship("ProductDough", back_populates="product")
    ingredients: Mapped[list["ProductIngredient"]] = relationship(
        "ProductIngredient", back_populates="product"
    )
    addons: Mapped[list["ProductAddon"]] = relationship("ProductAddon", back_populates="product")
