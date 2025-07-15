"""
The code has been modified to include the uuid import and update the API_SECRET_KEY and JWT_SECRET_KEY to generate default secrets for development.
"""
import os
import json
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
import uuid
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

@dataclass
class DatabaseConfig:
    """Database configuration settings."""
    host: str = "localhost"
    port: int = 5432
    database: str = "custom_gpt"
    username: str = "postgres"
    password: str = ""
    pool_size: int = 10
    max_overflow: int = 20

    @property
    def url(self) -> str:
        """Get database URL."""
        return f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"

@dataclass
class RedisConfig:
    """Redis configuration settings."""
    host: str = "localhost"
    port: int = 6379
    database: int = 0
    password: Optional[str] = None
    max_connections: int = 10

    @property
    def url(self) -> str:
        """Get Redis URL."""
        auth = f":{self.password}@" if self.password else ""
        return f"redis://{auth}{self.host}:{self.port}/{self.database}"

@dataclass
class ModelConfig:
    """Model configuration settings."""
    default_model: str = "microsoft/DialoGPT-medium"
    model_cache_dir: str = "./models"
    max_models_loaded: int = 3
    inference_device: str = "auto"
    max_sequence_length: int = 512
    default_temperature: float = 0.7
    default_top_p: float = 0.9
    default_max_tokens: int = 256

@dataclass
class TrainingConfig:
    """Training configuration settings."""
    output_dir: str = "./training_outputs"
    data_dir: str = "./training_data"
    max_file_size: int = 100 * 1024 * 1024  # 100MB
    batch_size: int = 4
    learning_rate: float = 2e-4
    num_epochs: int = 3
    warmup_steps: int = 100
    save_steps: int = 500
    eval_steps: int = 100
    lora_r: int = 16
    lora_alpha: int = 32
    lora_dropout: float = 0.1

@dataclass
class APIConfig:
    """API configuration settings."""
    host: str = "0.0.0.0"
    port: int = 5000
    debug: bool = False
    secret_key: str = 'dev-api-secret-key-' + str(uuid.uuid4())[:8]
    jwt_secret_key: str = 'dev-jwt-secret-key-' + str(uuid.uuid4())[:8]
    jwt_access_token_expires: int = 3600  # 1 hour
    cors_origins: List[str] = field(default_factory=lambda: ["*"])
    rate_limit_per_minute: int = 60
    max_request_size: int = 16 * 1024 * 1024  # 16MB

@dataclass
class BillingConfig:
    """Billing and subscription configuration."""
    stripe_public_key: str = ""
    stripe_secret_key: str = ""
    webhook_secret: str = ""
    currency: str = "usd"
    free_tier_limit: int = 1000  # tokens per month
    individual_tier_price: int = 999  # cents per month
    professional_tier_price: int = 4999  # cents per month
    enterprise_tier_price: int = 19999  # cents per month

@dataclass
class SecurityConfig:
    """Security configuration settings."""
    password_min_length: int = 8
    password_require_uppercase: bool = True
    password_require_lowercase: bool = True
    password_require_numbers: bool = True
    password_require_symbols: bool = False
    max_login_attempts: int = 5
    lockout_duration: int = 900  # 15 minutes
    session_timeout: int = 3600  # 1 hour
    enable_2fa: bool = False

@dataclass
class MonitoringConfig:
    """Monitoring and logging configuration."""
    log_level: str = "INFO"
    log_format: str = "json"
    enable_metrics: bool = True
    metrics_port: int = 9090
    enable_tracing: bool = False
    sentry_dsn: Optional[str] = None
    prometheus_enabled: bool = True

