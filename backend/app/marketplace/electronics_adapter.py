"""Electronics Marketplace Adapter (Croma / Reliance Digital) for PayPilot AI."""
from typing import List, Optional
from app.marketplace.base_provider import BaseMarketplaceProvider, NormalizedProduct

ELECTRONICS_CATALOG = [
    {
        "id": "elec-cr-001",
        "name": "Dell Inspiron 15 Core i5 16GB RAM 512GB SSD Laptop",
        "description": "Intel Core i5 12th Gen, 16GB DDR4 RAM, 512GB PCIe NVMe SSD, 15.6-inch FHD Anti-Glare Display, Backlit Keyboard, Windows 11 + MS Office.",
        "brand": "Dell",
        "price_paise": 4899000,  # ₹48,990.00 (under ₹50,000 / ₹60,000!)
        "original_price_paise": 6200000,
        "category": "Electronics and technology",
        "subcategory": "Laptops",
        "image_url": "https://images.unsplash.com/photo-1593642632823-8f785ba67e45?w=500&q=80",
        "product_url": "https://www.croma.com/dell-inspiron-15-laptop.html",
        "rating": 4.6,
        "rating_count": 940,
        "specifications": {
            "Processor": "Intel Core i5-1235U (10 Cores, up to 4.4 GHz)",
            "RAM": "16 GB DDR4 (Upgradable to 32 GB)",
            "Storage": "512 GB M.2 NVMe SSD",
            "Display": "15.6-inch FHD (1920x1080) 120Hz Anti-Glare",
            "Weight": "1.65 kg"
        },
        "delivery_info": "Free 2-Hour Express Delivery in Select Cities"
    },
    {
        "id": "elec-cr-002",
        "name": "Samsung Galaxy M34 5G 8GB RAM 128GB Prism Silver",
        "description": "120Hz Super AMOLED Display, 50MP No Shake OIS Camera, 6000mAh Monster Battery, Knox Security.",
        "brand": "Samsung",
        "price_paise": 1649900,  # ₹16,499.00
        "original_price_paise": 2499900,
        "category": "Electronics and technology",
        "subcategory": "Smartphones",
        "image_url": "https://images.unsplash.com/photo-1610945415295-d9bbf067e59c?w=500&q=80",
        "product_url": "https://www.croma.com/samsung-galaxy-m34-5g.html",
        "rating": 4.5,
        "rating_count": 1420,
        "specifications": {
            "Screen": "6.5-inch FHD+ 120Hz Super AMOLED",
            "Battery": "6000 mAh with 25W Fast Charging",
            "Rear Camera": "50MP (OIS) + 8MP Ultra-Wide + 2MP",
            "OS": "Android 14 with One UI 6"
        },
        "delivery_info": "Next-Day Delivery with Verified Handover"
    },
    {
        "id": "elec-cr-003",
        "name": "OnePlus Bullets Wireless Z2 Bluetooth Earphones",
        "description": "Bombastic 12.4mm Bass Drivers, 30 Hours Battery Life, 10-Minute Warp Charge for 20 Hours playback, IP55 Water Resistance.",
        "brand": "OnePlus",
        "price_paise": 179900,  # ₹1,799.00 (under ₹2,000!)
        "original_price_paise": 229900,
        "category": "Electronics and technology",
        "subcategory": "Earphones",
        "image_url": "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=500&q=80",
        "product_url": "https://www.croma.com/oneplus-bullets-wireless-z2.html",
        "rating": 4.4,
        "rating_count": 2850,
        "specifications": {
            "Driver": "12.4mm Deep Bass Dynamic Drivers",
            "Battery": "30 Hours total playtime",
            "Charging": "USB Type-C Warp Charge",
            "Waterproof": "IP55 Sweat & Splash Proof"
        },
        "delivery_info": "Free 1-Day Delivery"
    }
]


class ElectronicsMarketplaceAdapter(BaseMarketplaceProvider):
    def __init__(self):
        super().__init__(
            code="croma",
            name="Croma Electronics",
            primary_category="Electronics and technology",
            supported_categories=["Electronics and technology"],
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

        for item in ELECTRONICS_CATALOG:
            if min_price_paise is not None and item["price_paise"] < min_price_paise:
                continue
            if max_price_paise is not None and item["price_paise"] > max_price_paise:
                continue
            if brand and brand.lower() not in item["brand"].lower():
                continue

            if q_lower:
                match_text = f"{item['name']} {item['description']} {item['subcategory']} {item['brand']}".lower()
                terms = q_lower.split()
                if not any(term in match_text or term in ["laptop", "phone", "smartphone", "earphone", "dell", "samsung", "electronics"] for term in terms):
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
                    merchant="Croma Retail",
                    provider="Croma Marketplace",
                    provider_code="croma",
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
        for item in ELECTRONICS_CATALOG:
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
                    merchant="Croma Retail",
                    provider="Croma Marketplace",
                    provider_code="croma",
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
        return any(item["id"] == product_id for item in ELECTRONICS_CATALOG)
