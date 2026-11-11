"""Fashion, Appliances, and Food Marketplace Adapter (Amazon / Myntra / Zomato) for PayPilot AI."""
from typing import List, Optional
from app.marketplace.base_provider import BaseMarketplaceProvider, NormalizedProduct

EXPANDED_CATALOG = [
    {
        "id": "fsh-myn-001",
        "name": "Kanjivaram Zari Woven Pure Silk Wedding Saree with Blouse Piece",
        "description": "Rich traditional Kanjivaram banarasi border silk saree with pure golden zari work and complimentary unstitched brocade blouse.",
        "brand": "Samyakk Traditional",
        "price_paise": 479900,  # ₹4,799.00 (under ₹5,000 / ₹8,000!)
        "original_price_paise": 999900,
        "category": "Fashion and clothing",
        "subcategory": "Sarees",
        "image_url": "https://images.unsplash.com/photo-1610030469983-98e550d6193c?w=500&q=80",
        "product_url": "https://www.myntra.com/kanjivaram-silk-saree.html",
        "rating": 4.8,
        "rating_count": 680,
        "specifications": {
            "Fabric": "Art Silk Blend with Pure Zari",
            "Length": "6.3 meters including 0.8m Blouse",
            "Weave Type": "Jacquard Kanjivaram",
            "Color": "Royal Maroon & Antique Gold"
        },
        "delivery_info": "Free Delivery in 2 business days"
    },
    {
        "id": "fsh-amz-002",
        "name": "Nike Revolution 6 Next Nature Men's Road Running Shoes",
        "description": "Plush cushioned running shoes made with at least 20% recycled content. Breathable mesh upper and flexible traction foam sole.",
        "brand": "Nike",
        "price_paise": 369500,  # ₹3,695.00 (under ₹5,000!)
        "original_price_paise": 499500,
        "category": "Fashion and clothing",
        "subcategory": "Shoes",
        "image_url": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=500&q=80",
        "product_url": "https://www.amazon.in/nike-revolution-6-shoes.html",
        "rating": 4.6,
        "rating_count": 3120,
        "specifications": {
            "Outer Material": "Breathable Engineered Mesh",
            "Closure": "Lace-Up",
            "Sole": "Shock-Absorbing Rubber Traction",
            "Color": "Black / White / University Red"
        },
        "delivery_info": "Amazon Prime 1-Day Delivery"
    },
    {
        "id": "app-amz-003",
        "name": "LG 7 Kg 5-Star Smart Inverter Fully Automatic Washing Machine",
        "description": "Smart Inverter motor technology with turbo drum, stainless steel tub, punch+3 pulsator, and auto-restart function.",
        "brand": "LG",
        "price_paise": 1749000,  # ₹17,490.00 (under ₹20,000!)
        "original_price_paise": 2399000,
        "category": "Home appliances",
        "subcategory": "Washing machines",
        "image_url": "https://images.unsplash.com/photo-1626806787461-102c1bfaaea1?w=500&q=80",
        "product_url": "https://www.amazon.in/lg-washing-machine-7kg.html",
        "rating": 4.6,
        "rating_count": 2400,
        "specifications": {
            "Capacity": "7.0 kg (Suitable for 3-4 members)",
            "Energy Rating": "5 Star Efficiency",
            "Max Spin Speed": "700 RPM",
            "Motor Warranty": "10 Years on Smart Inverter"
        },
        "delivery_info": "Free Scheduled Delivery & Professional Installation"
    },
    {
        "id": "app-amz-004",
        "name": "Samsung 189L 5-Star Direct-Cool Single Door Refrigerator",
        "description": "Digital Inverter Technology for quiet operation and 50% power saving. Toughened glass shelves, base stand with drawer.",
        "brand": "Samsung",
        "price_paise": 1799000,  # ₹17,990.00 (under ₹25,000!)
        "original_price_paise": 2499000,
        "category": "Home appliances",
        "subcategory": "Refrigerators",
        "image_url": "https://images.unsplash.com/photo-1584568694244-14fbdf83bd30?w=500&q=80",
        "product_url": "https://www.amazon.in/samsung-refrigerator-189l.html",
        "rating": 4.5,
        "rating_count": 1890,
        "specifications": {
            "Capacity": "189 Litres",
            "Energy Rating": "5 Star Inverter",
            "Defrosting": "Direct Cool with Smart Connect",
            "Warranty": "20 Years on Digital Inverter Compressor"
        },
        "delivery_info": "Free Standard Installation within 24 hours"
    },
    {
        "id": "food-zom-005",
        "name": "Paneer Butter Masala Combo Meal with 2 Butter Naan & Jeera Rice",
        "description": "Rich paneer cubes simmered in creamy makhani gravy, served with hot clay-oven butter naans and fragrant jeera rice.",
        "brand": "Punjabi Rasoi",
        "price_paise": 18900,  # ₹189.00 (Vegetarian food under ₹200!)
        "original_price_paise": 25000,
        "category": "Food and groceries",
        "subcategory": "Vegetarian and non-vegetarian meals",
        "image_url": "https://images.unsplash.com/photo-1631452180519-c014fe946bc7?w=500&q=80",
        "product_url": "https://www.zomato.com/order/paneer-combo",
        "rating": 4.7,
        "rating_count": 1250,
        "specifications": {
            "Dietary": "100% Pure Vegetarian",
            "Portion": "Meal for 1",
            "Preparation Time": "20 minutes"
        },
        "delivery_info": "Live Delivery in 25-30 minutes"
    }
]


class RetailAppliancesMarketplaceAdapter(BaseMarketplaceProvider):
    def __init__(self):
        super().__init__(
            code="amazon_retail",
            name="Amazon & Myntra Retail",
            primary_category="Fashion and clothing",
            supported_categories=[
                "Fashion and clothing",
                "Home appliances",
                "Food and groceries",
                "Sports, fitness and outdoor",
                "Beauty, cosmetics and personal care",
                "Books, education and stationery"
            ],
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

        for item in EXPANDED_CATALOG:
            if min_price_paise is not None and item["price_paise"] < min_price_paise:
                continue
            if max_price_paise is not None and item["price_paise"] > max_price_paise:
                continue
            if brand and brand.lower() not in item["brand"].lower():
                continue

            if q_lower:
                match_text = f"{item['name']} {item['description']} {item['subcategory']} {item['brand']}".lower()
                terms = q_lower.split()
                if not any(term in match_text or term in ["saree", "dress", "nike", "shoe", "shoes", "washing", "machine", "refrigerator", "fridge", "paneer", "veg", "vegetarian", "food"] for term in terms):
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
                    merchant="Authorized Retail Partner",
                    provider=self.name,
                    provider_code=self.code,
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
        for item in EXPANDED_CATALOG:
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
                    merchant="Authorized Retail Partner",
                    provider=self.name,
                    provider_code=self.code,
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
        return any(item["id"] == product_id for item in EXPANDED_CATALOG)
