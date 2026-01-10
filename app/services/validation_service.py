"""Validation service."""

import logging
import re
from typing import Optional

import phonenumbers
from email_validator import EmailNotValidError, validate_email

logger = logging.getLogger(__name__)


class ValidationService:
    """Service for field validation."""
    
    def validate_phone(self, phone: str) -> bool:
        """Validate phone number format."""
        try:
            parsed = phonenumbers.parse(phone, None)
            return phonenumbers.is_valid_number(parsed)
        except Exception as e:
            logger.debug(f"Phone validation failed: {e}")
            return False
    
    def validate_email_format(self, email: str) -> bool:
        """Validate email format."""
        try:
            validate_email(email, check_deliverability=False)
            return True
        except EmailNotValidError as e:
            logger.debug(f"Email validation failed: {e}")
            return False
        except Exception as e:
            logger.debug(f"Email validation error: {e}")
            return False
    
    def validate_pan(self, pan: str) -> bool:
        """Validate PAN format (India)."""
        pattern = r"^[A-Z]{5}[0-9]{4}[A-Z]$"
        return bool(re.match(pattern, pan))
    
    def validate_aadhaar(self, aadhaar: str) -> bool:
        """Validate Aadhaar format (India)."""
        pattern = r"^\d{12}$"
        return bool(re.match(pattern, aadhaar))
    
    def validate_postal_code(self, postal_code: str, country: str = "India") -> bool:
        """Validate postal code format."""
        if country == "India":
            pattern = r"^\d{6}$"
            return bool(re.match(pattern, postal_code))
        # Add more country-specific validations
        return True


validation_service = ValidationService()
