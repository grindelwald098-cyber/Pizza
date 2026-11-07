from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base


class Cart(Base):
    __tablename__ = "carts"

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now)

    items: Mapped[list["CartItem"]] = relationship("CartItem", back_populates="cart")
    user: Mapped["User | None"] = relationship("User", back_populates="cart", uselist=False)
    guest: Mapped["Guest | None"] = relationship("Guest", back_populates="cart", uselist=False)