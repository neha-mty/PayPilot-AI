"""Central Spending-Policy Engine for PayPilot AI.

This module is completely independent from the LLM. It executes deterministic
rules to authorize, require approval, or block purchase requests.
"""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Literal, Optional, List, Dict, Any


PolicyDecisionType = Literal["ALLOW", "REQUIRE_APPROVAL", "BLOCK"]


@dataclass
class PolicyEvaluationResult:
    decision: PolicyDecisionType
    reasons: List[str]
    policy_details: Dict[str, Any] = field(default_factory=dict)
    evaluated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def primary_reason(self) -> str:
        if not self.reasons:
            return "Policy evaluation passed."
        return "; ".join(self.reasons)


class PolicyEngine:
    """Deterministic policy engine that governs payment requests."""

    @staticmethod
    def evaluate(
        amount_paise: int,
        product_price_paise: int,
        policy: Optional[Any],  # SpendingPolicy model or None
        budgets: List[Any],  # List of Budget models
        merchant: Optional[Any],  # Merchant model or None
        category: Optional[str] = None,
        spent_in_period: Optional[Dict[str, int]] = None,
        is_expired: bool = False,
    ) -> PolicyEvaluationResult:
        """Evaluate a payment request against user policies and budgets.
        
        Order of evaluation:
        1. Basic sanity & data tampering checks (BLOCK)
        2. Maximum transaction limit (BLOCK if exceeded)
        3. Periodic & category budget limits (BLOCK if budget exhausted)
        4. Merchant verification & unknown merchant rules (BLOCK or REQUIRE_APPROVAL)
        5. User policy approval_required rule (REQUIRE_APPROVAL)
        6. Default ALLOW if all checks pass without approval flag
        """
        reasons: List[str] = []
        details: Dict[str, Any] = {}
        spent_in_period = spent_in_period or {"daily": 0, "weekly": 0, "monthly": 0, "category": 0}

        # --- Rule 1: Expiry check ---
        if is_expired:
            return PolicyEvaluationResult(
                decision="BLOCK",
                reasons=["Payment request has expired."],
                policy_details={"rule": "expiry_check", "status": "expired"}
            )

        # --- Rule 2: Non-positive or Price Tampering check ---
        if amount_paise <= 0:
            return PolicyEvaluationResult(
                decision="BLOCK",
                reasons=["Transaction amount must be strictly positive."],
                policy_details={"rule": "price_tampering", "amount_paise": amount_paise}
            )

        if amount_paise != product_price_paise:
            return PolicyEvaluationResult(
                decision="BLOCK",
                reasons=[
                    f"Price mismatch detected: requested ₹{amount_paise/100:.2f} but official product price is ₹{product_price_paise/100:.2f}."
                ],
                policy_details={
                    "rule": "price_tampering",
                    "requested_paise": amount_paise,
                    "actual_paise": product_price_paise
                }
            )

        # --- Rule 3: User Policy Limit Check ---
        max_limit = getattr(policy, "max_transaction_paise", 50000) if policy else 50000  # Default ₹500
        details["max_transaction_paise"] = max_limit

        if amount_paise > max_limit:
            return PolicyEvaluationResult(
                decision="BLOCK",
                reasons=[
                    f"Amount ₹{amount_paise/100:.2f} exceeds user's maximum transaction limit of ₹{max_limit/100:.2f}."
                ],
                policy_details={"rule": "max_transaction_limit", "limit_paise": max_limit, "amount_paise": amount_paise}
            )

        # --- Rule 4: Budget Limits Check ---
        for b in (budgets or []):
            b_period = getattr(b, "period", "monthly")
            b_cat = getattr(b, "category", None)
            b_limit = getattr(b, "limit_amount_paise", 0)

            # Check general period budget
            if not b_cat:
                current_spent = spent_in_period.get(b_period, 0)
                if current_spent + amount_paise > b_limit:
                    return PolicyEvaluationResult(
                        decision="BLOCK",
                        reasons=[
                            f"Purchase of ₹{amount_paise/100:.2f} exceeds remaining {b_period} budget. Limit: ₹{b_limit/100:.2f}, Spent: ₹{current_spent/100:.2f}."
                        ],
                        policy_details={
                            "rule": f"{b_period}_budget_exceeded",
                            "limit_paise": b_limit,
                            "spent_paise": current_spent,
                            "requested_paise": amount_paise
                        }
                    )

            # Check category budget
            elif category and b_cat.lower() == category.lower():
                current_cat_spent = spent_in_period.get("category", 0)
                if current_cat_spent + amount_paise > b_limit:
                    return PolicyEvaluationResult(
                        decision="BLOCK",
                        reasons=[
                            f"Purchase exceeds {category} category budget of ₹{b_limit/100:.2f}. Spent so far: ₹{current_cat_spent/100:.2f}."
                        ],
                        policy_details={
                            "rule": "category_budget_exceeded",
                            "category": category,
                            "limit_paise": b_limit,
                            "spent_paise": current_cat_spent,
                            "requested_paise": amount_paise
                        }
                    )

        # --- Rule 5: Merchant Verification Check ---
        merchant_verified = getattr(merchant, "is_verified", False) if merchant else False
        unknown_action = getattr(policy, "unknown_merchant_action", "require_approval") if policy else "require_approval"
        details["merchant_verified"] = merchant_verified
        details["unknown_merchant_action"] = unknown_action

        if not merchant_verified:
            if unknown_action == "block":
                return PolicyEvaluationResult(
                    decision="BLOCK",
                    reasons=[f"Merchant '{getattr(merchant, 'name', 'Unknown')}' is unverified, and policy dictates BLOCK."],
                    policy_details={"rule": "unverified_merchant_block", "merchant": getattr(merchant, "name", "Unknown")}
                )
            elif unknown_action == "require_approval":
                reasons.append(f"Merchant '{getattr(merchant, 'name', 'Unknown')}' is unverified; explicit approval required.")

        # --- Rule 6: Mandatory Approval Rule ---
        approval_required = getattr(policy, "approval_required", True) if policy else True
        details["approval_required"] = approval_required

        if approval_required:
            reasons.append("User policy requires manual approval before payment execution.")

        # If any reasons trigger approval
        if reasons:
            return PolicyEvaluationResult(
                decision="REQUIRE_APPROVAL",
                reasons=reasons,
                policy_details=details
            )

        # Otherwise, ALLOW
        return PolicyEvaluationResult(
            decision="ALLOW",
            reasons=["All policy and budget criteria satisfied without mandatory approval."],
            policy_details=details
        )
