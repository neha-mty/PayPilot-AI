"""Abstract base class for payment providers."""
from abc import ABC, abstractmethod
from typing import Dict, Any


class PaymentProvider(ABC):
    @abstractmethod
    async def create_order(
        self, amount_paise: int, currency: str, receipt_id: str, notes: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a payment order with the gateway.
        
        Returns dict with keys:
          - order_id: str
          - amount_paise: int
          - currency: str
          - status: str
          - checkout_url: Optional[str]
          - raw_response: Dict[str, Any]
        """
        pass

    @abstractmethod
    def verify_webhook_signature(self, payload: bytes, signature: str) -> bool:
        """Verify HMAC signature of incoming webhook."""
        pass
