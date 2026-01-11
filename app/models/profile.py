"""Profile models."""

from datetime import date, datetime, timezone
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from app.models.enums import (
    EmploymentStatus,
    Gender,
    KYCStatus,
    MaritalStatus,
    ProfileStatus,
)


class ProfileBase(BaseModel):
    """Base profile model."""
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    full_name: Optional[str] = Field(None, min_length=1, max_length=200)
    date_of_birth: Optional[date] = None
    gender: Optional[Gender] = None
    marital_status: Optional[MaritalStatus] = None
    phone: Optional[str] = Field(None, pattern=r"^\+?[1-9]\d{1,14}$")
    email: Optional[EmailStr] = None
    alternative_phone: Optional[str] = Field(None, pattern=r"^\+?[1-9]\d{1,14}$")
    occupation_type: Optional[str] = Field(None, max_length=100)
    employer_name: Optional[str] = Field(None, max_length=200)
    job_title: Optional[str] = Field(None, max_length=100)
    employment_status: Optional[EmploymentStatus] = None
    annual_income: Optional[float] = Field(None, ge=0)


class ProfileCreate(ProfileBase):
    """Profile creation model."""
    user_id: str
    tenant_id: str


class ProfileUpdate(BaseModel):
    """Profile update model (mutable fields only)."""
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    full_name: Optional[str] = Field(None, min_length=1, max_length=200)
    phone: Optional[str] = Field(None, pattern=r"^\+?[1-9]\d{1,14}$")
    email: Optional[EmailStr] = None
    marital_status: Optional[MaritalStatus] = None
    occupation_type: Optional[str] = Field(None, max_length=100)
    employer_name: Optional[str] = Field(None, max_length=200)
    job_title: Optional[str] = Field(None, max_length=100)


class Profile(ProfileBase):
    """Full profile model."""
    id: UUID
    user_id: str
    tenant_id: str
    status: ProfileStatus = ProfileStatus.ACTIVE
    
    # Identity fields
    pan_id: Optional[str] = Field(None, max_length=10)
    aadhaar_id: Optional[str] = Field(None, max_length=12)
    aadhaar_masked: Optional[str] = Field(None, max_length=12)
    passport_id: Optional[str] = Field(None, max_length=20)
    
    # Financial fields
    salary_account_number: Optional[str] = Field(None, max_length=20)
    salary_account_ifsc: Optional[str] = Field(None, max_length=11)
    bank_name: Optional[str] = Field(None, max_length=100)
    
    # KYC fields
    kyc_status: KYCStatus = KYCStatus.PENDING
    kyc_id: Optional[UUID] = None
    kyc_completed_at: Optional[datetime] = None
    kyc_verified_at: Optional[datetime] = None
    kyc_expiry_at: Optional[datetime] = None
    
    # Verification timestamps
    identity_verified_at: Optional[datetime] = None
    address_verified_at: Optional[datetime] = None
    income_verified_at: Optional[datetime] = None
    document_verified_at: Optional[datetime] = None
    
    # Enrichment fields
    risk_score: Optional[float] = Field(None, ge=0, le=100)
    risk_grade: Optional[str] = None
    credit_grade: Optional[str] = None
    background_check_status: Optional[str] = None
    enriched_at: Optional[datetime] = None
    enriched_by: Optional[str] = None
    
    # Completeness
    completeness_percentage: float = Field(default=0.0, ge=0, le=100)
    
    # Audit fields
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: Optional[str] = None
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_by: Optional[str] = None
    deleted_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ProfileResponse(BaseModel):
    """Profile API response."""
    id: UUID
    user_id: str
    full_name: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[Gender] = None
    marital_status: Optional[MaritalStatus] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    occupation_type: Optional[str] = None
    employer_name: Optional[str] = None
    employment_status: Optional[EmploymentStatus] = None
    kyc_status: KYCStatus
    completeness_percentage: float
    updated_at: datetime
    
    # Optional masked identity fields
    pan_id_masked: Optional[str] = None
    aadhaar_masked: Optional[str] = None


class ProfileCompletenessResponse(BaseModel):
    """Profile completeness response."""
    overall_completeness: float
    field_completeness: dict
    missing_fields: list


class VerificationStatusResponse(BaseModel):
    """Verification status response."""
    identity_verified: bool
    address_verified: bool
    income_verified: bool
    document_verified: bool
    identity_verified_at: Optional[datetime] = None
    address_verified_at: Optional[datetime] = None
    income_verified_at: Optional[datetime] = None
    document_verified_at: Optional[datetime] = None
