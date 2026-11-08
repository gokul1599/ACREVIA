"""
ACREVIA - Canonical Agricultural Standards, Taxonomy & Connector Health Endpoints.
Stage 14: Canonical units, unit conversions, multi-lingual crop taxonomy, and adapter health checks.
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status

from backend.app.schemas.interoperability import (
    UnitConversionRequest,
    UnitConversionResponse,
    CropTaxonomyResponse,
)
from backend.app.services.canonical_standards import CanonicalStandardsService
from backend.app.services.connector_bridge import ConnectorBridgeManager

router = APIRouter(prefix="/standards", tags=["ACREVIA Standards"])


@router.get("/units", status_code=status.HTTP_200_OK)
def get_supported_units() -> Dict[str, List[str]]:
    """
    Returns supported measurement categories and units in the canonical registry.
    """
    return {cat: list(units.keys()) for cat, units in CanonicalStandardsService.CONVERSION_FACTORS.items()}


@router.post("/convert-unit", response_model=UnitConversionResponse, status_code=status.HTTP_200_OK)
def convert_unit(request: UnitConversionRequest):
    """
    Performs deterministic conversion between agricultural units.
    """
    try:
        converted, factor = CanonicalStandardsService.convert_unit(
            value=request.value,
            from_unit=request.from_unit,
            to_unit=request.to_unit,
            category=request.category,
        )
        return UnitConversionResponse(
            original_value=request.value,
            original_unit=request.from_unit,
            converted_value=converted,
            converted_unit=request.to_unit,
            category=request.category,
            conversion_factor=factor,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/taxonomy/crops", status_code=status.HTTP_200_OK)
def list_crop_taxonomy() -> Dict[str, Any]:
    """
    Returns canonical multilingual crop taxonomy (Cotton, Rice, Chilli) across English, Telugu, and Hindi.
    """
    return CanonicalStandardsService.get_crop_taxonomy()


@router.get("/taxonomy/crops/{crop_code}", status_code=status.HTTP_200_OK)
def get_crop_taxonomy_entry(crop_code: str) -> Dict[str, Any]:
    try:
        return CanonicalStandardsService.get_crop_taxonomy(crop_code=crop_code)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/health", status_code=status.HTTP_200_OK)
def check_connector_health() -> List[Dict[str, Any]]:
    """
    Executes live health checks across all ACREVIA Bridge integration connectors.
    """
    return ConnectorBridgeManager.run_all_health_checks()
