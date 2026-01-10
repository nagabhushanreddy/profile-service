"""External service clients."""

from app.clients.entity_service import EntityServiceClient, entity_service_client
from app.clients.document_service import DocumentServiceClient, document_service_client
from app.clients.authz_service import AuthZServiceClient, authz_service_client

__all__ = [
    "EntityServiceClient",
    "DocumentServiceClient",
    "AuthZServiceClient",
    "entity_service_client",
    "document_service_client",
    "authz_service_client",
]
