"""Marketplace Provider model for PayPilot Universal Discovery."""
import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Boolean, DateTime, Text, Float
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class MarketplaceProvider(Base):
    __tablename__ = "marketplace_providers"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    primary_category: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    supported_categories: Mapped[str] = mapped_column(String(500), nullable=False)  # Comma-separated
    website_url: Mapped[str] = mapped_column(String(255), nullable=True)
    logo_icon: Mapped[str] = mapped_column(String(50), nullable=True, default="🏬")
    description: Mapped[str] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    supports_integrated_checkout: Mapped[bool] = mapped_column(Boolean, default=True)
    data_source_type: Mapped[str] = mapped_column(String(20), default="DEMO")  # DEMO, LIVE, AFFILIATE, CACHED
    average_rating: Mapped[float] = mapped_column(Float, nullable=True, default=4.5)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
