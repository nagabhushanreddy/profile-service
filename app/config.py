"""Configuration management for Profile Service using utils.config."""

import os
from pathlib import Path
from typing import Dict, List

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from utils import config, init_utils

CONFIG_DIR = Path(os.environ.get("CONFIG_DIR", "config"))
init_utils(str(CONFIG_DIR))


def _get_bool(key: str, default: bool) -> bool:
    value = config.get(key, default)
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"true", "1", "yes", "on"}
    return bool(value)


def _get_int(key: str, default: int) -> int:
    try:
        return int(config.get(key, default))
    except (TypeError, ValueError):
        return default


REDIS_HOST = config.get("redis.host", "localhost")
REDIS_PORT = _get_int("redis.port", 6379)
REDIS_DB = _get_int("redis.db", 1)


class ServiceConfig(BaseModel):
    """Service configuration."""

    name: str = config.get("service.name", "profile-service")
    version: str = config.get("service.version", "1.0.0")
    port: int = _get_int("server.port", 8006)
    workers: int = _get_int("service.workers", 4)
    environment: str = config.get("service.environment", "development")


class SecurityConfig(BaseModel):
    """Security configuration."""

    jwt_algorithm: str = config.get("jwt.algorithm", "HS256")
    jwt_secret_key: str = config.get("jwt.access_secret", "your-super-secret-access-key-min-32-chars")
    api_key_header: str = config.get("api_key.header", "X-API-Key")


class CachingConfig(BaseModel):
    """Caching configuration."""

    profile_ttl: int = _get_int("caching.profile_ttl", 300)
    address_ttl: int = _get_int("caching.address_ttl", 600)
    kyc_status_ttl: int = _get_int("caching.kyc_status_ttl", 120)
    redis_url: str = config.get("redis.url", f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}")
    use_in_memory: bool = _get_bool("caching.use_in_memory", True)


class BusinessConfig(BaseModel):
    """Business logic configuration."""

    max_addresses_per_profile: int = _get_int("business.max_addresses_per_profile", 10)
    kyc_validity_days: int = _get_int("business.kyc_validity_days", 365)
    kyc_renewal_warning_days: int = _get_int("business.kyc_renewal_warning_days", 30)
    maker_checker_sla_hours: int = _get_int("business.maker_checker_sla_hours", 24)


class RateLimitConfig(BaseModel):
    """Rate limiting configuration."""

    profile_update_per_hour: int = _get_int("rate_limiting.profile_update_per_hour", 10)
    address_add_per_month: int = _get_int("rate_limiting.address_add_per_month", 20)
    document_upload_per_day: int = _get_int("rate_limiting.document_upload_per_day", 10)


class ExternalServiceConfig(BaseModel):
    """External service configuration."""

    base_url: str
    timeout: int = 10
    retry_attempts: int = 3


class AppConfig(BaseSettings):
    """Main configuration class loaded from utils.config defaults."""

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False, extra="ignore")

    service: ServiceConfig = Field(default_factory=ServiceConfig)
    security: SecurityConfig = Field(default_factory=SecurityConfig)
    caching: CachingConfig = Field(default_factory=CachingConfig)
    business: BusinessConfig = Field(default_factory=BusinessConfig)
    rate_limiting: RateLimitConfig = Field(default_factory=RateLimitConfig)

    # External services
    entity_service: ExternalServiceConfig = Field(
        default_factory=lambda: ExternalServiceConfig(
            base_url=config.get("external_services.entity_service.url", "http://localhost:8000"),
            timeout=_get_int("external_services.entity_service.timeout", 5),
            retry_attempts=_get_int("external_services.entity_service.retry_attempts", 3),
        )
    )
    document_service: ExternalServiceConfig = Field(
        default_factory=lambda: ExternalServiceConfig(
            base_url=config.get("external_services.document_service.url", "http://localhost:8001"),
            timeout=_get_int("external_services.document_service.timeout", 5),
            retry_attempts=_get_int("external_services.document_service.retry_attempts", 3),
        )
    )
    authz_service: ExternalServiceConfig = Field(
        default_factory=lambda: ExternalServiceConfig(
            base_url=config.get("external_services.authz_service.url", "http://localhost:3002"),
            timeout=_get_int("external_services.authz_service.timeout", 5),
            retry_attempts=_get_int("external_services.authz_service.retry_attempts", 3),
        )
    )
    notification_service: ExternalServiceConfig = Field(
        default_factory=lambda: ExternalServiceConfig(
            base_url=config.get("external_services.notification_service.url", "http://localhost:8004"),
            timeout=_get_int("external_services.notification_service.timeout", 5),
            retry_attempts=_get_int("external_services.notification_service.retry_attempts", 3),
        )
    )

    # Business data
    kyc_requirements: Dict[str, List[str]] = Field(default_factory=lambda: config.get("kyc_requirements", {}))
    profile_completeness_weights: Dict[str, int] = Field(
        default_factory=lambda: config.get("profile_completeness_weights", {
            "personal_info": 50,
            "address_info": 20,
            "kyc_info": 20,
            "documents_info": 10
        })
    )
    mandatory_consents: List[str] = Field(default_factory=lambda: config.get("mandatory_consents", []))


# Global configuration instance
config = AppConfig()
