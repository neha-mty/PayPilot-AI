"""Payment Request and Approval Workflow Service."""
import uuid
from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status

from app.models.payment_request import PaymentRequest
from app.models.approval import Approval
from app.models.product import Product
from app.models.merchant import Merchant
from app.models.policy import SpendingPolicy
from app.models.budget import Budget
from app.services.policy_engine import PolicyEngine
from app.services.budget_service import calculate_spent_amounts
from app.services.audit_service import log_event
from app.config import get_settings

settings = get_settings()


async def create_payment_request(
    db: AsyncSession,
    user_id: str,
    product_id: str,
    agent_id: Optional[str] = None,
    idempotency_key: Optional[str] = None,
) -> PaymentRequest:
    """Create a new payment request and immediately evaluate policy."""
    # Check idempotency
    if idempotency_key:
        existing = await db.execute(
            select(PaymentRequest).where(PaymentRequest.idempotency_key == idempotency_key)
        )
        existing_req = existing.scalar_one_or_none()
        if existing_req:
            await log_event(
                db,
                action="duplicate_request_detected",
                actor_type="system",
                user_id=user_id,
                payment_request_id=existing_req.id,
                decision_reason=f"Idempotent replay detected with key: {idempotency_key}",
            )
            return existing_req

    # Fetch authoritative product from database
    prod_res = await db.execute(select(Product).where(Product.id == product_id))
    product = prod_res.scalar_one_or_none()
    if not product:
        from app.marketplace.provider_manager import MarketplaceProviderManager
        norm_prod = await MarketplaceProviderManager.get_product_by_id(db, product_id)
        if norm_prod:
            # Resolve or create merchant record
            merch_res = await db.execute(select(Merchant).where(Merchant.name == norm_prod.merchant))
            merchant = merch_res.scalar_one_or_none()
            if not merchant:
                merchant = Merchant(
                    id=norm_prod.merchant_id or f"m-{norm_prod.provider_code}-auto",
                    name=norm_prod.merchant,
                    category=norm_prod.category,
                    is_verified=True,
                    is_active=True,
                )
                db.add(merchant)
                await db.flush()

            product = Product(
                id=norm_prod.id,
                merchant_id=merchant.id,
                name=norm_prod.name,
                description=norm_prod.description,
                price_paise=norm_prod.price_paise,
                original_price_paise=int(norm_prod.original_price_inr * 100) if norm_prod.original_price_inr else None,
                category=norm_prod.category,
                subcategory=norm_prod.subcategory,
                brand=norm_prod.brand,
                image_url=norm_prod.image_url,
                product_url=norm_prod.product_url,
                provider_code=norm_prod.provider_code,
                provider_name=norm_prod.provider,
                data_source_type=norm_prod.data_source_type,
                rating=norm_prod.rating,
                rating_count=norm_prod.rating_count,
                supports_integrated_checkout=norm_prod.supports_integrated_checkout,
                is_available=norm_prod.is_available,
            )
            db.add(product)
            await db.flush()
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    if not product.is_available:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Product is not currently available")

    # Fetch merchant
    merch_res = await db.execute(select(Merchant).where(Merchant.id == product.merchant_id))
    merchant = merch_res.scalar_one_or_none()

    # Fetch user policy
    pol_res = await db.execute(
        select(SpendingPolicy).where(SpendingPolicy.user_id == user_id, SpendingPolicy.is_active == True)
    )
    user_policy = pol_res.scalar_one_or_none()

    # Fetch user budgets
    budg_res = await db.execute(select(Budget).where(Budget.user_id == user_id))
    user_budgets = list(budg_res.scalars().all())

    # Calculate past spending
    spent = await calculate_spent_amounts(db, user_id, category=product.category)

    # Deterministic policy engine evaluation
    eval_result = PolicyEngine.evaluate(
        amount_paise=product.price_paise,
        product_price_paise=product.price_paise,
        policy=user_policy,
        budgets=user_budgets,
        merchant=merchant,
        category=product.category,
        spent_in_period=spent,
    )

    expiry = datetime.now(timezone.utc) + timedelta(minutes=settings.APPROVAL_EXPIRY_MINUTES)
    description = f"Purchase {product.name} from {merchant.name if merchant else 'Merchant'}"

    payment_request = PaymentRequest(
        id=str(uuid.uuid4()),
        user_id=user_id,
        agent_id=agent_id,
        merchant_id=product.merchant_id,
        product_id=product.id,
        amount_paise=product.price_paise,
        currency="INR",
        description=description,
        policy_decision=eval_result.decision,
        policy_reason=eval_result.primary_reason,
        status="policy_evaluated",
        idempotency_key=idempotency_key,
        expires_at=expiry,
        created_at=datetime.now(timezone.utc),
    )
    db.add(payment_request)
    await db.flush()

    # Log policy evaluation audit
    audit_action = f"policy_evaluated_{eval_result.decision.lower()}"
    await log_event(
        db,
        action=audit_action,
        actor_type="system",
        user_id=user_id,
        payment_request_id=payment_request.id,
        decision_reason=eval_result.primary_reason,
        metadata={
            "decision": eval_result.decision,
            "reasons": eval_result.reasons,
            "amount_paise": product.price_paise,
            "merchant_id": product.merchant_id,
            "policy_details": eval_result.policy_details,
        },
    )

    return payment_request


