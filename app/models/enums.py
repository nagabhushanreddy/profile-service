"""Enum definitions for Profile Service."""

from enum import Enum


class ProfileStatus(str, Enum):
    """Profile status enumeration."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    DELETED = "deleted"


class KYCStatus(str, Enum):
    """KYC status enumeration."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    VERIFIED = "verified"
    REJECTED = "rejected"
    EXPIRED = "expired"


class KYCType(str, Enum):
    """KYC type enumeration."""
    STANDARD = "standard"
    ENHANCED = "enhanced"
    LEGACY = "legacy"


class AddressType(str, Enum):
    """Address type enumeration."""
    RESIDENTIAL = "residential"
    OFFICE = "office"
    CORRESPONDENCE = "correspondence"


class VerificationStatus(str, Enum):
    """Verification status enumeration."""
    UNVERIFIED = "unverified"
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"


class DocumentType(str, Enum):
    """Document type enumeration."""
    PROFILE_PHOTO = "profile_photo"
    AADHAR = "aadhar"
    PAN = "pan"
    PASSPORT = "passport"
    DRIVING_LICENSE = "driving_license"
    UTILITY_BILL = "utility_bill"
    BANK_STATEMENT = "bank_statement"
    OTHERS = "others"


class ConsentType(str, Enum):
    """Consent type enumeration."""
    TERMS_AND_CONDITIONS = "terms_and_conditions"
    DATA_USAGE = "data_usage"
    MARKETING_COMMUNICATION = "marketing_communication"
    CIBIL_REPORT_PULL = "cibil_report_pull"


class ConsentStatus(str, Enum):
    """Consent status enumeration."""
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class RiskGrade(str, Enum):
    """Risk grade enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


class CreditGrade(str, Enum):
    """Credit grade enumeration."""
    A = "A"
    B = "B"
    C = "C"
    D = "D"
    E = "E"


class BackgroundCheckResult(str, Enum):
    """Background check result enumeration."""
    CLEAR = "clear"
    REVIEW = "review"
    FLAG = "flag"


class AuditAction(str, Enum):
    """Audit action enumeration."""
    CREATE = "create"
    UPDATE = "update"
    VERIFY = "verify"
    ENRICH = "enrich"
    DELETE = "delete"


class Gender(str, Enum):
    """Gender enumeration."""
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    PREFER_NOT_TO_SAY = "prefer_not_to_say"


class MaritalStatus(str, Enum):
    """Marital status enumeration."""
    SINGLE = "single"
    MARRIED = "married"
    DIVORCED = "divorced"
    WIDOWED = "widowed"


class EmploymentStatus(str, Enum):
    """Employment status enumeration."""
    EMPLOYED = "employed"
    SELF_EMPLOYED = "self_employed"
    UNEMPLOYED = "unemployed"
    RETIRED = "retired"
    STUDENT = "student"


class EnrichmentStatus(str, Enum):
    """Enrichment status for maker-checker workflow."""
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    REJECTED = "rejected"


class VerificationDecision(str, Enum):
    """Verification decision enumeration."""
    APPROVED = "approved"
    REJECTED = "rejected"


class CheckerDecision(str, Enum):
    """Checker decision for maker-checker workflow."""
    APPROVE = "approve"
    REJECT = "reject"
