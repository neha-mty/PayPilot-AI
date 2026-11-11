"""Application configuration loaded from environment variables."""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./paypilot.db"

    # JWT
    JWT_SECRET_KEY: str = "change-this-secret-key"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRY_HOURS: int = 24

    # AI
    GEMINI_API_KEY: str = ""

    # Web Search & External Intelligence (Optional API Keys)
    TAVILY_API_KEY: str = ""
    SERPAPI_API_KEY: str = ""
    BRAVE_SEARCH_API_KEY: str = ""

    # Payment
    PAYMENT_PROVIDER: str = "simulated"  # "simulated" or "razorpay"
    RAZORPAY_KEY_ID: str = ""
    RAZORPAY_KEY_SECRET: str = ""
    RAZORPAY_WEBHOOK_SECRET: str = ""
    SIMULATED_WEBHOOK_SECRET: str = "sim-webhook-secret-for-testing"

    # App
    APPROVAL_EXPIRY_MINUTES: int = 15
    DEFAULT_CURRENCY: str = "INR"

    model_config = {"env_file": ".env", "extra": "ignore"}


@lru_cache()
def get_settings() -> Settings:
    return Settings()
