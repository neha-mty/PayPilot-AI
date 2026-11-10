"""Payment orchestration and webhook endpoints."""
import json
import uuid
from typing import Dict, Any
from fastapi import APIRouter, Depends, Header, Request, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.transaction import PaymentCreate
from app.services.payment_service import create_payment_order, process_webhook
from app.providers.simulated import SimulatedPaymentProvider
from app.config import get_settings

router = APIRouter(prefix="/payments", tags=["Payments"])
settings = get_settings()


@router.post("/create")
async def create_order(
    payload: PaymentCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a gateway payment order after verifying policy and approvals."""
    return await create_payment_order(db, payload.payment_request_id, user.id)


@router.post("/webhook")
async def handle_webhook(
    request: Request,
    x_razorpay_signature: str = Header(None),
    x_simulated_signature: str = Header(None),
    db: AsyncSession = Depends(get_db),
):
    """Receive and verify payment provider webhook notification."""
    payload_bytes = await request.body()
    signature = x_razorpay_signature or x_simulated_signature
    provider_name = "razorpay" if x_razorpay_signature else "simulated"

    if not signature:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing provider webhook signature header.",
        )

    return await process_webhook(db, provider_name, payload_bytes, signature)


@router.post("/simulated-complete")
async def simulated_complete(
    order_id: str,
    outcome: str = "success",  # "success" or "fail"
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Simulate user finishing payment on the sandbox gateway.
    
    Generates genuine HMAC signature and processes it through the official webhook pipeline!
    """
    sim_provider = SimulatedPaymentProvider()
    payment_id = f"sim_pay_{uuid.uuid4().hex[:14]}"
    event_id = f"evt_{uuid.uuid4().hex[:12]}"

    payload = {
        "event_id": event_id,
        "event": "payment.captured" if outcome == "success" else "payment.failed",
        "order_id": order_id,
        "payment_id": payment_id,
        "status": "captured" if outcome == "success" else "failed",
    }
    payload_bytes = json.dumps(payload).encode("utf-8")
    signature = sim_provider.generate_test_signature(payload_bytes)

    # Process through standard webhook handler
    return await process_webhook(db, "simulated", payload_bytes, signature)
