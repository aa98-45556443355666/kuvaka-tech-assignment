"""
Configuration settings for the backend application, loaded from environment variables.
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    """
    Application settings loaded from environment variables using dotenv.
    """
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    REDIS_URL: str = os.getenv("REDIS_URL")
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY")
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24
    STRIPE_API_KEY: str = os.getenv("STRIPE_API_KEY")
    STRIPE_WEBHOOK_SECRET: str = os.getenv("STRIPE_WEBHOOK_SECRET")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY")
    OTP_EXPIRE_MINUTES: int = 10
    BASIC_DAILY_LIMIT: int = 5
    CACHE_TTL_SECONDS: int = 600  

settings = Settings() 