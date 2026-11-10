"""Pydantic schemas for payment requests."""
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel


class PaymentRequestCreate(BaseModel):
    product_id: str
    agent_type: str = "food"
    idempotency_key: Optional[str] = None


class PaymentRequestOut(BaseModel):
    id: str
    user_id: str
    agent_id: Optional[str] = None
    merchant_id: str
    product_id: str
    amount_paise: int
    currency: str
    description: Optional[str] = None
    policy_decision: Optional[str] = None
    policy_reason: Optional[str] = None
    status: str
    idempotency_key: Optional[str] = None
    expires_at: Optional[datetime] = None
    created_at: datetime
    merchant: Optional[Dict[str, Any]] = None
    product: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True
