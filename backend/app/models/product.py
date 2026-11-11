"""Product model for the universal purchasing catalog.

Prices are stored as integer paise (1 INR = 100 paise).
Example: ₹199.50 = 19950 paise.
"""
import uuid
from datetime import datetime, timezone
from sqlalchemy import String, BigInteger, Boolean, DateTime, ForeignKey, Text, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Product(Base):
    __tablename__ = "products"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    merchant_id: Mapped[str] = mapped_column(String(36), ForeignKey("merchants.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    price_paise: Mapped[int] = mapped_column(BigInteger, nullable=False)
    original_price_paise: Mapped[int] = mapped_column(BigInteger, nullable=True)
    category: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    subcategory: Mapped[str] = mapped_column(String(100), nullable=True, index=True)
    brand: Mapped[str] = mapped_column(String(100), nullable=True, index=True)
    tags: Mapped[str] = mapped_column(String(500), nullable=True)  # Comma-separated tags
    image_url: Mapped[str] = mapped_column(String(500), nullable=True)
    product_url: Mapped[str] = mapped_column(String(500), nullable=True)
    provider_code: Mapped[str] = mapped_column(String(50), nullable=True, default="internal", index=True)
    provider_name: Mapped[str] = mapped_column(String(100), nullable=True, default="PayPilot Catalog")
    data_source_type: Mapped[str] = mapped_column(String(20), default="DEMO")  # DEMO, LIVE, AFFILIATE, CACHED
    rating: Mapped[float] = mapped_column(Float, nullable=True, default=4.5)
    rating_count: Mapped[int] = mapped_column(BigInteger, nullable=True, default=120)
    specifications: Mapped[str] = mapped_column(Text, nullable=True)  # JSON formatted key-value pairs
    supports_integrated_checkout: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    is_available: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    merchant = relationship("Merchant", back_populates="products")
