"""
Redis-based caching utilities for chatroom data.
"""
from .config import settings
import redis
import json

redis_client = redis.Redis.from_url(settings.REDIS_URL)

def get_chatrooms_cache(user_id: int):
    """
    Retrieve cached chatrooms for a user from Redis, or None if not cached.
    """
    key = f"user:{user_id}:chatrooms"
    data = redis_client.get(key)
    if data:
        return json.loads(data)
    return None

def set_chatrooms_cache(user_id: int, chatrooms):
    """
    Cache chatrooms for a user in Redis with a TTL.
    """
    key = f"user:{user_id}:chatrooms"
    redis_client.setex(key, settings.CACHE_TTL_SECONDS, json.dumps(chatrooms))

def clear_chatrooms_cache(user_id: int):
    """
    Clear the cached chatrooms for a user in Redis.
    """
    key = f"user:{user_id}:chatrooms"
    redis_client.delete(key) 