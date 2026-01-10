"""Address routes."""

from typing import List, Optional

from fastapi import APIRouter, HTTPException, Request, status

from app.middleware import extract_user_context
from app.models.address import AddressCreate, AddressResponse, AddressUpdate
from app.models.common import ResponseMetadata, SuccessResponse
from app.services.address_service import address_service
from app.services.profile_service import profile_service

router = APIRouter(prefix="/api/v1/profiles/me/addresses", tags=["Addresses"])


@router.get("", response_model=SuccessResponse[List[AddressResponse]])
async def get_addresses(
    request: Request,
    type: Optional[str] = None
):
    """Get user's addresses."""
    context = extract_user_context(request)
    if not context["authenticated"]:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    
    profile = await profile_service.get_own_profile(context["user_id"], context["role"])
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    
    addresses = await address_service.get_addresses(profile["id"], type)
    
    address_responses = [
        AddressResponse(
            id=addr["id"],
            type=addr["type"],
            address_line1=addr["address_line1"],
            address_line2=addr.get("address_line2"),
            city=addr["city"],
            state=addr["state"],
            postal_code=addr["postal_code"],
            country=addr["country"],
            is_primary=addr["is_primary"],
            verification_status=addr["verification_status"],
            verified_at=addr.get("verified_at"),
            created_at=addr["created_at"],
            updated_at=addr["updated_at"]
        )
        for addr in addresses
    ]
    
    return SuccessResponse(data=address_responses, metadata=ResponseMetadata(correlation_id=context["correlation_id"]))


@router.post("", response_model=SuccessResponse[AddressResponse], status_code=status.HTTP_201_CREATED)
async def create_address(
    request: Request,
    address_data: AddressCreate
):
    """Create new address."""
    context = extract_user_context(request)
    if not context["authenticated"]:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    
    profile = await profile_service.get_own_profile(context["user_id"], context["role"])
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    
    try:
        address = await address_service.create_address(
            profile_id=profile["id"],
            address_data=address_data.model_dump(),
            user_id=context["user_id"],
            correlation_id=context["correlation_id"]
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    
    response = AddressResponse(
        id=address["id"],
        type=address["type"],
        address_line1=address["address_line1"],
        address_line2=address.get("address_line2"),
        city=address["city"],
        state=address["state"],
        postal_code=address["postal_code"],
        country=address["country"],
        is_primary=address["is_primary"],
        verification_status=address["verification_status"],
        verified_at=address.get("verified_at"),
        created_at=address["created_at"],
        updated_at=address["updated_at"]
    )
    
    return SuccessResponse(data=response, metadata=ResponseMetadata(correlation_id=context["correlation_id"]))


@router.patch("/{address_id}", response_model=SuccessResponse[AddressResponse])
async def update_address(
    address_id: str,
    request: Request,
    address_update: AddressUpdate
):
    """Update address."""
    context = extract_user_context(request)
    if not context["authenticated"]:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    
    address = await address_service.update_address(
        address_id=address_id,
        update_data=address_update.model_dump(exclude_unset=True),
        user_id=context["user_id"],
        correlation_id=context["correlation_id"]
    )
    
    if not address:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    
    response = AddressResponse(
        id=address["id"],
        type=address["type"],
        address_line1=address["address_line1"],
        address_line2=address.get("address_line2"),
        city=address["city"],
        state=address["state"],
        postal_code=address["postal_code"],
        country=address["country"],
        is_primary=address["is_primary"],
        verification_status=address["verification_status"],
        verified_at=address.get("verified_at"),
        created_at=address["created_at"],
        updated_at=address["updated_at"]
    )
    
    return SuccessResponse(data=response, metadata=ResponseMetadata(correlation_id=context["correlation_id"]))


@router.delete("/{address_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_address(
    address_id: str,
    request: Request
):
    """Delete address."""
    context = extract_user_context(request)
    if not context["authenticated"]:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    
    success = await address_service.delete_address(
        address_id=address_id,
        user_id=context["user_id"],
        correlation_id=context["correlation_id"]
    )
    
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
