"""Database seed script for demo merchants and products.

Run with: python -m app.seed
All merchants and products are clearly labelled as demo/sample data.
"""
import asyncio
from app.database import engine, Base, AsyncSessionLocal
from app.models import Merchant, Product

# Fixed UUIDs for demo data (makes testing easier)
MERCHANT_IDS = {
    "green_bowl": "m-0001-green-bowl-demo-0000",
    "daily_bites": "m-0002-daily-bites-demo-00",
    "techzone": "m-0003-techzone-demo-00000",
    "urban_store": "m-0004-urban-store-demo-00",
}

DEMO_MERCHANTS = [
    {
        "id": MERCHANT_IDS["green_bowl"],
        "name": "Green Bowl",
        "category": "Food",
        "description": "[DEMO] Healthy vegetarian restaurant offering fresh, home-style meals.",
        "is_verified": True,
        "is_active": True,
    },
    {
        "id": MERCHANT_IDS["daily_bites"],
        "name": "Daily Bites",
        "category": "Food",
        "description": "[DEMO] Quick meals and snacks for every taste.",
        "is_verified": True,
        "is_active": True,
    },
    {
        "id": MERCHANT_IDS["techzone"],
        "name": "TechZone",
        "category": "Electronics",
        "description": "[DEMO] Electronics accessories and gadgets at great prices.",
        "is_verified": True,
        "is_active": True,
    },
    {
        "id": MERCHANT_IDS["urban_store"],
        "name": "Urban Store",
        "category": "Shopping",
        "description": "[DEMO] Daily-use products and lifestyle items. [UNVERIFIED MERCHANT]",
        "is_verified": False,  # Intentionally unverified for testing
        "is_active": True,
    },
]

