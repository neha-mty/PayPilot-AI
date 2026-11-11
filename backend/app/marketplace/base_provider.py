"""Base class for Marketplace Providers in PayPilot AI."""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class NormalizedProduct(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    price_paise: int
    price_inr: float
    original_price_inr: Optional[float] = None
    discount_percent: Optional[int] = None
    currency: str = "INR"
    category: str
    subcategory: Optional[str] = None
    brand: Optional[str] = None
    merchant: str
    merchant_id: Optional[str] = None
    provider: str
    provider_code: str
    image_url: Optional[str] = None
    product_url: Optional[str] = None
    is_available: bool = True
    data_source_type: str = "DEMO"  # DEMO, LIVE, AFFILIATE, CACHED
    rating: Optional[float] = 4.5
    rating_count: Optional[int] = 100
    supports_integrated_checkout: bool = True
    specifications: Dict[str, Any] = Field(default_factory=dict)
    delivery_info: Optional[str] = None
    last_updated: Optional[str] = None


class BaseMarketplaceProvider(ABC):
    """Abstract interface for all marketplace adapters."""

    def __init__(self, code: str, name: str, primary_category: str, supported_categories: List[str]):
        self.code = code
        self.name = name
        self.primary_category = primary_category
        self.supported_categories = supported_categories

    @abstractmethod
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
        """Search products from this marketplace."""
        pass

    @abstractmethod
    async def get_product_details(self, product_id: str) -> Optional[NormalizedProduct]:
        """Get product details by ID."""
        pass

    @abstractmethod
    async def check_availability(self, product_id: str) -> bool:
        """Check if product is in stock / available."""
        pass

    def get_checkout_url(self, product_id: str) -> Optional[str]:
        """Return checkout or original provider URL."""
        return None
