"""
KisanVision Inference Service - API Route Handlers.
"""

from typing import Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status
from ml.inference_service.app.core.config import config
from ml.inference_service.app.schemas.response import (
    InferencePredictionResponse,
    ModelInfoResponse
)
from ml.inference_service.app.services.inference_engine import DedicatedInferenceEngine

router = APIRouter()
engine = DedicatedInferenceEngine()


@router.get(
    "/health",
    summary="Health & Readiness Probe"
)
def get_health():
    """Returns service health and operational status."""
    return {
        "status": "HEALTHY",
        "service": config.SERVICE_NAME,
        "version": config.SERVICE_VERSION,
        "environment": config.ENVIRONMENT,
        "supported_crops": config.SUPPORTED_CROPS,
        "execution_device": "AMD Ryzen 5 5500U CPU (ONNX Runtime)"
    }


@router.get(
    "/model-info",
    response_model=ModelInfoResponse,
    summary="Model Artifact & Governance Telemetry"
)
def get_model_info():
    """Returns metadata regarding active models, taxonomy version, and quantization."""
    inventory = engine.loader.get_inventory()
    return ModelInfoResponse(
        model_identifier="kisanvision_multicrop_mobilenet_v3_small",
        model_version=config.SERVICE_VERSION,
        architecture="mobilenet_v3_small",
        supported_crops=config.SUPPORTED_CROPS,
        supported_task="foliar_crop_disease_differential_diagnosis",
        taxonomy_version=config.TAXONOMY_VERSION,
        preprocessing_version=config.PREPROCESSING_VERSION,
        artifact_status="INT8_OPTIMIZED_APPROVED_INTERNAL_TESTING",
        quantization="INT8_DYNAMIC",
        inference_provider="ONNXRuntime_CPU",
        device="AMD_Ryzen_CPU",
        active_models=inventory
    )


@router.post(
    "/api/v1/predict",
    response_model=InferencePredictionResponse,
    summary="Foliar Crop Disease Diagnostic Inference"
)
async def predict_foliar_disease(
    image: UploadFile = File(..., description="Foliar plant image (JPEG/PNG/WebP)"),
    crop_type: str = Form(..., description="Target crop: cotton, rice, or chilli"),
    language: str = Form("en", description="Preferred response language: te, en, or hi"),
    farm_id: Optional[str] = Form(None, description="Optional tenant farm ID"),
    plot_id: Optional[str] = Form(None, description="Optional plot ID")
):
    """
    Executes agricultural diagnostic inference pipeline:
    1. Upload & MIME magic byte validation.
    2. Image quality gate (blur / exposure).
    3. Foliar botanical vegetation validation.
    4. INT8 ONNX execution with temperature scaling.
    5. Uncertainty & abstention decision state generation.
    6. Structured differential response creation.
    """
    crop_clean = crop_type.lower().strip()
    if crop_clean not in config.SUPPORTED_CROPS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported crop: '{crop_type}'. Supported crops are: {config.SUPPORTED_CROPS}"
        )

    image_bytes = await image.read()
    if len(image_bytes) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty (0 bytes)."
        )

    if len(image_bytes) > config.MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds maximum upload limit of {config.MAX_FILE_SIZE_BYTES // (1024 * 1024)} MB."
        )

    try:
        response = engine.predict(
            image_bytes=image_bytes,
            crop_type=crop_clean,
            filename=image.filename or "upload.jpg",
            preferred_language=language
        )
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Inference pipeline execution error: {str(e)}"
        )
