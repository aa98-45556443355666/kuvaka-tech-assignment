"""
Utility functions for password hashing, OTP generation, JWT handling, and Redis-based usage tracking.
"""
import random
import string
from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
from .config import settings
import redis

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
redis_client = redis.Redis.from_url(settings.REDIS_URL)

def generate_otp(length=6):
    """
    Generate a numeric OTP code of specified length.
    """
    return ''.join(random.choices(string.digits, k=length))

def hash_password(password: str) -> str:
    """
    Hash a plain password using bcrypt.
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed password.
    """
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    """
    Create a JWT access token with an optional expiration delta.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str):
    """
    Decode a JWT access token and return the payload, or None if invalid.
    """
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except Exception:
        return None

def get_daily_usage_key(user_id: int):
    """
    Generate a Redis key for tracking daily usage for a user.
    """
    return f"user:{user_id}:daily_usage:{datetime.utcnow().date()}"

def increment_daily_usage(user_id: int):
    """
    Increment the daily usage count for a user in Redis.
    Sets expiry to 24 hours if first increment of the day.
    """
    key = get_daily_usage_key(user_id)
    count = redis_client.incr(key)
    if count == 1:
        redis_client.expire(key, 86400)
    return count

def get_daily_usage(user_id: int):
    """
    Retrieve the current daily usage count for a user from Redis.
    """
    key = get_daily_usage_key(user_id)
    count = redis_client.get(key)
    return int(count) if count else 0 