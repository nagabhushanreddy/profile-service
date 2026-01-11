"""Document service."""

import logging
from datetime import datetime, timezone
from typing import List, Optional

from app.clients import document_service_client
from app.models.enums import VerificationStatus
from app.services import storage
from app.services.audit_service import AuditService

logger = logging.getLogger(__name__)


class DocumentService:
    """Service for document management."""
    
    def __init__(self):
        self.audit_service = AuditService()
    
    async def upload_document(
        self,
        profile_id: str,
        document_type: str,
        file_data: bytes,
        filename: str,
        metadata: Optional[dict] = None,
        user_id: str = None,
        correlation_id: Optional[str] = None
    ) -> dict:
        """Upload document."""
        # Upload to document service (simulated)
        doc_response = {
            "document_id": f"doc_{datetime.now(timezone.utc).timestamp()}",
            "filename": filename,
            "status": "uploaded"
        }
        
        # Store document metadata
        document_data = {
            "profile_id": profile_id,
            "document_id": doc_response["document_id"],
            "document_type": document_type,
            "verification_status": VerificationStatus.PENDING.value,
            "metadata": metadata or {}
        }
        
        if metadata:
            document_data["issue_date"] = metadata.get("issue_date")
            document_data["expiry_date"] = metadata.get("expiry_date")
        
        document = storage.create_document(document_data)
        
        await self.audit_service.create_audit_entry(
            profile_id=profile_id,
            action="create",
            actor_id=user_id,
            field_name="document",
            to_value={"type": document_type, "id": document["id"]},
            correlation_id=correlation_id
        )
        
        return document
    
    async def get_documents(
        self,
        profile_id: str,
        document_type: Optional[str] = None,
        verification_status: Optional[str] = None
    ) -> List[dict]:
        """Get documents for profile."""
        documents = storage.get_documents_by_profile_id(profile_id)
        
        if document_type:
            documents = [d for d in documents if d.get("document_type") == document_type]
        
        if verification_status:
            documents = [d for d in documents if d.get("verification_status") == verification_status]
        
        # Add download URLs (simulated)
        for doc in documents:
            doc["download_url"] = f"https://documents.example.com/{doc['document_id']}"
        
        return documents
    
    async def verify_document(
        self,
        document_id: str,
        verification_result: str,
        verification_notes: Optional[str] = None,
        verified_by: str = None,
        correlation_id: Optional[str] = None
    ) -> dict:
        """Verify document."""
        document = storage.get_document_by_id(document_id)
        if not document:
            raise ValueError("Document not found")
        
        status = VerificationStatus.VERIFIED if verification_result == "approved" else VerificationStatus.REJECTED
        
        update_data = {
            "verification_status": status.value,
            "verified_by": verified_by,
            "verified_at": datetime.now(timezone.utc).isoformat(),
            "verification_notes": verification_notes
        }
        
        updated_doc = storage.update_document(document_id, update_data)
        
        await self.audit_service.create_audit_entry(
            profile_id=document["profile_id"],
            action="verify",
            actor_id=verified_by,
            field_name="document",
            to_value={"id": document_id, "status": status.value},
            correlation_id=correlation_id
        )
        
        return updated_doc


document_service = DocumentService()
