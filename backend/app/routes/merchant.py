"""Merchant and Product catalog routes."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.merchant import MerchantOut, ProductOut
from app.services.merchant_service import (
    get_all_merchants,
    get_merchant_by_id,
    get_products_by_merchant,
)

router = APIRouter(prefix="/merchants", tags=["Merchants & Products"])


@router.get("", response_model=List[MerchantOut])
async def list_merchants(db: AsyncSession = Depends(get_db)):
    """List all demo merchants and their catalog items."""
    merchants = await get_all_merchants(db)
    result = []
    for m in merchants:
        products = await get_products_by_merchant(db, m.id)
        m_dict = {
            "id": m.id,
            "name": m.name,
            "category": m.category,
            "description": m.description,
            "is_verified": m.is_verified,
            "is_active": m.is_active,
            "created_at": m.created_at,
            "products": [
                ProductOut(
                    id=p.id,
                    merchant_id=p.merchant_id,
                    name=p.name,
                    description=p.description,
                    price_paise=p.price_paise,
                    category=p.category,
                    tags=p.tags,
                    is_available=p.is_available,
                    created_at=p.created_at,
                    merchant_name=m.name,
                    merchant_verified=m.is_verified,
                )
                for p in products
            ],
        }
        result.append(MerchantOut(**m_dict))
    return result


@router.get("/{merchant_id}/products", response_model=List[ProductOut])
async def list_merchant_products(merchant_id: str, db: AsyncSession = Depends(get_db)):
    """List products for a specific merchant."""
    merchant = await get_merchant_by_id(db, merchant_id)
    if not merchant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Merchant not found")

    products = await get_products_by_merchant(db, merchant_id)
    return [
        ProductOut(
            id=p.id,
            merchant_id=p.merchant_id,
            name=p.name,
            description=p.description,
            price_paise=p.price_paise,
            category=p.category,
            tags=p.tags,
            is_available=p.is_available,
            created_at=p.created_at,
            merchant_name=merchant.name,
            merchant_verified=merchant.is_verified,
        )
        for p in products
    ]
