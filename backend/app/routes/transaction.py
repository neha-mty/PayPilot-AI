"""Transaction history routes."""
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.transaction import Transaction
from app.models.payment_request import PaymentRequest
from app.schemas.transaction import TransactionOut

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.get("", response_model=List[TransactionOut])
async def list_transactions(
    user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """Retrieve full transaction history for current user."""
    stmt = (
        select(Transaction)
        .join(PaymentRequest, Transaction.payment_request_id == PaymentRequest.id)
        .where(PaymentRequest.user_id == user.id)
        .order_by(Transaction.created_at.desc())
    )
    res = await db.execute(stmt)
    txs = list(res.scalars().all())

    return [
        TransactionOut(
            id=t.id,
            payment_request_id=t.payment_request_id,
            provider=t.provider,
            provider_order_id=t.provider_order_id,
            provider_payment_id=t.provider_payment_id,
            amount_paise=t.amount_paise,
            currency=t.currency,
            status=t.status,
            description=t.payment_request.description if t.payment_request else "Transaction",
            created_at=t.created_at,
        )
        for t in txs
    ]