async def approve_payment_request(db: AsyncSession, payment_request_id: str, user_id: str) -> Approval:
    """Explicitly grant user approval for a payment request."""
    req_res = await db.execute(
        select(PaymentRequest).where(PaymentRequest.id == payment_request_id, PaymentRequest.user_id == user_id)
    )
    request = req_res.scalar_one_or_none()
    if not request:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment request not found or unauthorized")

    # Expiry check
    if request.expires_at and datetime.now(timezone.utc) > request.expires_at.replace(tzinfo=timezone.utc):
        request.status = "expired"
        await log_event(
            db,
            action="approval_failed_expired",
            actor_type="user",
            user_id=user_id,
            payment_request_id=request.id,
            decision_reason="Attempted to approve expired payment request",
        )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Payment request has expired")

    if request.policy_decision == "BLOCK":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot approve a blocked payment request: {request.policy_reason}",
        )

    # Check if already approved/rejected
    appr_res = await db.execute(select(Approval).where(Approval.payment_request_id == payment_request_id))
    existing_approval = appr_res.scalar_one_or_none()

    if existing_approval:
        if existing_approval.decision == "approved":
            return existing_approval
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Payment request was previously rejected")

    approval = Approval(
        id=str(uuid.uuid4()),
        payment_request_id=payment_request_id,
        user_id=user_id,
        decision="approved",
        approved_amount_paise=request.amount_paise,
        approved_at=datetime.now(timezone.utc),
        expires_at=request.expires_at,
        created_at=datetime.now(timezone.utc),
    )
    db.add(approval)
    request.status = "approved"

    await log_event(
        db,
        action="approval_granted",
        actor_type="user",
        user_id=user_id,
        payment_request_id=request.id,
        decision_reason=f"User approved transaction for ₹{request.amount_paise/100:.2f}",
        metadata={"approved_amount_paise": request.amount_paise},
    )

    return approval


async def reject_payment_request(db: AsyncSession, payment_request_id: str, user_id: str) -> Approval:
    """Explicitly reject a payment request."""
    req_res = await db.execute(
        select(PaymentRequest).where(PaymentRequest.id == payment_request_id, PaymentRequest.user_id == user_id)
    )
    request = req_res.scalar_one_or_none()
    if not request:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment request not found or unauthorized")

    approval = Approval(
        id=str(uuid.uuid4()),
        payment_request_id=payment_request_id,
        user_id=user_id,
        decision="rejected",
        approved_amount_paise=None,
        approved_at=None,
        expires_at=None,
        created_at=datetime.now(timezone.utc),
    )
    db.add(approval)
    request.status = "rejected"

    await log_event(
        db,
        action="approval_rejected",
        actor_type="user",
        user_id=user_id,
        payment_request_id=request.id,
        decision_reason="User manually rejected payment request",
    )

    return approval
