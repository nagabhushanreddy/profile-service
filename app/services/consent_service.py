"""Consent service."""

import logging
from datetime import datetime
from typing import List, Optional

from app.models.enums import ConsentStatus
from app.services import storage

logger = logging.getLogger(__name__)


class ConsentService:
    """Service for consent management."""
    
    async def get_consents(self, profile_id: str) -> List[dict]:
        """Get all consents for profile."""
        return storage.get_consents_by_profile_id(profile_id)
    
    async def accept_consent(
        self,
        profile_id: str,
        consent_type: str,
        decision: str,
        version: str,
        user_id: str
    ) -> dict:
        """Accept or reject consent."""
        # Check if consent already exists
        existing_consents = storage.get_consents_by_profile_id(profile_id)
        existing = next((c for c in existing_consents if c.get("consent_type") == consent_type), None)
        
        if existing:
            # Update existing consent
            update_data = {
                "status": decision,
                "consent_version": version
            }
            if decision == ConsentStatus.ACCEPTED.value:
                update_data["accepted_at"] = datetime.utcnow().isoformat()
            
            consent = storage.update_consent(existing["id"], update_data)
        else:
            # Create new consent
            consent_data = {
                "profile_id": profile_id,
                "consent_type": consent_type,
                "status": decision,
                "consent_version": version
            }
            if decision == ConsentStatus.ACCEPTED.value:
                consent_data["accepted_at"] = datetime.utcnow().isoformat()
            
            consent = storage.create_consent(consent_data)
        
        return consent


consent_service = ConsentService()
