"""Transaction model for recording payment outcomes.

Status flow: created → pending → successful/failed/cancelled
"""
import uuid
from datetime import datetime, timezone
from sqlalchemy import String, BigInteger, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    payment_request_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("payment_requests.id"), nullable=False, unique=True, index=True
    )
    provider: Mapped[str] = mapped_column(String(50), nullable=False)  # "simulated", "razorpay"
    provider_order_id: Mapped[str] = mapped_column(String(200), nullable=True, index=True)
    provider_payment_id: Mapped[str] = mapped_column(String(200), nullable=True)
    amount_paise: Mapped[int] = mapped_column(BigInteger, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="INR")
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="created"
    )  # created, pending, successful, failed, cancelled
    provider_response: Mapped[str] = mapped_column(String(2000), nullable=True)  # JSON string
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    payment_request = relationship("PaymentRequest", back_populates="transaction", lazy="selectin")
