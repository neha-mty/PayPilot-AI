"""Comprehensive Database seed script for Universal Marketplace Discovery.

Seeds all 18+ categories, subcategories, marketplace providers, verified merchants,
and a rich product catalog across all categories.
All data is clearly labelled with DEMO tags.
"""
import asyncio
from app.database import engine, Base, AsyncSessionLocal
from app.models import Merchant, Product, Category, Subcategory, MarketplaceProvider

CATEGORIES_DATA = [
    {
        "name": "Food and groceries",
        "slug": "food-groceries",
        "icon": "🍔",
        "description": "Restaurants, fast food, groceries, fresh produce, and gourmet meals.",
        "subcategories": [
            "Restaurants", "Fast food", "Vegetarian and non-vegetarian meals", "Groceries",
            "Fruits and vegetables", "Bakery products", "Snacks", "Beverages", "Dairy products", "Meal subscriptions"
        ]
    },
    {
        "name": "Fashion and clothing",
        "slug": "fashion-clothing",
        "icon": "👗",
        "description": "Men's, women's, and kids' wear, ethnic sarees, kurtas, jackets, and footwear.",
        "subcategories": [
            "Men's clothing", "Women's clothing", "Kids' clothing", "Ethnic wear", "Western wear",
            "Sarees", "Kurtas", "Dresses", "Shirts and trousers", "Jeans", "Jackets", "Winter wear",
            "Sportswear", "Shoes", "Sneakers", "Bags", "Handbags", "Wallets"
        ]
    },
    {
        "name": "Jewellery and accessories",
        "slug": "jewellery-accessories",
        "icon": "💍",
        "description": "Gold, silver, diamond jewellery, earrings, rings, luxury watches, and eyewear.",
        "subcategories": [
            "Gold jewellery", "Silver jewellery", "Diamond jewellery", "Artificial jewellery",
            "Earrings", "Necklaces", "Rings", "Bracelets", "Watches", "Sunglasses", "Spectacles"
        ]
    },
    {
        "name": "Electronics and technology",
        "slug": "electronics-technology",
        "icon": "💻",
        "description": "Laptops, smartphones, audio, smartwatches, monitors, and gaming.",
        "subcategories": [
            "Smartphones", "Laptops", "Desktop computers", "Tablets", "Smartwatches",
            "Headphones", "Earphones", "Speakers", "Cameras", "Gaming consoles", "Computer accessories"
        ]
    },
    {
        "name": "Furniture and home furnishing",
        "slug": "furniture-furnishing",
        "icon": "🛋️",
        "description": "Ergonomic chairs, solid wood sofas, beds, study desks, and modern decor.",
        "subcategories": [
            "Sofas", "Beds", "Mattresses", "Dining tables", "Chairs", "Office furniture",
            "Study tables", "Wardrobes", "Bookshelves", "Curtains", "Carpets", "Lighting"
        ]
    },
    {
        "name": "Home appliances",
        "slug": "home-appliances",
        "icon": "🧺",
        "description": "Washing machines, smart refrigerators, televisions, air purifiers, and microwaves.",
        "subcategories": [
            "Refrigerators", "Washing machines", "Air conditioners", "Televisions", "Microwaves",
            "Dishwashers", "Vacuum cleaners", "Water purifiers", "Fans", "Kitchen appliances"
        ]
    },
    {
        "name": "Beauty, cosmetics and personal care",
        "slug": "beauty-cosmetics",
        "icon": "💄",
        "description": "Skincare, luxury perfumes, cosmetics, haircare, and personal grooming.",
        "subcategories": [
            "Makeup", "Skincare", "Haircare", "Perfumes", "Deodorants", "Grooming products"
        ]
    },
    {
        "name": "Books, education and stationery",
        "slug": "books-stationery",
        "icon": "📚",
        "description": "Academic textbooks, fiction, competitive exam books, and stationery.",
        "subcategories": [
            "Academic books", "Fiction", "Non-fiction", "Competitive examination books", "Notebooks", "Office stationery"
        ]
    },
    {
        "name": "Sports, fitness and outdoor",
        "slug": "sports-fitness",
        "icon": "⚽",
        "description": "Gym equipment, running shoes, yoga mats, cricket gear, and camping accessories.",
        "subcategories": [
            "Gym equipment", "Dumbbells", "Treadmills", "Yoga mats", "Sports shoes", "Cricket equipment", "Outdoor accessories"
        ]
    },
    {
        "name": "Automotive and mobility",
        "slug": "automotive-mobility",
        "icon": "🚗",
        "description": "Helmets, car accessories, bike accessories, tyres, and vehicle electronics.",
        "subcategories": [
            "Bicycles", "Car accessories", "Bike accessories", "Helmets", "Tyres", "Automotive electronics"
        ]
    },
    {
        "name": "Travel and accommodation",
        "slug": "travel-accommodation",
        "icon": "✈️",
        "description": "Domestic flights, boutique mountain resorts, homestays, and holiday experiences.",
        "subcategories": [
            "Flights", "Hotels", "Resorts", "Homestays", "Train tickets", "Holiday packages"
        ]
    },
    {
        "name": "Transportation and local services",
        "slug": "transportation-services",
        "icon": "🚕",
        "description": "Airport transfers, vehicle rentals, and city moving services.",
        "subcategories": [
            "Cab booking", "Airport transfers", "Local transportation", "Vehicle rentals"
        ]
    },
    {
        "name": "Entertainment and experiences",
        "slug": "entertainment-experiences",
        "icon": "🎟️",
        "description": "Concert passes, movie tickets, theme parks, and cultural events.",
        "subcategories": [
            "Movie tickets", "Concert tickets", "Sports event tickets", "Theme parks", "Experiences and activities"
        ]
    },
    {
        "name": "Health and wellness products",
        "slug": "health-wellness",
        "icon": "🩺",
        "description": "BP monitors, pulse oximeters, ergonomic supports, and fitness trackers.",
        "subcategories": [
            "Fitness equipment", "Wellness accessories", "Health monitoring devices"
        ]
    },
    {
        "name": "Pet supplies",
        "slug": "pet-supplies",
        "icon": "🐾",
        "description": "Pet nutrition, interactive toys, collars, grooming, and aquarium supplies.",
        "subcategories": [
            "Pet food", "Toys", "Grooming products", "Pet accessories", "Pet furniture"
        ]
    },
    {
        "name": "Art, hobbies and collectibles",
        "slug": "art-hobbies",
        "icon": "🎨",
        "description": "Astronomical telescopes, musical keyboards, guitars, art paints, and board games.",
        "subcategories": [
            "Telescopes & Astronomy", "Musical keyboards", "Musical instruments", "Art supplies", "Collectibles"
        ]
    },
    {
        "name": "Industrial and professional products",
        "slug": "industrial-professional",
        "icon": "⚙️",
        "description": "Electric sewing machines, power tools, safety gear, and office hardware.",
        "subcategories": [
            "Sewing machines", "Tools", "Hardware", "Professional electronics", "Office equipment"
        ]
    },
    {
        "name": "Services and subscriptions",
        "slug": "services-subscriptions",
        "icon": "📱",
        "description": "Broadband fiber plans, mobile recharges, cloud storage, and home services.",
        "subcategories": [
            "Internet plans", "Mobile recharge", "Software subscriptions", "Home cleaning services"
        ]
    }
]

