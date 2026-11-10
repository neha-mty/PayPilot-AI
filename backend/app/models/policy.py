"""Spending policy model for configuring payment rules.

Each user can have one active policy at a time.
"""
import uuid
from datetime import datetime, timezone
from sqlalchemy import String, BigInteger, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class SpendingPolicy(Base):
    __tablename__ = "spending_policies"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    max_transaction_paise: Mapped[int] = mapped_column(BigInteger, nullable=False, default=50000)  # ₹500 default
    approval_required: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    unknown_merchant_action: Mapped[str] = mapped_column(
        String(20), nullable=False, default="require_approval"
    )  # "allow", "require_approval", "block"
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    user = relationship("User", back_populates="policies")
