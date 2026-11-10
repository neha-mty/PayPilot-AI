"""Payment Orchestration and Webhook Processing Service."""
import uuid
import json
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status

from app.models.payment_request import PaymentRequest
from app.models.approval import Approval
from app.models.transaction import Transaction
from app.models.webhook_event import WebhookEvent
from app.providers.base import PaymentProvider
from app.providers.simulated import SimulatedPaymentProvider
from app.providers.razorpay import RazorpayPaymentProvider
from app.services.audit_service import log_event
from app.config import get_settings

settings = get_settings()


def get_payment_provider() -> PaymentProvider:
    """Instantiate configured payment provider."""
    if settings.PAYMENT_PROVIDER == "razorpay" and settings.RAZORPAY_KEY_ID:
        return RazorpayPaymentProvider()
    return SimulatedPaymentProvider()


async def create_payment_order(
    db: AsyncSession, payment_request_id: str, user_id: str
) -> Dict[str, Any]:
    """Execute gateway order creation after strictly verifying policy and user approval."""
    # 1. Fetch payment request
    req_res = await db.execute(
        select(PaymentRequest).where(PaymentRequest.id == payment_request_id, PaymentRequest.user_id == user_id)
    )
    request = req_res.scalar_one_or_none()
    if not request:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment request not found")

    # 2. Prevent duplicate transaction creation (idempotency check on existing transaction)
    tx_res = await db.execute(
        select(Transaction).where(Transaction.payment_request_id == payment_request_id)
    )
    existing_tx = tx_res.scalar_one_or_none()
    if existing_tx and existing_tx.status in ["created", "pending", "successful"]:
        return {
            "transaction_id": existing_tx.id,
            "order_id": existing_tx.provider_order_id,
            "amount_paise": existing_tx.amount_paise,
            "currency": existing_tx.currency,
            "status": existing_tx.status,
            "provider": existing_tx.provider,
            "message": "Order already exists for this payment request.",
        }

    # 3. Policy & Approval authorization check
    if request.policy_decision == "BLOCK":
        await log_event(
            db,
            action="payment_attempt_blocked",
            actor_type="system",
            user_id=user_id,
            payment_request_id=request.id,
            decision_reason=f"Payment denied: Request is in BLOCKED state ({request.policy_reason})",
        )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Payment request was blocked by policy.")

    if request.policy_decision == "REQUIRE_APPROVAL":
        # Check approval record
        appr_res = await db.execute(
            select(Approval).where(Approval.payment_request_id == payment_request_id, Approval.decision == "approved")
        )
        approval = appr_res.scalar_one_or_none()
        if not approval:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Payment cannot proceed: Explicit user approval is required.",
            )

        # Check approval expiry
        if approval.expires_at and datetime.now(timezone.utc) > approval.expires_at.replace(tzinfo=timezone.utc):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Approval has expired. Re-approval required.")

        # Check amount tampering against approved amount
        if approval.approved_amount_paise != request.amount_paise:
            await log_event(
                db,
                action="security_tamper_detected",
                actor_type="system",
                user_id=user_id,
                payment_request_id=request.id,
                decision_reason=f"Approved amount {approval.approved_amount_paise} != request amount {request.amount_paise}",
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Security violation: Requested amount does not match approved amount.",
            )

    # 4. Dispatch order creation to Payment Gateway
    provider = get_payment_provider()
    order_data = await provider.create_order(
        amount_paise=request.amount_paise,
        currency=request.currency,
        receipt_id=request.id,
        notes={"user_id": user_id, "payment_request_id": request.id},
    )

    # 5. Record transaction in database
    transaction = Transaction(
        id=str(uuid.uuid4()),
        payment_request_id=request.id,
        provider=order_data.get("provider", "simulated"),
        provider_order_id=order_data.get("order_id"),
        amount_paise=request.amount_paise,
        currency=request.currency,
        status="created",
        provider_response=json.dumps(order_data.get("raw_response", {})),
        created_at=datetime.now(timezone.utc),
    )
    db.add(transaction)
    request.status = "payment_created"

    await log_event(
        db,
        action="payment_order_created",
        actor_type="payment_provider",
        user_id=user_id,
        payment_request_id=request.id,
        decision_reason=f"Gateway order {order_data.get('order_id')} created with {transaction.provider}",
        metadata={"order_id": order_data.get("order_id"), "amount_paise": request.amount_paise},
    )

    return {
        "transaction_id": transaction.id,
        "order_id": order_data.get("order_id"),
        "amount_paise": request.amount_paise,
        "currency": request.currency,
        "status": transaction.status,
        "provider": transaction.provider,
        "provider_label": order_data.get("provider_label", "Simulated Sandbox"),
        "checkout_url": order_data.get("checkout_url"),
    }


async def process_webhook(
    db: AsyncSession, provider_name: str, payload_bytes: bytes, signature: str
) -> Dict[str, Any]:
    """Process an asynchronous webhook notification from the payment provider with signature verification and idempotency."""
    provider = get_payment_provider()

    # 1. Verify HMAC Signature
    is_valid = provider.verify_webhook_signature(payload_bytes, signature)
    if not is_valid:
        await log_event(
            db,
            action="webhook_verification_failed",
            actor_type="payment_provider",
            decision_reason="Invalid HMAC signature on incoming webhook payload",
            metadata={"provider": provider_name, "signature": signature},
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid webhook signature.",
        )

    # 2. Parse payload
    try:
        data = json.loads(payload_bytes.decode("utf-8"))
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Malformed JSON in webhook")

    event_id = data.get("event_id") or data.get("id") or str(uuid.uuid4())
    event_type = data.get("event") or "payment.captured"

    # 3. Idempotency check in webhook_events
    existing_event = await db.execute(
        select(WebhookEvent).where(WebhookEvent.provider_event_id == event_id)
    )
    if existing_event.scalar_one_or_none():
        return {"status": "duplicate_event_ignored", "event_id": event_id}

    webhook_record = WebhookEvent(
        id=str(uuid.uuid4()),
        provider=provider_name,
        provider_event_id=event_id,
        event_type=event_type,
        payload_json=payload_bytes.decode("utf-8"),
        processing_status="processing",
        created_at=datetime.now(timezone.utc),
    )
    db.add(webhook_record)

    # 4. Resolve target transaction
    order_id = data.get("order_id") or data.get("payload", {}).get("payment", {}).get("entity", {}).get("order_id")
    payment_id = data.get("payment_id") or data.get("payload", {}).get("payment", {}).get("entity", {}).get("id")

    if order_id:
        tx_res = await db.execute(select(Transaction).where(Transaction.provider_order_id == order_id))
        transaction = tx_res.scalar_one_or_none()
        if transaction:
            transaction.provider_payment_id = payment_id
            transaction.status = "successful" if "fail" not in event_type else "failed"

            # Update payment request status
            req_res = await db.execute(
                select(PaymentRequest).where(PaymentRequest.id == transaction.payment_request_id)
            )
            req = req_res.scalar_one_or_none()
            if req:
                req.status = "completed" if transaction.status == "successful" else "failed"

            await log_event(
                db,
                action=f"payment_{transaction.status}",
                actor_type="payment_provider",
                user_id=req.user_id if req else None,
                payment_request_id=transaction.payment_request_id,
                decision_reason=f"Webhook confirmed payment {payment_id} status={transaction.status}",
                metadata={"order_id": order_id, "payment_id": payment_id},
            )

    webhook_record.processing_status = "processed"
    return {"status": "success", "event_id": event_id}
