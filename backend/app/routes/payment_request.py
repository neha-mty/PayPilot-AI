"""Payment request and approval workflow routes."""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.payment_request import PaymentRequest
from app.models.merchant import Merchant
from app.models.product import Product
from app.schemas.payment_request import PaymentRequestCreate, PaymentRequestOut
from app.schemas.approval import ApprovalOut
from app.services.approval_service import (
    create_payment_request,
    approve_payment_request,
    reject_payment_request,
)

router = APIRouter(prefix="/payment-requests", tags=["Payment Requests"])


def _format_request_out(req: PaymentRequest) -> PaymentRequestOut:
    """Format ORM payment request with nested product and merchant metadata."""
    merch_dict = None
    if req.merchant:
        merch_dict = {
            "id": req.merchant.id,
            "name": req.merchant.name,
            "category": req.merchant.category,
            "is_verified": req.merchant.is_verified,
        }

    prod_dict = None
    if req.product:
        prod_dict = {
            "id": req.product.id,
            "name": req.product.name,
            "price_paise": req.product.price_paise,
            "category": req.product.category,
            "description": req.product.description,
        }

    return PaymentRequestOut(
        id=req.id,
        user_id=req.user_id,
        agent_id=req.agent_id,
        merchant_id=req.merchant_id,
        product_id=req.product_id,
        amount_paise=req.amount_paise,
        currency=req.currency,
        description=req.description,
        policy_decision=req.policy_decision,
        policy_reason=req.policy_reason,
        status=req.status,
        idempotency_key=req.idempotency_key,
        expires_at=req.expires_at,
        created_at=req.created_at,
        merchant=merch_dict,
        product=prod_dict,
    )


@router.post("", response_model=PaymentRequestOut, status_code=status.HTTP_201_CREATED)
async def create_request(
    payload: PaymentRequestCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new payment request and evaluate spending policies."""
    req = await create_payment_request(
        db=db,
        user_id=user.id,
        product_id=payload.product_id,
        agent_id=None,
        idempotency_key=payload.idempotency_key,
    )
    await db.commit()
    # Refresh to load merchant and product relationships
    res = await db.execute(
        select(PaymentRequest)
        .where(PaymentRequest.id == req.id)
        .options(selectinload(PaymentRequest.merchant), selectinload(PaymentRequest.product))
    )
    loaded_req = res.scalar_one()
    return _format_request_out(loaded_req)


@router.get("", response_model=List[PaymentRequestOut])
async def list_user_requests(
    status_filter: Optional[str] = Query(None, alias="status"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List payment requests belonging to current user."""
    stmt = (
        select(PaymentRequest)
        .where(PaymentRequest.user_id == user.id)
        .options(selectinload(PaymentRequest.merchant), selectinload(PaymentRequest.product))
        .order_by(PaymentRequest.created_at.desc())
    )
    if status_filter:
        stmt = stmt.where(PaymentRequest.status == status_filter)

    res = await db.execute(stmt)
    requests = list(res.scalars().all())
    return [_format_request_out(r) for r in requests]


@router.get("/{request_id}", response_model=PaymentRequestOut)
async def get_request(
    request_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get single payment request with ownership validation."""
    res = await db.execute(
        select(PaymentRequest)
        .where(PaymentRequest.id == request_id, PaymentRequest.user_id == user.id)
        .options(selectinload(PaymentRequest.merchant), selectinload(PaymentRequest.product))
    )
    req = res.scalar_one_or_none()
    if not req:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment request not found")
    return _format_request_out(req)


@router.post("/{request_id}/approve", response_model=ApprovalOut)
async def approve_request(
    request_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """User grants explicit approval for a specific payment request."""
    approval = await approve_payment_request(db, request_id, user.id)
    return ApprovalOut.model_validate(approval)


@router.post("/{request_id}/reject", response_model=ApprovalOut)
async def reject_request(
    request_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """User manually rejects a payment request."""
    approval = await reject_payment_request(db, request_id, user.id)
    return ApprovalOut.model_validate(approval)
