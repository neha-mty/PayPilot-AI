"""Approval model for payment authorization.

Approvals are bound to a specific payment request with an exact amount.
If the amount or merchant changes, the approval becomes invalid.
Approvals expire after a configurable period.
"""
import uuid
from datetime import datetime, timezone
from sqlalchemy import String, BigInteger, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Approval(Base):
    __tablename__ = "approvals"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    payment_request_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("payment_requests.id"), nullable=False, unique=True, index=True
    )
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    decision: Mapped[str] = mapped_column(String(10), nullable=False)  # "approved", "rejected"
    approved_amount_paise: Mapped[int] = mapped_column(BigInteger, nullable=True)  # Set on approval
    approved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    payment_request = relationship("PaymentRequest", back_populates="approval")
    user = relationship("User", back_populates="approvals")
