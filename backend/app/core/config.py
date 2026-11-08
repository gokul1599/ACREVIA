"""
ACREVIA - Application Configuration.
Enterprise-grade settings management with environment variable overrides.
"""

import os
from pathlib import Path
from typing import List, Optional
from pydantic import BaseModel, Field

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


class Settings(BaseModel):
    # Official Project Identity
    PROJECT_NAME: str = "ACREVIA"
    PROJECT_TITLE: str = "ACREVIA — Agricultural Intelligence Platform"
    PROJECT_VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"
    ENVIRONMENT: str = Field(default_factory=lambda: os.getenv("ACREVIA_ENV", "development"))
    DEBUG: bool = Field(default_factory=lambda: os.getenv("ACREVIA_DEBUG", "false").lower() == "true")

    # Network Gateway
    HOST: str = Field(default_factory=lambda: os.getenv("ACREVIA_HOST", "0.0.0.0"))
    PORT: int = Field(default_factory=lambda: int(os.getenv("ACREVIA_PORT", "8000")))
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
    ]

    # Database Configuration (PostgreSQL with SQLite fallback for testing)
    DATABASE_URL: str = Field(
        default_factory=lambda: os.getenv(
            "DATABASE_URL",
            "sqlite:///./acrevia_dev.db"  # Reliable local development default
        )
    )
    DATABASE_POOL_SIZE: int = Field(default_factory=lambda: int(os.getenv("DATABASE_POOL_SIZE", "10")))
    DATABASE_MAX_OVERFLOW: int = Field(default_factory=lambda: int(os.getenv("DATABASE_MAX_OVERFLOW", "20")))

    # Authentication & Cryptographic Security
    JWT_SECRET_KEY: str = Field(
        default_factory=lambda: os.getenv(
            "JWT_SECRET_KEY",
            "acrevia-dev-secret-key-change-in-production-0123456789abcdef"
        )
    )
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # Storage Abstraction
    STORAGE_PROVIDER: str = Field(default_factory=lambda: os.getenv("STORAGE_PROVIDER", "LOCAL"))
    STORAGE_LOCAL_DIR: str = Field(
        default_factory=lambda: os.getenv(
            "STORAGE_LOCAL_DIR",
            str(Path(__file__).resolve().parent.parent.parent / "storage" / "uploads")
        )
    )
    S3_BUCKET_NAME: Optional[str] = Field(default_factory=lambda: os.getenv("S3_BUCKET_NAME", None))
    S3_REGION: Optional[str] = Field(default_factory=lambda: os.getenv("S3_REGION", "ap-south-1"))
    ALLOWED_IMAGE_MIMES: List[str] = ["image/jpeg", "image/png", "image/webp"]
    MAX_IMAGE_SIZE_BYTES: int = 15728640

    # ML Inference Microservice Integration
    ML_INFERENCE_URL: str = Field(
        default_factory=lambda: os.getenv("ML_INFERENCE_URL", "http://localhost:8001")
    )
    ML_INFERENCE_TIMEOUT_SECONDS: float = 10.0

    # Distributed Rate Limiting & Redis Configuration
    REDIS_URL: Optional[str] = Field(default_factory=lambda: os.getenv("REDIS_URL", None))
    RATE_LIMIT_ENABLED: bool = Field(default_factory=lambda: os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true")
    RATE_LIMIT_FAIL_MODE: str = Field(default_factory=lambda: os.getenv("RATE_LIMIT_FAIL_MODE", "fail_open"))  # "fail_open" or "fail_closed"
    RATE_LIMIT_NAMESPACE: str = Field(default_factory=lambda: os.getenv("RATE_LIMIT_NAMESPACE", "acrevia"))

    # Free External Services Integration Suite
    # 1. GroqCloud (Free AI Inference)
    GROQ_API_KEY: Optional[str] = Field(default_factory=lambda: os.getenv("GROQ_API_KEY", None))
    GROQ_MODEL: str = Field(default_factory=lambda: os.getenv("GROQ_MODEL", "qwen/qwen3.8-27b"))
    GROQ_TIMEOUT_SECONDS: float = 12.0

    # 4. Copernicus Data Space Ecosystem (Sentinel-2 Satellite Imagery)
    COPERNICUS_CLIENT_ID: Optional[str] = Field(default_factory=lambda: os.getenv("COPERNICUS_CLIENT_ID", None))
    COPERNICUS_CLIENT_SECRET: Optional[str] = Field(default_factory=lambda: os.getenv("COPERNICUS_CLIENT_SECRET", None))
    COPERNICUS_BASE_URL: str = Field(default_factory=lambda: os.getenv("COPERNICUS_BASE_URL", "https://catalogue.dataspace.copernicus.eu/odata/v1"))

    # 5. Hugging Face (Optional Hub & Model Metadata)
    HF_TOKEN: Optional[str] = Field(default_factory=lambda: os.getenv("HF_TOKEN", None))

    # 6. Open-Meteo (Agrometeorological Forecast & Historical API - Free Public)
    OPEN_METEO_API_URL: str = Field(default_factory=lambda: os.getenv("OPEN_METEO_API_URL", "https://api.open-meteo.com/v1/forecast"))

    # 7. data.gov.in (Indian Government Open Agricultural Datasets - Agmarknet Mandis)
    DATA_GOV_IN_API_KEY: Optional[str] = Field(default_factory=lambda: os.getenv("DATA_GOV_IN_API_KEY", None))
    DATA_GOV_IN_RESOURCE_ID: str = Field(default_factory=lambda: os.getenv("DATA_GOV_IN_RESOURCE_ID", "9ef84268-d588-465a-a308-a864a43d0070"))
    DATA_GOV_IN_TIMEOUT_SECONDS: float = 10.0

    # Agricultural Scope
    TARGET_GEOGRAPHY: str = "Telangana, India"
    SUPPORTED_CROPS: List[str] = ["cotton", "rice", "chilli"]
    SUPPORTED_LANGUAGES: List[str] = ["te", "en", "hi"]
    MAX_IMAGE_UPLOAD_BYTES: int = 10 * 1024 * 1024  # 10 MB


settings = Settings()
