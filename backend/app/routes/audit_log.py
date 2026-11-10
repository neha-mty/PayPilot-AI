"""Security and event audit log routes."""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.audit_log import AuditLog
from app.schemas.audit_log import AuditLogOut

router = APIRouter(prefix="/audit-logs", tags=["Audit Logs"])


@router.get("", response_model=List[AuditLogOut])
async def list_audit_logs(
    actor_type: Optional[str] = Query(None),
    limit: int = Query(50, le=100),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve security audit events associated with current user."""
    stmt = (
        select(AuditLog)
        .where(or_(AuditLog.user_id == user.id, AuditLog.user_id.is_(None)))
        .order_by(AuditLog.created_at.desc())
        .limit(limit)
    )
    if actor_type:
        stmt = stmt.where(AuditLog.actor_type == actor_type)

    res = await db.execute(stmt)
    logs = list(res.scalars().all())
    return [AuditLogOut.model_validate(l) for l in logs]
