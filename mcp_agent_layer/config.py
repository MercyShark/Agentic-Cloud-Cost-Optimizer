from pydantic_settings import BaseSettings
from typing import Optional
class Settings(BaseSettings):
    APP_NAME: str = "AWS Optimization Tools"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 4
    AWS_DEFAULT_REGION: str = "us-east-1"
    AWS_STS_SESSION_DURATION: int = 3600
    MAX_RETRIES: int = 3
    BASE_RETRY_DELAY: float = 1.0
    DEFAULT_PAGE_SIZE: int = 100
    MAX_PAGE_SIZE: int = 1000
    COST_EXPLORER_DEFAULT_DAYS: int = 30
    COST_FORECAST_DEFAULT_MONTHS: int = 3
    CLOUDWATCH_DEFAULT_PERIOD: int = 3600
    CLOUDWATCH_DEFAULT_HOURS: int = 24
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    CORS_ORIGINS: list = ["*"]
    CORS_CREDENTIALS: bool = True
    CORS_METHODS: list = ["*"]
    CORS_HEADERS: list = ["*"]
    class Config:
        env_file = ".env"
        case_sensitive = True
settings = Settings()
