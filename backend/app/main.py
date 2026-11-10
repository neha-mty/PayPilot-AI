"""PayPilot AI — FastAPI Application Entry Point.

A secure, policy-driven payment authorization platform for AI agents.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base
from app.seed import seed_database
from app.routes.auth import router as auth_router
from app.routes.budget import router as budget_router
from app.routes.policy import router as policy_router
from app.routes.merchant import router as merchant_router
from app.routes.payment_request import router as payment_request_router
from app.routes.payment import router as payment_router
from app.routes.transaction import router as transaction_router
from app.routes.audit_log import router as audit_log_router
from app.routes.assistant import router as assistant_router
from app.routes.dashboard import router as dashboard_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create database tables and seed demo catalog on startup."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await seed_database()
    yield


app = FastAPI(
    title="PayPilot AI",
    description="Secure, policy-driven payment authorization platform for AI agents.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — allow frontend (Vite dev server)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth_router)
app.include_router(budget_router)
app.include_router(policy_router)
app.include_router(merchant_router)
app.include_router(payment_request_router)
app.include_router(payment_router)
app.include_router(transaction_router)
app.include_router(audit_log_router)
app.include_router(assistant_router)
app.include_router(dashboard_router)


@app.get("/health")
async def health_check():
    """Health check endpoint to verify backend operational readiness."""
    return {"status": "healthy", "service": "PayPilot AI", "version": "1.0.0"}
