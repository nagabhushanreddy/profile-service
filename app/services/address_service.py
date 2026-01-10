"""Address service."""

import logging
from typing import List, Optional

from app.cache import cache_manager
from app.models.enums import VerificationStatus
from app.services import storage
from app.services.audit_service import AuditService

logger = logging.getLogger(__name__)


class AddressService:
    """Service for address management."""
    
    def __init__(self):
        self.audit_service = AuditService()
    
    async def get_addresses(self, profile_id: str, address_type: Optional[str] = None) -> List[dict]:
        """Get addresses for profile."""
        cached = await cache_manager.get_addresses(profile_id)
        if cached:
            addresses = cached
        else:
            addresses = storage.get_addresses_by_profile_id(profile_id)
            await cache_manager.set_addresses(profile_id, addresses)
        
        if address_type:
            addresses = [a for a in addresses if a.get("type") == address_type]
        
        return [a for a in addresses if not a.get("deleted_at")]
    
    async def create_address(
        self,
        profile_id: str,
        address_data: dict,
        user_id: str,
        correlation_id: Optional[str] = None
    ) -> dict:
        """Create new address."""
        # Check address limit
        existing = await self.get_addresses(profile_id)
        if len(existing) >= 10:
            raise ValueError("Maximum 10 addresses per profile")
        
        # If new address is primary, unset others
        if address_data.get("is_primary"):
            for addr in existing:
                if addr.get("is_primary"):
                    storage.update_address(addr["id"], {"is_primary": False})
        
        address_data["profile_id"] = profile_id
        address_data["verification_status"] = VerificationStatus.UNVERIFIED.value
        
        address = storage.create_address(address_data)
        
        # Invalidate cache
        await cache_manager.delete_addresses(profile_id)
        
        await self.audit_service.create_audit_entry(
            profile_id=profile_id,
            action="create",
            actor_id=user_id,
            field_name="address",
            to_value=address,
            correlation_id=correlation_id
        )
        
        return address
    
    async def update_address(
        self,
        address_id: str,
        update_data: dict,
        user_id: str,
        correlation_id: Optional[str] = None
    ) -> Optional[dict]:
        """Update address."""
        address = storage.get_address_by_id(address_id)
        if not address:
            return None
        
        # If already verified, mark as unverified after update
        if address.get("verification_status") == VerificationStatus.VERIFIED.value:
            update_data["verification_status"] = VerificationStatus.UNVERIFIED.value
        
        updated = storage.update_address(address_id, update_data)
        
        await cache_manager.delete_addresses(address["profile_id"])
        
        return updated
    
    async def delete_address(
        self,
        address_id: str,
        user_id: str,
        correlation_id: Optional[str] = None
    ) -> bool:
        """Soft delete address."""
        address = storage.get_address_by_id(address_id)
        if not address:
            return False
        
        success = storage.delete_address(address_id)
        
        if success:
            await cache_manager.delete_addresses(address["profile_id"])
            await self.audit_service.create_audit_entry(
                profile_id=address["profile_id"],
                action="delete",
                actor_id=user_id,
                field_name="address",
                from_value=address,
                correlation_id=correlation_id
            )
        
        return success


address_service = AddressService()
