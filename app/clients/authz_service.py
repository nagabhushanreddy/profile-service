"""AuthZ Service client for authorization checks."""

import logging
from typing import Any, Dict, List, Optional

from app.clients.base_client import BaseHTTPClient
from app.config import config

logger = logging.getLogger(__name__)


class AuthZServiceClient(BaseHTTPClient):
    """Client for AuthZ Service integration."""
    
    def __init__(self):
        super().__init__(
            base_url=config.authz_service.base_url,
            timeout=config.authz_service.timeout,
            retry_attempts=config.authz_service.retry_attempts
        )
    
    async def check_permission(
        self,
        user_id: str,
        resource_type: str,
        resource_id: str,
        action: str,
        correlation_id: Optional[str] = None
    ) -> bool:
        """Check if user has permission for action on resource."""
        try:
            response = await self.post(
                "/authz/check",
                json_data={
                    "user_id": user_id,
                    "resource_type": resource_type,
                    "resource_id": resource_id,
                    "action": action
                },
                correlation_id=correlation_id
            )
            return response.get("allowed", False)
        except Exception as e:
            logger.error(f"AuthZ check failed: {str(e)}")
            # Fail closed - deny access on error
            return False
    
    async def check_field_access(
        self,
        user_id: str,
        role: str,
        field_name: str,
        correlation_id: Optional[str] = None
    ) -> bool:
        """Check if user/role can access specific field."""
        try:
            response = await self.post(
                "/authz/field-access",
                json_data={
                    "user_id": user_id,
                    "role": role,
                    "field_name": field_name
                },
                correlation_id=correlation_id
            )
            return response.get("allowed", False)
        except Exception as e:
            logger.error(f"Field access check failed: {str(e)}")
            # Fail closed - deny access on error
            return False
    
    async def get_user_permissions(
        self,
        user_id: str,
        correlation_id: Optional[str] = None
    ) -> List[str]:
        """Get all permissions for user."""
        try:
            response = await self.get(
                f"/authz/users/{user_id}/permissions",
                correlation_id=correlation_id
            )
            return response.get("permissions", [])
        except Exception as e:
            logger.error(f"Failed to get user permissions: {str(e)}")
            return []
    
    async def check_ownership(
        self,
        user_id: str,
        resource_owner_id: str,
        correlation_id: Optional[str] = None
    ) -> bool:
        """Check if user owns the resource."""
        # Simple ownership check
        return user_id == resource_owner_id


# Global authz service client instance
authz_service_client = AuthZServiceClient()
