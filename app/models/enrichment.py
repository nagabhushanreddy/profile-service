"""Enrichment models."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.enums import (
    BackgroundCheckResult,
    CheckerDecision,
    CreditGrade,
    EnrichmentStatus,
    RiskGrade,
)


class EnrichmentCreate(BaseModel):
    """Enrichment creation request (Maker)."""
    risk_score: float = Field(..., ge=0, le=100)
    risk_grade: RiskGrade
    credit_grade: CreditGrade
    background_check_result: BackgroundCheckResult
    verification_notes: Optional[str] = Field(None, max_length=1000)


class EnrichmentReview(BaseModel):
    """Enrichment review request (Checker)."""
    decision: CheckerDecision
    checker_notes: Optional[str] = Field(None, max_length=1000)


class Enrichment(BaseModel):
    """Full enrichment model."""
    id: UUID
    profile_id: UUID
    risk_score: float
    risk_grade: RiskGrade
    credit_grade: CreditGrade
    background_check_result: BackgroundCheckResult
    
    # Maker details
    maker_id: str
    maker_notes: Optional[str] = None
    maker_submitted_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Checker details
    checker_id: Optional[str] = None
    checker_notes: Optional[str] = None
    checker_decision: Optional[CheckerDecision] = None
    checker_reviewed_at: Optional[datetime] = None
    
    # Status
    status: EnrichmentStatus = EnrichmentStatus.PENDING_REVIEW
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        from_attributes = True


class EnrichmentResponse(BaseModel):
    """Enrichment API response."""
    id: UUID
    risk_score: float
    risk_grade: RiskGrade
    credit_grade: CreditGrade
    background_check_result: BackgroundCheckResult
    status: EnrichmentStatus
    maker_id: str
    maker_submitted_at: datetime
    checker_id: Optional[str] = None
    checker_reviewed_at: Optional[datetime] = None
    checker_decision: Optional[CheckerDecision] = None
