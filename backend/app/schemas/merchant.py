"""Pydantic schemas for merchants and products."""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


class ProductOut(BaseModel):
    id: str
    merchant_id: str
    name: str
    description: Optional[str] = None
    price_paise: int
    category: str
    tags: Optional[str] = None
    is_available: bool
    created_at: datetime
    merchant_name: Optional[str] = None
    merchant_verified: Optional[bool] = None

    class Config:
        from_attributes = True


class MerchantOut(BaseModel):
    id: str
    name: str
    category: str
    description: Optional[str] = None
    is_verified: bool
    is_active: bool
    created_at: datetime
    products: List[ProductOut] = []

    class Config:
        from_attributes = True
