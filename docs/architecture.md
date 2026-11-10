# PayPilot AI: Architecture & Security Specifications

## 1. System Overview

PayPilot AI is a policy-driven payment authorization platform designed to safely integrate autonomous AI purchasing agents into financial transactions.

The central problem it addresses: **AI agents must never possess direct authority to initiate, modify, or authorize monetary debits.**

```
User Prompt (NL)
      │
      ▼
AI Assistant (LLM + Tools) ────► Catalog Query (DB authoritative prices)
      │
      ▼
Create Payment Request (Pending State)
      │
      ▼
Central Spending-Policy Engine ────► Deterministic checks (Limits, Budgets, Merchant verification)
      │
   ┌──┴────────────────────────┐
   ▼                           ▼
[ALLOW]                 [REQUIRE_APPROVAL]
   │                           │
   │                    User Reviews on Approval Screen
   │                    (Exact Amount & Merchant bound)
   │                           │
   └───────────┬───────────────┘
               ▼
Payment Orchestration Service ────► Generates Gateway Order (Simulated / Razorpay)
               │
               ▼
Gateway Checkout Flow ────► HMAC-SHA256 Signed Webhook Callback
               │
               ▼
Webhook Verification ────► Updates Transaction Ledger & Audit Trail
```

---

## 2. Core Security Guarantees

### A. Separation of AI Intelligence from Financial Authority
- The AI agent's tool set is strictly read-only for catalog exploration, plus one write action: `create_payment_request`.
- The AI has **zero access** to payment gateway credentials, webhook secrets, or order settlement endpoints.

### B. Price & Quantity Tamper Resistance
- The policy engine validates all amounts against authoritative product prices stored in the PostgreSQL/SQLite database.
- If an agent or client requests a modified amount (e.g. ₹50 instead of the official catalog price of ₹180), the policy engine immediately returns `BLOCK`.

### C. Approval Invalidation upon Detail Alteration
- Approvals are cryptographically bound to the exact payment request ID and `approved_amount_paise`.
- If the merchant, item, or amount changes, or if the 15-minute TTL window expires, the approval record becomes permanently invalid.

### D. HMAC-SHA256 Webhook Verification
- Transactions are marked `successful` **only** upon receipt of a valid webhook signed with the provider secret.
- Duplicate webhook notifications are safely dropped using the `webhook_events` idempotency table.

---

## 3. Database Schema

All monetary values are stored in **integer paise** (1 INR = 100 paise) to eliminate floating-point precision loss.

1. `users` — User credentials with Argon2id password hashes and UUIDs.
2. `budgets` — Daily, weekly, monthly, and category spending limits.
3. `spending_policies` — Per-user policy limits, mandatory approval flag, and unknown merchant rules.
4. `merchants` — Verified and unverified merchant directory.
5. `products` — Authoritative prices, categories, and availability.
6. `agents` — AI agent instances (Food Agent, Shopping Agent).
7. `payment_requests` — State machine, policy decision, reason, expiry.
8. `approvals` — User authorization records bound to exact payment details.
9. `transactions` — Gateway order IDs, payment IDs, status, and responses.
10. `audit_logs` — Immutable trail of all authorization decisions and security alerts.
11. `webhook_events` — Idempotency ledger for incoming provider notifications.
12. `agent_tool_calls` — Observability records of agent tool executions.
