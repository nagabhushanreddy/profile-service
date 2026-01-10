"""Main application entry point for Profile Service."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import config
from app.middleware import ErrorHandlingMiddleware, RequestContextMiddleware
from app.routes import (
    addresses,
    audit,
    consents,
    documents,
    enrichment,
    health,
    kyc,
    profiles,
    reference,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='{"timestamp": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "message": "%(message)s"}'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info(f"Starting {config.service.name} v{config.service.version}")
    logger.info(f"Environment: {config.service.environment}")
    logger.info(f"Port: {config.service.port}")
    
    yield
    
    # Shutdown
    logger.info(f"Shutting down {config.service.name}")


# Create FastAPI application
app = FastAPI(
    title="Profile Service API",
    description="User Profile and KYC Management Service",
    version=config.service.version,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom middleware
app.add_middleware(ErrorHandlingMiddleware)
app.add_middleware(RequestContextMiddleware)

# Register routes
app.include_router(health.router)
app.include_router(profiles.router)
app.include_router(addresses.router)
app.include_router(kyc.router)
app.include_router(documents.router)
app.include_router(consents.router)
app.include_router(enrichment.router)
app.include_router(audit.router)
app.include_router(reference.router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": config.service.name,
        "version": config.service.version,
        "status": "running",
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=config.service.port,
        reload=True if config.service.environment == "development" else False,
        log_level="info"
    )
