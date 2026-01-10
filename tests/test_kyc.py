"""Tests for KYC endpoints."""

from unittest.mock import patch


@patch("app.routes.kyc.extract_user_context")
def test_initiate_kyc_success(mock_context, client, sample_profile):
    """Test initiate KYC successfully."""
    mock_context.return_value = {
        "authenticated": True,
        "user_id": "test-user-id",
        "tenant_id": "test-tenant-id",
        "role": "customer",
        "correlation_id": "test-corr-id"
    }
    
    kyc_data = {
        "kyc_type": "standard"
    }
    
    response = client.post("/api/v1/profiles/me/kyc/initiate", json=kyc_data)
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert "kyc_id" in data["data"]
    assert "required_documents" in data["data"]
    assert data["data"]["status"] == "in_progress"


@patch("app.routes.kyc.extract_user_context")
def test_get_kyc_status_success(mock_context, client, sample_profile):
    """Test get KYC status successfully."""
    mock_context.return_value = {
        "authenticated": True,
        "user_id": "test-user-id",
        "tenant_id": "test-tenant-id",
        "role": "customer",
        "correlation_id": "test-corr-id"
    }
    
    # First initiate KYC
    kyc_data = {"kyc_type": "standard"}
    client.post("/api/v1/profiles/me/kyc/initiate", json=kyc_data)
    
    # Then get status
    response = client.get("/api/v1/profiles/me/kyc")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "kyc_status" in data["data"]
    assert "completed_checks" in data["data"]


@patch("app.routes.kyc.extract_user_context")
def test_get_kyc_status_not_initiated(mock_context, client):
    """Test get KYC status when not initiated."""
    # Create a different profile without KYC
    from app.services import storage
    profile_data = {
        "id": "test-profile-no-kyc",
        "user_id": "test-user-no-kyc",
        "tenant_id": "test-tenant-id",
        "status": "active",
        "kyc_status": "pending",
        "completeness_percentage": 0.0,
        "created_at": "2026-01-10T00:00:00",
        "updated_at": "2026-01-10T00:00:00"
    }
    storage.profiles_db[profile_data["id"]] = profile_data
    
    mock_context.return_value = {
        "authenticated": True,
        "user_id": "test-user-no-kyc",
        "tenant_id": "test-tenant-id",
        "role": "customer",
        "correlation_id": "test-corr-id"
    }
    
    response = client.get("/api/v1/profiles/me/kyc")
    assert response.status_code == 404