PROVIDERS_DATA = [
    {
        "code": "lenskart",
        "name": "Lenskart Eyewear",
        "primary_category": "Jewellery and accessories",
        "supported_categories": "Jewellery and accessories,Fashion and clothing,Sports, fitness and outdoor",
        "website_url": "https://www.lenskart.com",
        "logo_icon": "👓",
        "description": "Direct eyewear catalog offering UV-polarized sunglasses, lightweight spectacles, and computer glasses.",
        "supports_integrated_checkout": True,
        "data_source_type": "DEMO",
        "average_rating": 4.6
    },
    {
        "code": "croma",
        "name": "Croma Electronics",
        "primary_category": "Electronics and technology",
        "supported_categories": "Electronics and technology,Home appliances",
        "website_url": "https://www.croma.com",
        "logo_icon": "💻",
        "description": "Consumer electronics, laptops from Dell & HP, smartphones, and wireless earphones.",
        "supports_integrated_checkout": True,
        "data_source_type": "DEMO",
        "average_rating": 4.5
    },
    {
        "code": "pepperfry",
        "name": "Pepperfry Furniture",
        "primary_category": "Furniture and home furnishing",
        "supported_categories": "Furniture and home furnishing,Home appliances",
        "website_url": "https://www.pepperfry.com",
        "logo_icon": "🛋️",
        "description": "Ergonomic mesh chairs, Sheesham wood compact sofas, and modern workstation desks.",
        "supports_integrated_checkout": True,
        "data_source_type": "DEMO",
        "average_rating": 4.6
    },
    {
        "code": "tanishq",
        "name": "Tanishq Jewellery",
        "primary_category": "Jewellery and accessories",
        "supported_categories": "Jewellery and accessories,Fashion and clothing",
        "website_url": "https://www.tanishq.co.in",
        "logo_icon": "💎",
        "description": "18KT hallmarked gold floral earrings, Titan quartz watches, and sterling silver rings.",
        "supports_integrated_checkout": True,
        "data_source_type": "DEMO",
        "average_rating": 4.8
    },
    {
        "code": "makemytrip",
        "name": "MakeMyTrip Travel",
        "primary_category": "Travel and accommodation",
        "supported_categories": "Travel and accommodation,Transportation and local services",
        "website_url": "https://www.makemytrip.com",
        "logo_icon": "✈️",
        "description": "Domestic flights (Kolkata to Delhi), mountain resorts in Darjeeling, and vacation stays.",
        "supports_integrated_checkout": True,
        "data_source_type": "DEMO",
        "average_rating": 4.5
    },
    {
        "code": "amazon_retail",
        "name": "Amazon & Myntra Retail",
        "primary_category": "Fashion and clothing",
        "supported_categories": "Fashion and clothing,Home appliances,Sports, fitness and outdoor,Food and groceries",
        "website_url": "https://www.amazon.in",
        "logo_icon": "📦",
        "description": "Pure silk wedding sarees, Nike running shoes, 5-star washing machines, and refrigerators.",
        "supports_integrated_checkout": True,
        "data_source_type": "DEMO",
        "average_rating": 4.6
    },
    {
        "code": "dynamic_specialty",
        "name": "Specialty & Niche Marketplaces",
        "primary_category": "Specialty",
        "supported_categories": "*",
        "website_url": "https://paypilot.ai/specialty",
        "logo_icon": "🔭",
        "description": "Astronomical telescopes, automated zig-zag sewing machines, smart security cameras, and musical instruments.",
        "supports_integrated_checkout": True,
        "data_source_type": "DEMO",
        "average_rating": 4.7
    }
]

