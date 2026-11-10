"""Pydantic schemas for spending policies."""
from datetime import datetime
from pydantic import BaseModel, Field


class SpendingPolicyUpdate(BaseModel):
    max_transaction_paise: int = Field(..., gt=0)
    approval_required: bool = True
    unknown_merchant_action: str = Field(default="require_approval", pattern="^(allow|require_approval|block)$")
    is_active: bool = True


class SpendingPolicyOut(BaseModel):
    id: str
    user_id: str
    max_transaction_paise: int
    approval_required: bool
    unknown_merchant_action: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
