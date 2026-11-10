"""Authentication routes."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.user import User
from app.models.policy import SpendingPolicy
from app.schemas.auth import UserRegister, UserLogin, AuthResponse, UserOut
from app.services.auth_service import hash_password, verify_password, create_access_token
from app.services.audit_service import log_event

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(payload: UserRegister, db: AsyncSession = Depends(get_db)):
    """Register a new user account with default spending policy."""
    # Check if email is already taken
    existing = await db.execute(select(User).where(User.email == payload.email.lower()))
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists.",
        )

    # Create user
    user = User(
        name=payload.name,
        email=payload.email.lower(),
        password_hash=hash_password(payload.password),
    )
    db.add(user)
    await db.flush()

    # Create default active spending policy for user (max ₹500, approval required, require approval for unknown)
    policy = SpendingPolicy(
        user_id=user.id,
        max_transaction_paise=50000,
        approval_required=True,
        unknown_merchant_action="require_approval",
        is_active=True,
    )
    db.add(policy)

    # Log registration audit event
    await log_event(
        db,
        action="user_registered",
        actor_type="user",
        user_id=user.id,
        decision_reason="New account registered",
    )

    token = create_access_token(user.id)
    return AuthResponse(user=UserOut.model_validate(user), token=token)


@router.post("/login", response_model=AuthResponse)
async def login(payload: UserLogin, db: AsyncSession = Depends(get_db)):
    """Authenticate existing user and issue JWT."""
    result = await db.execute(select(User).where(User.email == payload.email.lower()))
    user = result.scalar_one_or_none()

    if not user or not verify_password(payload.password, user.password_hash):
        await log_event(
            db,
            action="login_failed",
            actor_type="user",
            decision_reason=f"Failed login attempt for email {payload.email}",
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
        )

    await log_event(
        db,
        action="login_success",
        actor_type="user",
        user_id=user.id,
        decision_reason="Successful user authentication",
    )

    token = create_access_token(user.id)
    return AuthResponse(user=UserOut.model_validate(user), token=token)
