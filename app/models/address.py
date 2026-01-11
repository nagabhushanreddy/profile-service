"""Address models."""

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.enums import AddressType, VerificationStatus


class AddressBase(BaseModel):
    """Base address model."""
    type: AddressType
    address_line1: str = Field(..., min_length=1, max_length=200)
    address_line2: Optional[str] = Field(None, max_length=200)
    city: str = Field(..., min_length=1, max_length=100)
    state: str = Field(..., min_length=1, max_length=100)
    postal_code: str = Field(..., pattern=r"^\d{5,10}$")
    country: str = Field(default="India", max_length=100)
    is_primary: bool = False


class AddressCreate(AddressBase):
    """Address creation model."""
    pass


class AddressUpdate(BaseModel):
    """Address update model."""
    type: Optional[AddressType] = None
    address_line1: Optional[str] = Field(None, min_length=1, max_length=200)
    address_line2: Optional[str] = Field(None, max_length=200)
    city: Optional[str] = Field(None, min_length=1, max_length=100)
    state: Optional[str] = Field(None, min_length=1, max_length=100)
    postal_code: Optional[str] = Field(None, pattern=r"^\d{5,10}$")
    country: Optional[str] = Field(None, max_length=100)
    is_primary: Optional[bool] = None


class Address(AddressBase):
    """Full address model."""
    id: UUID
    profile_id: UUID
    verification_status: VerificationStatus = VerificationStatus.UNVERIFIED
    verified_at: Optional[datetime] = None
    verified_by: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    deleted_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class AddressResponse(BaseModel):
    """Address API response."""
    id: UUID
    type: AddressType
    address_line1: str
    address_line2: Optional[str] = None
    city: str
    state: str
    postal_code: str
    country: str
    is_primary: bool
    verification_status: VerificationStatus
    verified_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
