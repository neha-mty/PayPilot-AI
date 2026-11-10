"""Pydantic schemas for audit logs."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class AuditLogOut(BaseModel):
    id: str
    user_id: Optional[str] = None
    payment_request_id: Optional[str] = None
    actor_type: str
    action: str
    decision_reason: Optional[str] = None
    metadata_json: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
