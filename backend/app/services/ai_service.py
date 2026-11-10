"""AI Purchasing Assistant Service.

Uses Google Gemini API when GEMINI_API_KEY is present; otherwise provides
an intelligent deterministic fallback simulation for offline/local evaluation.
"""
import re
import json
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.merchant_service import search_products
from app.services.approval_service import create_payment_request
from app.config import get_settings

settings = get_settings()

SYSTEM_PROMPT = """
You are PayPilot AI, a secure purchasing assistant.
Your role is to understand user purchase requests, search available product catalogs,
compare options based on price, category, and user constraints, and recommend the best options.

SECURITY RULES:
1. You DO NOT have authority to make payments or transfer money.
2. You can only search products and recommend options.
3. Once the user picks a product, you can request a payment authorization.
4. You must never invent or assume prices — always use verified prices from the catalog.
5. All payment authorization is handled by the deterministic backend policy engine and the user.
"""


class AIAssistantService:
    @staticmethod
    async def process_user_message(
        db: AsyncSession,
        user_id: str,
        message: str,
        agent_type: str = "food",
    ) -> Dict[str, Any]:
        """Process natural language request, execute discovery, and return recommendations."""
        msg_lower = message.lower()

        # Parse constraints from natural language
        vegetarian_only = "veg" in msg_lower and "non-veg" not in msg_lower
        
        # Extract budget/price constraint (e.g., "under 200", "under ₹200", "below 1000")
        max_price_paise = None
        price_match = re.search(r"(?:under|below|max|within|less than)\s*(?:₹|rs\.?|inr)?\s*(\d+)", msg_lower)
        if price_match:
            max_price_paise = int(price_match.group(1)) * 100

        # Determine category based on agent_type or query
        category = "Food" if agent_type == "food" else "Electronics"
        if "electronic" in msg_lower or "earphone" in msg_lower or "mouse" in msg_lower or "charger" in msg_lower:
            category = "Electronics"
        elif "shop" in msg_lower or "bag" in msg_lower or "bottle" in msg_lower or "lamp" in msg_lower:
            category = "Shopping"

        # Search authoritative catalog
        products = await search_products(
            db=db,
            query=None,
            category=category,
            max_price_paise=max_price_paise,
            vegetarian_only=vegetarian_only,
        )

        recommendations = [
            {
                "id": p.id,
                "name": p.name,
                "description": p.description,
                "price_paise": p.price_paise,
                "price_inr": p.price_paise / 100,
                "category": p.category,
                "merchant_id": p.merchant_id,
                "is_available": p.is_available,
            }
            for p in products[:4]
        ]

        # If Gemini API key is configured, use it for friendly conversational response
        if settings.GEMINI_API_KEY:
            try:
                import google.generativeai as genai
                genai.configure(api_key=settings.GEMINI_API_KEY)
                model = genai.GenerativeModel("gemini-1.5-flash")
                prompt = f"""
{SYSTEM_PROMPT}

User query: "{message}"
Matching products found from verified catalog:
{json.dumps(recommendations, indent=2)}

Please provide a helpful, concise summary of the recommendations.
Remind the user that selecting an option will create a payment request subject to policy engine checks and their explicit approval.
"""
                resp = model.generate_content(prompt)
                reply_text = resp.text
            except Exception:
                reply_text = AIAssistantService._generate_fallback_reply(
                    message, recommendations, vegetarian_only, max_price_paise
                )
        else:
            reply_text = AIAssistantService._generate_fallback_reply(
                message, recommendations, vegetarian_only, max_price_paise
            )

        return {
            "reply": reply_text,
            "agent_type": agent_type,
            "recommendations": recommendations,
            "action_taken": "catalog_searched",
        }

    @staticmethod
    def _generate_fallback_reply(
        message: str, recommendations: List[Dict[str, Any]], vegetarian_only: bool, max_price_paise: Optional[int]
    ) -> str:
        constraints = []
        if vegetarian_only:
            constraints.append("dietary preference: Vegetarian")
        if max_price_paise:
            constraints.append(f"budget: under ₹{max_price_paise/100:.2f}")

        constraint_str = f" ({', '.join(constraints)})" if constraints else ""

        if not recommendations:
            return f"I understood your request{constraint_str}, but couldn't find any products in our verified catalog matching those exact criteria. Would you like to adjust your budget or preferences?"

        items_str = ", ".join([f"**{r['name']}** (₹{r['price_inr']:.2f})" for r in recommendations])
        return (
            f"I found {len(recommendations)} matching options{constraint_str}: {items_str}.\n\n"
            "🛡️ **Security note:** I have prepared recommendations based on verified merchant catalog prices. "
            "Please select a product below to create a payment request. The transaction will be checked by your spending-policy engine before any authorization."
        )
