"""API routes."""

from app.routes import health, profiles, addresses, kyc, documents, consents, enrichment, audit, reference

__all__ = [
    "health",
    "profiles",
    "addresses",
    "kyc",
    "documents",
    "consents",
    "enrichment",
    "audit",
    "reference",
]
