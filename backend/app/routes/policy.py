"""Spending policy configuration routes."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.policy import SpendingPolicy
from app.schemas.policy import SpendingPolicyUpdate, SpendingPolicyOut
from app.services.audit_service import log_event

router = APIRouter(prefix="/policies", tags=["Policies"])


@router.get("", response_model=SpendingPolicyOut)
async def get_active_policy(
    user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """Get active spending policy for current user."""
    res = await db.execute(
        select(SpendingPolicy).where(SpendingPolicy.user_id == user.id, SpendingPolicy.is_active == True)
    )
    policy = res.scalar_one_or_none()
    if not policy:
        # Create default if not found
        policy = SpendingPolicy(
            user_id=user.id,
            max_transaction_paise=50000,
            approval_required=True,
            unknown_merchant_action="require_approval",
            is_active=True,
        )
        db.add(policy)
        await db.flush()

    return SpendingPolicyOut.model_validate(policy)


@router.post("", response_model=SpendingPolicyOut)
async def update_policy(
    payload: SpendingPolicyUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update user's spending policy rules."""
    res = await db.execute(
        select(SpendingPolicy).where(SpendingPolicy.user_id == user.id, SpendingPolicy.is_active == True)
    )
    policy = res.scalar_one_or_none()

    if not policy:
        policy = SpendingPolicy(user_id=user.id)
        db.add(policy)

    policy.max_transaction_paise = payload.max_transaction_paise
    policy.approval_required = payload.approval_required
    policy.unknown_merchant_action = payload.unknown_merchant_action
    policy.is_active = payload.is_active

    await log_event(
        db,
        action="policy_updated",
        actor_type="user",
        user_id=user.id,
        decision_reason=(
            f"Policy updated: max_tx=₹{payload.max_transaction_paise/100:.2f}, "
            f"approval={payload.approval_required}, unknown={payload.unknown_merchant_action}"
        ),
        metadata=payload.model_dump(),
    )

    return SpendingPolicyOut.model_validate(policy)
