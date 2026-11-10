"""Agent tool call model for tracking AI agent actions.

Records every tool invocation by an AI agent for audit purposes.
"""
import uuid
from datetime import datetime, timezone
from sqlalchemy import String, DateTime, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class AgentToolCall(Base):
    __tablename__ = "agent_tool_calls"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    agent_id: Mapped[str] = mapped_column(String(36), ForeignKey("agents.id"), nullable=False, index=True)
    tool_name: Mapped[str] = mapped_column(String(100), nullable=False)
    tool_input_json: Mapped[str] = mapped_column(Text, nullable=True)
    result_status: Mapped[str] = mapped_column(String(20), nullable=False)  # "success", "error"
    result_summary: Mapped[str] = mapped_column(Text, nullable=True)
    related_payment_request_id: Mapped[str] = mapped_column(String(36), nullable=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    agent = relationship("Agent", back_populates="tool_calls")
