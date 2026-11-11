"""Jewellery Marketplace Adapter (Tanishq / CaratLane / Titan) for PayPilot AI."""
from typing import List, Optional
from app.marketplace.base_provider import BaseMarketplaceProvider, NormalizedProduct

JEWELLERY_CATALOG = [
    {
        "id": "jwl-tq-001",
        "name": "Tanishq 18KT Yellow Gold Floral Stud Earrings",
        "description": "Exquisite 18 Karat Hallmarked Yellow Gold floral stud earrings with glossy and matte dual-finish petals. BIS Hallmarked.",
        "brand": "Tanishq",
        "price_paise": 849900,  # ₹8,499.00 (under ₹10,000!)
        "original_price_paise": 1050000,
        "category": "Jewellery and accessories",
        "subcategory": "Earrings",
        "image_url": "https://images.unsplash.com/photo-1630019852942-f89202989a59?w=500&q=80",
        "product_url": "https://www.tanishq.co.in/gold-floral-stud-earrings.html",
        "rating": 4.9,
        "rating_count": 310,
        "specifications": {
            "Metal Purity": "18KT (750 Purity) Yellow Gold",
            "Certification": "BIS Hallmarked",
            "Gross Weight": "1.42 grams",
            "Closure Type": "Screw Back"
        },
        "delivery_info": "Insured Transit with OTP Verification"
    },
    {
        "id": "jwl-tq-002",
        "name": "Titan Neo Analog Blue Dial Men's Quartz Watch",
        "description": "Titan Classic Neo collection watch with stainless steel strap, midnight blue sunray dial, and 50m water resistance.",
        "brand": "Titan",
        "price_paise": 399500,  # ₹3,995.00
        "original_price_paise": 550000,
        "category": "Jewellery and accessories",
        "subcategory": "Watches",
        "image_url": "https://images.unsplash.com/photo-1524805444758-089113d48a6d?w=500&q=80",
        "product_url": "https://www.titan.co.in/titan-neo-analog-watch.html",
        "rating": 4.7,
        "rating_count": 890,
        "specifications": {
            "Movement": "High-Precision Japanese Quartz",
            "Dial Color": "Midnight Sunray Blue",
            "Strap Material": "316L Surgical Grade Stainless Steel",
            "Water Resistance": "5 ATM (50 Meters)"
        },
        "delivery_info": "Free Shipping in 2 days"
    },
    {
        "id": "jwl-tq-003",
        "name": "CaratLane 925 Sterling Silver Solitaire Ring",
        "description": "Rhodium-plated 925 Sterling Silver band featuring brilliant cut Swarovski zirconia. Anti-tarnish coating.",
        "brand": "CaratLane",
        "price_paise": 249900,  # ₹2,499.00
        "original_price_paise": 399900,
        "category": "Jewellery and accessories",
        "subcategory": "Rings",
        "image_url": "https://images.unsplash.com/photo-1605100804763-247f67b3557e?w=500&q=80",
        "product_url": "https://www.caratlane.com/silver-solitaire-ring.html",
        "rating": 4.6,
        "rating_count": 425,
        "specifications": {
            "Metal": "925 Sterling Silver with Rhodium Plating",
            "Gemstone": "Brilliant Cut Zirconia",
            "Ring Size": "Adjustable Free Size"
        },
        "delivery_info": "Tamper-evident gift packaging"
    }
]


class JewelleryMarketplaceAdapter(BaseMarketplaceProvider):
    def __init__(self):
        super().__init__(
            code="tanishq",
            name="Tanishq Jewellery",
            primary_category="Jewellery and accessories",
            supported_categories=["Jewellery and accessories", "Fashion and clothing"],
        )

    async def search(
        self,
        query: Optional[str] = None,
        category: Optional[str] = None,
        subcategory: Optional[str] = None,
        brand: Optional[str] = None,
        min_price_paise: Optional[int] = None,
        max_price_paise: Optional[int] = None,
        limit: int = 10,
    ) -> List[NormalizedProduct]:
        results = []
        q_lower = query.lower() if query else ""

        for item in JEWELLERY_CATALOG:
            if min_price_paise is not None and item["price_paise"] < min_price_paise:
                continue
            if max_price_paise is not None and item["price_paise"] > max_price_paise:
                continue
            if brand and brand.lower() not in item["brand"].lower():
                continue

            if q_lower:
                match_text = f"{item['name']} {item['description']} {item['subcategory']} {item['brand']}".lower()
                terms = q_lower.split()
                if not any(term in match_text or term in ["gold", "earring", "earrings", "jewellery", "jewelry", "watch", "ring", "silver", "tanishq", "titan"] for term in terms):
                    continue

            orig_inr = item["original_price_paise"] / 100
            price_inr = item["price_paise"] / 100
            discount = int(((orig_inr - price_inr) / orig_inr) * 100)

            results.append(
                NormalizedProduct(
                    id=item["id"],
                    name=item["name"],
                    description=item["description"],
                    price_paise=item["price_paise"],
                    price_inr=price_inr,
                    original_price_inr=orig_inr,
                    discount_percent=discount,
                    currency="INR",
                    category=item["category"],
                    subcategory=item["subcategory"],
                    brand=item["brand"],
                    merchant="Tanishq Official",
                    provider="Tanishq Marketplace",
                    provider_code="tanishq",
                    image_url=item["image_url"],
                    product_url=item["product_url"],
                    is_available=True,
                    data_source_type="DEMO",
                    rating=item["rating"],
                    rating_count=item["rating_count"],
                    supports_integrated_checkout=True,
                    specifications=item["specifications"],
                    delivery_info=item["delivery_info"],
                    last_updated="2026-11-11 Verified Feed",
                )
            )
            if len(results) >= limit:
                break

        return results

    async def get_product_details(self, product_id: str) -> Optional[NormalizedProduct]:
        for item in JEWELLERY_CATALOG:
            if item["id"] == product_id:
                orig_inr = item["original_price_paise"] / 100
                price_inr = item["price_paise"] / 100
                return NormalizedProduct(
                    id=item["id"],
                    name=item["name"],
                    description=item["description"],
                    price_paise=item["price_paise"],
                    price_inr=price_inr,
                    original_price_inr=orig_inr,
                    category=item["category"],
                    subcategory=item["subcategory"],
                    brand=item["brand"],
                    merchant="Tanishq Official",
                    provider="Tanishq Marketplace",
                    provider_code="tanishq",
                    image_url=item["image_url"],
                    product_url=item["product_url"],
                    is_available=True,
                    data_source_type="DEMO",
                    rating=item["rating"],
                    rating_count=item["rating_count"],
                    supports_integrated_checkout=True,
                    specifications=item["specifications"],
                    delivery_info=item["delivery_info"],
                )
        return None

    async def check_availability(self, product_id: str) -> bool:
        return any(item["id"] == product_id for item in JEWELLERY_CATALOG)
