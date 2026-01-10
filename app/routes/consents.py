"""Consent routes."""

from typing import List

from fastapi import APIRouter, HTTPException, Request, status

from app.middleware import extract_user_context
from app.models.common import ResponseMetadata, SuccessResponse
from app.models.consent import ConsentDecision, ConsentResponse
from app.services.consent_service import consent_service
from app.services.profile_service import profile_service

router = APIRouter(prefix="/api/v1/profiles/me/consents", tags=["Consents"])


@router.get("", response_model=SuccessResponse[List[ConsentResponse]])
async def get_consents(request: Request):
    """Get all consents."""
    context = extract_user_context(request)
    if not context["authenticated"]:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    
    profile = await profile_service.get_own_profile(context["user_id"], context["role"])
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    
    consents = await consent_service.get_consents(profile["id"])
    
    responses = [
        ConsentResponse(
            id=c["id"],
            consent_type=c["consent_type"],
            status=c["status"],
            accepted_at=c.get("accepted_at"),
            version=c["consent_version"],
            created_at=c["created_at"]
        )
        for c in consents
    ]
    
    return SuccessResponse(data=responses, metadata=ResponseMetadata(correlation_id=context["correlation_id"]))


@router.post("/{consent_type}", response_model=SuccessResponse[ConsentResponse])
async def accept_consent(
    consent_type: str,
    request: Request,
    decision: ConsentDecision
):
    """Accept or reject consent."""
    context = extract_user_context(request)
    if not context["authenticated"]:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    
    profile = await profile_service.get_own_profile(context["user_id"], context["role"])
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    
    consent = await consent_service.accept_consent(
        profile_id=profile["id"],
        consent_type=consent_type,
        decision=decision.decision.value,
        version=decision.version,
        user_id=context["user_id"]
    )
    
    response = ConsentResponse(
        id=consent["id"],
        consent_type=consent["consent_type"],
        status=consent["status"],
        accepted_at=consent.get("accepted_at"),
        version=consent["consent_version"],
        created_at=consent["created_at"]
    )
    
    return SuccessResponse(data=response, metadata=ResponseMetadata(correlation_id=context["correlation_id"]))
