"""Profile routes."""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Request, status

from app.middleware import extract_user_context
from app.models.common import ResponseMetadata, SuccessResponse
from app.models.profile import (
    ProfileCompletenessResponse,
    ProfileResponse,
    ProfileUpdate,
)
from app.services.profile_service import profile_service

router = APIRouter(prefix="/api/v1/profiles", tags=["Profiles"])


@router.get("/me", response_model=SuccessResponse[ProfileResponse])
async def get_own_profile(request: Request):
    """Get authenticated user's profile."""
    context = extract_user_context(request)
    
    if not context["authenticated"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    profile = await profile_service.get_own_profile(
        user_id=context["user_id"],
        role=context["role"],
        correlation_id=context["correlation_id"]
    )
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    
    # Convert to response model
    profile_response = ProfileResponse(
        id=profile["id"],
        user_id=profile["user_id"],
        full_name=profile.get("full_name"),
        first_name=profile.get("first_name"),
        last_name=profile.get("last_name"),
        date_of_birth=profile.get("date_of_birth"),
        gender=profile.get("gender"),
        marital_status=profile.get("marital_status"),
        phone=profile.get("phone"),
        email=profile.get("email"),
        occupation_type=profile.get("occupation_type"),
        employer_name=profile.get("employer_name"),
        employment_status=profile.get("employment_status"),
        kyc_status=profile.get("kyc_status"),
        completeness_percentage=profile.get("completeness_percentage", 0),
        updated_at=profile.get("updated_at"),
        pan_id_masked=profile.get("pan_id_masked"),
        aadhaar_masked=profile.get("aadhaar_masked")
    )
    
    return SuccessResponse(
        data=profile_response,
        metadata=ResponseMetadata(correlation_id=context["correlation_id"])
    )


@router.patch("/me", response_model=SuccessResponse[ProfileResponse])
async def update_own_profile(
    request: Request,
    profile_update: ProfileUpdate
):
    """Update authenticated user's profile."""
    context = extract_user_context(request)
    
    if not context["authenticated"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    updated_profile = await profile_service.update_own_profile(
        user_id=context["user_id"],
        update_data=profile_update,
        correlation_id=context["correlation_id"]
    )
    
    if not updated_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    
    profile_response = ProfileResponse(
        id=updated_profile["id"],
        user_id=updated_profile["user_id"],
        full_name=updated_profile.get("full_name"),
        first_name=updated_profile.get("first_name"),
        last_name=updated_profile.get("last_name"),
        date_of_birth=updated_profile.get("date_of_birth"),
        gender=updated_profile.get("gender"),
        marital_status=updated_profile.get("marital_status"),
        phone=updated_profile.get("phone"),
        email=updated_profile.get("email"),
        occupation_type=updated_profile.get("occupation_type"),
        employer_name=updated_profile.get("employer_name"),
        employment_status=updated_profile.get("employment_status"),
        kyc_status=updated_profile.get("kyc_status"),
        completeness_percentage=updated_profile.get("completeness_percentage", 0),
        updated_at=updated_profile.get("updated_at")
    )
    
    return SuccessResponse(
        data=profile_response,
        metadata=ResponseMetadata(correlation_id=context["correlation_id"])
    )


@router.get("/{profile_id}", response_model=SuccessResponse[ProfileResponse])
async def get_profile_by_id(
    profile_id: str,
    request: Request
):
    """Get profile by ID (bank-side access)."""
    context = extract_user_context(request)
    
    if not context["authenticated"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    profile = await profile_service.get_profile_by_id(
        profile_id=profile_id,
        user_id=context["user_id"],
        role=context["role"],
        correlation_id=context["correlation_id"]
    )
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found or access denied"
        )
    
    profile_response = ProfileResponse(
        id=profile["id"],
        user_id=profile["user_id"],
        full_name=profile.get("full_name"),
        first_name=profile.get("first_name"),
        last_name=profile.get("last_name"),
        date_of_birth=profile.get("date_of_birth"),
        gender=profile.get("gender"),
        marital_status=profile.get("marital_status"),
        phone=profile.get("phone"),
        email=profile.get("email"),
        occupation_type=profile.get("occupation_type"),
        employer_name=profile.get("employer_name"),
        employment_status=profile.get("employment_status"),
        kyc_status=profile.get("kyc_status"),
        completeness_percentage=profile.get("completeness_percentage", 0),
        updated_at=profile.get("updated_at")
    )
    
    return SuccessResponse(
        data=profile_response,
        metadata=ResponseMetadata(correlation_id=context["correlation_id"])
    )


@router.get("/me/completeness", response_model=SuccessResponse[ProfileCompletenessResponse])
async def get_profile_completeness(request: Request):
    """Get profile completeness details."""
    context = extract_user_context(request)
    
    if not context["authenticated"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    profile = await profile_service.get_own_profile(
        user_id=context["user_id"],
        role=context["role"],
        correlation_id=context["correlation_id"]
    )
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    
    completeness = await profile_service.get_profile_completeness(profile["id"])
    
    return SuccessResponse(
        data=ProfileCompletenessResponse(**completeness),
        metadata=ResponseMetadata(correlation_id=context["correlation_id"])
    )
