"""Caching utilities for Profile Service."""

import json
import logging
from datetime import timedelta
from typing import Any, Optional

from app.config import config

logger = logging.getLogger(__name__)


class InMemoryCache:
    """Simple in-memory cache implementation."""
    
    def __init__(self):
        self._cache: dict = {}
        self._ttl: dict = {}
    
    async def get(self, key: str) -> Optional[str]:
        """Get value from cache."""
        import time
        if key in self._cache:
            if key in self._ttl and time.time() > self._ttl[key]:
                # Expired
                del self._cache[key]
                del self._ttl[key]
                return None
            return self._cache[key]
        return None
    
    async def set(self, key: str, value: str, ttl: int) -> None:
        """Set value in cache with TTL."""
        import time
        self._cache[key] = value
        self._ttl[key] = time.time() + ttl
    
    async def delete(self, key: str) -> None:
        """Delete key from cache."""
        if key in self._cache:
            del self._cache[key]
        if key in self._ttl:
            del self._ttl[key]
    
    async def clear(self) -> None:
        """Clear all cache."""
        self._cache.clear()
        self._ttl.clear()


class RedisCache:
    """Redis cache implementation."""
    
    def __init__(self):
        try:
            import redis.asyncio as aioredis
            self.redis = aioredis.from_url(config.caching.redis_url)
        except Exception as e:
            logger.warning(f"Failed to connect to Redis: {e}. Falling back to in-memory cache.")
            self.redis = None
    
    async def get(self, key: str) -> Optional[str]:
        """Get value from Redis."""
        if not self.redis:
            return None
        try:
            value = await self.redis.get(key)
            return value.decode() if value else None
        except Exception as e:
            logger.error(f"Redis get error: {e}")
            return None
    
    async def set(self, key: str, value: str, ttl: int) -> None:
        """Set value in Redis with TTL."""
        if not self.redis:
            return
        try:
            await self.redis.setex(key, ttl, value)
        except Exception as e:
            logger.error(f"Redis set error: {e}")
    
    async def delete(self, key: str) -> None:
        """Delete key from Redis."""
        if not self.redis:
            return
        try:
            await self.redis.delete(key)
        except Exception as e:
            logger.error(f"Redis delete error: {e}")
    
    async def clear(self) -> None:
        """Clear all Redis cache (use with caution)."""
        if not self.redis:
            return
        try:
            await self.redis.flushdb()
        except Exception as e:
            logger.error(f"Redis clear error: {e}")


class CacheManager:
    """Cache manager that abstracts cache implementation."""
    
    def __init__(self):
        if config.caching.use_in_memory:
            self.cache = InMemoryCache()
            logger.info("Using in-memory cache")
        else:
            self.cache = RedisCache()
            logger.info("Using Redis cache")
    
    async def get_profile(self, profile_id: str) -> Optional[dict]:
        """Get profile from cache."""
        key = f"profile:{profile_id}"
        data = await self.cache.get(key)
        if data:
            return json.loads(data)
        return None
    
    async def set_profile(self, profile_id: str, profile_data: dict) -> None:
        """Set profile in cache."""
        key = f"profile:{profile_id}"
        await self.cache.set(key, json.dumps(profile_data), config.caching.profile_ttl)
    
    async def delete_profile(self, profile_id: str) -> None:
        """Delete profile from cache."""
        key = f"profile:{profile_id}"
        await self.cache.delete(key)
    
    async def get_addresses(self, profile_id: str) -> Optional[list]:
        """Get addresses from cache."""
        key = f"addresses:{profile_id}"
        data = await self.cache.get(key)
        if data:
            return json.loads(data)
        return None
    
    async def set_addresses(self, profile_id: str, addresses: list) -> None:
        """Set addresses in cache."""
        key = f"addresses:{profile_id}"
        await self.cache.set(key, json.dumps(addresses), config.caching.address_ttl)
    
    async def delete_addresses(self, profile_id: str) -> None:
        """Delete addresses from cache."""
        key = f"addresses:{profile_id}"
        await self.cache.delete(key)
    
    async def get_kyc_status(self, profile_id: str) -> Optional[dict]:
        """Get KYC status from cache."""
        key = f"kyc:{profile_id}"
        data = await self.cache.get(key)
        if data:
            return json.loads(data)
        return None
    
    async def set_kyc_status(self, profile_id: str, kyc_data: dict) -> None:
        """Set KYC status in cache."""
        key = f"kyc:{profile_id}"
        await self.cache.set(key, json.dumps(kyc_data), config.caching.kyc_status_ttl)
    
    async def delete_kyc_status(self, profile_id: str) -> None:
        """Delete KYC status from cache."""
        key = f"kyc:{profile_id}"
        await self.cache.delete(key)


# Global cache instance
cache_manager = CacheManager()