MERCHANTS_DATA = [
    {
        "id": "m-lenskart-001",
        "name": "Lenskart Official",
        "category": "Jewellery and accessories",
        "description": "[DEMO] Verified eyewear merchant with 100% genuine polarized UV400 lenses and frames.",
        "website_url": "https://www.lenskart.com",
        "is_verified": True,
        "is_active": True,
    },
    {
        "id": "m-pepperfry-002",
        "name": "Pepperfry Home",
        "category": "Furniture and home furnishing",
        "description": "[DEMO] Verified home decor and ergonomic furniture merchant.",
        "website_url": "https://www.pepperfry.com",
        "is_verified": True,
        "is_active": True,
    },
    {
        "id": "m-croma-003",
        "name": "Croma Retail",
        "category": "Electronics and technology",
        "description": "[DEMO] Verified consumer electronics and computing retailer.",
        "website_url": "https://www.croma.com",
        "is_verified": True,
        "is_active": True,
    },
    {
        "id": "m-tanishq-004",
        "name": "Tanishq Official",
        "category": "Jewellery and accessories",
        "description": "[DEMO] Verified precious jewellery and luxury watch retailer.",
        "website_url": "https://www.tanishq.co.in",
        "is_verified": True,
        "is_active": True,
    },
    {
        "id": "m-makemytrip-005",
        "name": "MakeMyTrip Booking Services",
        "category": "Travel and accommodation",
        "description": "[DEMO] Verified flight tickets, resort reservations, and travel partner.",
        "website_url": "https://www.makemytrip.com",
        "is_verified": True,
        "is_active": True,
    },
    {
        "id": "m-authorized-retail-006",
        "name": "Authorized Retail Partner",
        "category": "Fashion and clothing",
        "description": "[DEMO] Verified partner for apparel, footwear, and consumer appliances.",
        "website_url": "https://www.amazon.in",
        "is_verified": True,
        "is_active": True,
    },
    {
        "id": "m-specialty-distributor-007",
        "name": "Authorized Specialty Distributor",
        "category": "Specialty",
        "description": "[DEMO] Verified distributor for astronomy optics, sewing machinery, and smart devices.",
        "website_url": "https://paypilot.ai/specialty",
        "is_verified": True,
        "is_active": True,
    },
    {
        "id": "m-0001-green-bowl-demo-0000",
        "name": "Green Bowl",
        "category": "Food and groceries",
        "description": "[DEMO] Healthy vegetarian restaurant offering fresh, home-style meals.",
        "website_url": "https://greenbowl.demo",
        "is_verified": True,
        "is_active": True,
    },
    {
        "id": "m-0002-daily-bites-demo-00",
        "name": "Daily Bites",
        "category": "Food and groceries",
        "description": "[DEMO] Quick meals and snacks for every taste.",
        "website_url": "https://dailybites.demo",
        "is_verified": True,
        "is_active": True,
    },
    {
        "id": "m-0004-urban-store-demo-00",
        "name": "Urban Store",
        "category": "Shopping",
        "description": "[DEMO] Daily-use products and lifestyle items. [UNVERIFIED MERCHANT]",
        "website_url": "https://urbanstore.demo",
        "is_verified": False,  # Intentionally unverified for policy test
        "is_active": True,
    }
]

