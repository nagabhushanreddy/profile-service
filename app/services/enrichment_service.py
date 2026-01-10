"""Enrichment service with maker-checker workflow."""

import logging
from datetime import datetime
from typing import List, Optional

from app.models.enums import EnrichmentStatus
from app.services import storage
from app.services.audit_service import AuditService

logger = logging.getLogger(__name__)


class EnrichmentService:
    """Service for profile enrichment with maker-checker."""
    
    def __init__(self):
        self.audit_service = AuditService()
    
    async def create_enrichment(
        self,
        profile_id: str,
        enrichment_data: dict,
        maker_id: str,
        correlation_id: Optional[str] = None
    ) -> dict:
        """Create enrichment (Maker submission)."""
        data = {
            "profile_id": profile_id,
            "risk_score": enrichment_data["risk_score"],
            "risk_grade": enrichment_data["risk_grade"],
            "credit_grade": enrichment_data["credit_grade"],
            "background_check_result": enrichment_data["background_check_result"],
            "maker_id": maker_id,
            "maker_notes": enrichment_data.get("verification_notes"),
            "maker_submitted_at": datetime.utcnow().isoformat(),
            "status": EnrichmentStatus.PENDING_REVIEW.value
        }
        
        enrichment = storage.create_enrichment(data)
        
        await self.audit_service.create_audit_entry(
            profile_id=profile_id,
            action="enrich",
            actor_id=maker_id,
            actor_role="maker",
            to_value=enrichment,
            correlation_id=correlation_id
        )
        
        return enrichment
    
    async def review_enrichment(
        self,
        enrichment_id: str,
        decision: str,
        checker_id: str,
        checker_notes: Optional[str] = None,
        correlation_id: Optional[str] = None
    ) -> dict:
        """Review enrichment (Checker decision)."""
        enrichment = storage.get_enrichment_by_id(enrichment_id)
        if not enrichment:
            raise ValueError("Enrichment not found")
        
        # Validate: checker cannot be same as maker
        if enrichment["maker_id"] == checker_id:
            raise ValueError("Checker cannot be the same as maker")
        
        status = EnrichmentStatus.APPROVED if decision == "approve" else EnrichmentStatus.REJECTED
        
        update_data = {
            "checker_id": checker_id,
            "checker_notes": checker_notes,
            "checker_decision": decision,
            "checker_reviewed_at": datetime.utcnow().isoformat(),
            "status": status.value
        }
        
        updated = storage.update_enrichment(enrichment_id, update_data)
        
        # If approved, update profile
        if status == EnrichmentStatus.APPROVED:
            storage.update_profile(enrichment["profile_id"], {
                "risk_score": enrichment["risk_score"],
                "risk_grade": enrichment["risk_grade"],
                "credit_grade": enrichment["credit_grade"],
                "background_check_status": enrichment["background_check_result"],
                "enriched_at": datetime.utcnow().isoformat(),
                "enriched_by": enrichment["maker_id"]
            })
        
        await self.audit_service.create_audit_entry(
            profile_id=enrichment["profile_id"],
            action="enrich",
            actor_id=checker_id,
            actor_role="checker",
            to_value={"decision": decision, "enrichment_id": enrichment_id},
            correlation_id=correlation_id
        )
        
        return updated
    
    async def get_enrichments(self, profile_id: str) -> List[dict]:
        """Get all enrichments for profile."""
        return storage.get_enrichments_by_profile_id(profile_id)


enrichment_service = EnrichmentService()
