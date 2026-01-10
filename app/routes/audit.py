"""Audit routes."""

from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query, Request, status

from app.middleware import extract_user_context
from app.models.audit import AuditResponse
from app.models.common import ResponseMetadata, SuccessResponse
from app.services.audit_service import audit_service
from app.services.profile_service import profile_service

router = APIRouter(prefix="/api/v1/profiles/me/audit", tags=["Audit"])


@router.get("", response_model=SuccessResponse[List[AuditResponse]])
async def get_audit_trail(
    request: Request,
    action_type: Optional[str] = None,
    limit: int = Query(default=50, le=100),
    offset: int = Query(default=0, ge=0)
):
    """Get audit trail for profile."""
    context = extract_user_context(request)
    if not context["authenticated"]:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    
    profile = await profile_service.get_own_profile(context["user_id"], context["role"])
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    
    entries = await audit_service.get_audit_trail(
        profile_id=profile["id"],
        limit=limit,
        offset=offset,
        action_type=action_type
    )
    
    responses = [
        AuditResponse(
            id=entry["id"],
            action=entry["action"],
            actor_id=entry["actor_id"],
            actor_role=entry.get("actor_role"),
            from_value=entry.get("from_value"),
            to_value=entry.get("to_value"),
            field_name=entry.get("field_name"),
            reason=entry.get("reason"),
            timestamp=entry["timestamp"],
            correlation_id=entry.get("correlation_id")
        )
        for entry in entries
    ]
    
    return SuccessResponse(data=responses, metadata=ResponseMetadata(correlation_id=context["correlation_id"]))
