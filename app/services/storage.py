"""In-memory storage for profile data (simulating database)."""

import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional
from uuid import UUID

# In-memory storage (simulating database)
profiles_db: Dict[str, dict] = {}
addresses_db: Dict[str, dict] = {}
kyc_workflows_db: Dict[str, dict] = {}
documents_db: Dict[str, dict] = {}
consents_db: Dict[str, dict] = {}
enrichments_db: Dict[str, dict] = {}
audit_entries_db: Dict[str, dict] = {}


def generate_uuid() -> str:
    """Generate UUID string."""
    return str(uuid.uuid4())


def get_profile_by_id(profile_id: str) -> Optional[dict]:
    """Get profile by ID."""
    return profiles_db.get(profile_id)


def get_profile_by_user_id(user_id: str) -> Optional[dict]:
    """Get profile by user ID."""
    for profile in profiles_db.values():
        if profile.get("user_id") == user_id:
            return profile
    return None


def create_profile(profile_data: dict) -> dict:
    """Create new profile."""
    profile_id = generate_uuid()
    profile_data["id"] = profile_id
    profile_data["created_at"] = datetime.now(timezone.utc).isoformat()
    profile_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    profiles_db[profile_id] = profile_data
    return profile_data


def update_profile(profile_id: str, update_data: dict) -> Optional[dict]:
    """Update profile."""
    if profile_id not in profiles_db:
        return None
    profiles_db[profile_id].update(update_data)
    profiles_db[profile_id]["updated_at"] = datetime.now(timezone.utc).isoformat()
    return profiles_db[profile_id]


def get_addresses_by_profile_id(profile_id: str) -> List[dict]:
    """Get all addresses for profile."""
    return [addr for addr in addresses_db.values() if addr.get("profile_id") == profile_id]


def create_address(address_data: dict) -> dict:
    """Create new address."""
    address_id = generate_uuid()
    address_data["id"] = address_id
    address_data["created_at"] = datetime.now(timezone.utc).isoformat()
    address_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    addresses_db[address_id] = address_data
    return address_data


def get_address_by_id(address_id: str) -> Optional[dict]:
    """Get address by ID."""
    return addresses_db.get(address_id)


def update_address(address_id: str, update_data: dict) -> Optional[dict]:
    """Update address."""
    if address_id not in addresses_db:
        return None
    addresses_db[address_id].update(update_data)
    addresses_db[address_id]["updated_at"] = datetime.now(timezone.utc).isoformat()
    return addresses_db[address_id]


def delete_address(address_id: str) -> bool:
    """Soft delete address."""
    if address_id not in addresses_db:
        return False
    addresses_db[address_id]["deleted_at"] = datetime.now(timezone.utc).isoformat()
    return True


def create_kyc_workflow(kyc_data: dict) -> dict:
    """Create KYC workflow."""
    kyc_id = generate_uuid()
    kyc_data["id"] = kyc_id
    kyc_data["created_at"] = datetime.now(timezone.utc).isoformat()
    kyc_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    kyc_workflows_db[kyc_id] = kyc_data
    return kyc_data


def get_kyc_by_profile_id(profile_id: str) -> Optional[dict]:
    """Get KYC workflow by profile ID."""
    for kyc in kyc_workflows_db.values():
        if kyc.get("profile_id") == profile_id:
            return kyc
    return None


def update_kyc_workflow(kyc_id: str, update_data: dict) -> Optional[dict]:
    """Update KYC workflow."""
    if kyc_id not in kyc_workflows_db:
        return None
    kyc_workflows_db[kyc_id].update(update_data)
    kyc_workflows_db[kyc_id]["updated_at"] = datetime.now(timezone.utc).isoformat()
    return kyc_workflows_db[kyc_id]


def create_document(document_data: dict) -> dict:
    """Create document record."""
    doc_id = generate_uuid()
    document_data["id"] = doc_id
    document_data["created_at"] = datetime.now(timezone.utc).isoformat()
    documents_db[doc_id] = document_data
    return document_data


def get_documents_by_profile_id(profile_id: str) -> List[dict]:
    """Get all documents for profile."""
    return [doc for doc in documents_db.values() if doc.get("profile_id") == profile_id]


def get_document_by_id(doc_id: str) -> Optional[dict]:
    """Get document by ID."""
    return documents_db.get(doc_id)


def update_document(doc_id: str, update_data: dict) -> Optional[dict]:
    """Update document."""
    if doc_id not in documents_db:
        return None
    documents_db[doc_id].update(update_data)
    return documents_db[doc_id]


def create_consent(consent_data: dict) -> dict:
    """Create consent record."""
    consent_id = generate_uuid()
    consent_data["id"] = consent_id
    consent_data["created_at"] = datetime.now(timezone.utc).isoformat()
    consent_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    consents_db[consent_id] = consent_data
    return consent_data


def get_consents_by_profile_id(profile_id: str) -> List[dict]:
    """Get all consents for profile."""
    return [c for c in consents_db.values() if c.get("profile_id") == profile_id]


def update_consent(consent_id: str, update_data: dict) -> Optional[dict]:
    """Update consent."""
    if consent_id not in consents_db:
        return None
    consents_db[consent_id].update(update_data)
    consents_db[consent_id]["updated_at"] = datetime.now(timezone.utc).isoformat()
    return consents_db[consent_id]


def create_enrichment(enrichment_data: dict) -> dict:
    """Create enrichment record."""
    enrichment_id = generate_uuid()
    enrichment_data["id"] = enrichment_id
    enrichment_data["created_at"] = datetime.now(timezone.utc).isoformat()
    enrichments_db[enrichment_id] = enrichment_data
    return enrichment_data


def get_enrichments_by_profile_id(profile_id: str) -> List[dict]:
    """Get all enrichments for profile."""
    return [e for e in enrichments_db.values() if e.get("profile_id") == profile_id]


def get_enrichment_by_id(enrichment_id: str) -> Optional[dict]:
    """Get enrichment by ID."""
    return enrichments_db.get(enrichment_id)


def update_enrichment(enrichment_id: str, update_data: dict) -> Optional[dict]:
    """Update enrichment."""
    if enrichment_id not in enrichments_db:
        return None
    enrichments_db[enrichment_id].update(update_data)
    return enrichments_db[enrichment_id]


def create_audit_entry(audit_data: dict) -> dict:
    """Create audit entry."""
    audit_id = generate_uuid()
    audit_data["id"] = audit_id
    audit_data["timestamp"] = datetime.now(timezone.utc).isoformat()
    audit_entries_db[audit_id] = audit_data
    return audit_data


def get_audit_entries_by_profile_id(profile_id: str, limit: int = 50, offset: int = 0) -> List[dict]:
    """Get audit entries for profile."""
    entries = [e for e in audit_entries_db.values() if e.get("profile_id") == profile_id]
    # Sort by timestamp descending
    entries.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    return entries[offset:offset + limit]
