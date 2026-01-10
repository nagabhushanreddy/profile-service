"""Document Service client for file management."""

import logging
from typing import Any, Dict, Optional
from uuid import UUID

from app.clients.base_client import BaseHTTPClient
from app.config import config

logger = logging.getLogger(__name__)


class DocumentServiceClient(BaseHTTPClient):
    """Client for Document Service integration."""
    
    def __init__(self):
        super().__init__(
            base_url=config.document_service.base_url,
            timeout=config.document_service.timeout,
            retry_attempts=config.document_service.retry_attempts
        )
    
    async def upload_document(
        self,
        file_data: bytes,
        filename: str,
        content_type: str,
        metadata: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Upload document to document-service."""
        try:
            # Note: In real implementation, this would use multipart/form-data
            # For now, we'll simulate the upload
            response = await self.post(
                "/documents/upload",
                json_data={
                    "filename": filename,
                    "content_type": content_type,
                    "metadata": metadata or {}
                },
                correlation_id=correlation_id
            )
            return response
        except Exception as e:
            logger.error(f"Failed to upload document: {str(e)}")
            raise
    
    async def get_document_metadata(
        self,
        document_id: str,
        correlation_id: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Get document metadata from document-service."""
        try:
            response = await self.get(
                f"/documents/{document_id}",
                correlation_id=correlation_id
            )
            return response if not response.get("error") else None
        except Exception as e:
            logger.error(f"Failed to get document metadata: {str(e)}")
            return None
    
    async def get_document_download_url(
        self,
        document_id: str,
        correlation_id: Optional[str] = None
    ) -> Optional[str]:
        """Get pre-signed download URL for document."""
        try:
            response = await self.get(
                f"/documents/{document_id}/download-url",
                correlation_id=correlation_id
            )
            return response.get("url") if not response.get("error") else None
        except Exception as e:
            logger.error(f"Failed to get document download URL: {str(e)}")
            return None
    
    async def delete_document(
        self,
        document_id: str,
        correlation_id: Optional[str] = None
    ) -> bool:
        """Soft delete document in document-service."""
        try:
            response = await self.delete(
                f"/documents/{document_id}",
                correlation_id=correlation_id
            )
            return not response.get("error")
        except Exception as e:
            logger.error(f"Failed to delete document: {str(e)}")
            return False


# Global document service client instance
document_service_client = DocumentServiceClient()
