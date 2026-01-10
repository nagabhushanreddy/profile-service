"""Common response models."""

from datetime import datetime
from typing import Any, Generic, Optional, TypeVar

from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    """Error detail model."""
    code: str
    message: str
    details: Optional[Any] = None


class ResponseMetadata(BaseModel):
    """Response metadata."""
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    correlation_id: Optional[str] = None


class ErrorResponse(BaseModel):
    """Error response model."""
    success: bool = False
    error: ErrorDetail
    data: None = None
    metadata: ResponseMetadata


T = TypeVar('T')


class SuccessResponse(BaseModel, Generic[T]):
    """Success response model."""
    success: bool = True
    error: None = None
    data: T
    metadata: ResponseMetadata


class PaginationMetadata(BaseModel):
    """Pagination metadata."""
    limit: int
    offset: int
    total: Optional[int] = None
    has_more: Optional[bool] = None


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    service: str
    version: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