DEMO_PRODUCTS = [
    # Green Bowl products
    {"merchant_id": MERCHANT_IDS["green_bowl"], "name": "Paneer Tikka Thali", "description": "Fresh paneer tikka with roti, rice, dal, and salad. Pure vegetarian.", "price_paise": 18000, "category": "Food", "tags": "vegetarian,thali,paneer,lunch,dinner", "is_available": True},
    {"merchant_id": MERCHANT_IDS["green_bowl"], "name": "Veg Biryani Bowl", "description": "Fragrant vegetable biryani with raita and papad. Vegetarian.", "price_paise": 15000, "category": "Food", "tags": "vegetarian,biryani,rice,lunch", "is_available": True},
    {"merchant_id": MERCHANT_IDS["green_bowl"], "name": "Garden Fresh Salad", "description": "Mixed greens with cherry tomatoes, cucumber, and house dressing. Vegan.", "price_paise": 12000, "category": "Food", "tags": "vegan,salad,healthy,light", "is_available": True},
    {"merchant_id": MERCHANT_IDS["green_bowl"], "name": "Masala Dosa Combo", "description": "Crispy masala dosa with sambar and coconut chutney. Vegetarian.", "price_paise": 9000, "category": "Food", "tags": "vegetarian,dosa,south-indian,breakfast", "is_available": True},
    {"merchant_id": MERCHANT_IDS["green_bowl"], "name": "Dal Makhani with Naan", "description": "Creamy black lentil dal served with butter naan. Vegetarian.", "price_paise": 16000, "category": "Food", "tags": "vegetarian,dal,north-indian,dinner", "is_available": True},
    # Daily Bites products
    {"merchant_id": MERCHANT_IDS["daily_bites"], "name": "Chicken Biryani", "description": "Hyderabadi style chicken biryani with raita. Non-vegetarian.", "price_paise": 22000, "category": "Food", "tags": "non-vegetarian,biryani,chicken,lunch", "is_available": True},
    {"merchant_id": MERCHANT_IDS["daily_bites"], "name": "Veg Sandwich Meal", "description": "Grilled vegetable sandwich with fries and a drink. Vegetarian.", "price_paise": 8000, "category": "Food", "tags": "vegetarian,sandwich,snack,light", "is_available": True},
    {"merchant_id": MERCHANT_IDS["daily_bites"], "name": "Butter Chicken Thali", "description": "Rich butter chicken with naan, rice, and dessert. Non-vegetarian.", "price_paise": 25000, "category": "Food", "tags": "non-vegetarian,chicken,thali,dinner", "is_available": True},
    {"merchant_id": MERCHANT_IDS["daily_bites"], "name": "Mixed Fruit Smoothie", "description": "Fresh seasonal fruit smoothie. Vegan.", "price_paise": 11000, "category": "Food", "tags": "vegan,smoothie,drink,healthy", "is_available": True},
    {"merchant_id": MERCHANT_IDS["daily_bites"], "name": "Aloo Paratha Set", "description": "Two aloo parathas with curd and pickle. Vegetarian.", "price_paise": 7000, "category": "Food", "tags": "vegetarian,paratha,breakfast,north-indian", "is_available": True},
    # TechZone products
    {"merchant_id": MERCHANT_IDS["techzone"], "name": "Wireless Earbuds Pro", "description": "Bluetooth 5.3 wireless earbuds with 30-hour battery life and active noise cancellation. Great for music and calls.", "price_paise": 89900, "category": "Electronics", "tags": "wireless,earphones,earbuds,bluetooth,battery,audio", "is_available": True},
    {"merchant_id": MERCHANT_IDS["techzone"], "name": "USB-C Fast Charger", "description": "65W GaN fast charger, compatible with laptops and phones. Compact design.", "price_paise": 49900, "category": "Electronics", "tags": "charger,usb-c,fast-charging,laptop,phone", "is_available": True},
    {"merchant_id": MERCHANT_IDS["techzone"], "name": "Laptop Stand", "description": "Adjustable aluminum laptop stand with ergonomic design. Fits 10-17 inch laptops.", "price_paise": 65000, "category": "Electronics", "tags": "laptop,stand,ergonomic,aluminum", "is_available": True},
    {"merchant_id": MERCHANT_IDS["techzone"], "name": "Wireless Mouse", "description": "Silent click wireless mouse with USB receiver. 18-month battery life.", "price_paise": 35000, "category": "Electronics", "tags": "mouse,wireless,silent,usb", "is_available": True},
    {"merchant_id": MERCHANT_IDS["techzone"], "name": "Phone Screen Protector", "description": "9H tempered glass screen protector with anti-fingerprint coating. Easy installation.", "price_paise": 14900, "category": "Electronics", "tags": "screen-protector,phone,tempered-glass", "is_available": True},
    # Urban Store products
    {"merchant_id": MERCHANT_IDS["urban_store"], "name": "Bamboo Water Bottle", "description": "Eco-friendly bamboo water bottle, 500ml capacity. BPA-free and sustainable.", "price_paise": 29900, "category": "Shopping", "tags": "bottle,eco-friendly,bamboo,sustainable", "is_available": True},
    {"merchant_id": MERCHANT_IDS["urban_store"], "name": "Cotton Tote Bag", "description": "Organic cotton tote bag. Machine washable, perfect for daily use.", "price_paise": 19900, "category": "Shopping", "tags": "bag,cotton,eco-friendly,tote", "is_available": True},
    {"merchant_id": MERCHANT_IDS["urban_store"], "name": "LED Desk Lamp", "description": "Adjustable LED desk lamp with 3 brightness levels. USB powered.", "price_paise": 45000, "category": "Shopping", "tags": "lamp,desk,led,usb", "is_available": True},
    {"merchant_id": MERCHANT_IDS["urban_store"], "name": "Notebook Set (3-pack)", "description": "A5 ruled notebooks, 200 pages each. Premium quality paper.", "price_paise": 18000, "category": "Shopping", "tags": "notebook,stationery,paper", "is_available": True},
    {"merchant_id": MERCHANT_IDS["urban_store"], "name": "Stainless Steel Lunch Box", "description": "3-compartment stainless steel lunch box with insulated bag.", "price_paise": 35000, "category": "Shopping", "tags": "lunchbox,kitchen,stainless-steel", "is_available": True},
]


async def seed_database():
    """Seed the database with demo merchants and products."""
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        # Check if data already exists
        from sqlalchemy import select, func
        result = await session.execute(select(func.count()).select_from(Merchant))
        count = result.scalar()

        if count > 0:
            print(f"Database already has {count} merchants. Skipping seed.")
            return

        # Seed merchants
        for merchant_data in DEMO_MERCHANTS:
            merchant = Merchant(**merchant_data)
            session.add(merchant)
        print(f"Seeded {len(DEMO_MERCHANTS)} demo merchants.")

        # Seed products
        for product_data in DEMO_PRODUCTS:
            product = Product(**product_data)
            session.add(product)
        print(f"Seeded {len(DEMO_PRODUCTS)} demo products.")

        await session.commit()
        print("Database seeding complete!")


if __name__ == "__main__":
    asyncio.run(seed_database())
