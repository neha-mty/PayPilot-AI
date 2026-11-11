"""Internal Catalog Adapter for PayPilot database products."""
import json
from typing import List, Optional
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.marketplace.base_provider import BaseMarketplaceProvider, NormalizedProduct
from app.models.product import Product


class InternalCatalogAdapter(BaseMarketplaceProvider):
    def __init__(self, db_session: AsyncSession):
        super().__init__(
            code="internal",
            name="PayPilot Verified Catalog",
            primary_category="All",
            supported_categories=["*"],
        )
        self.db = db_session

    async def search(
        self,
        query: Optional[str] = None,
        category: Optional[str] = None,
        subcategory: Optional[str] = None,
        brand: Optional[str] = None,
        min_price_paise: Optional[int] = None,
        max_price_paise: Optional[int] = None,
        limit: int = 15,
    ) -> List[NormalizedProduct]:
        conditions = [Product.is_available == True]

        if category and category.lower() != "all":
            conditions.append(Product.category.ilike(f"%{category}%"))

        if subcategory:
            conditions.append(Product.subcategory.ilike(f"%{subcategory}%"))

        if brand:
            conditions.append(Product.brand.ilike(f"%{brand}%"))

        if min_price_paise is not None:
            conditions.append(Product.price_paise >= min_price_paise)

        if max_price_paise is not None:
            conditions.append(Product.price_paise <= max_price_paise)

        if query:
            terms = query.strip().split()
            term_filters = []
            for t in terms:
                term_filters.append(
                    or_(
                        Product.name.ilike(f"%{t}%"),
                        Product.description.ilike(f"%{t}%"),
                        Product.tags.ilike(f"%{t}%"),
                        Product.brand.ilike(f"%{t}%") if hasattr(Product, 'brand') else False,
                    )
                )
            if term_filters:
                conditions.append(and_(*term_filters))

        stmt = select(Product).options(selectinload(Product.merchant)).where(and_(*conditions)).limit(limit)
        result = await self.db.execute(stmt)
        products = result.scalars().all()

        normalized = []
        for p in products:
            specs = {}
            if p.specifications:
                try:
                    specs = json.loads(p.specifications)
                except Exception:
                    pass

            merchant_name = p.merchant.name if p.merchant else "Verified Merchant"
            orig_inr = (p.original_price_paise / 100) if p.original_price_paise else None
            price_inr = p.price_paise / 100
            discount = None
            if orig_inr and orig_inr > price_inr:
                discount = int(((orig_inr - price_inr) / orig_inr) * 100)

            normalized.append(
                NormalizedProduct(
                    id=p.id,
                    name=p.name,
                    description=p.description or "",
                    price_paise=p.price_paise,
                    price_inr=price_inr,
                    original_price_inr=orig_inr,
                    discount_percent=discount,
                    currency="INR",
                    category=p.category,
                    subcategory=p.subcategory,
                    brand=p.brand or merchant_name,
                    merchant=merchant_name,
                    merchant_id=p.merchant_id,
                    provider=p.provider_name or "PayPilot Catalog",
                    provider_code=p.provider_code or "internal",
                    image_url=p.image_url or "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=500&q=80",
                    product_url=p.product_url,
                    is_available=p.is_available,
                    data_source_type=p.data_source_type or "DEMO",
                    rating=p.rating or 4.5,
                    rating_count=p.rating_count or 85,
                    supports_integrated_checkout=p.supports_integrated_checkout,
                    specifications=specs,
                    delivery_info="2-4 business days (Verified Dispatch)",
                )
            )
        return normalized

    async def get_product_details(self, product_id: str) -> Optional[NormalizedProduct]:
        stmt = select(Product).options(selectinload(Product.merchant)).where(Product.id == product_id)
        result = await self.db.execute(stmt)
        p = result.scalar_one_or_none()
        if not p:
            return None

        specs = {}
        if p.specifications:
            try:
                specs = json.loads(p.specifications)
            except Exception:
                pass

        merchant_name = p.merchant.name if p.merchant else "Verified Merchant"
        price_inr = p.price_paise / 100
        orig_inr = (p.original_price_paise / 100) if p.original_price_paise else None

        return NormalizedProduct(
            id=p.id,
            name=p.name,
            description=p.description or "",
            price_paise=p.price_paise,
            price_inr=price_inr,
            original_price_inr=orig_inr,
            category=p.category,
            subcategory=p.subcategory,
            brand=p.brand or merchant_name,
            merchant=merchant_name,
            merchant_id=p.merchant_id,
            provider=p.provider_name or "PayPilot Catalog",
            provider_code=p.provider_code or "internal",
            image_url=p.image_url,
            product_url=p.product_url,
            is_available=p.is_available,
            data_source_type=p.data_source_type or "DEMO",
            rating=p.rating or 4.5,
            rating_count=p.rating_count or 100,
            supports_integrated_checkout=p.supports_integrated_checkout,
            specifications=specs,
        )

    async def check_availability(self, product_id: str) -> bool:
        stmt = select(Product.is_available).where(Product.id == product_id)
        result = await self.db.execute(stmt)
        avail = result.scalar_one_or_none()
        return bool(avail)
