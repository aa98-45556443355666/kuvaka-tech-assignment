"""
Custom middleware for CORS and rate limiting based on user subscription tier.
"""
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from .utils import get_daily_usage, increment_daily_usage
from .models import Subscription
from .config import settings
from sqlalchemy.orm import Session
from .database import SessionLocal
from jose import jwt

class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware to enforce daily message limits for basic users on chatroom message endpoints.
    """
    async def dispatch(self, request: Request, call_next):
        """
        Intercept chatroom message requests and enforce rate limits for basic users.
        """
        if request.url.path.startswith("/chatroom") and request.method == "POST" and "/message" in request.url.path:
            token = request.headers.get("Authorization", "").replace("Bearer ", "")
            if token:
                try:
                    payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
                    user_id = int(payload["sub"])
                except Exception:
                    return JSONResponse(status_code=401, content={"status": "error", "message": "Invalid token"})
                db: Session = SessionLocal()
                sub = db.query(Subscription).filter(Subscription.user_id == user_id).first()
                if not sub or sub.tier == "basic":
                    count = get_daily_usage(user_id)
                    if count >= settings.BASIC_DAILY_LIMIT:
                        return JSONResponse(status_code=429, content={"status": "error", "message": "Daily message limit reached for Basic tier."})
                    increment_daily_usage(user_id)
                db.close()
        response = await call_next(request)
        return response 