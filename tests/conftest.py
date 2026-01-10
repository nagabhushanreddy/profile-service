"""Test configuration and fixtures."""

import pytest
from fastapi.testclient import TestClient

from app.services import storage
from main import app


@pytest.fixture
def client():
    """Test client fixture."""
    return TestClient(app)


@pytest.fixture
def auth_headers():
    """Mock authentication headers."""
    # In real implementation, would generate valid JWT
    return {
        "Authorization": "Bearer mock_token",
        "X-Correlation-Id": "test-correlation-id"
    }


@pytest.fixture(autouse=True)
def reset_storage():
    """Reset in-memory storage before each test."""
    storage.profiles_db.clear()
    storage.addresses_db.clear()
    storage.kyc_workflows_db.clear()
    storage.documents_db.clear()
    storage.consents_db.clear()
    storage.enrichments_db.clear()
    storage.audit_entries_db.clear()
    yield


@pytest.fixture
def sample_profile():
    """Create a sample profile for testing."""
    import uuid
    profile_id = str(uuid.uuid4())
    profile_data = {
        "id": profile_id,
        "user_id": "test-user-id",
        "tenant_id": "test-tenant-id",
        "first_name": "John",
        "last_name": "Doe",
        "full_name": "John Doe",
        "email": "john.doe@example.com",
        "phone": "+919876543210",
        "status": "active",
        "kyc_status": "pending",
        "completeness_percentage": 0.0,
        "created_at": "2026-01-10T00:00:00",
        "updated_at": "2026-01-10T00:00:00"
    }
    storage.profiles_db[profile_data["id"]] = profile_data
    return profile_data


@pytest.fixture
def mock_jwt_payload():
    """Mock JWT payload."""
    return {
        "user_id": "test-user-id",
        "tenant_id": "test-tenant-id",
        "role": "customer"
    }
