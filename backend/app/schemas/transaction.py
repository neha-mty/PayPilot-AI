"""Pydantic schemas for transactions."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class PaymentCreate(BaseModel):
    payment_request_id: str


class PaymentVerify(BaseModel):
    payment_request_id: str
    provider_order_id: str
    provider_payment_id: str
    signature: str


class TransactionOut(BaseModel):
    id: str
    payment_request_id: str
    provider: str
    provider_order_id: Optional[str] = None
    provider_payment_id: Optional[str] = None
    amount_paise: int
    currency: str
    status: str
    description: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
