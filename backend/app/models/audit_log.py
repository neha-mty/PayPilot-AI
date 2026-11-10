"""Audit log model for recording all security-relevant events.

Every important action (policy evaluation, approval, payment, etc.)
is recorded here for a complete audit trail.
"""
import uuid
from datetime import datetime, timezone
from sqlalchemy import String, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), nullable=True, index=True)
    payment_request_id: Mapped[str] = mapped_column(String(36), nullable=True, index=True)
    actor_type: Mapped[str] = mapped_column(
        String(20), nullable=False
    )  # "user", "agent", "system", "payment_provider"
    action: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    decision_reason: Mapped[str] = mapped_column(Text, nullable=True)
    metadata_json: Mapped[str] = mapped_column(Text, nullable=True)  # Additional context as JSON
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True
    )
