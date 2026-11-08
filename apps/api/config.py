"""
KisanVision API - Application Configuration.
Environment variables and runtime defaults for the Agricultural Intelligence Gateway.
"""

import os
from pathlib import Path
from typing import List
from pydantic import BaseModel, Field


class APISettings(BaseModel):
    """
    Central API configuration settings.
    """
    APP_NAME: str = "KisanVision Agricultural Intelligence API"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = Field(default_factory=lambda: os.getenv("KISANVISION_ENV", "development"))
    DEBUG: bool = Field(default_factory=lambda: os.getenv("KISANVISION_DEBUG", "false").lower() == "true")

    HOST: str = Field(default_factory=lambda: os.getenv("KISANVISION_HOST", "0.0.0.0"))
    PORT: int = Field(default_factory=lambda: int(os.getenv("KISANVISION_PORT", "8000")))

    # Model and Data Paths
    MODELS_DIR: str = Field(default_factory=lambda: os.getenv("KISANVISION_MODELS_DIR", "ml/exports"))
    TAXONOMY_DIR: str = Field(default_factory=lambda: os.getenv("KISANVISION_TAXONOMY_DIR", "ml/configs/taxonomy"))
    
    # Supported Crops
    SUPPORTED_CROPS: List[str] = ["cotton", "rice", "chilli"]

    # Ingestion constraints
    MAX_IMAGE_SIZE_BYTES: int = 15 * 1024 * 1024  # 15 MB
    MIN_IMAGE_DIMENSION: int = 224

    # Confidence Gates
    HIGH_CONFIDENCE_THRESHOLD: float = 0.85
    AMBIGUITY_ENTROPY_THRESHOLD: float = 0.65


settings = APISettings()
