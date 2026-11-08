"""
KisanVision API - CropVision Inference Endpoints.
Serves real-time foliar pathology diagnostics, image quality validation,
and differential candidate ranking.
"""

from typing import List, Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status
from apps.api.config import settings
from apps.api.schemas.vision import VisionDiagnosisResponse, ModelInfoResponse
from apps.api.services.vision_service import vision_service

router = APIRouter(prefix="/vision", tags=["CropVision"])


@router.get(
    "/models",
    response_model=List[ModelInfoResponse],
    summary="List Active Vision Diagnostic Models"
)
def list_models():
    """Returns active vision backbones, class counts, and INT8 quantization status."""
    return vision_service.get_models_metadata()


@router.post(
    "/predict",
    response_model=VisionDiagnosisResponse,
    summary="Foliar Crop Disease Diagnosis"
)
async def predict_crop_disease(
    image: UploadFile = File(..., description="Foliar plant photograph (JPEG/PNG)"),
    crop_type: str = Form(..., description="Target crop: cotton, rice, or chilli"),
    language: str = Form("en", description="Preferred response language: te, en, or hi"),
    farm_id: Optional[str] = Form(None, description="Optional farm identifier"),
    plot_id: Optional[str] = Form(None, description="Optional plot identifier")
):
    """
    Submits a foliar leaf image for multi-stage agricultural analysis:
    1. Rejects blurry or poorly illuminated imagery.
    2. Verifies presence of natural foliar vegetation.
    3. Runs CPU-quantized INT8 ONNX vision model.
    4. Evaluates prediction entropy, uncertainty, and margin.
    5. Returns differential diagnosis with CIBRC chemical safety advisory.
    """
    crop_clean = crop_type.lower().strip()
    if crop_clean not in settings.SUPPORTED_CROPS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported crop: '{crop_type}'. Supported crops are: {settings.SUPPORTED_CROPS}"
        )

    # Read image contents
    image_bytes = await image.read()
    if len(image_bytes) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty. Please provide a valid JPEG or PNG image."
        )

    if len(image_bytes) > settings.MAX_IMAGE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Image size exceeds maximum limit of {settings.MAX_IMAGE_SIZE_BYTES // (1024 * 1024)} MB."
        )

    try:
        diagnosis_response = vision_service.diagnose_image(
            image_bytes=image_bytes,
            crop_type=crop_clean,
            preferred_language=language
        )
        return diagnosis_response
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Inference pipeline error: {str(e)}"
        )
