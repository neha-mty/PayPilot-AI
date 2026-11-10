"""Pydantic schemas for payment approvals."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class ApprovalOut(BaseModel):
    id: str
    payment_request_id: str
    user_id: str
    decision: str
    approved_amount_paise: Optional[int] = None
    approved_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True
