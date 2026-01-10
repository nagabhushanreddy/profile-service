"""KYC models."""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.enums import KYCStatus, KYCType


class CompletedChecks(BaseModel):
    """KYC completed checks."""
    identity_verified: bool = False
    address_verified: bool = False
    income_verified: bool = False
    document_verified: bool = False


class KYCWorkflowBase(BaseModel):
    """Base KYC workflow model."""
    kyc_type: KYCType = KYCType.STANDARD
    status: KYCStatus = KYCStatus.PENDING
    required_documents: List[str] = []
    completed_checks: CompletedChecks = Field(default_factory=CompletedChecks)


class KYCInitiate(BaseModel):
    """KYC initiation request."""
    kyc_type: KYCType = KYCType.STANDARD


class KYCWorkflow(KYCWorkflowBase):
    """Full KYC workflow model."""
    id: UUID
    profile_id: UUID
    identity_verification_date: Optional[datetime] = None
    address_verification_date: Optional[datetime] = None
    income_verification_date: Optional[datetime] = None
    document_verification_date: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    expiry_date: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        from_attributes = True


class KYCStatusResponse(BaseModel):
    """KYC status API response."""
    kyc_id: UUID
    kyc_status: KYCStatus
    kyc_type: KYCType
    completed_checks: CompletedChecks
    identity_verification_date: Optional[datetime] = None
    address_verification_date: Optional[datetime] = None
    income_verification_date: Optional[datetime] = None
    document_verification_date: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    expiry_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class KYCInitiateResponse(BaseModel):
    """KYC initiation response."""
    kyc_id: UUID
    required_documents: List[str]
    status: KYCStatus
