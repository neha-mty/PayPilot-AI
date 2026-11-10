"""Audit logging service for tracking security events and payment actions."""
import json
from datetime import datetime, timezone
from typing import Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.audit_log import AuditLog


async def log_event(
    db: AsyncSession,
    action: str,
    actor_type: str,  # "user", "agent", "system", "payment_provider"
    user_id: Optional[str] = None,
    payment_request_id: Optional[str] = None,
    decision_reason: Optional[str] = None,
    metadata: Optional[Any] = None,
) -> AuditLog:
    """Record an immutable security audit event."""
    metadata_json = None
    if metadata is not None:
        if isinstance(metadata, str):
            metadata_json = metadata
        else:
            try:
                metadata_json = json.dumps(metadata)
            except Exception:
                metadata_json = str(metadata)

    event = AuditLog(
        user_id=user_id,
        payment_request_id=payment_request_id,
        actor_type=actor_type,
        action=action,
        decision_reason=decision_reason,
        metadata_json=metadata_json,
        created_at=datetime.now(timezone.utc),
    )
    db.add(event)
    await db.flush()
    return event
