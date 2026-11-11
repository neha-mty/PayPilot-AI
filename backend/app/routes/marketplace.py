"""Marketplace Universal Discovery & Comparison Routes."""
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.category import Category
from app.models.marketplace_provider import MarketplaceProvider
from app.models.search_log import SearchLog
from app.marketplace.provider_manager import MarketplaceProviderManager
from app.marketplace.registry import marketplace_registry
from app.marketplace.base_provider import NormalizedProduct
from app.services.nlp_classifier import NLPQueryClassifier

router = APIRouter(prefix="/marketplace", tags=["Universal Marketplace Discovery"])


@router.get("/search", response_model=List[NormalizedProduct])
async def search_marketplaces(
    q: Optional[str] = Query(None, description="Free-form or natural language query"),
    category: Optional[str] = Query(None, description="Category filter"),
    subcategory: Optional[str] = Query(None, description="Subcategory filter"),
    brand: Optional[str] = Query(None, description="Brand filter"),
    provider: Optional[str] = Query(None, description="Provider filter code (e.g. lenskart, pepperfry)"),
    min_price: Optional[float] = Query(None, description="Minimum price in INR"),
    max_price: Optional[float] = Query(None, description="Maximum price in INR"),
    sort_by: str = Query("relevance", description="Sort order: relevance, price_asc, price_desc, rating, discount"),
    limit: int = Query(24, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """Execute parallel search across all relevant configured marketplaces."""
    min_paise = int(min_price * 100) if min_price is not None else None
    max_paise = int(max_price * 100) if max_price is not None else None

    # If user provided a natural query without explicit category, detect it dynamically
    intent = None
    if q and not category:
        intent = NLPQueryClassifier.classify_query(q)
        if intent.get("detected_category") and intent["detected_category"] != "Specialty & Dynamically Discovered":
            category = intent["detected_category"]
        if not subcategory and intent.get("detected_subcategory"):
            subcategory = intent["detected_subcategory"]
        if not brand and intent.get("detected_brand"):
            brand = intent["detected_brand"]
        if max_paise is None and intent.get("max_price_paise"):
            max_paise = intent["max_price_paise"]

    results = await MarketplaceProviderManager.search_all_marketplaces(
        db=db,
        query=q,
        category=category,
        subcategory=subcategory,
        brand=brand,
        provider_code=provider,
        min_price_paise=min_paise,
        max_price_paise=max_paise,
        sort_by=sort_by,
        limit=limit,
    )

    # Log search for telemetry
    try:
        log = SearchLog(
            query=q or (category or "all"),
            detected_category=category,
            detected_subcategory=subcategory,
            detected_brand=brand,
            detected_max_price_paise=max_paise,
            results_count=len(results),
        )
        db.add(log)
        await db.commit()
    except Exception:
        pass

    return results


@router.get("/categories")
async def list_categories(db: AsyncSession = Depends(get_db)) -> List[Dict[str, Any]]:
    """List all supported marketplace categories and subcategories."""
    stmt = select(Category).options(selectinload(Category.subcategories)).where(Category.is_active == True)
    res = await db.execute(stmt)
    categories = res.scalars().all()

    return [
        {
            "id": c.id,
            "name": c.name,
            "slug": c.slug,
            "icon": c.icon,
            "description": c.description,
            "subcategories": [
                {"id": s.id, "name": s.name, "slug": s.slug}
                for s in c.subcategories
                if s.is_active
            ],
        }
        for c in categories
    ]


@router.get("/providers")
async def list_providers(db: AsyncSession = Depends(get_db)) -> List[Dict[str, Any]]:
    """List all registered marketplace providers, connection status, and rating."""
    stmt = select(MarketplaceProvider).where(MarketplaceProvider.is_active == True)
    res = await db.execute(stmt)
    providers = res.scalars().all()

    return [
        {
            "id": p.id,
            "code": p.code,
            "name": p.name,
            "primary_category": p.primary_category,
            "supported_categories": p.supported_categories.split(","),
            "website_url": p.website_url,
            "logo_icon": p.logo_icon,
            "description": p.description,
            "supports_integrated_checkout": p.supports_integrated_checkout,
            "data_source_type": p.data_source_type,
            "average_rating": p.average_rating,
        }
        for p in providers
    ]


@router.get("/product/{product_id}", response_model=NormalizedProduct)
async def get_product_details(product_id: str, db: AsyncSession = Depends(get_db)):
    """Fetch authoritative product details and real-time specifications."""
    prod = await MarketplaceProviderManager.get_product_by_id(db, product_id)
    if not prod:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found across configured marketplaces")
    return prod


@router.post("/detect-intent")
async def detect_query_intent(payload: Dict[str, str]) -> Dict[str, Any]:
    """Analyze query and extract categories, budget, brand, and specifications."""
    query_text = payload.get("query", "")
    return NLPQueryClassifier.classify_query(query_text)
