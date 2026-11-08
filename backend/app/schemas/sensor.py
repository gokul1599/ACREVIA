"""
ACREVIA - IoT & Sensor Ecosystem Pydantic Schemas.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel, Field, ConfigDict


class SensorDeviceCreate(BaseModel):
    device_serial_number: str = Field(..., min_length=4, max_length=100)
    device_category: Literal["SOIL_PROBE", "WEATHER_STATION", "LEAF_WETNESS", "NPK_PROBE"]
    plot_id: Optional[str] = None
    firmware_version: Optional[str] = "1.0.0"


class SensorDeviceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    farm_id: str
    plot_id: Optional[str] = None
    device_serial_number: str
    device_category: str
    status: str
    firmware_version: Optional[str] = None
    last_heartbeat_at: Optional[datetime] = None
    auth_token: Optional[str] = Field(None, description="Returned only during device registration")


class SensorMeasurementsDict(BaseModel):
    soil_moisture_pct: Optional[float] = Field(None, ge=0.0, le=100.0)
    soil_temperature_c: Optional[float] = Field(None, ge=-10.0, le=70.0)
    ambient_temperature_c: Optional[float] = Field(None, ge=-20.0, le=65.0)
    relative_humidity_pct: Optional[float] = Field(None, ge=0.0, le=100.0)
    leaf_wetness_pct: Optional[float] = Field(None, ge=0.0, le=100.0)
    solar_radiation_w_m2: Optional[float] = Field(None, ge=0.0, le=2000.0)


class SensorTelemetryPush(BaseModel):
    device_id: str
    plot_id: str
    timestamp: datetime
    measurements: SensorMeasurementsDict
    battery_pct: Optional[float] = Field(None, ge=0.0, le=100.0)
    signal_rssi: Optional[int] = Field(None, ge=-140, le=0)


class SensorTelemetryResponse(BaseModel):
    status: str
    measurement_id: str
    data_quality_flag: str
    calibration_valid: bool
    quality_notes: Optional[str] = None


class SensorMeasurementItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    timestamp: datetime
    soil_moisture_pct: Optional[float] = None
    soil_temperature_c: Optional[float] = None
    ambient_temperature_c: Optional[float] = None
    relative_humidity_pct: Optional[float] = None
    leaf_wetness_pct: Optional[float] = None
    solar_radiation_w_m2: Optional[float] = None
    data_quality_flag: str


class SensorPlotTelemetryHistoryResponse(BaseModel):
    plot_id: str
    count: int
    measurements: List[SensorMeasurementItem]


class SensorCalibrationCreate(BaseModel):
    valid_days: int = Field(180, ge=1, le=730)
    calibrated_by: str = Field(..., min_length=2, max_length=100)
    coefficients: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None


class SensorCalibrationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    device_id: str
    calibrated_at: datetime
    valid_until: datetime
    calibrated_by: str
    is_valid: bool
