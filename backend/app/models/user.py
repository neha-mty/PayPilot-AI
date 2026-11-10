"""User model for authentication and ownership."""
import uuid
from datetime import datetime, timezone
from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    budgets = relationship("Budget", back_populates="user", lazy="selectin")
    policies = relationship("SpendingPolicy", back_populates="user", lazy="selectin")
    agents = relationship("Agent", back_populates="user", lazy="selectin")
    payment_requests = relationship("PaymentRequest", back_populates="user", lazy="selectin")
    approvals = relationship("Approval", back_populates="user", lazy="selectin")
