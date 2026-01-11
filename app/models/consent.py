"""Consent models."""

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.enums import ConsentStatus, ConsentType


class ConsentDecision(BaseModel):
    """Consent decision request."""
    decision: ConsentStatus
    version: str = Field(..., max_length=20)


class Consent(BaseModel):
    """Full consent model."""
    id: UUID
    profile_id: UUID
    consent_type: ConsentType
    status: ConsentStatus = ConsentStatus.PENDING
    accepted_at: Optional[datetime] = None
    consent_version: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    class Config:
        from_attributes = True


class ConsentResponse(BaseModel):
    """Consent API response."""
    id: UUID
    consent_type: ConsentType
    status: ConsentStatus
    accepted_at: Optional[datetime] = None
    version: str
    created_at: datetime
