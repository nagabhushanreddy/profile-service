"""Audit models."""

from datetime import datetime, timezone
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.enums import AuditAction


class AuditEntry(BaseModel):
    """Full audit entry model."""
    id: UUID
    profile_id: UUID
    action: AuditAction
    actor_id: str
    actor_role: Optional[str] = None
    from_value: Optional[Any] = None
    to_value: Optional[Any] = None
    field_name: Optional[str] = None
    reason: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    correlation_id: Optional[str] = None
    
    class Config:
        from_attributes = True


class AuditResponse(BaseModel):
    """Audit entry API response."""
    id: UUID
    action: AuditAction
    actor_id: str
    actor_role: Optional[str] = None
    from_value: Optional[Any] = None
    to_value: Optional[Any] = None
    field_name: Optional[str] = None
    reason: Optional[str] = None
    timestamp: datetime
    correlation_id: Optional[str] = None
