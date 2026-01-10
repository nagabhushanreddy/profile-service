"""Entity Service client for profile metadata persistence."""

import logging
from typing import Any, Dict, Optional
from uuid import UUID

from app.clients.base_client import BaseHTTPClient
from app.config import config

logger = logging.getLogger(__name__)


class EntityServiceClient(BaseHTTPClient):
    """Client for Entity Service integration."""
    
    def __init__(self):
        super().__init__(
            base_url=config.entity_service.base_url,
            timeout=config.entity_service.timeout,
            retry_attempts=config.entity_service.retry_attempts
        )
    
    async def create_profile_entity(
        self,
        profile_data: Dict[str, Any],
        correlation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create profile entity in entity-service."""
        try:
            response = await self.post(
                "/entities/profiles",
                json_data=profile_data,
                correlation_id=correlation_id
            )
            return response
        except Exception as e:
            logger.error(f"Failed to create profile entity: {str(e)}")
            raise
    
    async def get_profile_entity(
        self,
        profile_id: UUID,
        correlation_id: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Get profile entity from entity-service."""
        try:
            response = await self.get(
                f"/entities/profiles/{profile_id}",
                correlation_id=correlation_id
            )
            return response if not response.get("error") else None
        except Exception as e:
            logger.error(f"Failed to get profile entity: {str(e)}")
            return None
    
    async def update_profile_entity(
        self,
        profile_id: UUID,
        update_data: Dict[str, Any],
        correlation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update profile entity in entity-service."""
        try:
            response = await self.patch(
                f"/entities/profiles/{profile_id}",
                json_data=update_data,
                correlation_id=correlation_id
            )
            return response
        except Exception as e:
            logger.error(f"Failed to update profile entity: {str(e)}")
            raise
    
    async def create_address_entity(
        self,
        address_data: Dict[str, Any],
        correlation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create address entity in entity-service."""
        try:
            response = await self.post(
                "/entities/addresses",
                json_data=address_data,
                correlation_id=correlation_id
            )
            return response
        except Exception as e:
            logger.error(f"Failed to create address entity: {str(e)}")
            raise
    
    async def get_addresses_by_profile(
        self,
        profile_id: UUID,
        correlation_id: Optional[str] = None
    ) -> list:
        """Get all addresses for a profile."""
        try:
            response = await self.get(
                f"/entities/profiles/{profile_id}/addresses",
                correlation_id=correlation_id
            )
            return response.get("data", []) if not response.get("error") else []
        except Exception as e:
            logger.error(f"Failed to get addresses: {str(e)}")
            return []


# Global entity service client instance
entity_service_client = EntityServiceClient()
