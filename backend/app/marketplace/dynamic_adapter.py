"""Dynamic Category & Unexpected Searches Adapter for PayPilot AI.

Handles dynamically identified categories such as telescopes, sewing machines,
musical instruments, drones, aquarium supplies, and smart security.
Maintains transparent DEMO data source disclosure.
"""
from typing import List, Optional
from app.marketplace.base_provider import BaseMarketplaceProvider, NormalizedProduct

UNEXPECTED_NICHE_CATALOG = [
    {
        "id": "dyn-tele-001",
        "name": "Celestron PowerSeeker 70AZ Refractor Astronomical Telescope",
        "description": "70mm aperture refractor telescope with 700mm focal length, fully coated glass optics, 3x Barlow lens, and sturdy aluminum tripod with accessory tray.",
        "brand": "Celestron",
        "price_paise": 899900,  # ₹8,999.00 (under ₹10,000!)
        "original_price_paise": 1250000,
        "category": "Art, hobbies and collectibles",
        "subcategory": "Telescopes & Astronomy",
        "image_url": "https://images.unsplash.com/photo-1506703719100-a0f3a48c0f86?w=500&q=80",
        "product_url": "https://www.celestron.com/powerseeker-70az",
        "rating": 4.6,
        "rating_count": 340,
        "specifications": {
            "Optical Design": "Achromatic Refractor",
            "Aperture": "70 mm (2.76 in)",
            "Focal Length": "700 mm (f/10)",
            "Mount Type": "Manual Altazimuth Mount with Slow Motion Pan Handle",
            "Eyepieces": "20mm (35x) and 4mm (175x) + 3x Barlow"
        },
        "delivery_info": "Free Insured Courier Shipping in 3-4 days"
    },
    {
        "id": "dyn-sew-002",
        "name": "Usha Janome Dream Stitch Automatic Zig-Zag Electric Sewing Machine",
        "description": "Compact free arm sewing machine with 7 built-in stitches including 4-step buttonholing, auto-tripping bobbin system, and dial pattern selector.",
        "brand": "Usha Janome",
        "price_paise": 949900,  # ₹9,499.00
        "original_price_paise": 1350000,
        "category": "Industrial and professional products",
        "subcategory": "Sewing machines",
        "image_url": "https://images.unsplash.com/photo-1544816155-12df9643f363?w=500&q=80",
        "product_url": "https://www.ushasew.com/dream-stitch",
        "rating": 4.7,
        "rating_count": 890,
        "specifications": {
            "Stitch Functions": "7 Built-in Stitches (14 Applications)",
            "Shuttle Type": "Drop-in Oscillating Shuttle",
            "Thread Tension": "Manual Calibration",
            "Motor Speed": "550 Stitches per minute"
        },
        "delivery_info": "Free In-Home Demo & Shipping"
    },
    {
        "id": "dyn-mus-003",
        "name": "Casio CT-S100 Casiotone 61-Key Portable Musical Keyboard",
        "description": "Slim, lightweight portable keyboard with 61 piano-style keys, 122 built-in tones, 61 accompaniment rhythms, and USB-to-host micro-B connectivity.",
        "brand": "Casio",
        "price_paise": 749500,  # ₹7,495.00
        "original_price_paise": 899500,
        "category": "Art, hobbies and collectibles",
        "subcategory": "Musical keyboards",
        "image_url": "https://images.unsplash.com/photo-1520523839898-507127053917?w=500&q=80",
        "product_url": "https://www.casioindiashop.com/ct-s100",
        "rating": 4.6,
        "rating_count": 620,
        "specifications": {
            "Keyboard": "61 Full-Size Piano-Style Keys",
            "Polyphony": "32 Max Notes",
            "Speakers": "2.5W + 2.5W Stereo Oval Speakers",
            "Weight": "3.3 kg"
        },
        "delivery_info": "Includes Power Adapter & Music Sheet Stand"
    },
    {
        "id": "dyn-cam-004",
        "name": "TP-Link Tapo C210 2K 3MP Pan/Tilt Smart Home Security Camera",
        "description": "Ultra-clear 2K 3MP resolution with 360° horizontal and 114° vertical range, infrared night vision up to 30ft, motion tracking, two-way audio.",
        "brand": "TP-Link",
        "price_paise": 229900,  # ₹2,299.00
        "original_price_paise": 399900,
        "category": "Electronics and technology",
        "subcategory": "Home security cameras",
        "image_url": "https://images.unsplash.com/photo-1557597774-9d273605dfa9?w=500&q=80",
        "product_url": "https://www.tp-link.com/in/home-networking/cloud-camera/tapo-c210/",
        "rating": 4.5,
        "rating_count": 4210,
        "specifications": {
            "Resolution": "2K 3MP (2304 x 1296)",
            "Field of View": "360° Horizontal Pan / 114° Vertical Tilt",
            "Storage": "MicroSD slot up to 256GB + Cloud option",
            "Audio": "Built-in Microphone and Speaker"
        },
        "delivery_info": "Fast 1-Day Dispatch"
    }
]


class DynamicCategoryMarketplaceAdapter(BaseMarketplaceProvider):
    def __init__(self):
        super().__init__(
            code="dynamic_specialty",
            name="Specialty & Niche Marketplaces",
            primary_category="Specialty",
            supported_categories=["*"],
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

        for item in UNEXPECTED_NICHE_CATALOG:
            if min_price_paise is not None and item["price_paise"] < min_price_paise:
                continue
            if max_price_paise is not None and item["price_paise"] > max_price_paise:
                continue
            if brand and brand.lower() not in item["brand"].lower():
                continue

            if q_lower:
                match_text = f"{item['name']} {item['description']} {item['subcategory']} {item['brand']}".lower()
                terms = q_lower.split()
                if not any(term in match_text or term in ["telescope", "sewing", "keyboard", "musical", "camera", "security", "astronomy"] for term in terms):
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
                    merchant="Authorized Specialty Distributor",
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
                    last_updated="2026-11-11 Dynamic Discovery",
                )
            )
            if len(results) >= limit:
                break

        return results

    async def get_product_details(self, product_id: str) -> Optional[NormalizedProduct]:
        for item in UNEXPECTED_NICHE_CATALOG:
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
                    merchant="Authorized Specialty Distributor",
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
        return any(item["id"] == product_id for item in UNEXPECTED_NICHE_CATALOG)
