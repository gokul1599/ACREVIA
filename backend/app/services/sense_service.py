"""
ACREVIA - IoT & Sensor Ecosystem Service (Pillar C: Acrevia Sense).
Handles hardware device registration, token authentication, telemetry stream ingestion,
quality anomaly checks (stuck, spike, bounds), and calibration validity tracking.
"""

import hashlib
import secrets
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import select, and_, desc

from backend.app.models.sensor import SensorDevice, SensorMeasurement, SensorCalibration
from backend.app.models.farm import Farm, Plot
from backend.app.core.exceptions import ValidationError, NotFoundError, AuthenticationError


class SenseService:
    @staticmethod
    def hash_token(token: str) -> str:
        """SHA-256 hash of device authentication secret."""
        return hashlib.sha256(token.encode("utf-8")).hexdigest()

    @staticmethod
    def register_device(
        db: Session,
        farm_id: str,
        serial_number: str,
        category: str,
        plot_id: Optional[str] = None,
        firmware_version: Optional[str] = "1.0.0"
    ) -> Tuple[SensorDevice, str]:
        """Registers a field hardware unit and generates a private push token."""
        farm = db.get(Farm, farm_id)
        if not farm or farm.is_archived:
            raise NotFoundError("Farm not found.")

        if plot_id:
            plot = db.get(Plot, plot_id)
            if not plot or plot.is_archived or plot.farm_id != farm_id:
                raise ValidationError("Plot does not belong to the specified farm.")

        existing = db.execute(
            select(SensorDevice).where(SensorDevice.device_serial_number == serial_number)
        ).scalar_one_or_none()
        if existing:
            raise ValidationError(f"Sensor device with serial '{serial_number}' is already registered.")

        raw_token = f"dev_sec_{secrets.token_hex(24)}"
        hashed_token = SenseService.hash_token(raw_token)

        device = SensorDevice(
            farm_id=farm_id,
            plot_id=plot_id,
            device_serial_number=serial_number,
            device_category=category,
            auth_token_hash=hashed_token,
            firmware_version=firmware_version,
            status="ACTIVE"
        )
        db.add(device)
        db.commit()
        db.refresh(device)

        return device, raw_token

    @staticmethod
    def authenticate_device(db: Session, device_id: str, raw_token: str) -> SensorDevice:
        """Verifies device token and returns active device."""
        device = db.get(SensorDevice, device_id)
        if not device or device.status != "ACTIVE":
            raise AuthenticationError("Invalid or inactive sensor device.")

        if device.auth_token_hash != SenseService.hash_token(raw_token):
            raise AuthenticationError("Device authentication failed.")

        return device

    @staticmethod
    def check_calibration_status(db: Session, device_id: str) -> Tuple[bool, Optional[str]]:
        """
        Checks if the device has a valid active calibration.
        Returns: (is_calibrated, warning_note)
        """
        now = datetime.now(timezone.utc)
        latest_cal = db.execute(
            select(SensorCalibration).where(
                and_(
                    SensorCalibration.device_id == device_id,
                    SensorCalibration.is_valid == True
                )
            ).order_by(desc(SensorCalibration.calibrated_at)).limit(1)
        ).scalar_one_or_none()

        if not latest_cal:
            return False, "Device has no calibration record on file."

        # SQLite/PostgreSQL timezone handling
        valid_until = latest_cal.valid_until
        if valid_until.tzinfo is None:
            valid_until = valid_until.replace(tzinfo=timezone.utc)

        if now > valid_until:
            return False, f"Calibration expired on {valid_until.strftime('%Y-%m-%d')}."

        return True, None

    @staticmethod
    def validate_measurement_quality(
        db: Session,
        device_id: str,
        measurements: Dict[str, Any]
    ) -> Tuple[str, Optional[str]]:
        """
        Runs quality control gates on new telemetry payload.
        Flags: VALID, SUSPECT_STUCK, SUSPECT_SPIKE, UNCALIBRATED, OUT_OF_BOUNDS
        """
        # 1. Biophysical Bounds Check
        sm = measurements.get("soil_moisture_pct")
        if sm is not None and not (0.0 <= sm <= 100.0):
            return "OUT_OF_BOUNDS", f"Soil moisture {sm}% outside [0, 100] bounds."

        rh = measurements.get("relative_humidity_pct")
        if rh is not None and not (0.0 <= rh <= 100.0):
            return "OUT_OF_BOUNDS", f"Relative humidity {rh}% outside [0, 100] bounds."

        temp = measurements.get("ambient_temperature_c")
        if temp is not None and not (-15.0 <= temp <= 65.0):
            return "OUT_OF_BOUNDS", f"Ambient temperature {temp}C outside realistic bounds."

        # 2. Calibration Check
        is_calibrated, cal_note = SenseService.check_calibration_status(db, device_id)
        if not is_calibrated:
            return "UNCALIBRATED", f"Uncalibrated reading: {cal_note}"

        # 3. Stuck Sensor Check (Inspect last 5 readings)
        recent = db.execute(
            select(SensorMeasurement).where(
                SensorMeasurement.device_id == device_id
            ).order_by(desc(SensorMeasurement.timestamp)).limit(5)
        ).scalars().all()

        if len(recent) >= 4 and sm is not None:
            prev_values = [r.soil_moisture_pct for r in recent if r.soil_moisture_pct is not None]
            if len(prev_values) >= 4 and all(abs(v - sm) < 0.001 for v in prev_values):
                return "SUSPECT_STUCK", "Soil moisture sensor reported identical value across 5 consecutive packets."

        return "VALID", None

    @staticmethod
    def ingest_telemetry(
        db: Session,
        device_id: str,
        plot_id: str,
        timestamp: datetime,
        measurements: Dict[str, Any],
        battery_pct: Optional[float] = None,
        signal_rssi: Optional[int] = None
    ) -> SensorMeasurement:
        """Ingests raw sensor telemetry packet with automated quality verification."""
        device = db.get(SensorDevice, device_id)
        if not device or device.status != "ACTIVE":
            raise NotFoundError("Sensor device not found or inactive.")

        plot = db.get(Plot, plot_id)
        if not plot or plot.is_archived:
            raise NotFoundError("Plot not found.")

        flag, quality_notes = SenseService.validate_measurement_quality(db, device_id, measurements)

        measurement = SensorMeasurement(
            device_id=device_id,
            plot_id=plot_id,
            timestamp=timestamp,
            soil_moisture_pct=measurements.get("soil_moisture_pct"),
            soil_temperature_c=measurements.get("soil_temperature_c"),
            ambient_temperature_c=measurements.get("ambient_temperature_c"),
            relative_humidity_pct=measurements.get("relative_humidity_pct"),
            leaf_wetness_pct=measurements.get("leaf_wetness_pct"),
            solar_radiation_w_m2=measurements.get("solar_radiation_w_m2"),
            battery_pct=battery_pct,
            signal_rssi=signal_rssi,
            data_quality_flag=flag,
            quality_notes=quality_notes
        )
        db.add(measurement)

        # Update device heartbeat
        device.last_heartbeat_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(measurement)
        return measurement

    @staticmethod
    def record_calibration(
        db: Session,
        device_id: str,
        calibrated_by: str,
        valid_days: int = 180,
        coefficients: Optional[Dict[str, Any]] = None,
        notes: Optional[str] = None
    ) -> SensorCalibration:
        """Records a physical calibration certificate for a device."""
        device = db.get(SensorDevice, device_id)
        if not device:
            raise NotFoundError("Sensor device not found.")

        now = datetime.now(timezone.utc)
        valid_until = now + timedelta(days=valid_days)

        cal = SensorCalibration(
            device_id=device_id,
            calibrated_at=now,
            valid_until=valid_until,
            calibrated_by=calibrated_by,
            calibration_coefficients_json=coefficients or {},
            is_valid=True,
            notes=notes
        )
        db.add(cal)
        db.commit()
        db.refresh(cal)
        return cal

    @staticmethod
    def get_plot_telemetry(db: Session, plot_id: str, hours: int = 48) -> List[SensorMeasurement]:
        """Returns recent sensor measurements for a plot."""
        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
        stmt = select(SensorMeasurement).where(
            and_(
                SensorMeasurement.plot_id == plot_id,
                SensorMeasurement.timestamp >= cutoff
            )
        ).order_by(SensorMeasurement.timestamp.desc())

        return list(db.execute(stmt).scalars().all())
