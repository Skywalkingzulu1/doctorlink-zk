"""DoctorLink Health Services - Config and Settings."""

import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "DoctorLink Health Services"
    APP_VERSION: str = "1.0.0"
    DATABASE_URL: str = "sqlite:///./health_services.db"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    STELLAR_NETWORK: str = "testnet"
    ZK_VERIFIER_CONTRACT: str = ""
    HEALTH_TOKEN_CONTRACT: str = ""
    STELLAR_SECRET_KEY: str = ""
    OPENROUTER_API_KEY: str = ""
    OPENROUTER_MODEL: str = "google/gemini-2.5-flash-lite"
    OCTOPARSE_API_KEY: str = ""
    OCTOPARSE_TASK_GROUP_ID: int = 0

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()