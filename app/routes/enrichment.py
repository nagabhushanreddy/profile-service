"""Enrichment routes."""

from fastapi import APIRouter, HTTPException, Request, status

from app.middleware import extract_user_context
from app.models.common import ResponseMetadata, SuccessResponse
from app.models.enrichment import EnrichmentCreate, EnrichmentResponse, EnrichmentReview
from app.services.enrichment_service import enrichment_service

router = APIRouter(prefix="/api/v1/profiles", tags=["Enrichment"])


@router.post("/{profile_id}/enrichment", response_model=SuccessResponse[EnrichmentResponse], status_code=status.HTTP_201_CREATED)
async def create_enrichment(
    profile_id: str,
    request: Request,
    enrichment_data: EnrichmentCreate
):
    """Create enrichment (Maker)."""
    context = extract_user_context(request)
    if not context["authenticated"]:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    
    # Check if user has enrichment permission
    if context["role"] not in ["risk_officer", "credit_officer"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    
    try:
        enrichment = await enrichment_service.create_enrichment(
            profile_id=profile_id,
            enrichment_data=enrichment_data.model_dump(),
            maker_id=context["user_id"],
            correlation_id=context["correlation_id"]
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    
    response = EnrichmentResponse(
        id=enrichment["id"],
        risk_score=enrichment["risk_score"],
        risk_grade=enrichment["risk_grade"],
        credit_grade=enrichment["credit_grade"],
        background_check_result=enrichment["background_check_result"],
        status=enrichment["status"],
        maker_id=enrichment["maker_id"],
        maker_submitted_at=enrichment["maker_submitted_at"],
        checker_id=enrichment.get("checker_id"),
        checker_reviewed_at=enrichment.get("checker_reviewed_at"),
        checker_decision=enrichment.get("checker_decision")
    )
    
    return SuccessResponse(data=response, metadata=ResponseMetadata(correlation_id=context["correlation_id"]))


@router.post("/{profile_id}/enrichment/{enrichment_id}/review", response_model=SuccessResponse[EnrichmentResponse])
async def review_enrichment(
    profile_id: str,
    enrichment_id: str,
    request: Request,
    review: EnrichmentReview
):
    """Review enrichment (Checker)."""
    context = extract_user_context(request)
    if not context["authenticated"]:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    
    # Check if user has checker permission
    if context["role"] not in ["senior_risk_officer", "senior_credit_officer"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    
    try:
        enrichment = await enrichment_service.review_enrichment(
            enrichment_id=enrichment_id,
            decision=review.decision.value,
            checker_id=context["user_id"],
            checker_notes=review.checker_notes,
            correlation_id=context["correlation_id"]
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    
    response = EnrichmentResponse(
        id=enrichment["id"],
        risk_score=enrichment["risk_score"],
        risk_grade=enrichment["risk_grade"],
        credit_grade=enrichment["credit_grade"],
        background_check_result=enrichment["background_check_result"],
        status=enrichment["status"],
        maker_id=enrichment["maker_id"],
        maker_submitted_at=enrichment["maker_submitted_at"],
        checker_id=enrichment.get("checker_id"),
        checker_reviewed_at=enrichment.get("checker_reviewed_at"),
        checker_decision=enrichment.get("checker_decision")
    )
    
    return SuccessResponse(data=response, metadata=ResponseMetadata(correlation_id=context["correlation_id"]))
