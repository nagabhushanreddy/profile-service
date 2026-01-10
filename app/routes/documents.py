"""Document routes."""

from typing import List, Optional

from fastapi import APIRouter, HTTPException, Request, status

from app.middleware import extract_user_context
from app.models.common import ResponseMetadata, SuccessResponse
from app.models.document import DocumentResponse, DocumentUpload, DocumentVerify
from app.services.document_service import document_service
from app.services.profile_service import profile_service

router = APIRouter(prefix="/api/v1/profiles/me/documents", tags=["Documents"])


@router.post("", response_model=SuccessResponse[DocumentResponse], status_code=status.HTTP_201_CREATED)
async def upload_document(
    request: Request,
    document_upload: DocumentUpload
):
    """Upload document."""
    context = extract_user_context(request)
    if not context["authenticated"]:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    
    profile = await profile_service.get_own_profile(context["user_id"], context["role"])
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    
    # Simulate file upload
    document = await document_service.upload_document(
        profile_id=profile["id"],
        document_type=document_upload.document_type.value,
        file_data=b"",  # In real implementation, would handle file upload
        filename="document.pdf",
        metadata=document_upload.model_dump(exclude={"document_type"}),
        user_id=context["user_id"],
        correlation_id=context["correlation_id"]
    )
    
    response = DocumentResponse(
        id=document["id"],
        document_id=document["document_id"],
        document_type=document["document_type"],
        issue_date=document.get("issue_date"),
        expiry_date=document.get("expiry_date"),
        verification_status=document["verification_status"],
        verified_by=document.get("verified_by"),
        verified_at=document.get("verified_at"),
        uploaded_at=document["created_at"]
    )
    
    return SuccessResponse(data=response, metadata=ResponseMetadata(correlation_id=context["correlation_id"]))


@router.get("", response_model=SuccessResponse[List[DocumentResponse]])
async def get_documents(
    request: Request,
    document_type: Optional[str] = None,
    verification_status: Optional[str] = None
):
    """Get documents."""
    context = extract_user_context(request)
    if not context["authenticated"]:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    
    profile = await profile_service.get_own_profile(context["user_id"], context["role"])
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    
    documents = await document_service.get_documents(
        profile_id=profile["id"],
        document_type=document_type,
        verification_status=verification_status
    )
    
    responses = [
        DocumentResponse(
            id=doc["id"],
            document_id=doc["document_id"],
            document_type=doc["document_type"],
            issue_date=doc.get("issue_date"),
            expiry_date=doc.get("expiry_date"),
            verification_status=doc["verification_status"],
            verified_by=doc.get("verified_by"),
            verified_at=doc.get("verified_at"),
            uploaded_at=doc["created_at"],
            download_url=doc.get("download_url")
        )
        for doc in documents
    ]
    
    return SuccessResponse(data=responses, metadata=ResponseMetadata(correlation_id=context["correlation_id"]))


@router.post("/{profile_id}/documents/{document_id}/verify", response_model=SuccessResponse[DocumentResponse])
async def verify_document(
    profile_id: str,
    document_id: str,
    request: Request,
    verification: DocumentVerify
):
    """Verify document (bank-side)."""
    context = extract_user_context(request)
    if not context["authenticated"]:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    
    # Check if user has verification permission (simplified)
    if context["role"] not in ["risk_officer", "credit_officer"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    
    document = await document_service.verify_document(
        document_id=document_id,
        verification_result=verification.verification_result.value,
        verification_notes=verification.verification_notes,
        verified_by=context["user_id"],
        correlation_id=context["correlation_id"]
    )
    
    response = DocumentResponse(
        id=document["id"],
        document_id=document["document_id"],
        document_type=document["document_type"],
        verification_status=document["verification_status"],
        verified_by=document.get("verified_by"),
        verified_at=document.get("verified_at"),
        uploaded_at=document["created_at"]
    )
    
    return SuccessResponse(data=response, metadata=ResponseMetadata(correlation_id=context["correlation_id"]))
