"""Profile service for business logic."""

import logging
from datetime import datetime
from typing import Optional
from uuid import UUID

from app.cache import cache_manager
from app.clients import authz_service_client
from app.config import config
from app.models.enums import KYCStatus, ProfileStatus
from app.models.profile import ProfileCreate, ProfileUpdate
from app.services import storage
from app.services.audit_service import AuditService

logger = logging.getLogger(__name__)


class ProfileService:
    """Service for profile management."""
    
    def __init__(self):
        self.audit_service = AuditService()
    
    async def get_profile_by_id(
        self,
        profile_id: str,
        user_id: str,
        role: str,
        correlation_id: Optional[str] = None
    ) -> Optional[dict]:
        """Get profile by ID with authorization check."""
        # Check cache first
        cached = await cache_manager.get_profile(profile_id)
        if cached:
            logger.info(f"Profile {profile_id} retrieved from cache")
            return await self._apply_pii_masking(cached, role)
        
        # Get from storage
        profile = storage.get_profile_by_id(profile_id)
        if not profile:
            return None
        
        # Check authorization
        is_owner = await authz_service_client.check_ownership(
            user_id,
            profile.get("user_id"),
            correlation_id
        )
        
        if not is_owner:
            # Check if user has permission to view this profile
            has_permission = await authz_service_client.check_permission(
                user_id,
                "profile",
                profile_id,
                "read",
                correlation_id
            )
            if not has_permission:
                logger.warning(f"User {user_id} unauthorized to view profile {profile_id}")
                return None
        
        # Cache the profile
        await cache_manager.set_profile(profile_id, profile)
        
        # Apply PII masking
        return await self._apply_pii_masking(profile, role)
    
    async def get_own_profile(
        self,
        user_id: str,
        role: str,
        correlation_id: Optional[str] = None
    ) -> Optional[dict]:
        """Get user's own profile."""
        profile = storage.get_profile_by_user_id(user_id)
        if not profile:
            return None
        
        return await self._apply_pii_masking(profile, role)
    
    async def create_profile(
        self,
        profile_data: ProfileCreate,
        created_by: str,
        correlation_id: Optional[str] = None
    ) -> dict:
        """Create new profile."""
        # Prepare profile data
        data = profile_data.model_dump()
        data["status"] = ProfileStatus.ACTIVE.value
        data["kyc_status"] = KYCStatus.PENDING.value
        data["completeness_percentage"] = 0.0
        data["created_by"] = created_by
        data["updated_by"] = created_by
        
        # Create in storage
        profile = storage.create_profile(data)
        
        # Create audit entry
        await self.audit_service.create_audit_entry(
            profile_id=profile["id"],
            action="create",
            actor_id=created_by,
            actor_role="system",
            correlation_id=correlation_id
        )
        
        # Calculate completeness
        await self._update_completeness(profile["id"])
        
        return profile
    
    async def update_own_profile(
        self,
        user_id: str,
        update_data: ProfileUpdate,
        correlation_id: Optional[str] = None
    ) -> Optional[dict]:
        """Update user's own profile (mutable fields only)."""
        # Get existing profile
        profile = storage.get_profile_by_user_id(user_id)
        if not profile:
            return None
        
        profile_id = profile["id"]
        
        # Store old values for audit
        old_values = {k: profile.get(k) for k in update_data.model_dump(exclude_unset=True).keys()}
        
        # Update profile
        update_dict = update_data.model_dump(exclude_unset=True)
        update_dict["updated_by"] = user_id
        
        updated_profile = storage.update_profile(profile_id, update_dict)
        
        # Create audit entries for each changed field
        for field, new_value in update_dict.items():
            if field != "updated_by" and old_values.get(field) != new_value:
                await self.audit_service.create_audit_entry(
                    profile_id=profile_id,
                    action="update",
                    actor_id=user_id,
                    actor_role="customer",
                    field_name=field,
                    from_value=old_values.get(field),
                    to_value=new_value,
                    correlation_id=correlation_id
                )
        
        # Invalidate cache
        await cache_manager.delete_profile(profile_id)
        
        # Update completeness
        await self._update_completeness(profile_id)
        
        return updated_profile
    
    async def _apply_pii_masking(self, profile: dict, role: str) -> dict:
        """Apply PII masking based on role."""
        masked = profile.copy()
        
        # Customer sees all own data, bank officers see all if authorized
        if role in ["customer", "risk_officer", "credit_officer", "loan_officer"]:
            # Show last 4 digits of Aadhaar
            if masked.get("aadhaar_id"):
                masked["aadhaar_masked"] = "XXXX-XXXX-" + masked["aadhaar_id"][-4:]
                masked.pop("aadhaar_id", None)
            
            # Partially mask PAN
            if masked.get("pan_id"):
                masked["pan_id_masked"] = masked["pan_id"][:3] + "XXXX" + masked["pan_id"][-1:]
                if role == "customer":
                    masked.pop("pan_id", None)
        else:
            # Other roles: full masking
            masked.pop("aadhaar_id", None)
            masked.pop("pan_id", None)
            masked.pop("salary_account_number", None)
        
        return masked
    
    async def _update_completeness(self, profile_id: str) -> float:
        """Calculate and update profile completeness."""
        profile = storage.get_profile_by_id(profile_id)
        if not profile:
            return 0.0
        
        weights = config.profile_completeness_weights
        
        # Personal info (50%)
        personal_score = 0
        personal_fields = ["first_name", "last_name", "date_of_birth", "gender", "phone", "email"]
        filled_personal = sum(1 for f in personal_fields if profile.get(f))
        personal_score = (filled_personal / len(personal_fields)) * weights["personal_info"]
        
        # Address info (20%) - check if has verified address
        addresses = storage.get_addresses_by_profile_id(profile_id)
        address_score = weights["address_info"] if any(a.get("verification_status") == "verified" for a in addresses) else 0
        
        # KYC info (20%)
        kyc_score = weights["kyc_info"] if profile.get("kyc_status") == KYCStatus.VERIFIED.value else 0
        
        # Documents (10%)
        documents = storage.get_documents_by_profile_id(profile_id)
        doc_score = weights["documents_info"] if len(documents) >= 3 else 0
        
        completeness = personal_score + address_score + kyc_score + doc_score
        
        # Update profile
        storage.update_profile(profile_id, {"completeness_percentage": completeness})
        
        return completeness
    
    async def get_profile_completeness(self, profile_id: str) -> dict:
        """Get detailed profile completeness."""
        await self._update_completeness(profile_id)
        profile = storage.get_profile_by_id(profile_id)
        
        missing_fields = []
        if not profile.get("first_name"):
            missing_fields.append("first_name")
        if not profile.get("date_of_birth"):
            missing_fields.append("date_of_birth")
        if not profile.get("pan_id"):
            missing_fields.append("pan_id")
        
        addresses = storage.get_addresses_by_profile_id(profile_id)
        if not any(a.get("verification_status") == "verified" for a in addresses):
            missing_fields.append("verified_address")
        
        return {
            "overall_completeness": profile.get("completeness_percentage", 0),
            "field_completeness": {
                "personal_info": 70.0,  # Simplified
                "address_info": 50.0,
                "kyc_info": 30.0,
                "documents_info": 40.0
            },
            "missing_fields": missing_fields
        }


# Global profile service instance
profile_service = ProfileService()
