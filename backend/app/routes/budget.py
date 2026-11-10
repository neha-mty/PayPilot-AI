"""Budget routes."""
from datetime import date
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.budget import Budget
from app.schemas.budget import BudgetCreate, BudgetOut
from app.services.budget_service import get_user_budgets, calculate_spent_amounts
from app.services.audit_service import log_event

router = APIRouter(prefix="/budget", tags=["Budgets"])


@router.get("", response_model=List[BudgetOut])
async def list_budgets(
    user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """Retrieve all budgets configured by the current user."""
    budgets = await get_user_budgets(db, user.id)
    spent = await calculate_spent_amounts(db, user.id)

    response = []
    for b in budgets:
        spent_amount = spent.get(b.period, 0) if not b.category else spent.get("category", 0)
        remaining = max(0, b.limit_amount_paise - spent_amount)
        response.append(
            BudgetOut(
                id=b.id,
                user_id=b.user_id,
                category=b.category,
                period=b.period,
                limit_amount_paise=b.limit_amount_paise,
                spent_amount_paise=spent_amount,
                remaining_paise=remaining,
                start_date=b.start_date,
                end_date=b.end_date,
                created_at=b.created_at,
            )
        )
    return response


@router.post("", response_model=BudgetOut, status_code=status.HTTP_201_CREATED)
async def create_budget(
    payload: BudgetCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new budget limit."""
    budget = Budget(
        user_id=user.id,
        category=payload.category,
        period=payload.period,
        limit_amount_paise=payload.limit_amount_paise,
        start_date=payload.start_date or date.today(),
        end_date=payload.end_date,
    )
    db.add(budget)
    await db.flush()

    await log_event(
        db,
        action="budget_created",
        actor_type="user",
        user_id=user.id,
        decision_reason=f"Created {payload.period} budget limit of ₹{payload.limit_amount_paise/100:.2f}",
    )

    return BudgetOut(
        id=budget.id,
        user_id=budget.user_id,
        category=budget.category,
        period=budget.period,
        limit_amount_paise=budget.limit_amount_paise,
        spent_amount_paise=0,
        remaining_paise=budget.limit_amount_paise,
        start_date=budget.start_date,
        end_date=budget.end_date,
        created_at=budget.created_at,
    )
