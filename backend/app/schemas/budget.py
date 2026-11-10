"""Pydantic schemas for budget management."""
from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel, Field


class BudgetCreate(BaseModel):
    category: Optional[str] = None
    period: str = Field(..., pattern="^(daily|weekly|monthly)$")
    limit_amount_paise: int = Field(..., gt=0)
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class BudgetOut(BaseModel):
    id: str
    user_id: str
    category: Optional[str] = None
    period: str
    limit_amount_paise: int
    spent_amount_paise: int = 0
    remaining_paise: int = 0
    start_date: date
    end_date: Optional[date] = None
    created_at: datetime

    class Config:
        from_attributes = True
