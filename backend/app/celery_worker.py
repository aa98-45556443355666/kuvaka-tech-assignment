"""
Celery worker configuration for background Gemini tasks using Redis as broker and backend.
"""
from celery import Celery
from .config import settings

celery_app = Celery(
    "gemini_tasks",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
) 