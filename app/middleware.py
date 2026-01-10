"""Middleware for request processing."""

import logging
import time
import uuid
from typing import Callable

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from jose import JWTError, jwt
from starlette.middleware.base import BaseHTTPMiddleware

from app.config import config

logger = logging.getLogger(__name__)


class RequestContextMiddleware(BaseHTTPMiddleware):
    """Middleware to manage request context (correlation ID, JWT extraction)."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and add context."""
        # Generate or extract correlation ID
        correlation_id = request.headers.get("X-Correlation-Id", str(uuid.uuid4()))
        request.state.correlation_id = correlation_id
        
        # Extract JWT claims if present
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            try:
                payload = jwt.decode(
                    token,
                    config.security.jwt_secret_key,
                    algorithms=[config.security.jwt_algorithm]
                )
                request.state.user_id = payload.get("user_id")
                request.state.tenant_id = payload.get("tenant_id")
                request.state.role = payload.get("role")
                request.state.authenticated = True
            except JWTError as e:
                logger.warning(f"JWT validation failed: {e}", extra={"correlation_id": correlation_id})
                request.state.authenticated = False
        else:
            request.state.authenticated = False
        
        # Process request
        start_time = time.time()
        response = await call_next(request)
        duration = time.time() - start_time
        
        # Add headers to response
        response.headers["X-Correlation-Id"] = correlation_id
        response.headers["X-Response-Time"] = f"{duration:.3f}s"
        
        # Log request
        logger.info(
            f"{request.method} {request.url.path} - {response.status_code}",
            extra={
                "correlation_id": correlation_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration": duration,
                "user_id": getattr(request.state, "user_id", None)
            }
        )
        
        return response


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Middleware for global error handling."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Handle errors globally."""
        try:
            response = await call_next(request)
            return response
        except Exception as e:
            logger.error(
                f"Unhandled exception: {str(e)}",
                exc_info=True,
                extra={"correlation_id": getattr(request.state, "correlation_id", "unknown")}
            )
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "error": {
                        "code": "INTERNAL_SERVER_ERROR",
                        "message": "An unexpected error occurred",
                        "details": None
                    },
                    "data": None,
                    "metadata": {
                        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                        "correlation_id": getattr(request.state, "correlation_id", "unknown")
                    }
                }
            )


def extract_user_context(request: Request) -> dict:
    """Extract user context from request state."""
    return {
        "user_id": getattr(request.state, "user_id", None),
        "tenant_id": getattr(request.state, "tenant_id", None),
        "role": getattr(request.state, "role", None),
        "correlation_id": getattr(request.state, "correlation_id", None),
        "authenticated": getattr(request.state, "authenticated", False)
    }
