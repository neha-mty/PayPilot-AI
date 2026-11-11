"""Travel & Accommodation Marketplace Adapter (MakeMyTrip / Flight & Hotel) for PayPilot AI."""
from typing import List, Optional
from app.marketplace.base_provider import BaseMarketplaceProvider, NormalizedProduct

TRAVEL_CATALOG = [
    {
        "id": "trv-mmt-001",
        "name": "IndiGo Flight 6E-204: Kolkata (CCU) to Delhi (DEL)",
        "description": "Non-stop economy flight. Departure: Netaji Subhash Chandra Bose Intl (CCU) 06:15 AM -> Arrival: Indira Gandhi Intl (DEL) 08:35 AM. 2h 20m duration. 15kg check-in baggage included.",
        "brand": "IndiGo Airlines",
        "price_paise": 449900,  # ₹4,499.00 (cheapest flight CCU to DEL!)
        "original_price_paise": 620000,
        "category": "Travel and accommodation",
        "subcategory": "Flights",
        "image_url": "https://images.unsplash.com/photo-1436491865332-7a61a109cc05?w=500&q=80",
        "product_url": "https://www.makemytrip.com/flights/ccu-del.html",
        "rating": 4.5,
        "rating_count": 3410,
        "specifications": {
            "Route": "Kolkata (CCU) -> New Delhi (DEL)",
            "Flight No": "6E-204 Non-Stop",
            "Duration": "2 hours 20 minutes",
            "Cabin Class": "Economy Regular Fare",
            "Baggage": "7kg Cabin + 15kg Check-in"
        },
        "delivery_info": "Instant E-Ticket Delivery via SMS & Email"
    },
    {
        "id": "trv-mmt-002",
        "name": "The Himalayan View Heritage Homestay & Resort, Darjeeling",
        "description": "Boutique heritage stay overlooking Kanchenjunga snow peaks. Free high-speed WiFi, complimentary organic Darjeeling tea, room heater, and heated shower.",
        "brand": "Himalayan View Stays",
        "price_paise": 269900,  # ₹2,699.00 per night (under ₹3,000!)
        "original_price_paise": 420000,
        "category": "Travel and accommodation",
        "subcategory": "Hotels",
        "image_url": "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=500&q=80",
        "product_url": "https://www.makemytrip.com/hotels/darjeeling-himalayan-view.html",
        "rating": 4.7,
        "rating_count": 482,
        "specifications": {
            "Location": "Mall Road (Near Observatory Hill), Darjeeling",
            "Room Type": "Deluxe Mountain Facing King Room",
            "Inclusions": "Complimentary Breakfast & Mountain View",
            "Check-in / Check-out": "12:00 PM / 11:00 AM"
        },
        "delivery_info": "Instant Voucher Confirmation with Free Cancellation up to 48 hrs"
    }
]


class TravelMarketplaceAdapter(BaseMarketplaceProvider):
    def __init__(self):
        super().__init__(
            code="makemytrip",
            name="MakeMyTrip Travel",
            primary_category="Travel and accommodation",
            supported_categories=["Travel and accommodation", "Transportation and local services"],
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

        for item in TRAVEL_CATALOG:
            if min_price_paise is not None and item["price_paise"] < min_price_paise:
                continue
            if max_price_paise is not None and item["price_paise"] > max_price_paise:
                continue
            if brand and brand.lower() not in item["brand"].lower():
                continue

            if q_lower:
                match_text = f"{item['name']} {item['description']} {item['subcategory']} {item['brand']}".lower()
                terms = q_lower.split()
                if not any(term in match_text or term in ["flight", "hotel", "travel", "kolkata", "delhi", "darjeeling"] for term in terms):
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
                    merchant="MakeMyTrip Booking Services",
                    provider="MakeMyTrip Travel",
                    provider_code="makemytrip",
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
        for item in TRAVEL_CATALOG:
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
                    merchant="MakeMyTrip Booking Services",
                    provider="MakeMyTrip Travel",
                    provider_code="makemytrip",
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
        return any(item["id"] == product_id for item in TRAVEL_CATALOG)
