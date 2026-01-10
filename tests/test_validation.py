"""Tests for validation service."""

from app.services.validation_service import validation_service


def test_validate_phone_valid():
    """Test valid phone number."""
    assert validation_service.validate_phone("+919876543210") is True


def test_validate_phone_invalid():
    """Test invalid phone number."""
    assert validation_service.validate_phone("invalid") is False


def test_validate_email_valid():
    """Test valid email."""
    assert validation_service.validate_email_format("test@example.com") is True


def test_validate_email_invalid():
    """Test invalid email."""
    assert validation_service.validate_email_format("invalid-email") is False


def test_validate_pan_valid():
    """Test valid PAN."""
    assert validation_service.validate_pan("ABCDE1234F") is True


def test_validate_pan_invalid():
    """Test invalid PAN."""
    assert validation_service.validate_pan("invalid") is False


def test_validate_aadhaar_valid():
    """Test valid Aadhaar."""
    assert validation_service.validate_aadhaar("123456789012") is True


def test_validate_aadhaar_invalid():
    """Test invalid Aadhaar."""
    assert validation_service.validate_aadhaar("invalid") is False


def test_validate_postal_code_valid():
    """Test valid postal code."""
    assert validation_service.validate_postal_code("400001", "India") is True


def test_validate_postal_code_invalid():
    """Test invalid postal code."""
    assert validation_service.validate_postal_code("invalid", "India") is False
