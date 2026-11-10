from typing import Dict, Any

try:
    import razorpay
    RAZORPAY_AVAILABLE = True
except (ImportError, Exception):
    razorpay = None
    RAZORPAY_AVAILABLE = False

from app.providers.base import PaymentProvider
from app.config import get_settings

settings = get_settings()


class RazorpayPaymentProvider(PaymentProvider):
    def __init__(self):
        self.key_id = settings.RAZORPAY_KEY_ID
        self.key_secret = settings.RAZORPAY_KEY_SECRET
        self.webhook_secret = settings.RAZORPAY_WEBHOOK_SECRET
        if RAZORPAY_AVAILABLE and self.key_id and self.key_secret:
            self.client = razorpay.Client(auth=(self.key_id, self.key_secret))
        else:
            self.client = None

    async def create_order(
        self, amount_paise: int, currency: str, receipt_id: str, notes: Dict[str, Any]
    ) -> Dict[str, Any]:
        if not self.client:
            raise ValueError("Razorpay client is not initialized. Please set RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET.")

        data = {
            "amount": amount_paise,
            "currency": currency,
            "receipt": receipt_id,
            "notes": notes,
        }
        order = self.client.order.create(data=data)
        return {
            "order_id": order["id"],
            "amount_paise": order["amount"],
            "currency": order["currency"],
            "status": order["status"],
            "provider": "razorpay",
            "provider_label": "Razorpay Sandbox",
            "raw_response": order,
        }

    def verify_webhook_signature(self, payload: bytes, signature: str) -> bool:
        if not self.client or not self.webhook_secret:
            return False
        try:
            self.client.utility.verify_webhook_signature(
                payload.decode("utf-8"), signature, self.webhook_secret
            )
            return True
        except Exception:
            return False
