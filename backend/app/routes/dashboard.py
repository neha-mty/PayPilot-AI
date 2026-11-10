"""Dashboard summary route."""
from typing import Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.services.budget_service import get_dashboard_summary

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/summary")
async def dashboard_summary(
    user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Retrieve user dashboard financial health and pending approvals."""
    return await get_dashboard_summary(db, user.id)
