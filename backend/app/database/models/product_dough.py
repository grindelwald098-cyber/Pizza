from sqlalchemy import UUID, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.database import Base
import uuid


class ProductDough(Base):
    __tablename__ = "product_doughs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    dough_type_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("dough_types.id"), nullable=False
    )
    is_default: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    product: Mapped["Product"] = relationship("Product", back_populates="doughs")
    dough_type: Mapped["DoughType"] = relationship("DoughType")
