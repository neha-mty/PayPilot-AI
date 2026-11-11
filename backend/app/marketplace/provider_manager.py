"""Provider Manager for parallel multi-provider search orchestration and result comparison."""
import asyncio
import logging
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from app.marketplace.base_provider import NormalizedProduct
from app.marketplace.registry import marketplace_registry
from app.marketplace.internal_adapter import InternalCatalogAdapter

logger = logging.getLogger(__name__)


class MarketplaceProviderManager:
    @staticmethod
    async def search_all_marketplaces(
        db: AsyncSession,
        query: Optional[str] = None,
        category: Optional[str] = None,
        subcategory: Optional[str] = None,
        brand: Optional[str] = None,
        provider_code: Optional[str] = None,
        min_price_paise: Optional[int] = None,
        max_price_paise: Optional[int] = None,
        sort_by: str = "relevance",  # relevance, price_asc, price_desc, rating
        limit: int = 24,
    ) -> List[NormalizedProduct]:
        """Search in parallel across internal database and all relevant external marketplace adapters."""
        tasks = []

        # 1. Internal DB catalog task
        internal_adapter = InternalCatalogAdapter(db)
        if not provider_code or provider_code == "internal":
            tasks.append(
                MarketplaceProviderManager._safe_search(
                    internal_adapter, query, category, subcategory, brand, min_price_paise, max_price_paise, limit
                )
            )

        # 2. Marketplace adapters
        if provider_code and provider_code != "internal":
            specific_provider = marketplace_registry.get_provider(provider_code)
            if specific_provider:
                tasks.append(
                    MarketplaceProviderManager._safe_search(
                        specific_provider, query, category, subcategory, brand, min_price_paise, max_price_paise, limit
                    )
                )
        else:
            relevant_providers = marketplace_registry.get_providers_for_category(category)
            for p in relevant_providers:
                tasks.append(
                    MarketplaceProviderManager._safe_search(
                        p, query, category, subcategory, brand, min_price_paise, max_price_paise, limit
                    )
                )

        # Execute all searches in parallel with a 3.0 second timeout
        results_lists = await asyncio.gather(*tasks, return_exceptions=True)

        all_products: List[NormalizedProduct] = []
        seen_ids = set()

        for res in results_lists:
            if isinstance(res, list):
                for prod in res:
                    if prod.id not in seen_ids:
                        seen_ids.add(prod.id)
                        all_products.append(prod)
            elif isinstance(res, Exception):
                logger.error(f"Error during marketplace search: {res}")

        # Post-search sorting
        if sort_by == "price_asc":
            all_products.sort(key=lambda x: x.price_paise)
        elif sort_by == "price_desc":
            all_products.sort(key=lambda x: x.price_paise, reverse=True)
        elif sort_by == "rating":
            all_products.sort(key=lambda x: (x.rating or 0, x.rating_count or 0), reverse=True)
        elif sort_by == "discount":
            all_products.sort(key=lambda x: x.discount_percent or 0, reverse=True)

        return all_products[:limit]

    @staticmethod
    async def _safe_search(
        provider, query, category, subcategory, brand, min_price_paise, max_price_paise, limit
    ) -> List[NormalizedProduct]:
        try:
            return await asyncio.wait_for(
                provider.search(
                    query=query,
                    category=category,
                    subcategory=subcategory,
                    brand=brand,
                    min_price_paise=min_price_paise,
                    max_price_paise=max_price_paise,
                    limit=limit,
                ),
                timeout=2.5,
            )
        except Exception as e:
            logger.warning(f"Provider {provider.name} failed or timed out: {e}")
            return []

    @staticmethod
    async def get_product_by_id(db: AsyncSession, product_id: str) -> Optional[NormalizedProduct]:
        """Fetch details from whichever provider or internal catalog owns this product."""
        # Check internal first
        internal_adapter = InternalCatalogAdapter(db)
        prod = await internal_adapter.get_product_details(product_id)
        if prod:
            return prod

        # Check all registered providers
        for p in marketplace_registry.get_all_providers():
            try:
                prod = await p.get_product_details(product_id)
                if prod:
                    return prod
            except Exception:
                continue
        return None
