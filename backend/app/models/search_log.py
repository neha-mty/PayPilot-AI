"""SearchLog model for recording search queries and analytics."""
import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Integer, DateTime, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class SearchLog(Base):
    __tablename__ = "search_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=True, index=True)
    query: Mapped[str] = mapped_column(String(500), nullable=False)
    detected_category: Mapped[str] = mapped_column(String(100), nullable=True)
    detected_subcategory: Mapped[str] = mapped_column(String(100), nullable=True)
    detected_brand: Mapped[str] = mapped_column(String(100), nullable=True)
    detected_max_price_paise: Mapped[int] = mapped_column(Integer, nullable=True)
    results_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
