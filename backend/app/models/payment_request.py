"""Payment request model.

Every purchase attempt creates a payment request. The policy engine
evaluates the request and returns ALLOW, REQUIRE_APPROVAL, or BLOCK.
Only approved/allowed requests can proceed to payment.

Status flow:
  pending → policy_evaluated → approved/rejected → payment_created → completed/failed
"""
import uuid
from datetime import datetime, timezone
from sqlalchemy import String, BigInteger, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class PaymentRequest(Base):
    __tablename__ = "payment_requests"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    agent_id: Mapped[str] = mapped_column(String(36), ForeignKey("agents.id"), nullable=True)
    merchant_id: Mapped[str] = mapped_column(String(36), ForeignKey("merchants.id"), nullable=False)
    product_id: Mapped[str] = mapped_column(String(36), ForeignKey("products.id"), nullable=False)
    amount_paise: Mapped[int] = mapped_column(BigInteger, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="INR")
    description: Mapped[str] = mapped_column(Text, nullable=True)
    policy_decision: Mapped[str] = mapped_column(
        String(20), nullable=True
    )  # "ALLOW", "REQUIRE_APPROVAL", "BLOCK"
    policy_reason: Mapped[str] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="pending", index=True
    )  # pending, policy_evaluated, approved, rejected, payment_created, completed, failed, expired, cancelled
    idempotency_key: Mapped[str] = mapped_column(String(100), unique=True, nullable=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    user = relationship("User", back_populates="payment_requests")
    agent = relationship("Agent", back_populates="payment_requests")
    merchant = relationship("Merchant", lazy="selectin")
    product = relationship("Product", lazy="selectin")
    approval = relationship("Approval", back_populates="payment_request", uselist=False, lazy="selectin")
    transaction = relationship("Transaction", back_populates="payment_request", uselist=False, lazy="selectin")
