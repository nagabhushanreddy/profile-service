"""Configuration management for Profile Service."""

import os
from pathlib import Path
from typing import Any, Dict, List

import yaml
from pydantic import Field
from pydantic_settings import BaseSettings


class ServiceConfig(BaseSettings):
    """Service configuration."""
    
    name: str = "profile-service"
    version: str = "1.0.0"
    port: int = 8006
    workers: int = 4
    environment: str = Field(default="development", env="ENVIRONMENT")


class SecurityConfig(BaseSettings):
    """Security configuration."""
    
    jwt_algorithm: str = "HS256"
    jwt_secret_key: str = Field(env="JWT_SECRET_KEY")
    api_key_header: str = "X-API-Key"


class CachingConfig(BaseSettings):
    """Caching configuration."""
    
    profile_ttl: int = 300
    address_ttl: int = 600
    kyc_status_ttl: int = 120
    redis_url: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    use_in_memory: bool = Field(default=True, env="USE_IN_MEMORY_CACHE")


class BusinessConfig(BaseSettings):
    """Business logic configuration."""
    
    max_addresses_per_profile: int = 10
    kyc_validity_days: int = 365
    kyc_renewal_warning_days: int = 30
    maker_checker_sla_hours: int = 24


class RateLimitConfig(BaseSettings):
    """Rate limiting configuration."""
    
    profile_update_per_hour: int = 10
    address_add_per_month: int = 20
    document_upload_per_day: int = 10


class ExternalServiceConfig(BaseSettings):
    """External service configuration."""
    
    base_url: str
    timeout: int = 10
    retry_attempts: int = 3


class Config:
    """Main configuration class."""
    
    def __init__(self):
        self.config_path = Path(__file__).parent.parent / "config" / "app_config.yaml"
        self._config_data = self._load_config()
        
        self.service = ServiceConfig(**self._config_data.get("service", {}))
        self.security = SecurityConfig(**self._config_data.get("security", {}))
        self.caching = CachingConfig(**self._config_data.get("caching", {}))
        self.business = BusinessConfig(**self._config_data.get("business", {}))
        self.rate_limiting = RateLimitConfig(**self._config_data.get("rate_limiting", {}))
        
        # External services
        external_services = self._config_data.get("external_services", {})
        self.entity_service = self._create_external_service_config(external_services.get("entity_service", {}))
        self.document_service = self._create_external_service_config(external_services.get("document_service", {}))
        self.authz_service = self._create_external_service_config(external_services.get("authz_service", {}))
        self.notification_service = self._create_external_service_config(external_services.get("notification_service", {}))
        
        # Business data
        self.kyc_requirements: Dict[str, List[str]] = self._config_data.get("kyc_requirements", {})
        self.profile_completeness_weights: Dict[str, int] = self._config_data.get("profile_completeness_weights", {})
        self.mandatory_consents: List[str] = self._config_data.get("mandatory_consents", [])
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file with environment variable substitution."""
        if not self.config_path.exists():
            return {}
        
        with open(self.config_path) as f:
            content = f.read()
            
        # Simple environment variable substitution
        import re
        def replace_env(match):
            var_name = match.group(1)
            default = match.group(2) if match.group(2) else ""
            return os.getenv(var_name, default)
        
        content = re.sub(r'\$\{(\w+)(?::([^}]*))?\}', replace_env, content)
        return yaml.safe_load(content)
    
    def _create_external_service_config(self, data: Dict[str, Any]) -> ExternalServiceConfig:
        """Create external service configuration."""
        return ExternalServiceConfig(**data)


# Global configuration instance
config = Config()
