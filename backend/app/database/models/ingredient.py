from decimal import Decimal
from sqlalchemy import UUID, String, Text, Boolean, Numeric
from sqlalchemy.orm import Mapped, mapped_column
from app.database.database import Base
import uuid


class Ingredient(Base):
    __tablename__ = "ingredients"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    image_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=Decimal("0.00"))
    is_available: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
