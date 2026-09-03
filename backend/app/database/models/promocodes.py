from sqlalchemy import UUID, Integer, String, Text, Boolean, Numeric, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from decimal import Decimal
from app.database.database import Base
import uuid
from datetime import datetime


class Promocode(Base):
    __tablename__ = "promocodes"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    discount_value: Mapped[Decimal] = mapped_column(Numeric(precision=10, scale=2), nullable=False)
    discount_type: Mapped[str] = mapped_column(String(255), nullable=False)
    min_order_amount: Mapped[Decimal] = mapped_column(Numeric(precision=10, scale=2), nullable=False)
    max_discount_amount: Mapped[Decimal] = mapped_column(Numeric(precision=10, scale=2), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    usage_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    usage_limit: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    starts_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now)