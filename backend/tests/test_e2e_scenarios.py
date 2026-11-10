"""End-to-end integration scenario testing for PayPilot AI."""
import httpx
import pytest

BASE_URL = "http://127.0.0.1:8000"


@pytest.mark.asyncio
async def test_complete_purchasing_and_security_scenarios():
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=10.0) as client:
        # 1. Health check
        res = await client.get("/health")
        assert res.status_code == 200
        assert res.json()["status"] == "healthy"

        # 2. Registration
        user_email = f"student_eval_{hash(BASE_URL)}@college.edu"
        reg_res = await client.post(
            "/auth/register",
            json={"name": "Aarav Sharma", "email": user_email, "password": "SecurePassword123!"},
        )
        if reg_res.status_code == 400:
            # Login if user already created
            login_res = await client.post(
                "/auth/login",
                json={"email": user_email, "password": "SecurePassword123!"},
            )
            assert login_res.status_code == 200
            token = login_res.json()["token"]
        else:
            assert reg_res.status_code == 201
            token = reg_res.json()["token"]

        headers = {"Authorization": f"Bearer {token}"}

        # 3. AI Purchasing Assistant: Query for vegetarian lunch under ₹200
        chat_res = await client.post(
            "/assistant/chat",
            json={"message": "Find me a vegetarian lunch under ₹200. Don't make any payment until I approve.", "agent_type": "food"},
            headers=headers,
        )
        assert chat_res.status_code == 200
        chat_data = chat_res.json()
        assert len(chat_data["recommendations"]) > 0
        selected_product = chat_data["recommendations"][0]
        assert selected_product["price_paise"] <= 20000

        # 4. Create Payment Request for selected product
        req_res = await client.post(
            "/payment-requests",
            json={"product_id": selected_product["id"], "agent_type": "food"},
            headers=headers,
        )
        assert req_res.status_code == 201
        pay_req = req_res.json()
        assert pay_req["amount_paise"] == selected_product["price_paise"]
        assert pay_req["policy_decision"] in ["REQUIRE_APPROVAL", "ALLOW"]

        # 5. User Authorization: Approve the request
        appr_res = await client.post(
            f"/payment-requests/{pay_req['id']}/approve",
            headers=headers,
        )
        assert appr_res.status_code == 200
        assert appr_res.json()["decision"] == "approved"

        # 6. Payment Orchestration: Create Gateway Order
        order_res = await client.post(
            "/payments/create",
            json={"payment_request_id": pay_req["id"]},
            headers=headers,
        )
        assert order_res.status_code == 200
        order_data = order_res.json()
        assert order_data["status"] == "created"
        assert "sim_ord_" in order_data["order_id"]

        # 7. Complete Sandbox Payment via Verified HMAC Webhook
        complete_res = await client.post(
            f"/payments/simulated-complete?order_id={order_data['order_id']}&outcome=success",
            headers=headers,
        )
        assert complete_res.status_code == 200
        assert complete_res.json()["status"] == "success"

        # 8. Verify Transaction History is updated
        tx_res = await client.get("/transactions", headers=headers)
        assert tx_res.status_code == 200
        transactions = tx_res.json()
        matching_tx = next((t for t in transactions if t["payment_request_id"] == pay_req["id"]), None)
        assert matching_tx is not None
        assert matching_tx["status"] == "successful"

        # 9. Scenario: Policy Violation (Block when exceeding max limit)
        # Update user's max transaction limit to ₹100 (10000 paise)
        await client.post(
            "/policies",
            json={"max_transaction_paise": 10000, "approval_required": True, "unknown_merchant_action": "require_approval", "is_active": True},
            headers=headers,
        )

        # Attempt to buy Paneer Tikka Thali (₹180 / 18000 paise)
        block_req_res = await client.post(
            "/payment-requests",
            json={"product_id": selected_product["id"], "agent_type": "food"},
            headers=headers,
        )
        assert block_req_res.status_code == 201
        assert block_req_res.json()["policy_decision"] == "BLOCK"
        assert "exceeds user's maximum transaction limit" in block_req_res.json()["policy_reason"]

        # 10. Scenario: Verify Audit Log captures security and decision events
        audit_res = await client.get("/audit-logs", headers=headers)
        assert audit_res.status_code == 200
        logs = audit_res.json()
        actions = [l["action"] for l in logs]
        assert any("policy_evaluated" in a for a in actions)
        assert any("approval_granted" in a for a in actions)
        assert any("payment_successful" in a for a in actions)
