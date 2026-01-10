"""KYC service."""

import logging
from datetime import datetime, timedelta
from typing import Optional

from app.cache import cache_manager
from app.config import config
from app.models.enums import KYCStatus, KYCType
from app.services import storage

logger = logging.getLogger(__name__)


class KYCService:
    """Service for KYC workflow management."""
    
    async def get_kyc_status(self, profile_id: str) -> Optional[dict]:
        """Get KYC status for profile."""
        cached = await cache_manager.get_kyc_status(profile_id)
        if cached:
            return cached
        
        kyc = storage.get_kyc_by_profile_id(profile_id)
        if kyc:
            await cache_manager.set_kyc_status(profile_id, kyc)
        
        return kyc
    
    async def initiate_kyc(
        self,
        profile_id: str,
        kyc_type: KYCType = KYCType.STANDARD,
        user_id: str = None
    ) -> dict:
        """Initiate KYC workflow."""
        # Check if KYC already exists
        existing = storage.get_kyc_by_profile_id(profile_id)
        if existing and existing.get("status") != KYCStatus.REJECTED.value:
            return existing
        
        # Get required documents
        required_docs = config.kyc_requirements.get(kyc_type.value, [])
        
        kyc_data = {
            "profile_id": profile_id,
            "kyc_type": kyc_type.value,
            "status": KYCStatus.IN_PROGRESS.value,
            "required_documents": required_docs,
            "completed_checks": {
                "identity_verified": False,
                "address_verified": False,
                "income_verified": False,
                "document_verified": False
            }
        }
        
        kyc = storage.create_kyc_workflow(kyc_data)
        
        # Update profile KYC status
        storage.update_profile(profile_id, {
            "kyc_id": kyc["id"],
            "kyc_status": KYCStatus.IN_PROGRESS.value
        })
        
        await cache_manager.delete_kyc_status(profile_id)
        
        return kyc
    
    async def update_kyc_check(
        self,
        kyc_id: str,
        check_name: str,
        verified: bool
    ) -> dict:
        """Update a specific KYC check."""
        kyc = storage.kyc_workflows_db.get(kyc_id)
        if not kyc:
            raise ValueError("KYC workflow not found")
        
        completed_checks = kyc.get("completed_checks", {})
        completed_checks[check_name] = verified
        
        if verified:
            kyc[f"{check_name.replace('_verified', '')}_verification_date"] = datetime.utcnow().isoformat()
        
        # Check if all required checks are complete
        all_complete = all(completed_checks.values())
        
        update_data = {
            "completed_checks": completed_checks
        }
        
        if all_complete:
            update_data["status"] = KYCStatus.VERIFIED.value
            update_data["expiry_date"] = (datetime.utcnow() + timedelta(days=config.business.kyc_validity_days)).isoformat()
            
            # Update profile
            storage.update_profile(kyc["profile_id"], {
                "kyc_status": KYCStatus.VERIFIED.value,
                "kyc_verified_at": datetime.utcnow().isoformat(),
                "kyc_expiry_at": update_data["expiry_date"]
            })
        
        updated_kyc = storage.update_kyc_workflow(kyc_id, update_data)
        
        await cache_manager.delete_kyc_status(kyc["profile_id"])
        
        return updated_kyc


kyc_service = KYCService()
