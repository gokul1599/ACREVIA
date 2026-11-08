"""
KisanVision Dedicated ML Inference Service - Configuration.
"""

import os
from pathlib import Path
from typing import List
from pydantic import BaseModel, Field


class InferenceServiceConfig(BaseModel):
    SERVICE_NAME: str = "KisanVision Dedicated ML Inference Service"
    SERVICE_VERSION: str = "1.0.0"
    TAXONOMY_VERSION: str = "1.0.0"
    PREPROCESSING_VERSION: str = "1.0.0"
    
    ENVIRONMENT: str = Field(default_factory=lambda: os.getenv("KISANVISION_ENV", "development"))
    HOST: str = Field(default_factory=lambda: os.getenv("INFERENCE_HOST", "0.0.0.0"))
    PORT: int = Field(default_factory=lambda: int(os.getenv("INFERENCE_PORT", "8001")))

    # Model Artifact Storage
    MODELS_DIR: str = Field(default_factory=lambda: os.getenv("KISANVISION_MODELS_DIR", "ml/exports"))
    TAXONOMY_DIR: str = Field(default_factory=lambda: os.getenv("KISANVISION_TAXONOMY_DIR", "ml/configs/taxonomy"))

    # Security & Ingestion Limits
    MAX_FILE_SIZE_BYTES: int = 10 * 1024 * 1024  # 10 MB
    ALLOWED_MIME_TYPES: List[str] = ["image/jpeg", "image/png", "image/webp"]
    ALLOWED_EXTENSIONS: List[str] = [".jpg", ".jpeg", ".png", ".webp"]

    # Target Scope
    SUPPORTED_CROPS: List[str] = ["cotton", "rice", "chilli"]

    # Uncertainty & Diagnostic Thresholds
    HIGH_CONFIDENCE_THRESHOLD: float = 0.85
    MINIMUM_USABLE_CONFIDENCE: float = 0.50
    MAXIMUM_NORMALIZED_ENTROPY: float = 0.65
    MINIMUM_PREDICTION_MARGIN: float = 0.15


config = InferenceServiceConfig()