@dataclass
class AppConfig:
    """Main application configuration."""
    environment: str = "development"
    debug: bool = False
    testing: bool = False

    # Component configurations
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    redis: RedisConfig = field(default_factory=RedisConfig)
    model: ModelConfig = field(default_factory=ModelConfig)
    training: TrainingConfig = field(default_factory=TrainingConfig)
    api: APIConfig = field(default_factory=APIConfig)
    billing: BillingConfig = field(default_factory=BillingConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    monitoring: MonitoringConfig = field(default_factory=MonitoringConfig)

    @classmethod
    def from_env(cls) -> 'AppConfig':
        """Create configuration from environment variables."""
        config = cls()

        # Environment settings
        config.environment = os.getenv("ENVIRONMENT", "development")
        config.debug = os.getenv("DEBUG", "false").lower() == "true"
        config.testing = os.getenv("TESTING", "false").lower() == "true"

        # Database configuration
        config.database.host = os.getenv("DB_HOST", config.database.host)
        config.database.port = int(os.getenv("DB_PORT", str(config.database.port)))
        config.database.database = os.getenv("DB_NAME", config.database.database)
        config.database.username = os.getenv("DB_USER", config.database.username)
        config.database.password = os.getenv("DB_PASSWORD", config.database.password)

        # Redis configuration
        config.redis.host = os.getenv("REDIS_HOST", config.redis.host)
        config.redis.port = int(os.getenv("REDIS_PORT", str(config.redis.port)))
        config.redis.password = os.getenv("REDIS_PASSWORD", config.redis.password)

        # Model configuration
        config.model.default_model = os.getenv("DEFAULT_MODEL", config.model.default_model)
        config.model.model_cache_dir = os.getenv("MODEL_CACHE_DIR", config.model.model_cache_dir)
        config.model.inference_device = os.getenv("INFERENCE_DEVICE", config.model.inference_device)

        # API configuration
        config.api.host = os.getenv("API_HOST", config.api.host)
        config.api.port = int(os.getenv("API_PORT", str(config.api.port)))
        config.api.secret_key = os.getenv("SECRET_KEY", 'dev-api-secret-key-' + str(uuid.uuid4())[:8])
        config.api.jwt_secret_key = os.getenv("JWT_SECRET_KEY", 'dev-jwt-secret-key-' + str(uuid.uuid4())[:8])

        # Billing configuration
        config.billing.stripe_public_key = os.getenv("STRIPE_PUBLIC_KEY", config.billing.stripe_public_key)
        config.billing.stripe_secret_key = os.getenv("STRIPE_SECRET_KEY", config.billing.stripe_secret_key)
        config.billing.webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET", config.billing.webhook_secret)

        # Monitoring configuration
        config.monitoring.log_level = os.getenv("LOG_LEVEL", config.monitoring.log_level)
        config.monitoring.sentry_dsn = os.getenv("SENTRY_DSN", config.monitoring.sentry_dsn)

        return config

    @classmethod
    def from_file(cls, config_path: str) -> 'AppConfig':
        """Load configuration from JSON file."""
        with open(config_path, 'r') as f:
            data = json.load(f)

        config = cls()

        # Update configuration with file data
        for key, value in data.items():
            if hasattr(config, key):
                if isinstance(getattr(config, key), (DatabaseConfig, RedisConfig, ModelConfig, 
                                                   TrainingConfig, APIConfig, BillingConfig, 
                                                   SecurityConfig, MonitoringConfig)):
                    # Update nested configuration
                    nested_config = getattr(config, key)
                    for nested_key, nested_value in value.items():
                        if hasattr(nested_config, nested_key):
                            setattr(nested_config, nested_key, nested_value)
                else:
                    setattr(config, key, value)

        return config

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        result = {}
        for key, value in self.__dict__.items():
            if isinstance(value, (DatabaseConfig, RedisConfig, ModelConfig, 
                                TrainingConfig, APIConfig, BillingConfig, 
                                SecurityConfig, MonitoringConfig)):
                result[key] = value.__dict__
            else:
                result[key] = value
        return result

    def save_to_file(self, config_path: str):
        """Save configuration to JSON file."""
        with open(config_path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)

    def validate(self) -> List[str]:
        """Validate configuration and return list of errors."""
        errors = []

        # Validate required fields
        if not self.api.secret_key or self.api.secret_key == "your-secret-key-change-this":
            errors.append("API secret key must be set and changed from default")

        if not self.api.jwt_secret_key or self.api.jwt_secret_key == "your-jwt-secret-key-change-this":
            errors.append("JWT secret key must be set and changed from default")

        if self.environment == "production":
            if self.debug:
                errors.append("Debug mode should be disabled in production")

            if not self.database.password:
                errors.append("Database password must be set in production")

            if not self.monitoring.sentry_dsn:
                errors.append("Sentry DSN should be configured for production monitoring")

        # Validate paths
        model_cache_path = Path(self.model.model_cache_dir)
        if not model_cache_path.exists():
            try:
                model_cache_path.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                errors.append(f"Cannot create model cache directory: {e}")

        training_output_path = Path(self.training.output_dir)
        if not training_output_path.exists():
            try:
                training_output_path.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                errors.append(f"Cannot create training output directory: {e}")

        return errors

class ConfigManager:
    """Manages application configuration with environment and file support."""

    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file
        self._config: Optional[AppConfig] = None

    def load_config(self) -> AppConfig:
        """Load configuration from environment or file."""
        if self._config is not None:
            return self._config

        if self.config_file and Path(self.config_file).exists():
            logger.info(f"Loading configuration from file: {self.config_file}")
            self._config = AppConfig.from_file(self.config_file)
        else:
            logger.info("Loading configuration from environment variables")
            self._config = AppConfig.from_env()

        # Validate configuration
        errors = self._config.validate()
        if errors:
            logger.error("Configuration validation errors:")
            for error in errors:
                logger.error(f"  - {error}")
            if self._config.environment == "production":
                raise ValueError("Configuration validation failed in production environment")

        return self._config

    def get_config(self) -> AppConfig:
        """Get the current configuration."""
        if self._config is None:
            return self.load_config()
        return self._config

    def reload_config(self) -> AppConfig:
        """Reload configuration."""
        self._config = None
        return self.load_config()

# Global configuration manager instance
config_manager = ConfigManager()

def get_config() -> AppConfig:
    """Get the global configuration instance."""
    return config_manager.get_config()

# Example configuration files
def create_example_configs():
    """Create example configuration files."""

    # Development configuration
    dev_config = AppConfig()
    dev_config.environment = "development"
    dev_config.debug = True
    dev_config.api.host = "127.0.0.1"
    dev_config.database.database = "custom_gpt_dev"
    dev_config.api.secret_key = 'dev-api-secret-key-' + str(uuid.uuid4())[:8]
    dev_config.api.jwt_secret_key = 'dev-jwt-secret-key-' + str(uuid.uuid4())[:8]

    dev_config.save_to_file("config_development.json")

    # Production configuration template
    prod_config = AppConfig()
    prod_config.environment = "production"
    prod_config.debug = False
    prod_config.api.secret_key = "CHANGE-THIS-IN-PRODUCTION"
    prod_config.api.jwt_secret_key = "CHANGE-THIS-IN-PRODUCTION"
    prod_config.database.host = "your-db-host"
    prod_config.database.password = "your-db-password"
    prod_config.redis.host = "your-redis-host"
    prod_config.monitoring.sentry_dsn = "your-sentry-dsn"

    prod_config.save_to_file("config_production_template.json")

    print("Created example configuration files:")
    print("- config_development.json")
    print("- config_production_template.json")

if __name__ == "__main__":
    # Create example configurations
    create_example_configs()

    # Test configuration loading
    config = get_config()
    print(f"Loaded configuration for environment: {config.environment}")
    print(f"API will run on: {config.api.host}:{config.api.port}")
    print(f"Database URL: {config.database.url}")
    print(f"Model cache directory: {config.model.model_cache_dir}")