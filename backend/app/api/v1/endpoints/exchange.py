"""
ACREVIA - Agricultural Data Exchange & Portability Endpoints.
Stage 14: Data Export, Data Import, Conflict Tracking, Cryptographic Manifests, and Mapping Profiles.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from backend.app.database.session import get_db
from backend.app.models.user import User
from backend.app.schemas.exchange import (
    DataExportRequest,
    DataImportRequest,
    DataExchangeJobResponse,
    DataMappingProfileCreate,
    DataMappingProfileResponse,
)
from backend.app.security.dependencies import get_current_user
from backend.app.services.exchange_service import DataExchangeService
from backend.app.models.exchange import DataExchangeJob

router = APIRouter(prefix="/exchange", tags=["ACREVIA Exchange"])


@router.post("/export", response_model=DataExchangeJobResponse, status_code=status.HTTP_201_CREATED)
def request_data_export(
    request: DataExportRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Creates an agricultural data export package with cryptographic SHA-256 manifest.
    Supports JSON, CSV, GeoJSON, and multi-file ZIP archives.
    """
    job = DataExchangeService.create_export_job(
        db=db,
        user_id=current_user.id,
        farm_id=request.farm_id,
        categories=request.categories,
        export_format=request.format,
        redact_pii=request.redact_pii,
        redact_gps=request.redact_gps,
    )
    return job


@router.get("/export/{job_id}", response_model=DataExchangeJobResponse, status_code=status.HTTP_200_OK)
def get_export_job(
    job_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    job = db.get(DataExchangeJob, job_id)
    if not job or job.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Export job not found")
    return job


@router.get("/download/{job_id}", status_code=status.HTTP_200_OK)
def download_export_artifact(
    job_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    job = db.get(DataExchangeJob, job_id)
    if not job or job.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Export job not found")

    payload = DataExchangeService.get_export_payload(job_id)
    if not payload:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Export artifact not found or expired")

    mime_type, data_bytes = payload
    extension = "zip" if "zip" in mime_type else "json" if "json" in mime_type else "csv"
    headers = {
        "Content-Disposition": f'attachment; filename="acrevia-export-{job_id[:8]}.{extension}"'
    }
    return Response(content=data_bytes, media_type=mime_type, headers=headers)


@router.post("/import", response_model=DataExchangeJobResponse, status_code=status.HTTP_201_CREATED)
def request_data_import(
    request: DataImportRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Imports agricultural data into ACREVIA without silent overwrites.
    Retains existing records and marks conflicts for explicit verification.
    """
    job = DataExchangeService.create_import_job(
        db=db,
        user_id=current_user.id,
        farm_id=request.farm_id,
        target_category=request.target_category,
        data_payload=request.data_payload,
        data_format=request.format,
        mapping_profile_id=request.mapping_profile_id,
        preserve_conflicts=request.preserve_conflicts,
    )
    return job


@router.get("/import/{job_id}", response_model=DataExchangeJobResponse, status_code=status.HTTP_200_OK)
def get_import_job(
    job_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    job = db.get(DataExchangeJob, job_id)
    if not job or job.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Import job not found")
    return job


@router.post("/mapping-profiles", response_model=DataMappingProfileResponse, status_code=status.HTTP_201_CREATED)
def create_mapping_profile(
    request: DataMappingProfileCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = DataExchangeService.create_mapping_profile(
        db=db,
        user_id=current_user.id,
        name=request.name,
        source_format=request.source_format,
        target_entity=request.target_entity,
        mapping_rules=request.mapping_rules,
    )
    return profile


@router.get("/mapping-profiles", response_model=List[DataMappingProfileResponse], status_code=status.HTTP_200_OK)
def list_mapping_profiles(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return DataExchangeService.list_mapping_profiles(db=db, user_id=current_user.id)
