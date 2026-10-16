from datetime import UTC, datetime

from sqlalchemy import CheckConstraint, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from .db import Base


class Equipment(Base):
    __tablename__ = "equipment"
    __table_args__ = (
        CheckConstraint("quantity >= 0", name="ck_equipment_quantity"),
        CheckConstraint("low_stock_threshold >= 0", name="ck_equipment_threshold"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    category: Mapped[str] = mapped_column(String(60), index=True)
    quantity: Mapped[int]
    low_stock_threshold: Mapped[int]
    location: Mapped[str] = mapped_column(String(120))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
