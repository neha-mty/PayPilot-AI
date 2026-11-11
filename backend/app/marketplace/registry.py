"""Marketplace Provider Registry for PayPilot AI."""
from typing import Dict, List, Optional
from app.marketplace.base_provider import BaseMarketplaceProvider
from app.marketplace.lenskart_adapter import LenskartMarketplaceAdapter
from app.marketplace.furniture_adapter import FurnitureMarketplaceAdapter
from app.marketplace.electronics_adapter import ElectronicsMarketplaceAdapter
from app.marketplace.jewellery_adapter import JewelleryMarketplaceAdapter
from app.marketplace.travel_adapter import TravelMarketplaceAdapter
from app.marketplace.fashion_appliances_adapter import RetailAppliancesMarketplaceAdapter
from app.marketplace.dynamic_adapter import DynamicCategoryMarketplaceAdapter
from app.marketplace.web_search_adapter import InternetWebSearchAdapter


class MarketplaceRegistry:
    def __init__(self):
        self._providers: Dict[str, BaseMarketplaceProvider] = {}
        self._initialize_default_providers()

    def _initialize_default_providers(self):
        providers = [
            InternetWebSearchAdapter(),
            LenskartMarketplaceAdapter(),
            FurnitureMarketplaceAdapter(),
            ElectronicsMarketplaceAdapter(),
            JewelleryMarketplaceAdapter(),
            TravelMarketplaceAdapter(),
            RetailAppliancesMarketplaceAdapter(),
            DynamicCategoryMarketplaceAdapter(),
        ]
        for p in providers:
            self._providers[p.code] = p

    def get_provider(self, code: str) -> Optional[BaseMarketplaceProvider]:
        return self._providers.get(code)

    def get_all_providers(self) -> List[BaseMarketplaceProvider]:
        return list(self._providers.values())

    def get_providers_for_category(self, category: Optional[str]) -> List[BaseMarketplaceProvider]:
        if not category or category.lower() in ["all", "*"]:
            return list(self._providers.values())

        cat_lower = category.lower()
        matched = []
        for p in self._providers.values():
            if "*" in p.supported_categories:
                matched.append(p)
            elif any(cat_lower in sc.lower() or sc.lower() in cat_lower for sc in p.supported_categories):
                matched.append(p)
        return matched if matched else list(self._providers.values())


# Singleton instance
marketplace_registry = MarketplaceRegistry()
