"""
ACREVIA - IoT & Sensor Ecosystem REST API (Pillar C: Acrevia Sense).
Handles hardware device registration, telemetry push, data quality verification,
and calibration ledger recording.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Header, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import select

from backend.app.database.session import get_db
from backend.app.models.user import User
from backend.app.models.sensor import SensorDevice
from backend.app.schemas.sensor import (
    SensorDeviceCreate,
    SensorDeviceResponse,
    SensorTelemetryPush,
    SensorTelemetryResponse,
    SensorMeasurementItem,
    SensorPlotTelemetryHistoryResponse,
    SensorCalibrationCreate,
    SensorCalibrationResponse
)
from backend.app.security.dependencies import get_current_user
from backend.app.services.sense_service import SenseService
from backend.app.core.exceptions import AuthenticationError

router = APIRouter(prefix="/sense", tags=["Acrevia Sense"])


@router.post("/farms/{farm_id}/devices", response_model=SensorDeviceResponse, status_code=status.HTTP_201_CREATED)
def register_sensor_device(
    farm_id: str,
    payload: SensorDeviceCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Registers a field IoT node and returns a unique authentication secret."""
    device, raw_token = SenseService.register_device(
        db=db,
        farm_id=farm_id,
        serial_number=payload.device_serial_number,
        category=payload.device_category,
        plot_id=payload.plot_id,
        firmware_version=payload.firmware_version
    )
    return SensorDeviceResponse(
        id=device.id,
        farm_id=device.farm_id,
        plot_id=device.plot_id,
        device_serial_number=device.device_serial_number,
        device_category=device.device_category,
        status=device.status,
        firmware_version=device.firmware_version,
        last_heartbeat_at=device.last_heartbeat_at,
        auth_token=raw_token
    )


@router.get("/farms/{farm_id}/devices", response_model=List[SensorDeviceResponse])
def list_farm_devices(
    farm_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Lists registered sensor devices for a farm."""
    stmt = select(SensorDevice).where(SensorDevice.farm_id == farm_id)
    devices = list(db.execute(stmt).scalars().all())
    return [
        SensorDeviceResponse(
            id=d.id,
            farm_id=d.farm_id,
            plot_id=d.plot_id,
            device_serial_number=d.device_serial_number,
            device_category=d.device_category,
            status=d.status,
            firmware_version=d.firmware_version,
            last_heartbeat_at=d.last_heartbeat_at
        )
        for d in devices
    ]


@router.post("/telemetry", response_model=SensorTelemetryResponse, status_code=status.HTTP_201_CREATED)
def ingest_telemetry_stream(
    payload: SensorTelemetryPush,
    authorization: Optional[str] = Header(None),
    x_device_token: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """
    Ingests sensor telemetry stream.
    Authenticates via Bearer token in Authorization header or X-Device-Token.
    """
    token = x_device_token
    if not token and authorization:
        parts = authorization.split(" ")
        if len(parts) == 2 and parts[0].lower() == "bearer":
            token = parts[1]

    if not token:
        raise AuthenticationError("Device authentication token required.")

    # Authenticate device
    SenseService.authenticate_device(db, device_id=payload.device_id, raw_token=token)

    # Ingest telemetry
    measurement = SenseService.ingest_telemetry(
        db=db,
        device_id=payload.device_id,
        plot_id=payload.plot_id,
        timestamp=payload.timestamp,
        measurements=payload.measurements.model_dump(),
        battery_pct=payload.battery_pct,
        signal_rssi=payload.signal_rssi
    )

    is_calibrated, _ = SenseService.check_calibration_status(db, payload.device_id)

    return SensorTelemetryResponse(
        status="ACCEPTED",
        measurement_id=measurement.id,
        data_quality_flag=measurement.data_quality_flag,
        calibration_valid=is_calibrated,
        quality_notes=measurement.quality_notes
    )


@router.get("/plots/{plot_id}/telemetry", response_model=SensorPlotTelemetryHistoryResponse)
def get_plot_telemetry_history(
    plot_id: str,
    hours: int = Query(48, ge=1, le=720),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieves recent sensor measurements and quality flags for a plot."""
    measurements = SenseService.get_plot_telemetry(db=db, plot_id=plot_id, hours=hours)
    return SensorPlotTelemetryHistoryResponse(
        plot_id=plot_id,
        count=len(measurements),
        measurements=[SensorMeasurementItem.model_validate(m) for m in measurements]
    )


@router.post("/devices/{device_id}/calibration", response_model=SensorCalibrationResponse, status_code=status.HTTP_201_CREATED)
def record_device_calibration(
    device_id: str,
    payload: SensorCalibrationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Records a physical sensor calibration event in the ledger."""
    cal = SenseService.record_calibration(
        db=db,
        device_id=device_id,
        calibrated_by=payload.calibrated_by,
        valid_days=payload.valid_days,
        coefficients=payload.coefficients,
        notes=payload.notes
    )
    return cal
