from datetime import datetime
from decimal import Decimal
from sqlalchemy import UUID, Numeric, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.database import Base
import uuid


class PromocodeUsage(Base):
    __tablename__ = "promocode_usages"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    promocode_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("promocodes.id"), nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    order_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("orders.id"), nullable=False
    )
    used_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now)
    discount_amount: Mapped[Decimal] = mapped_column(Numeric(precision=10, scale=2), nullable=False)

    promocode: Mapped["Promocode"] = relationship("Promocode")
    user: Mapped["User"] = relationship("User")
    order: Mapped["Order"] = relationship("Order")
