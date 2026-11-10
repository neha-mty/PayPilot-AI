"""Unit tests for payment provider and webhook security."""
import json
import uuid
import pytest
from app.providers.simulated import SimulatedPaymentProvider


def test_simulated_order_creation():
    provider = SimulatedPaymentProvider()
    import asyncio

    order = asyncio.run(
        provider.create_order(
            amount_paise=18000,
            currency="INR",
            receipt_id="req-1234",
            notes={"test": "true"},
        )
    )

    assert order["amount_paise"] == 18000
    assert order["currency"] == "INR"
    assert order["status"] == "created"
    assert order["order_id"].startswith("sim_ord_")
    assert "simulated" in order["provider"]


def test_webhook_hmac_signature_verification_success():
    provider = SimulatedPaymentProvider()
    payload = {"event": "payment.captured", "order_id": "sim_ord_test123", "amount": 18000}
    payload_bytes = json.dumps(payload).encode("utf-8")

    import hmac
    import hashlib
    valid_sig = hmac.new(provider.secret, payload_bytes, hashlib.sha256).hexdigest()

    assert provider.verify_webhook_signature(payload_bytes, valid_sig) is True


def test_webhook_hmac_signature_verification_failure():
    provider = SimulatedPaymentProvider()
    payload_bytes = b'{"event":"payment.captured"}'
    fake_sig = "invalid_tampered_signature_hex_1234567890"

    assert provider.verify_webhook_signature(payload_bytes, fake_sig) is False
