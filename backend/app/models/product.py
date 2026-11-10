"""Product model for the purchasing catalog.

Prices are stored as integer paise (1 INR = 100 paise).
Example: ₹199.50 = 19950 paise.
"""
import uuid
from datetime import datetime, timezone
from sqlalchemy import String, BigInteger, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Product(Base):
    __tablename__ = "products"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    merchant_id: Mapped[str] = mapped_column(String(36), ForeignKey("merchants.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    price_paise: Mapped[int] = mapped_column(BigInteger, nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    tags: Mapped[str] = mapped_column(String(500), nullable=True)  # Comma-separated tags for search
    is_available: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    merchant = relationship("Merchant", back_populates="products")
