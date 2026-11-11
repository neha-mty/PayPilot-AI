"""Tests for Universal Marketplace Discovery and Search."""
import pytest
import httpx
from app.main import app
from app.services.nlp_classifier import NLPQueryClassifier

BASE_URL = "http://testserver"


def test_nlp_intent_classification():
    # 1. Lenskart sunglasses under ₹2,000
    res = NLPQueryClassifier.classify_query("Find sunglasses from Lenskart under ₹2,000")
    assert res["detected_subcategory"] == "Sunglasses"
    assert res["detected_brand"] == "Lenskart"
    assert res["max_price_paise"] == 200000

    # 2. Office chair under ₹5,000
    res = NLPQueryClassifier.classify_query("Find a comfortable office chair under ₹5,000")
    assert res["detected_category"] == "Furniture and home furnishing"
    assert res["detected_subcategory"] == "Office furniture"
    assert res["max_price_paise"] == 500000

    # 3. Gold earrings under ₹10,000
    res = NLPQueryClassifier.classify_query("Find gold earrings under ₹10,000")
    assert res["detected_category"] == "Jewellery and accessories"
    assert res["detected_subcategory"] == "Earrings"
    assert res["max_price_paise"] == 1000000

    # 4. Telescope under ₹10,000 (Unexpected dynamic category)
    res = NLPQueryClassifier.classify_query("Find a good telescope under ₹10,000")
    assert res["detected_subcategory"] == "Telescopes & Astronomy"
    assert res["max_price_paise"] == 1000000


@pytest.mark.asyncio
async def test_marketplace_api_endpoints():
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url=BASE_URL) as client:
        # Categories list
        cat_res = await client.get("/marketplace/categories")
        assert cat_res.status_code == 200
        cats = cat_res.json()
        assert len(cats) >= 5

        # Providers list
        prov_res = await client.get("/marketplace/providers")
        assert prov_res.status_code == 200
        providers = prov_res.json()
        assert any(p["code"] == "lenskart" for p in providers)
        assert any(p["code"] == "pepperfry" for p in providers)

        # Multi-provider search: Lenskart sunglasses
        search_res = await client.get("/marketplace/search?q=sunglasses&provider=lenskart")
        assert search_res.status_code == 200
        items = search_res.json()
        assert len(items) > 0
        assert any("Vincent Chase" in item["name"] for item in items)
