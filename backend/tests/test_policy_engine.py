"""Unit tests for the deterministic PolicyEngine."""
from types import SimpleNamespace
from app.services.policy_engine import PolicyEngine


def test_policy_allow_when_criteria_met():
    policy = SimpleNamespace(
        max_transaction_paise=50000,
        approval_required=False,
        unknown_merchant_action="require_approval",
    )
    merchant = SimpleNamespace(name="Green Bowl", is_verified=True)
    budgets = [SimpleNamespace(period="daily", category=None, limit_amount_paise=100000)]
    spent = {"daily": 10000}

    result = PolicyEngine.evaluate(
        amount_paise=18000,
        product_price_paise=18000,
        policy=policy,
        budgets=budgets,
        merchant=merchant,
        category="Food",
        spent_in_period=spent,
    )

    assert result.decision == "ALLOW"
    assert "satisfied" in result.primary_reason.lower()


def test_policy_require_approval_by_default_setting():
    policy = SimpleNamespace(
        max_transaction_paise=50000,
        approval_required=True,
        unknown_merchant_action="require_approval",
    )
    merchant = SimpleNamespace(name="Green Bowl", is_verified=True)
    budgets = []

    result = PolicyEngine.evaluate(
        amount_paise=18000,
        product_price_paise=18000,
        policy=policy,
        budgets=budgets,
        merchant=merchant,
        category="Food",
    )

    assert result.decision == "REQUIRE_APPROVAL"
    assert any("approval" in r.lower() for r in result.reasons)


def test_policy_require_approval_for_unverified_merchant():
    policy = SimpleNamespace(
        max_transaction_paise=50000,
        approval_required=False,
        unknown_merchant_action="require_approval",
    )
    merchant = SimpleNamespace(name="Urban Store", is_verified=False)

    result = PolicyEngine.evaluate(
        amount_paise=18000,
        product_price_paise=18000,
        policy=policy,
        budgets=[],
        merchant=merchant,
        category="Shopping",
    )

    assert result.decision == "REQUIRE_APPROVAL"
    assert any("unverified" in r.lower() for r in result.reasons)


def test_policy_block_when_exceeding_max_transaction():
    policy = SimpleNamespace(
        max_transaction_paise=25000,  # ₹250 max
        approval_required=False,
        unknown_merchant_action="require_approval",
    )
    merchant = SimpleNamespace(name="TechZone", is_verified=True)

    result = PolicyEngine.evaluate(
        amount_paise=60000,  # ₹600 requested
        product_price_paise=60000,
        policy=policy,
        budgets=[],
        merchant=merchant,
        category="Electronics",
    )

    assert result.decision == "BLOCK"
    assert "exceeds user's maximum transaction limit" in result.primary_reason


def test_policy_block_on_price_tampering():
    policy = SimpleNamespace(
        max_transaction_paise=100000,
        approval_required=False,
        unknown_merchant_action="require_approval",
    )
    merchant = SimpleNamespace(name="Green Bowl", is_verified=True)

    # Requested amount differs from authoritative DB product price
    result = PolicyEngine.evaluate(
        amount_paise=5000,  # Attempting to buy for ₹50
        product_price_paise=18000,  # Actual price is ₹180
        policy=policy,
        budgets=[],
        merchant=merchant,
        category="Food",
    )

    assert result.decision == "BLOCK"
    assert "Price mismatch detected" in result.primary_reason


def test_policy_block_when_budget_exhausted():
    policy = SimpleNamespace(
        max_transaction_paise=100000,
        approval_required=False,
        unknown_merchant_action="require_approval",
    )
    merchant = SimpleNamespace(name="Green Bowl", is_verified=True)
    budgets = [SimpleNamespace(period="daily", category=None, limit_amount_paise=20000)]  # ₹200 limit
    spent = {"daily": 15000}  # Already spent ₹150

    result = PolicyEngine.evaluate(
        amount_paise=8000,  # Needs ₹80, but remaining is only ₹50
        product_price_paise=8000,
        policy=policy,
        budgets=budgets,
        merchant=merchant,
        category="Food",
        spent_in_period=spent,
    )

    assert result.decision == "BLOCK"
    assert "exceeds remaining daily budget" in result.primary_reason


def test_policy_block_unverified_merchant_strict_rule():
    policy = SimpleNamespace(
        max_transaction_paise=100000,
        approval_required=False,
        unknown_merchant_action="block",  # Strict policy
    )
    merchant = SimpleNamespace(name="Shady Seller", is_verified=False)

    result = PolicyEngine.evaluate(
        amount_paise=10000,
        product_price_paise=10000,
        policy=policy,
        budgets=[],
        merchant=merchant,
        category="Food",
    )

    assert result.decision == "BLOCK"
    assert "unverified, and policy dictates BLOCK" in result.primary_reason
