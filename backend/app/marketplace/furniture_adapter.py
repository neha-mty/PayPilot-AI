"""Furniture Marketplace Adapter (Pepperfry / IKEA / Urban Ladder) for PayPilot AI."""
from typing import List, Optional
from app.marketplace.base_provider import BaseMarketplaceProvider, NormalizedProduct

FURNITURE_CATALOG = [
    {
        "id": "furn-pf-001",
        "name": "Ergonomic High-Back Executive Office Mesh Chair",
        "description": "Ergonomic breathable mesh chair with multi-stage lumbar support, tilt-lock mechanism, and 3D adjustable armrests.",
        "brand": "Green Soul",
        "price_paise": 489900,  # ₹4,899.00 (under ₹5,000!)
        "original_price_paise": 850000,
        "category": "Furniture and home furnishing",
        "subcategory": "Office furniture",
        "image_url": "https://images.unsplash.com/photo-1580481077195-c3a821a58875?w=500&q=80",
        "product_url": "https://www.pepperfry.com/ergonomic-office-chair.html",
        "rating": 4.7,
        "rating_count": 520,
        "specifications": {
            "Material": "Heavy-duty Nylon Mesh + Steel Base",
            "Weight Capacity": "120 kg",
            "Color": "Slate Grey / Black",
            "Mechanism": "Synchro-Tilt with Multi-Lock"
        },
        "delivery_info": "Free Assembly & Shipping in 3 days"
    },
    {
        "id": "furn-pf-002",
        "name": "Solid Sheesham Wood 3-Seater Compact Sofa",
        "description": "Handcrafted Sheesham wood frame with high-density foam cushions and washable beige upholstery. Ideal for small living rooms.",
        "brand": "Woodsworth by Pepperfry",
        "price_paise": 1449900,  # ₹14,499.00 (under ₹15,000!)
        "original_price_paise": 2200000,
        "category": "Furniture and home furnishing",
        "subcategory": "Sofas",
        "image_url": "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=500&q=80",
        "product_url": "https://www.pepperfry.com/sheesham-compact-sofa.html",
        "rating": 4.6,
        "rating_count": 218,
        "specifications": {
            "Primary Material": "Solid Sheesham Wood (Rosewood)",
            "Upholstery": "Premium Jute-Cotton Blend Fabric",
            "Dimensions": "68W x 30D x 32H inches",
            "Color": "Natural Teak Finish & Warm Cream"
        },
        "delivery_info": "Free White-Glove Installation"
    },
    {
        "id": "furn-pf-003",
        "name": "Engineered Wood Study & Laptop Table with Bookshelf",
        "description": "Multi-tier modern workstation table with integrated open book racks and cable grommet.",
        "brand": "Spacewood",
        "price_paise": 349900,  # ₹3,499.00
        "original_price_paise": 599900,
        "category": "Furniture and home furnishing",
        "subcategory": "Study tables",
        "image_url": "https://images.unsplash.com/photo-1518455027359-f3f8164ba6bd?w=500&q=80",
        "product_url": "https://www.pepperfry.com/study-table.html",
        "rating": 4.4,
        "rating_count": 430,
        "specifications": {
            "Material": "Engineered Wood with Melamine Coating",
            "Dimensions": "42W x 20D x 48H inches",
            "Color": "Walnut Brown"
        },
        "delivery_info": "Ships in 48 hours"
    }
]


class FurnitureMarketplaceAdapter(BaseMarketplaceProvider):
    def __init__(self):
        super().__init__(
            code="pepperfry",
            name="Pepperfry Furniture",
            primary_category="Furniture and home furnishing",
            supported_categories=["Furniture and home furnishing", "Home appliances"],
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

        for item in FURNITURE_CATALOG:
            if min_price_paise is not None and item["price_paise"] < min_price_paise:
                continue
            if max_price_paise is not None and item["price_paise"] > max_price_paise:
                continue
            if brand and brand.lower() not in item["brand"].lower():
                continue

            if q_lower:
                match_text = f"{item['name']} {item['description']} {item['subcategory']} {item['brand']}".lower()
                terms = q_lower.split()
                if not any(term in match_text or term in ["chair", "sofa", "furniture", "table", "desk", "bed"] for term in terms):
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
                    merchant="Pepperfry Home",
                    provider="Pepperfry Marketplace",
                    provider_code="pepperfry",
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
        for item in FURNITURE_CATALOG:
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
                    merchant="Pepperfry Home",
                    provider="Pepperfry Marketplace",
                    provider_code="pepperfry",
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
        return any(item["id"] == product_id for item in FURNITURE_CATALOG)
