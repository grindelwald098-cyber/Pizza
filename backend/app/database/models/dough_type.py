from sqlalchemy import UUID, Integer, String, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from app.database.database import Base
import uuid


class DoughType(Base):
    __tablename__ = "dough_types"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
