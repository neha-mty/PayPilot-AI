"""Intelligent NLP Intent & Category Extractor for Universal Marketplace Search."""
import re
from typing import Dict, Any, Optional

# Supported major category map with common keyword associations
CATEGORY_KEYWORD_MAP = {
    "Food and groceries": [
        "food", "groceries", "grocery", "restaurant", "meal", "dinner", "lunch", "breakfast",
        "vegetarian", "veg", "non-veg", "paneer", "pizza", "biryani", "bakery", "snack", "beverage"
    ],
    "Fashion and clothing": [
        "clothing", "saree", "sarees", "dress", "dresses", "shirt", "trousers", "jeans", "jacket",
        "kurta", "ethnic", "shoe", "shoes", "sneaker", "sneakers", "running shoe", "nike", "handbag", "wallet"
    ],
    "Jewellery and accessories": [
        "jewellery", "jewelry", "earring", "earrings", "gold", "silver", "diamond", "necklace", "ring",
        "rings", "bracelet", "watch", "watches", "sunglass", "sunglasses", "spectacles", "eyewear", "lenskart", "tanishq", "titan"
    ],
    "Electronics and technology": [
        "electronics", "laptop", "laptops", "smartphone", "smartphones", "phone", "tablet", "smartwatch",
        "headphone", "headphones", "earphone", "earphones", "speaker", "camera", "dell", "samsung", "croma"
    ],
    "Furniture and home furnishing": [
        "furniture", "chair", "office chair", "sofa", "bed", "mattress", "table", "study table",
        "dining table", "wardrobe", "bookshelf", "curtain", "carpet", "pepperfry", "ikea"
    ],
    "Home appliances": [
        "appliance", "washing machine", "refrigerator", "fridge", "air conditioner", "television", "tv",
        "microwave", "dishwasher", "vacuum", "water purifier", "fan", "geyser"
    ],
    "Beauty, cosmetics and personal care": [
        "beauty", "cosmetics", "makeup", "skincare", "haircare", "perfume", "deodorant", "grooming"
    ],
    "Books, education and stationery": [
        "book", "books", "novel", "stationery", "notebook", "pen", "exam", "course"
    ],
    "Sports, fitness and outdoor": [
        "sports", "fitness", "gym", "dumbbell", "treadmill", "yoga mat", "cricket", "football", "badminton"
    ],
    "Automotive and mobility": [
        "car", "bike", "motorcycle", "scooter", "bicycle", "helmet", "tyre", "automotive"
    ],
    "Travel and accommodation": [
        "flight", "flights", "hotel", "hotels", "resort", "homestay", "train", "bus", "travel", "kolkata", "delhi", "darjeeling"
    ],
    "Transportation and local services": [
        "cab", "taxi", "rental", "airport transfer", "moving", "delivery"
    ],
    "Entertainment and experiences": [
        "movie", "concert", "ticket", "tickets", "theatre", "theme park", "event"
    ],
    "Health and wellness products": [
        "health", "wellness", "monitor", "bp monitor", "pulse oximeter", "thermometer"
    ],
    "Pet supplies": [
        "pet", "dog food", "cat food", "pet toy", "leash", "aquarium"
    ],
    "Art, hobbies and collectibles": [
        "telescope", "astronomy", "musical", "keyboard", "piano", "guitar", "painting", "craft", "collectible"
    ],
    "Industrial and professional products": [
        "sewing machine", "tools", "hardware", "power tool", "office equipment"
    ],
    "Services and subscriptions": [
        "recharge", "subscription", "wifi", "internet", "cleaning"
    ],
}

KNOWN_BRANDS = {
    "lenskart": ("Lenskart", "lenskart", "Jewellery and accessories"),
    "vincent chase": ("Vincent Chase by Lenskart", "lenskart", "Jewellery and accessories"),
    "john jacobs": ("John Jacobs", "lenskart", "Jewellery and accessories"),
    "tanishq": ("Tanishq", "tanishq", "Jewellery and accessories"),
    "titan": ("Titan", "tanishq", "Jewellery and accessories"),
    "caratlane": ("CaratLane", "tanishq", "Jewellery and accessories"),
    "dell": ("Dell", "croma", "Electronics and technology"),
    "samsung": ("Samsung", "croma", "Electronics and technology"),
    "nike": ("Nike", "amazon_retail", "Fashion and clothing"),
    "pepperfry": ("Pepperfry Home", "pepperfry", "Furniture and home furnishing"),
    "ikea": ("IKEA", "pepperfry", "Furniture and home furnishing"),
    "celestron": ("Celestron", "dynamic_specialty", "Art, hobbies and collectibles"),
    "usha": ("Usha Janome", "dynamic_specialty", "Industrial and professional products"),
    "casio": ("Casio", "dynamic_specialty", "Art, hobbies and collectibles"),
    "indigo": ("IndiGo Airlines", "makemytrip", "Travel and accommodation"),
}


