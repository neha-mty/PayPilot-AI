# PayPilot AI: REST API Documentation

Base URL: `http://localhost:8000` (or reverse proxied via frontend at `/api`)
Interactive Swagger Docs: `http://localhost:8000/docs`

---

## 1. Authentication

### `POST /auth/register`
Create user account and initialize default policy rules.
- **Request Body**:
  ```json
  {
    "name": "Aarav Sharma",
    "email": "aarav@example.com",
    "password": "Password123!"
  }
  ```
- **Response** (`201 Created`):
  ```json
  {
    "user": { "id": "uuid", "name": "Aarav Sharma", "email": "aarav@example.com" },
    "token": "eyJhbGciOiJIUzI1NiIs..."
  }
  ```

### `POST /auth/login`
Authenticate with email and password to receive JWT bearer token.

---

## 2. AI Assistant

### `POST /assistant/chat`
Submit natural language purchase queries to agent.
- **Headers**: `Authorization: Bearer <JWT>`
- **Request Body**:
  ```json
  {
    "message": "Find me a vegetarian lunch under ₹200. Don't make any payment until I approve.",
    "agent_type": "food"
  }
  ```
- **Response**:
  ```json
  {
    "reply": "I found 3 matching options...",
    "agent_type": "food",
    "recommendations": [
      {
        "id": "p-001",
        "name": "Paneer Tikka Thali",
        "price_paise": 18000,
        "price_inr": 180.0
      }
    ],
    "action_taken": "catalog_searched"
  }
  ```

---

## 3. Spending Policy & Budgets

### `GET /policies`
Retrieve user's active spending rules.

### `POST /policies`
Update policy parameters:
```json
{
  "max_transaction_paise": 50000,
  "approval_required": true,
  "unknown_merchant_action": "require_approval",
  "is_active": true
}
```

### `GET /budget`
List all active period and category budget ceilings.

### `POST /budget`
Create new spending limit:
```json
{
  "period": "daily",
  "category": "Food",
  "limit_amount_paise": 20000
}
```

---

## 4. Payment Requests & Approvals

### `POST /payment-requests`
Create payment request and immediately evaluate deterministic policy rules.
- **Request Body**:
  ```json
  {
    "product_id": "p-001",
    "agent_type": "food",
    "idempotency_key": "opt-key-123"
  }
  ```
- **Response**:
  ```json
  {
    "id": "req-uuid",
    "amount_paise": 18000,
    "currency": "INR",
    "policy_decision": "REQUIRE_APPROVAL",
    "policy_reason": "User policy requires manual approval before payment execution.",
    "status": "policy_evaluated"
  }
  ```

### `POST /payment-requests/{id}/approve`
Explicitly authorize a payment request.

### `POST /payment-requests/{id}/reject`
Explicitly reject a payment request.

---

## 5. Payment Orchestration & Webhooks

### `POST /payments/create`
Rechecks policy and approval; creates order with the configured payment gateway.

### `POST /payments/webhook`
Receives payment provider callbacks, verifies HMAC-SHA256 signature, and updates transaction ledger.

### `POST /payments/simulated-complete?order_id=...&outcome=success`
Simulates customer completing payment in sandbox, dispatching an authentic HMAC-SHA256 signed webhook.

---

## 6. Audit & History

### `GET /transactions`
List confirmed, failed, and pending transactions.

### `GET /audit-logs`
Inspect the tamper-evident security audit trail with optional actor filter (`user`, `agent`, `system`, `payment_provider`).
