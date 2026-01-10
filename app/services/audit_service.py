"""Audit service."""

import logging
from datetime import datetime
from typing import List, Optional

from app.services import storage

logger = logging.getLogger(__name__)


class AuditService:
    """Service for audit trail management."""
    
    async def create_audit_entry(
        self,
        profile_id: str,
        action: str,
        actor_id: str,
        actor_role: Optional[str] = None,
        field_name: Optional[str] = None,
        from_value: Optional[any] = None,
        to_value: Optional[any] = None,
        reason: Optional[str] = None,
        correlation_id: Optional[str] = None
    ) -> dict:
        """Create immutable audit entry."""
        audit_data = {
            "profile_id": profile_id,
            "action": action,
            "actor_id": actor_id,
            "actor_role": actor_role,
            "field_name": field_name,
            "from_value": from_value,
            "to_value": to_value,
            "reason": reason,
            "correlation_id": correlation_id
        }
        
        entry = storage.create_audit_entry(audit_data)
        logger.info(f"Audit entry created: {entry['id']}", extra={"correlation_id": correlation_id})
        
        return entry
    
    async def get_audit_trail(
        self,
        profile_id: str,
        limit: int = 50,
        offset: int = 0,
        action_type: Optional[str] = None
    ) -> List[dict]:
        """Get audit trail for profile."""
        entries = storage.get_audit_entries_by_profile_id(profile_id, limit, offset)
        
        if action_type:
            entries = [e for e in entries if e.get("action") == action_type]
        
        return entries


audit_service = AuditService()
