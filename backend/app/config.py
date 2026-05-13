from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict
import os
from typing import Optional

ENV_FILE = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', '..', '.env')
)

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        case_sensitive=False,
        extra="ignore"
    )

    # App environment
    ENV: str = "dev"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str

    # Docker PostgreSQL
    POSTGRES_USER: str = "inventory_user"
    POSTGRES_PASSWORD: str = "inventory_password"
    POSTGRES_DB: str = "inventory_db"

    # Security / Authentication
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Forecasting / Business Logic
    FORECAST_HORIZON_DAYS: int = 30
    MIN_STOCK_LEVEL: int = 10

    # External Services
    REDIS_URL: str = "redis://localhost:6379/0"
    EXTERNAL_API_KEY: Optional[str] = None

    # Logging
    LOG_LEVEL: str = "DEBUG"

    # Google OAuth2
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    GOOGLE_REDIRECT_URI: str

settings = Settings()