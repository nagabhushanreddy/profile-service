"""KYC routes."""

from fastapi import APIRouter, HTTPException, Request, status

from app.middleware import extract_user_context
from app.models.common import ResponseMetadata, SuccessResponse
from app.models.kyc import KYCInitiate, KYCInitiateResponse, KYCStatusResponse
from app.services.kyc_service import kyc_service
from app.services.profile_service import profile_service

router = APIRouter(prefix="/api/v1/profiles/me/kyc", tags=["KYC"])


@router.get("", response_model=SuccessResponse[KYCStatusResponse])
async def get_kyc_status(request: Request):
    """Get KYC status."""
    context = extract_user_context(request)
    if not context["authenticated"]:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    
    profile = await profile_service.get_own_profile(context["user_id"], context["role"])
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    
    kyc = await kyc_service.get_kyc_status(profile["id"])
    
    if not kyc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="KYC not initiated")
    
    response = KYCStatusResponse(
        kyc_id=kyc["id"],
        kyc_status=kyc["status"],
        kyc_type=kyc["kyc_type"],
        completed_checks=kyc["completed_checks"],
        identity_verification_date=kyc.get("identity_verification_date"),
        address_verification_date=kyc.get("address_verification_date"),
        income_verification_date=kyc.get("income_verification_date"),
        document_verification_date=kyc.get("document_verification_date"),
        rejection_reason=kyc.get("rejection_reason"),
        expiry_date=kyc.get("expiry_date"),
        created_at=kyc["created_at"],
        updated_at=kyc["updated_at"]
    )
    
    return SuccessResponse(data=response, metadata=ResponseMetadata(correlation_id=context["correlation_id"]))


@router.post("/initiate", response_model=SuccessResponse[KYCInitiateResponse], status_code=status.HTTP_201_CREATED)
async def initiate_kyc(
    request: Request,
    kyc_initiate: KYCInitiate
):
    """Initiate KYC workflow."""
    context = extract_user_context(request)
    if not context["authenticated"]:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    
    profile = await profile_service.get_own_profile(context["user_id"], context["role"])
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    
    kyc = await kyc_service.initiate_kyc(
        profile_id=profile["id"],
        kyc_type=kyc_initiate.kyc_type,
        user_id=context["user_id"]
    )
    
    response = KYCInitiateResponse(
        kyc_id=kyc["id"],
        required_documents=kyc["required_documents"],
        status=kyc["status"]
    )
    
    return SuccessResponse(data=response, metadata=ResponseMetadata(correlation_id=context["correlation_id"]))
