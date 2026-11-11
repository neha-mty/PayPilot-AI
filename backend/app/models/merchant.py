"""Merchant model for the product catalog.

Merchants can be verified or unverified. The policy engine uses
verification status to decide whether to allow, require approval,
or block transactions.
"""
import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Boolean, DateTime, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Merchant(Base):
    __tablename__ = "merchants"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    description: Mapped[str] = mapped_column(String(500), nullable=True)
    website_url: Mapped[str] = mapped_column(String(255), nullable=True)
    logo_icon: Mapped[str] = mapped_column(String(50), nullable=True, default="🏬")
    rating: Mapped[float] = mapped_column(Float, nullable=True, default=4.5)
    is_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    products = relationship("Product", back_populates="merchant", lazy="selectin")
