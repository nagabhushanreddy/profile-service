"""Tests for reference data endpoints."""

def test_get_profile_statuses(client):
    """Test get profile status enum values."""
    response = client.get("/api/v1/reference/profile-statuses")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "statuses" in data["data"]
    assert "active" in data["data"]["statuses"]


def test_get_kyc_statuses(client):
    """Test get KYC status enum values."""
    response = client.get("/api/v1/reference/kyc-statuses")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "statuses" in data["data"]
    assert "pending" in data["data"]["statuses"]


def test_get_address_types(client):
    """Test get address type enum values."""
    response = client.get("/api/v1/reference/address-types")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "types" in data["data"]
    assert "residential" in data["data"]["types"]


def test_get_document_types(client):
    """Test get document type enum values."""
    response = client.get("/api/v1/reference/document-types")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "types" in data["data"]
    assert "pan" in data["data"]["types"]


def test_get_consent_types(client):
    """Test get consent type enum values."""
    response = client.get("/api/v1/reference/consent-types")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "types" in data["data"]
    assert "terms_and_conditions" in data["data"]["types"]
