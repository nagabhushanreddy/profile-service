"""Tests for address endpoints."""

from unittest.mock import patch


@patch("app.routes.addresses.extract_user_context")
def test_get_addresses_success(mock_context, client, sample_profile):
    """Test get addresses successfully."""
    mock_context.return_value = {
        "authenticated": True,
        "user_id": "test-user-id",
        "tenant_id": "test-tenant-id",
        "role": "customer",
        "correlation_id": "test-corr-id"
    }
    
    response = client.get("/api/v1/profiles/me/addresses")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert isinstance(data["data"], list)


@patch("app.routes.addresses.extract_user_context")
def test_create_address_success(mock_context, client, sample_profile):
    """Test create address successfully."""
    mock_context.return_value = {
        "authenticated": True,
        "user_id": "test-user-id",
        "tenant_id": "test-tenant-id",
        "role": "customer",
        "correlation_id": "test-corr-id"
    }
    
    address_data = {
        "type": "residential",
        "address_line1": "123 Main St",
        "city": "Mumbai",
        "state": "Maharashtra",
        "postal_code": "400001",
        "country": "India",
        "is_primary": True
    }
    
    response = client.post("/api/v1/profiles/me/addresses", json=address_data)
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert data["data"]["type"] == "residential"
    assert data["data"]["address_line1"] == "123 Main St"


@patch("app.routes.addresses.extract_user_context")
def test_create_address_max_limit(mock_context, client, sample_profile):
    """Test create address exceeding max limit."""
    mock_context.return_value = {
        "authenticated": True,
        "user_id": "test-user-id",
        "tenant_id": "test-tenant-id",
        "role": "customer",
        "correlation_id": "test-corr-id"
    }
    
    # Create 10 addresses
    for i in range(10):
        address_data = {
            "type": "residential",
            "address_line1": f"{i} Main St",
            "city": "Mumbai",
            "state": "Maharashtra",
            "postal_code": "400001",
            "country": "India"
        }
        client.post("/api/v1/profiles/me/addresses", json=address_data)
    
    # Try to create 11th address
    address_data = {
        "type": "residential",
        "address_line1": "11 Main St",
        "city": "Mumbai",
        "state": "Maharashtra",
        "postal_code": "400001",
        "country": "India"
    }
    
    response = client.post("/api/v1/profiles/me/addresses", json=address_data)
    assert response.status_code == 400
