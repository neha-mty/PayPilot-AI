"""Merchant and Product catalog discovery service."""
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.merchant import Merchant
from app.models.product import Product


async def get_all_merchants(db: AsyncSession) -> List[Merchant]:
    """Retrieve all active merchants."""
    result = await db.execute(select(Merchant).where(Merchant.is_active == True))
    return list(result.scalars().all())


async def get_merchant_by_id(db: AsyncSession, merchant_id: str) -> Optional[Merchant]:
    """Retrieve merchant by ID."""
    result = await db.execute(select(Merchant).where(Merchant.id == merchant_id))
    return result.scalar_one_or_none()


async def get_products_by_merchant(db: AsyncSession, merchant_id: str) -> List[Product]:
    """Retrieve products for a specific merchant."""
    result = await db.execute(
        select(Product).where(Product.merchant_id == merchant_id, Product.is_available == True)
    )
    return list(result.scalars().all())


async def search_products(
    db: AsyncSession,
    query: Optional[str] = None,
    category: Optional[str] = None,
    max_price_paise: Optional[int] = None,
    vegetarian_only: bool = False,
) -> List[Product]:
    """Search available products with category, price, and dietary filtering."""
    stmt = select(Product).join(Merchant).where(Product.is_available == True)

    if category:
        stmt = stmt.where(Product.category.ilike(f"%{category}%"))

    if max_price_paise is not None:
        stmt = stmt.where(Product.price_paise <= max_price_paise)

    result = await db.execute(stmt)
    products = list(result.scalars().all())

    # Additional text search & dietary preference filter
    filtered = []
    for p in products:
        combined_text = f"{p.name} {p.description or ''} {p.tags or ''}".lower()

        if vegetarian_only:
            is_veg = "vegetarian" in combined_text or "vegan" in combined_text
            is_non_veg = "non-vegetarian" in combined_text or "chicken" in combined_text
            if not is_veg or is_non_veg:
                continue

        if query:
            q_terms = query.lower().split()
            if not all(term in combined_text for term in q_terms):
                continue

        filtered.append(p)

    return filtered
