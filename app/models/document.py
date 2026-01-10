"""Document models."""

from datetime import date, datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.enums import DocumentType, VerificationDecision, VerificationStatus


class DocumentUpload(BaseModel):
    """Document upload request."""
    document_type: DocumentType
    issue_date: Optional[date] = None
    expiry_date: Optional[date] = None
    metadata: Optional[dict] = None


class DocumentVerify(BaseModel):
    """Document verification request."""
    verification_result: VerificationDecision
    verification_notes: Optional[str] = Field(None, max_length=500)


class Document(BaseModel):
    """Full document model."""
    id: UUID
    profile_id: UUID
    document_id: str  # Reference to document-service
    document_type: DocumentType
    issue_date: Optional[date] = None
    expiry_date: Optional[date] = None
    verification_status: VerificationStatus = VerificationStatus.UNVERIFIED
    verified_by: Optional[str] = None
    verified_at: Optional[datetime] = None
    verification_notes: Optional[str] = None
    metadata: Optional[dict] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        from_attributes = True


class DocumentResponse(BaseModel):
    """Document API response."""
    id: UUID
    document_id: str
    document_type: DocumentType
    issue_date: Optional[date] = None
    expiry_date: Optional[date] = None
    verification_status: VerificationStatus
    verified_by: Optional[str] = None
    verified_at: Optional[datetime] = None
    uploaded_at: datetime
    download_url: Optional[str] = None  # Pre-signed URL from document-service