INITIAL_PRODUCTS = [
    # Lenskart items
    {
        "id": "lenskart-sg-001",
        "merchant_id": "m-lenskart-001",
        "name": "Vincent Chase Polarized Wayfarer Sunglasses",
        "description": "Matte Black Full Rim Wayfarer Sunglasses with UV400 Polarized Green lenses.",
        "price_paise": 119900,
        "original_price_paise": 200000,
        "category": "Jewellery and accessories",
        "subcategory": "Sunglasses",
        "brand": "Vincent Chase by Lenskart",
        "tags": "sunglasses,shades,eyewear,lenskart,polarized,uv400",
        "image_url": "https://images.unsplash.com/photo-1511499767150-a48a237f0083?w=500&q=80",
        "product_url": "https://www.lenskart.com/vincent-chase-wayfarer.html",
        "provider_code": "lenskart",
        "provider_name": "Lenskart Eyewear",
        "data_source_type": "DEMO",
        "rating": 4.6,
        "rating_count": 842,
        "supports_integrated_checkout": True,
        "is_available": True
    },
    {
        "id": "lenskart-sg-002",
        "merchant_id": "m-lenskart-001",
        "name": "Vincent Chase Aviator Sunglasses Golden Green",
        "description": "Full Rim Aviator Stainless Steel Sunglasses with Gradient Lenses.",
        "price_paise": 149900,
        "original_price_paise": 250000,
        "category": "Jewellery and accessories",
        "subcategory": "Sunglasses",
        "brand": "Vincent Chase by Lenskart",
        "tags": "sunglasses,aviator,gold,lenskart,eyewear",
        "image_url": "https://images.unsplash.com/photo-1572635196237-14b3f281503f?w=500&q=80",
        "product_url": "https://www.lenskart.com/vincent-chase-aviator.html",
        "provider_code": "lenskart",
        "provider_name": "Lenskart Eyewear",
        "data_source_type": "DEMO",
        "rating": 4.5,
        "rating_count": 612,
        "supports_integrated_checkout": True,
        "is_available": True
    },
    # Furniture items
    {
        "id": "furn-pf-001",
        "merchant_id": "m-pepperfry-002",
        "name": "Ergonomic High-Back Executive Office Mesh Chair",
        "description": "Ergonomic breathable mesh chair with multi-stage lumbar support and 3D adjustable armrests.",
        "price_paise": 489900,
        "original_price_paise": 850000,
        "category": "Furniture and home furnishing",
        "subcategory": "Office furniture",
        "brand": "Green Soul",
        "tags": "chair,office chair,ergonomic,furniture,pepperfry",
        "image_url": "https://images.unsplash.com/photo-1580481077195-c3a821a58875?w=500&q=80",
        "product_url": "https://www.pepperfry.com/ergonomic-office-chair.html",
        "provider_code": "pepperfry",
        "provider_name": "Pepperfry Furniture",
        "data_source_type": "DEMO",
        "rating": 4.7,
        "rating_count": 520,
        "supports_integrated_checkout": True,
        "is_available": True
    },
    {
        "id": "furn-pf-002",
        "merchant_id": "m-pepperfry-002",
        "name": "Solid Sheesham Wood 3-Seater Compact Sofa",
        "description": "Handcrafted Sheesham wood frame with high-density foam cushions and washable beige upholstery. Ideal for small living rooms.",
        "price_paise": 1449900,
        "original_price_paise": 2200000,
        "category": "Furniture and home furnishing",
        "subcategory": "Sofas",
        "brand": "Woodsworth by Pepperfry",
        "tags": "sofa,couch,sheesham wood,living room,furniture,pepperfry",
        "image_url": "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=500&q=80",
        "product_url": "https://www.pepperfry.com/sheesham-compact-sofa.html",
        "provider_code": "pepperfry",
        "provider_name": "Pepperfry Furniture",
        "data_source_type": "DEMO",
        "rating": 4.6,
        "rating_count": 218,
        "supports_integrated_checkout": True,
        "is_available": True
    },
    # Electronics items
    {
        "id": "elec-cr-001",
        "merchant_id": "m-croma-003",
        "name": "Dell Inspiron 15 Core i5 16GB RAM 512GB SSD Laptop",
        "description": "Intel Core i5 12th Gen, 16GB DDR4 RAM, 512GB PCIe NVMe SSD, 15.6-inch FHD Anti-Glare Display, Windows 11.",
        "price_paise": 4899000,
        "original_price_paise": 6200000,
        "category": "Electronics and technology",
        "subcategory": "Laptops",
        "brand": "Dell",
        "tags": "laptop,dell,programming,student,croma,intel i5",
        "image_url": "https://images.unsplash.com/photo-1593642632823-8f785ba67e45?w=500&q=80",
        "product_url": "https://www.croma.com/dell-inspiron-15.html",
        "provider_code": "croma",
        "provider_name": "Croma Electronics",
        "data_source_type": "DEMO",
        "rating": 4.6,
        "rating_count": 940,
        "supports_integrated_checkout": True,
        "is_available": True
    },
    # Jewellery items
    {
        "id": "jwl-tq-001",
        "merchant_id": "m-tanishq-004",
        "name": "Tanishq 18KT Yellow Gold Floral Stud Earrings",
        "description": "18 Karat Hallmarked Yellow Gold floral stud earrings with dual-finish petals. BIS Hallmarked.",
        "price_paise": 849900,
        "original_price_paise": 1050000,
        "category": "Jewellery and accessories",
        "subcategory": "Earrings",
        "brand": "Tanishq",
        "tags": "gold,earrings,tanishq,jewellery,18kt,bis hallmarked",
        "image_url": "https://images.unsplash.com/photo-1630019852942-f89202989a59?w=500&q=80",
        "product_url": "https://www.tanishq.co.in/gold-floral-earrings.html",
        "provider_code": "tanishq",
        "provider_name": "Tanishq Jewellery",
        "data_source_type": "DEMO",
        "rating": 4.9,
        "rating_count": 310,
        "supports_integrated_checkout": True,
        "is_available": True
    },
    # Travel items
    {
        "id": "trv-mmt-001",
        "merchant_id": "m-makemytrip-005",
        "name": "IndiGo Flight 6E-204: Kolkata (CCU) to Delhi (DEL)",
        "description": "Non-stop economy flight. 2h 20m duration. 15kg check-in baggage included.",
        "price_paise": 449900,
        "original_price_paise": 620000,
        "category": "Travel and accommodation",
        "subcategory": "Flights",
        "brand": "IndiGo Airlines",
        "tags": "flight,kolkata,delhi,ccu,del,indigo,travel,makemytrip",
        "image_url": "https://images.unsplash.com/photo-1436491865332-7a61a109cc05?w=500&q=80",
        "product_url": "https://www.makemytrip.com/flights/ccu-del.html",
        "provider_code": "makemytrip",
        "provider_name": "MakeMyTrip Travel",
        "data_source_type": "DEMO",
        "rating": 4.5,
        "rating_count": 3410,
        "supports_integrated_checkout": True,
        "is_available": True
    },
    {
        "id": "trv-mmt-002",
        "merchant_id": "m-makemytrip-005",
        "name": "The Himalayan View Heritage Homestay, Darjeeling",
        "description": "Boutique heritage stay overlooking Kanchenjunga snow peaks. Free high-speed WiFi and organic breakfast.",
        "price_paise": 269900,
        "original_price_paise": 420000,
        "category": "Travel and accommodation",
        "subcategory": "Hotels",
        "brand": "Himalayan View Stays",
        "tags": "hotel,darjeeling,resort,homestay,travel,makemytrip",
        "image_url": "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=500&q=80",
        "product_url": "https://www.makemytrip.com/hotels/darjeeling.html",
        "provider_code": "makemytrip",
        "provider_name": "MakeMyTrip Travel",
        "data_source_type": "DEMO",
        "rating": 4.7,
        "rating_count": 482,
        "supports_integrated_checkout": True,
        "is_available": True
    },
    # Fashion & Appliances
    {
        "id": "fsh-myn-001",
        "merchant_id": "m-authorized-retail-006",
        "name": "Kanjivaram Zari Woven Pure Silk Wedding Saree",
        "description": "Rich traditional Kanjivaram banarasi border silk saree with pure golden zari work and brocade blouse.",
        "price_paise": 479900,
        "original_price_paise": 999900,
        "category": "Fashion and clothing",
        "subcategory": "Sarees",
        "brand": "Samyakk Traditional",
        "tags": "saree,wedding,silk,kanjivaram,ethnic,fashion",
        "image_url": "https://images.unsplash.com/photo-1610030469983-98e550d6193c?w=500&q=80",
        "product_url": "https://www.myntra.com/kanjivaram-silk-saree.html",
        "provider_code": "amazon_retail",
        "provider_name": "Amazon & Myntra Retail",
        "data_source_type": "DEMO",
        "rating": 4.8,
        "rating_count": 680,
        "supports_integrated_checkout": True,
        "is_available": True
    },
    {
        "id": "app-amz-003",
        "merchant_id": "m-authorized-retail-006",
        "name": "LG 7 Kg 5-Star Smart Inverter Washing Machine",
        "description": "Smart Inverter motor technology with turbo drum and stainless steel tub.",
        "price_paise": 1749000,
        "original_price_paise": 2399000,
        "category": "Home appliances",
        "subcategory": "Washing machines",
        "brand": "LG",
        "tags": "washing machine,appliances,lg,5-star,smart inverter",
        "image_url": "https://images.unsplash.com/photo-1626806787461-102c1bfaaea1?w=500&q=80",
        "product_url": "https://www.amazon.in/lg-washing-machine.html",
        "provider_code": "amazon_retail",
        "provider_name": "Amazon & Myntra Retail",
        "data_source_type": "DEMO",
        "rating": 4.6,
        "rating_count": 2400,
        "supports_integrated_checkout": True,
        "is_available": True
    },
    {
        "id": "app-amz-004",
        "merchant_id": "m-authorized-retail-006",
        "name": "Samsung 189L 5-Star Single Door Refrigerator",
        "description": "Digital Inverter Technology for quiet operation and 50% power saving.",
        "price_paise": 1799000,
        "original_price_paise": 2499000,
        "category": "Home appliances",
        "subcategory": "Refrigerators",
        "brand": "Samsung",
        "tags": "refrigerator,fridge,samsung,5-star,appliances",
        "image_url": "https://images.unsplash.com/photo-1584568694244-14fbdf83bd30?w=500&q=80",
        "product_url": "https://www.amazon.in/samsung-fridge.html",
        "provider_code": "amazon_retail",
        "provider_name": "Amazon & Myntra Retail",
        "data_source_type": "DEMO",
        "rating": 4.5,
        "rating_count": 1890,
        "supports_integrated_checkout": True,
        "is_available": True
    },
    # Dynamic Specialty items (Telescope)
    {
        "id": "dyn-tele-001",
        "merchant_id": "m-specialty-distributor-007",
        "name": "Celestron PowerSeeker 70AZ Refractor Astronomical Telescope",
        "description": "70mm aperture refractor telescope with 700mm focal length, fully coated glass optics, and 3x Barlow lens.",
        "price_paise": 899900,
        "original_price_paise": 1250000,
        "category": "Art, hobbies and collectibles",
        "subcategory": "Telescopes & Astronomy",
        "brand": "Celestron",
        "tags": "telescope,astronomy,celestron,optics,stargazing",
        "image_url": "https://images.unsplash.com/photo-1506703719100-a0f3a48c0f86?w=500&q=80",
        "product_url": "https://www.celestron.com/powerseeker-70az",
        "provider_code": "dynamic_specialty",
        "provider_name": "Specialty & Niche Marketplaces",
        "data_source_type": "DEMO",
        "rating": 4.6,
        "rating_count": 340,
        "supports_integrated_checkout": True,
        "is_available": True
    },
    # Vegetarian food meal
    {
        "id": "food-gb-001",
        "merchant_id": "m-0001-green-bowl-demo-0000",
        "name": "Paneer Tikka Thali with 2 Roti, Dal Makhani & Rice",
        "description": "Authentic North Indian thali with fresh paneer tikka, yellow dal tadka, steamed basmati rice, and salad. 100% pure vegetarian.",
        "price_paise": 18000,
        "original_price_paise": 24000,
        "category": "Food and groceries",
        "subcategory": "Vegetarian and non-vegetarian meals",
        "brand": "Green Bowl",
        "tags": "vegetarian,veg,paneer,thali,lunch,dinner,food",
        "image_url": "https://images.unsplash.com/photo-1631452180519-c014fe946bc7?w=500&q=80",
        "product_url": "https://greenbowl.demo/paneer-thali",
        "provider_code": "internal",
        "provider_name": "Green Bowl Kitchen",
        "data_source_type": "DEMO",
        "rating": 4.8,
        "rating_count": 420,
        "supports_integrated_checkout": True,
        "is_available": True
    }
]


