"""AI Purchasing Assistant Service for Universal Marketplace Discovery.

Uses Google Gemini API when configured; otherwise provides deterministic,
high-precision intent parsing and marketplace recommendation synthesis.
"""
import re
import json
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.nlp_classifier import NLPQueryClassifier
from app.marketplace.provider_manager import MarketplaceProviderManager
from app.config import get_settings

settings = get_settings()

UNIVERSAL_SYSTEM_PROMPT = """
You are PayPilot AI, a secure universal marketplace purchasing assistant.
Your role is to understand user purchase requests across ANY product or service category,
search configured and accessible marketplaces, compare options based on price and features,
and recommend the best verified options.

SECURITY RULES:
1. You DO NOT have authority to make payments or transfer money.
2. You can only search products and recommend options.
3. Once the user picks a product, you can create a payment request.
4. You must never invent or assume prices — always use verified prices from the marketplace results.
5. All payment authorization is handled by the deterministic backend policy engine and the user.
"""


class AIAssistantService:
    @staticmethod
    async def process_user_message(
        db: AsyncSession,
        user_id: str,
        message: str,
        agent_type: str = "universal",
    ) -> Dict[str, Any]:
        """Process natural language request, dynamically detect category/intent, search multi-providers, and return unified results."""
        # Classify intent dynamically
        intent = NLPQueryClassifier.classify_query(message)

        # Multi-provider parallel search
        normalized_products = await MarketplaceProviderManager.search_all_marketplaces(
            db=db,
            query=message,
            category=intent["detected_category"],
            subcategory=intent["detected_subcategory"],
            brand=intent["detected_brand"],
            provider_code=intent["detected_provider_code"],
            min_price_paise=intent["min_price_paise"],
            max_price_paise=intent["max_price_paise"],
            limit=6,
        )

        recommendations = [
            {
                "id": p.id,
                "name": p.name,
                "description": p.description,
                "price_paise": p.price_paise,
                "price_inr": p.price_inr,
                "original_price_inr": p.original_price_inr,
                "discount_percent": p.discount_percent,
                "category": p.category,
                "subcategory": p.subcategory,
                "brand": p.brand,
                "merchant": p.merchant,
                "merchant_id": p.merchant_id,
                "provider": p.provider,
                "provider_code": p.provider_code,
                "image_url": p.image_url,
                "product_url": p.product_url,
                "is_available": p.is_available,
                "data_source_type": p.data_source_type,
                "rating": p.rating,
                "rating_count": p.rating_count,
                "supports_integrated_checkout": p.supports_integrated_checkout,
                "delivery_info": p.delivery_info,
            }
            for p in normalized_products
        ]

        # Conversational summary
        if settings.GEMINI_API_KEY:
            try:
                import google.generativeai as genai
                genai.configure(api_key=settings.GEMINI_API_KEY)
                model = genai.GenerativeModel("gemini-1.5-flash")
                prompt = f"""
{UNIVERSAL_SYSTEM_PROMPT}

User query: "{message}"
Detected Category: {intent['detected_category']} (Subcategory: {intent['detected_subcategory']})
Detected Brand/Provider: {intent['detected_brand']} ({intent['detected_provider_code']})
Budget: max {intent['max_price_paise']/100 if intent['max_price_paise'] else 'None'} INR

Marketplace Search Results:
{json.dumps(recommendations, indent=2)}

Provide a concise, professional comparison summary.
State which provider each option is from, highlight key features, and remind the user
that selecting any option will submit it to PayPilot's centralized spending-policy engine for validation.
"""
                resp = model.generate_content(prompt)
                reply_text = resp.text
            except Exception:
                reply_text = AIAssistantService._generate_fallback_reply(message, intent, recommendations)
        else:
            reply_text = AIAssistantService._generate_fallback_reply(message, intent, recommendations)

        return {
            "reply": reply_text,
            "agent_type": agent_type,
            "detected_intent": intent,
            "recommendations": recommendations,
            "action_taken": "multi_provider_marketplace_search",
        }

    @staticmethod
    def _generate_fallback_reply(
        message: str, intent: Dict[str, Any], recommendations: List[Dict[str, Any]]
    ) -> str:
        constraints = []
        if intent.get("detected_category"):
            constraints.append(f"Category: {intent['detected_category']}")
        if intent.get("detected_brand"):
            constraints.append(f"Brand: {intent['detected_brand']}")
        if intent.get("max_price_paise"):
            constraints.append(f"Budget: Under ₹{intent['max_price_paise']/100:,.2f}")
        if intent.get("vegetarian_only"):
            constraints.append("Dietary: Vegetarian")

        constraint_str = f" ({', '.join(constraints)})" if constraints else ""

        if not recommendations:
            return (
                f"I searched configured marketplaces for your request{constraint_str}, "
                "but couldn't find matching items within the specified criteria. "
                "You can try expanding your budget or adjusting the search keywords."
            )

        items_str = ", ".join([f"**{r['name']}** from *{r['provider']}* (₹{r['price_inr']:,.2f})" for r in recommendations[:3]])
        return (
            f"🔍 Found {len(recommendations)} matching items across supported marketplaces{constraint_str}.\n\n"
            f"Top matches include: {items_str}.\n\n"
            "🛡️ **Security & Policy Notice:** Prices and availability are fetched from verified provider feeds. "
            "Select any item below to inspect details or create a policy-checked payment request. "
            "No funds will be authorized without your explicit approval."
        )
