import os
from pydantic_settings import BaseSettings
from typing import Optional

# Absolute path to .env at project root
# config.py is at backend/app/config.py
# so we go up two levels to reach predictive_inventory/.env
ENV_FILE = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', '..', '.env')
)

class Settings(BaseSettings):
    # App environment
    ENV: str = "dev"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str

    # Security / Authentication
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Forecasting / Business Logic
    FORECAST_HORIZON_DAYS: int = 30
    MIN_STOCK_LEVEL: int = 10

    # External Services / Integrations
    REDIS_URL: str = "redis://localhost:6379/0"
    EXTERNAL_API_KEY: Optional[str] = None

    # Optional / Logging
    LOG_LEVEL: str = "DEBUG"

    # Google OAuth2
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    GOOGLE_REDIRECT_URI: str

    class Config:
        env_file = ENV_FILE
        case_sensitive = False

settings = Settings()