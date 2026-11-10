"""Budget model for tracking spending limits.

Money is stored as integer paise (1 INR = 100 paise).
Example: ₹200 = 20000 paise.
"""
import uuid
from datetime import datetime, timezone, date
from sqlalchemy import String, BigInteger, Date, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Budget(Base):
    __tablename__ = "budgets"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(50), nullable=True)  # None = all categories
    period: Mapped[str] = mapped_column(String(10), nullable=False)  # "daily", "weekly", "monthly"
    limit_amount_paise: Mapped[int] = mapped_column(BigInteger, nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=True)  # None = ongoing
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    user = relationship("User", back_populates="budgets")
