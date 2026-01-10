"""Reference data routes."""

from fastapi import APIRouter

from app.models.common import ResponseMetadata, SuccessResponse
from app.models.enums import AddressType, ConsentType, DocumentType, KYCStatus

router = APIRouter(prefix="/api/v1/reference", tags=["Reference"])


@router.get("/profile-statuses", response_model=SuccessResponse[dict])
async def get_profile_statuses():
    """Get profile status enum values."""
    return SuccessResponse(
        data={
            "statuses": ["active", "inactive", "suspended", "deleted"]
        },
        metadata=ResponseMetadata()
    )


@router.get("/kyc-statuses", response_model=SuccessResponse[dict])
async def get_kyc_statuses():
    """Get KYC status enum values."""
    return SuccessResponse(
        data={
            "statuses": [status.value for status in KYCStatus]
        },
        metadata=ResponseMetadata()
    )


@router.get("/address-types", response_model=SuccessResponse[dict])
async def get_address_types():
    """Get address type enum values."""
    return SuccessResponse(
        data={
            "types": [addr_type.value for addr_type in AddressType]
        },
        metadata=ResponseMetadata()
    )


@router.get("/document-types", response_model=SuccessResponse[dict])
async def get_document_types():
    """Get document type enum values."""
    return SuccessResponse(
        data={
            "types": [doc_type.value for doc_type in DocumentType]
        },
        metadata=ResponseMetadata()
    )


@router.get("/consent-types", response_model=SuccessResponse[dict])
async def get_consent_types():
    """Get consent type enum values."""
    return SuccessResponse(
        data={
            "types": [consent_type.value for consent_type in ConsentType]
        },
        metadata=ResponseMetadata()
    )