class NLPQueryClassifier:
    @staticmethod
    def classify_query(text: str) -> Dict[str, Any]:
        """Dynamically detect category, merchant, brand, budget, and search intent from natural language."""
        raw_text = text.strip()
        lower_text = raw_text.lower()

        # 1. Budget extraction (e.g., "under 2000", "below ₹5,000", "within 10000", "under 200 per night")
        max_price_paise = None
        min_price_paise = None

        price_patterns = [
            r"(?:under|below|max|within|less than|up to)\s*(?:₹|rs\.?|inr)?\s*([\d,]+)",
            r"(?:budget\s*of|price\s*of)\s*(?:₹|rs\.?|inr)?\s*([\d,]+)",
        ]
        for pat in price_patterns:
            m = re.search(pat, lower_text)
            if m:
                val_str = m.group(1).replace(",", "")
                try:
                    max_price_paise = int(val_str) * 100
                    break
                except ValueError:
                    pass

        min_patterns = [
            r"(?:above|more than|at least|over)\s*(?:₹|rs\.?|inr)?\s*([\d,]+)"
        ]
        for pat in min_patterns:
            m = re.search(pat, lower_text)
            if m:
                val_str = m.group(1).replace(",", "")
                try:
                    min_price_paise = int(val_str) * 100
                    break
                except ValueError:
                    pass

        # 2. Brand & Merchant detection
        detected_brand = None
        detected_provider_code = None
        brand_suggested_category = None

        for b_key, (b_name, p_code, cat_hint) in KNOWN_BRANDS.items():
            if b_key in lower_text:
                detected_brand = b_name
                detected_provider_code = p_code
                brand_suggested_category = cat_hint
                break

        # 3. Category detection
        detected_category = brand_suggested_category
        detected_subcategory = None

        if not detected_category:
            best_cat = None
            max_matches = 0
            for cat_name, keywords in CATEGORY_KEYWORD_MAP.items():
                matches = sum(1 for kw in keywords if kw in lower_text)
                if matches > max_matches:
                    max_matches = matches
                    best_cat = cat_name
            detected_category = best_cat or "Specialty & Dynamically Discovered"

        # Specific subcategory refinement
        if "sunglass" in lower_text or "shades" in lower_text:
            detected_subcategory = "Sunglasses"
        elif "earring" in lower_text:
            detected_subcategory = "Earrings"
        elif "saree" in lower_text:
            detected_subcategory = "Sarees"
        elif "laptop" in lower_text:
            detected_subcategory = "Laptops"
        elif "chair" in lower_text:
            detected_subcategory = "Office furniture"
        elif "sofa" in lower_text:
            detected_subcategory = "Sofas"
        elif "telescope" in lower_text:
            detected_subcategory = "Telescopes & Astronomy"
        elif "washing machine" in lower_text:
            detected_subcategory = "Washing machines"
        elif "refrigerator" in lower_text or "fridge" in lower_text:
            detected_subcategory = "Refrigerators"
        elif "flight" in lower_text:
            detected_subcategory = "Flights"
        elif "hotel" in lower_text:
            detected_subcategory = "Hotels"

        # Dietary preference
        vegetarian_only = ("veg" in lower_text or "vegetarian" in lower_text) and "non-veg" not in lower_text

        # Sanitize clean query string without prepositional fillers
        clean_query = re.sub(r"(?:find|search|get|show|me|under|below|for|a|an|the|in|from|within|at|least|approx|₹|rs\.?|inr|\d+)", " ", lower_text)
        clean_terms = [t for t in clean_query.split() if len(t) > 1]
        search_terms = " ".join(clean_terms)

        return {
            "original_query": raw_text,
            "search_query": search_terms if search_terms else raw_text,
            "detected_category": detected_category,
            "detected_subcategory": detected_subcategory,
            "detected_brand": detected_brand,
            "detected_provider_code": detected_provider_code,
            "max_price_paise": max_price_paise,
            "min_price_paise": min_price_paise,
            "vegetarian_only": vegetarian_only,
        }
