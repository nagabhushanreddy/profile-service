"""Tests for profile endpoints."""

import pytest
from unittest.mock import patch


def test_get_own_profile_unauthorized(client):
    """Test get own profile without authentication."""
    response = client.get("/api/v1/profiles/me")
    assert response.status_code == 401


@patch("app.routes.profiles.extract_user_context")
def test_get_own_profile_success(mock_context, client, sample_profile):
    """Test get own profile successfully."""
    mock_context.return_value = {
        "authenticated": True,
        "user_id": "test-user-id",
        "tenant_id": "test-tenant-id",
        "role": "customer",
        "correlation_id": "test-corr-id"
    }
    
    response = client.get("/api/v1/profiles/me")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["user_id"] == "test-user-id"
    assert data["data"]["full_name"] == "John Doe"


@patch("app.routes.profiles.extract_user_context")
def test_get_own_profile_not_found(mock_context, client):
    """Test get own profile when profile doesn't exist."""
    mock_context.return_value = {
        "authenticated": True,
        "user_id": "nonexistent-user",
        "tenant_id": "test-tenant-id",
        "role": "customer",
        "correlation_id": "test-corr-id"
    }
    
    response = client.get("/api/v1/profiles/me")
    assert response.status_code == 404


@patch("app.routes.profiles.extract_user_context")
def test_update_own_profile_success(mock_context, client, sample_profile):
    """Test update own profile successfully."""
    mock_context.return_value = {
        "authenticated": True,
        "user_id": "test-user-id",
        "tenant_id": "test-tenant-id",
        "role": "customer",
        "correlation_id": "test-corr-id"
    }
    
    update_data = {
        "first_name": "Jane",
        "last_name": "Smith",
        "phone": "+919876543211"
    }
    
    response = client.patch("/api/v1/profiles/me", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["first_name"] == "Jane"
    assert data["data"]["last_name"] == "Smith"


@patch("app.routes.profiles.extract_user_context")
def test_get_profile_completeness(mock_context, client, sample_profile):
    """Test get profile completeness."""
    mock_context.return_value = {
        "authenticated": True,
        "user_id": "test-user-id",
        "tenant_id": "test-tenant-id",
        "role": "customer",
        "correlation_id": "test-corr-id"
    }
    
    response = client.get("/api/v1/profiles/me/completeness")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "overall_completeness" in data["data"]
    assert "field_completeness" in data["data"]
    assert "missing_fields" in data["data"]