async def seed_database():
    """Create all tables and seed data idempotently."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        # 1. Seed Categories & Subcategories
        for cat_info in CATEGORIES_DATA:
            existing_cat = await session.get(Category, cat_info["slug"])
            if not existing_cat:
                cat = Category(
                    id=cat_info["slug"],
                    name=cat_info["name"],
                    slug=cat_info["slug"],
                    icon=cat_info["icon"],
                    description=cat_info["description"],
                )
                session.add(cat)
                await session.flush()
                for sub_name in cat_info["subcategories"]:
                    sub_slug = sub_name.lower().replace(" ", "-").replace("'", "").replace(",", "")
                    sub = Subcategory(
                        id=f"{cat_info['slug']}-{sub_slug}",
                        category_id=cat.id,
                        name=sub_name,
                        slug=sub_slug,
                    )
                    session.add(sub)

        # 2. Seed Providers
        for p_info in PROVIDERS_DATA:
            existing_p = await session.get(MarketplaceProvider, p_info["code"])
            if not existing_p:
                p = MarketplaceProvider(
                    id=p_info["code"],
                    code=p_info["code"],
                    name=p_info["name"],
                    primary_category=p_info["primary_category"],
                    supported_categories=p_info["supported_categories"],
                    website_url=p_info["website_url"],
                    logo_icon=p_info["logo_icon"],
                    description=p_info["description"],
                    supports_integrated_checkout=p_info["supports_integrated_checkout"],
                    data_source_type=p_info["data_source_type"],
                    average_rating=p_info["average_rating"],
                )
                session.add(p)

        # 3. Seed Merchants
        for m_info in MERCHANTS_DATA:
            existing_m = await session.get(Merchant, m_info["id"])
            if not existing_m:
                m = Merchant(
                    id=m_info["id"],
                    name=m_info["name"],
                    category=m_info["category"],
                    description=m_info["description"],
                    website_url=m_info["website_url"],
                    is_verified=m_info["is_verified"],
                    is_active=m_info["is_active"],
                )
                session.add(m)

        # 4. Seed Products
        for prod_info in INITIAL_PRODUCTS:
            existing_prod = await session.get(Product, prod_info["id"])
            if not existing_prod:
                prod = Product(
                    id=prod_info["id"],
                    merchant_id=prod_info["merchant_id"],
                    name=prod_info["name"],
                    description=prod_info["description"],
                    price_paise=prod_info["price_paise"],
                    original_price_paise=prod_info.get("original_price_paise"),
                    category=prod_info["category"],
                    subcategory=prod_info.get("subcategory"),
                    brand=prod_info.get("brand"),
                    tags=prod_info.get("tags"),
                    image_url=prod_info.get("image_url"),
                    product_url=prod_info.get("product_url"),
                    provider_code=prod_info.get("provider_code", "internal"),
                    provider_name=prod_info.get("provider_name", "PayPilot Catalog"),
                    data_source_type=prod_info.get("data_source_type", "DEMO"),
                    rating=prod_info.get("rating", 4.5),
                    rating_count=prod_info.get("rating_count", 100),
                    supports_integrated_checkout=prod_info.get("supports_integrated_checkout", True),
                    is_available=prod_info.get("is_available", True),
                )
                session.add(prod)

        await session.commit()
        print("[SUCCESS] Universal Marketplace catalog, categories, providers, and merchants seeded successfully!")


if __name__ == "__main__":
    asyncio.run(seed_database())
