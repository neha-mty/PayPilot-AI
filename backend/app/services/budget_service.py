"""Budget management and spending calculation service."""
from datetime import datetime, timezone, timedelta, date
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.budget import Budget
from app.models.payment_request import PaymentRequest
from app.models.transaction import Transaction


async def get_user_budgets(db: AsyncSession, user_id: str) -> List[Budget]:
    """Retrieve all budget limits set by the user."""
    result = await db.execute(select(Budget).where(Budget.user_id == user_id))
    return list(result.scalars().all())


async def calculate_spent_amounts(
    db: AsyncSession, user_id: str, category: Optional[str] = None
) -> Dict[str, int]:
    """Calculate total paise spent in current day, week, month, and specified category.
    
    Only counts successful transactions or payment requests in completed/payment_created state.
    """
    now = datetime.now(timezone.utc)
    start_of_day = datetime(now.year, now.month, now.day, tzinfo=timezone.utc)
    start_of_week = start_of_day - timedelta(days=now.weekday())
    start_of_month = datetime(now.year, now.month, 1, tzinfo=timezone.utc)

    # Base query for successful transactions by this user
    base_stmt = (
        select(func.coalesce(func.sum(Transaction.amount_paise), 0))
        .join(PaymentRequest, Transaction.payment_request_id == PaymentRequest.id)
        .where(PaymentRequest.user_id == user_id)
        .where(Transaction.status == "successful")
    )

    # Daily spent
    daily_res = await db.execute(base_stmt.where(Transaction.created_at >= start_of_day))
    daily_spent = daily_res.scalar() or 0

    # Weekly spent
    weekly_res = await db.execute(base_stmt.where(Transaction.created_at >= start_of_week))
    weekly_spent = weekly_res.scalar() or 0

    # Monthly spent
    monthly_res = await db.execute(base_stmt.where(Transaction.created_at >= start_of_month))
    monthly_spent = monthly_res.scalar() or 0

    # Category spent (for current month)
    category_spent = 0
    if category:
        from app.models.product import Product
        cat_stmt = (
            base_stmt
            .join(Product, PaymentRequest.product_id == Product.id)
            .where(Product.category.ilike(category))
            .where(Transaction.created_at >= start_of_month)
        )
        cat_res = await db.execute(cat_stmt)
        category_spent = cat_res.scalar() or 0

    return {
        "daily": int(daily_spent),
        "weekly": int(weekly_spent),
        "monthly": int(monthly_spent),
        "category": int(category_spent),
    }


async def get_dashboard_summary(db: AsyncSession, user_id: str) -> Dict[str, Any]:
    """Provide aggregated spending and pending approval metrics for dashboard."""
    budgets = await get_user_budgets(db, user_id)
    spent = await calculate_spent_amounts(db, user_id)

    total_budget_paise = sum(b.limit_amount_paise for b in budgets if not b.category)
    if not total_budget_paise:
        total_budget_paise = 100000  # Default ₹1000 demo budget if none set

    total_spent_paise = spent["monthly"]
    remaining_paise = max(0, total_budget_paise - total_spent_paise)

    # Count pending approvals
    pending_stmt = select(func.count()).select_from(PaymentRequest).where(
        PaymentRequest.user_id == user_id,
        PaymentRequest.policy_decision == "REQUIRE_APPROVAL",
        PaymentRequest.status == "policy_evaluated"
    )
    pending_res = await db.execute(pending_stmt)
    pending_approvals = pending_res.scalar() or 0

    # Fetch recent transactions
    tx_stmt = (
        select(Transaction)
        .join(PaymentRequest, Transaction.payment_request_id == PaymentRequest.id)
        .where(PaymentRequest.user_id == user_id)
        .order_by(Transaction.created_at.desc())
        .limit(5)
    )
    tx_res = await db.execute(tx_stmt)
    recent_transactions = list(tx_res.scalars().all())

    return {
        "total_budget_paise": total_budget_paise,
        "total_spent_paise": total_spent_paise,
        "remaining_paise": remaining_paise,
        "pending_approvals": pending_approvals,
        "recent_transactions": [
            {
                "id": t.id,
                "amount_paise": t.amount_paise,
                "currency": t.currency,
                "status": t.status,
                "description": t.payment_request.description if t.payment_request else "Purchase",
                "created_at": t.created_at.isoformat(),
            }
            for t in recent_transactions
        ],
    }
