"""
Application configuration and settings
"""
import os
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""

    # App
    APP_NAME: str = "BiliNote SaaS"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"

    # Server
    BACKEND_HOST: str = os.getenv("BACKEND_HOST", "0.0.0.0")
    BACKEND_PORT: int = int(os.getenv("BACKEND_PORT", "8483"))

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./bili_note.db")

    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 30  # 30 days

    # CORS
    CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:3015",
        "http://localhost:5173",
        "https://bilinote.app",
        "https://www.bilinote.app",
    ]

    # Email (for verification)
    SMTP_HOST: Optional[str] = os.getenv("SMTP_HOST")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER: Optional[str] = os.getenv("SMTP_USER")
    SMTP_PASSWORD: Optional[str] = os.getenv("SMTP_PASSWORD")
    EMAILS_FROM_EMAIL: Optional[str] = os.getenv("EMAILS_FROM_EMAIL", "noreply@bilinote.app")
    EMAILS_FROM_NAME: str = "BiliNote"

    # Stripe
    STRIPE_API_KEY: Optional[str] = os.getenv("STRIPE_API_KEY")
    STRIPE_WEBHOOK_SECRET: Optional[str] = os.getenv("STRIPE_WEBHOOK_SECRET")
    STRIPE_PRICE_FREE: str = ""  # No price ID for free
    STRIPE_PRICE_BASIC_MONTHLY: Optional[str] = os.getenv("STRIPE_PRICE_BASIC_MONTHLY")
    STRIPE_PRICE_BASIC_YEARLY: Optional[str] = os.getenv("STRIPE_PRICE_BASIC_YEARLY")
    STRIPE_PRICE_PRO_MONTHLY: Optional[str] = os.getenv("STRIPE_PRICE_PRO_MONTHLY")
    STRIPE_PRICE_PRO_YEARLY: Optional[str] = os.getenv("STRIPE_PRICE_PRO_YEARLY")
    STRIPE_PRICE_ENTERPRISE_MONTHLY: Optional[str] = os.getenv("STRIPE_PRICE_ENTERPRISE_MONTHLY")
    STRIPE_PRICE_ENTERPRISE_YEARLY: Optional[str] = os.getenv("STRIPE_PRICE_ENTERPRISE_YEARLY")

    # Frontend URL
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000")

    # OAuth
    GOOGLE_CLIENT_ID: Optional[str] = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET: Optional[str] = os.getenv("GOOGLE_CLIENT_SECRET")
    GITHUB_CLIENT_ID: Optional[str] = os.getenv("GITHUB_CLIENT_ID")
    GITHUB_CLIENT_SECRET: Optional[str] = os.getenv("GITHUB_CLIENT_SECRET")

    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()
