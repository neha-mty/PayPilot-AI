"""Simulated Sandbox Payment Provider for testing and local demonstration.

Clearly labelled as SIMULATED — DOES NOT MOVE REAL MONEY.
Provides realistic order creation, HMAC-SHA256 signature verification,
and test checkout states.
"""
import hmac
import hashlib
import uuid
from typing import Dict, Any
from app.providers.base import PaymentProvider
from app.config import get_settings

settings = get_settings()


class SimulatedPaymentProvider(PaymentProvider):
    def __init__(self):
        self.secret = settings.SIMULATED_WEBHOOK_SECRET.encode("utf-8")

    async def create_order(
        self, amount_paise: int, currency: str, receipt_id: str, notes: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a simulated test order."""
        order_id = f"sim_ord_{uuid.uuid4().hex[:16]}"
        return {
            "order_id": order_id,
            "amount_paise": amount_paise,
            "currency": currency,
            "status": "created",
            "provider": "simulated",
            "provider_label": "Simulated Sandbox Gateway (Test Mode)",
            "checkout_url": f"/sandbox/checkout?order_id={order_id}",
            "raw_response": {
                "id": order_id,
                "entity": "order",
                "amount": amount_paise,
                "currency": currency,
                "receipt": receipt_id,
                "status": "created",
                "simulated": True,
            },
        }

    def generate_test_signature(self, payload_or_order: Any, payment_id: str = "") -> str:
        """Helper to generate a valid HMAC signature for automated tests and demo checkout."""
        if isinstance(payload_or_order, bytes):
            message = payload_or_order
        elif isinstance(payload_or_order, str) and payment_id:
            message = f"{payload_or_order}|{payment_id}".encode("utf-8")
        else:
            message = str(payload_or_order).encode("utf-8")
        return hmac.new(self.secret, message, hashlib.sha256).hexdigest()

    def verify_webhook_signature(self, payload: bytes, signature: str) -> bool:
        """Verify HMAC-SHA256 signature against secret."""
        if not signature:
            return False
        expected_sig = hmac.new(self.secret, payload, hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected_sig, signature)
