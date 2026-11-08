"""
ACREVIA - Digital Twin Core Service (Pillar A: ACREVIA Twin).
Aggregates multi-source agricultural telemetry, enforces 8-tier provenance,
computes completeness vectors, and manages immutable state snapshots.
"""

import hashlib
import json
import uuid
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, desc
from fastapi import HTTPException, status

from backend.app.models.user import User
from backend.app.models.farm import Farm, Plot
from backend.app.models.crop import CropSeason
from backend.app.models.sensor import SensorDevice, SensorMeasurement
from backend.app.models.satellite import SatelliteObservation
from backend.app.models.operation import FarmOperation
from backend.app.models.digital_twin import (
    FarmTwin,
    TwinSnapshot,
    TwinStateRecord,
    TwinSynchronizationEvent,
)
from backend.app.schemas.digital_twin import (
    FarmTwinResponse,
    TwinSnapshotSummaryResponse,
    TwinSnapshotDetailResponse,
    TwinStateRecordResponse,
    DataCompletenessResponse,
    TwinReconcileResponse,
)

PROVENANCE_HIERARCHY = [
    "MEASURED",
    "FARMER_REPORTED",
    "EXPERT_REVIEWED",
    "AI_ESTIMATED",
    "PROVIDER_OBSERVATION",
    "SIMULATED",
    "INFERRED",
    "UNKNOWN",
]


class TwinService:
    @staticmethod
    def get_or_create_twin(farm: Farm, db: Session) -> FarmTwin:
        twin = db.query(FarmTwin).filter(FarmTwin.farm_id == farm.id).first()
        if not twin:
            twin = FarmTwin(
                farm_id=farm.id,
                twin_version=1,
                state_status="SYNCHRONIZED",
                completeness_score=0.0,
                last_synchronized_at=datetime.now(timezone.utc),
            )
            db.add(twin)
            db.commit()
            db.refresh(twin)
            # Create initial baseline snapshot
            TwinService.create_snapshot(farm=farm, user=None, db=db, twin=twin)
        return twin

    @staticmethod
    def calculate_completeness(farm: Farm, db: Session) -> DataCompletenessResponse:
        plots = db.query(Plot).filter(Plot.farm_id == farm.id).all()
        plot_ids = [p.id for p in plots]

        # 1. Cadastral Boundary (100 if plots exist with acreage > 0)
        has_plots = len(plots) > 0 and all(p.acreage > 0 for p in plots)
        cadastral_score = 100.0 if has_plots else 0.0

        # 2. Soil Profile
        soil_score = 100.0 if any(p.soil_type for p in plots) else 40.0

        # 3. Active Crop Season
        active_seasons = (
            db.query(CropSeason)
            .filter(CropSeason.plot_id.in_(plot_ids), CropSeason.status == "ACTIVE")
            .all()
            if plot_ids
            else []
        )
        season_score = 100.0 if active_seasons else 0.0

        # 4. Sowing Date
        sowing_score = (
            100.0
            if active_seasons and all(s.sowing_date is not None for s in active_seasons)
            else 0.0
        )

        # 5. IoT Sensor Telemetry
        sensors = (
            db.query(SensorDevice).filter(SensorDevice.plot_id.in_(plot_ids)).all()
            if plot_ids
            else []
        )
        sensor_score = 100.0 if sensors else 50.0

        # 6. Satellite Coverage
        satellite_obs = (
            db.query(SatelliteObservation)
            .filter(SatelliteObservation.plot_id.in_(plot_ids))
            .all()
            if plot_ids
            else []
        )
        satellite_score = 100.0 if satellite_obs else 60.0

        # 7. Operations & Scouting
        operations = (
            db.query(FarmOperation)
            .filter(FarmOperation.plot_id.in_(plot_ids))
            .all()
            if plot_ids
            else []
        )
        scouting_score = 100.0 if operations else 50.0

        dimensions = {
            "cadastral_boundary": cadastral_score,
            "soil_profile": soil_score,
            "crop_season_active": season_score,
            "sowing_date": sowing_score,
            "iot_telemetry": sensor_score,
            "satellite_coverage": satellite_score,
            "pest_scouting": scouting_score,
        }

        # Weighted calculation
        weights = {
            "cadastral_boundary": 0.15,
            "soil_profile": 0.15,
            "crop_season_active": 0.20,
            "sowing_date": 0.15,
            "iot_telemetry": 0.15,
            "satellite_coverage": 0.10,
            "pest_scouting": 0.10,
        }
        overall = sum(dimensions[k] * weights[k] for k in dimensions)

        missing = []
        recommendations = []
        if season_score == 0.0:
            missing.append("active_crop_season")
            recommendations.append("Register an active crop season for accurate agronomic modeling.")
        if sowing_score == 0.0 and active_seasons:
            missing.append("sowing_date")
            recommendations.append("Record crop sowing date to enable thermal GDD stage tracking.")
        if soil_score < 100.0:
            missing.append("soil_texture_profile")
            recommendations.append("Specify soil type (e.g. Vertisol/Black Cotton, Chalkas) for water retention calculation.")
        if sensor_score < 100.0:
            recommendations.append("Connect calibrated soil moisture sensors for empirical irrigation triggers.")

        return DataCompletenessResponse(
            farm_id=farm.id,
            overall_score=round(overall, 1),
            dimensions=dimensions,
            missing_critical_fields=missing,
            recommendations=recommendations,
        )

    @staticmethod
    def create_snapshot(
        farm: Farm,
        user: Optional[User],
        db: Session,
        twin: Optional[FarmTwin] = None,
    ) -> TwinSnapshot:
        if not twin:
            twin = db.query(FarmTwin).filter(FarmTwin.farm_id == farm.id).first()
            if not twin:
                twin = FarmTwin(
                    farm_id=farm.id,
                    twin_version=1,
                    state_status="SYNCHRONIZED",
                    completeness_score=0.0,
                    last_synchronized_at=datetime.now(timezone.utc),
                )
                db.add(twin)
                db.flush()

        plots = db.query(Plot).filter(Plot.farm_id == farm.id).all()
        plot_ids = [p.id for p in plots]

        completeness = TwinService.calculate_completeness(farm=farm, db=db)

        # Build state payload
        state_payload = {
            "farm_id": farm.id,
            "farm_name": farm.name,
            "district": farm.district,
            "mandal": farm.mandal,
            "total_acreage": farm.total_acreage,
            "plots": [],
        }

        records_to_create = []
        now_utc = datetime.now(timezone.utc)

        for plot in plots:
            active_season = (
                db.query(CropSeason)
                .filter(CropSeason.plot_id == plot.id, CropSeason.status == "ACTIVE")
                .first()
            )

            plot_dict: Dict[str, Any] = {
                "plot_id": plot.id,
                "name": plot.name,
                "area_hectares": plot.acreage * 0.404686,
                "soil_type": plot.soil_type or "BLACK_COTTON",
            }

            if active_season:
                c_name = active_season.crop.name_en if active_season.crop else active_season.crop_id
                v_name = active_season.variety.name if active_season.variety else None
                plot_dict["active_season"] = {
                    "season_id": active_season.id,
                    "crop_name": c_name,
                    "variety_name": v_name,
                    "sowing_date": active_season.sowing_date.isoformat() if active_season.sowing_date else None,
                    "growth_stage": active_season.current_stage,
                }
                # Record: Crop stage
                records_to_create.append(
                    {
                        "entity_type": "CROP",
                        "entity_id": active_season.id,
                        "property_name": "growth_stage",
                        "property_value_json": {"stage": active_season.current_stage},
                        "unit": "stage_name",
                        "provenance_type": "FARMER_REPORTED",
                        "observed_at": now_utc,
                    }
                )

            # Record: Soil type
            records_to_create.append(
                {
                    "entity_type": "SOIL",
                    "entity_id": plot.id,
                    "property_name": "soil_type",
                    "property_value_json": {"type": plot.soil_type or "BLACK_COTTON"},
                    "unit": "usda_classification",
                    "provenance_type": "INFERRED" if not plot.soil_type else "FARMER_REPORTED",
                    "observed_at": now_utc,
                }
            )

            # Recent telemetry
            latest_meas = (
                db.query(SensorMeasurement)
                .filter(SensorMeasurement.plot_id == plot.id)
                .order_by(desc(SensorMeasurement.timestamp))
                .first()
            )
            if latest_meas and latest_meas.soil_moisture_pct is not None:
                plot_dict["latest_sensor_reading"] = {
                    "parameter": "soil_moisture_pct",
                    "value": latest_meas.soil_moisture_pct,
                    "unit": "%",
                    "recorded_at": latest_meas.timestamp.isoformat(),
                }
                records_to_create.append(
                    {
                        "entity_type": "SENSOR",
                        "entity_id": latest_meas.device_id,
                        "property_name": "soil_moisture_pct",
                        "property_value_json": {"value": latest_meas.soil_moisture_pct},
                        "unit": "%",
                        "provenance_type": "MEASURED",
                        "observed_at": latest_meas.timestamp,
                    }
                )

            # Latest Satellite Observation
            latest_sat = (
                db.query(SatelliteObservation)
                .filter(SatelliteObservation.plot_id == plot.id)
                .order_by(desc(SatelliteObservation.observation_date))
                .first()
            )
            if latest_sat:
                plot_dict["latest_satellite"] = {
                    "ndvi": latest_sat.ndvi_mean,
                    "observation_date": latest_sat.observation_date.isoformat(),
                }
                records_to_create.append(
                    {
                        "entity_type": "SATELLITE",
                        "entity_id": latest_sat.id,
                        "property_name": "ndvi_mean",
                        "property_value_json": {"ndvi": latest_sat.ndvi_mean},
                        "unit": "index",
                        "provenance_type": "PROVIDER_OBSERVATION",
                        "observed_at": datetime.combine(latest_sat.observation_date, datetime.min.time(), tzinfo=timezone.utc),
                    }
                )

            state_payload["plots"].append(plot_dict)

        # Source manifest
        source_manifest = {
            "plots_count": len(plots),
            "sensors_checked": len(plot_ids),
            "provenance_summary": {
                p: sum(1 for r in records_to_create if r["provenance_type"] == p)
                for p in PROVENANCE_HIERARCHY
            },
        }

        # SHA-256 Hash of deterministic state payload
        raw_json = json.dumps(state_payload, sort_keys=True).encode("utf-8")
        payload_hash = hashlib.sha256(raw_json).hexdigest()

        new_version = twin.twin_version + 1

        snapshot = TwinSnapshot(
            twin_id=twin.id,
            farm_id=farm.id,
            plot_id=plots[0].id if plots else None,
            crop_season_id=None,
            snapshot_version=new_version,
            state_payload_json=state_payload,
            source_manifest_json=source_manifest,
            data_completeness_pct=completeness.overall_score,
            payload_hash=payload_hash,
            generated_at=now_utc,
            created_by=user.id if user else None,
        )
        db.add(snapshot)
        db.flush()

        # Insert state records
        for item in records_to_create:
            rec = TwinStateRecord(
                snapshot_id=snapshot.id,
                entity_type=item["entity_type"],
                entity_id=item["entity_id"],
                property_name=item["property_name"],
                property_value_json=item["property_value_json"],
                unit=item.get("unit"),
                provenance_type=item["provenance_type"],
                source_reference=item.get("source_reference"),
                observed_at=item["observed_at"],
                quality_status="VERIFIED",
            )
            db.add(rec)

        twin.twin_version = new_version
        twin.state_status = "SYNCHRONIZED"
        twin.completeness_score = completeness.overall_score
        twin.last_synchronized_at = now_utc

        db.commit()
        db.refresh(snapshot)
        db.refresh(twin)
        return snapshot

    @staticmethod
    def reconcile_twin(farm: Farm, db: Session) -> TwinReconcileResponse:
        twin = TwinService.get_or_create_twin(farm=farm, db=db)
        prev_ver = twin.twin_version

        # Record a reconciliation event
        event_payload = {"trigger": "MANUAL_RECONCILE", "timestamp": datetime.now(timezone.utc).isoformat()}
        raw_event = json.dumps(event_payload, sort_keys=True).encode("utf-8")
        event_hash = hashlib.sha256(raw_event + str(uuid.uuid4()).encode("utf-8")).hexdigest()

        sync_event = TwinSynchronizationEvent(
            twin_id=twin.id,
            event_type="RECONCILIATION_RUN",
            event_hash=event_hash,
            payload_json=event_payload,
            processed_at=datetime.now(timezone.utc),
        )
        db.add(sync_event)
        db.flush()

        # Generate fresh snapshot
        snapshot = TwinService.create_snapshot(farm=farm, user=None, db=db, twin=twin)

        return TwinReconcileResponse(
            twin_id=twin.id,
            farm_id=farm.id,
            reconciled_events_count=1,
            previous_version=prev_ver,
            current_version=twin.twin_version,
            status="SYNCHRONIZED",
            timestamp=datetime.now(timezone.utc),
        )

    @staticmethod
    def get_twin_summary(farm: Farm, db: Session) -> FarmTwinResponse:
        twin = TwinService.get_or_create_twin(farm=farm, db=db)
        latest_snapshot = (
            db.query(TwinSnapshot)
            .filter(TwinSnapshot.twin_id == twin.id)
            .order_by(desc(TwinSnapshot.snapshot_version))
            .first()
        )
        plots_count = db.query(Plot).filter(Plot.farm_id == farm.id).count()

        summary_resp = None
        if latest_snapshot:
            summary_resp = TwinSnapshotSummaryResponse(
                id=latest_snapshot.id,
                twin_id=latest_snapshot.twin_id,
                farm_id=latest_snapshot.farm_id,
                plot_id=latest_snapshot.plot_id,
                crop_season_id=latest_snapshot.crop_season_id,
                snapshot_version=latest_snapshot.snapshot_version,
                data_completeness_pct=latest_snapshot.data_completeness_pct,
                payload_hash=latest_snapshot.payload_hash,
                generated_at=latest_snapshot.generated_at,
                source_manifest_json=latest_snapshot.source_manifest_json,
            )

        return FarmTwinResponse(
            id=twin.id,
            farm_id=twin.farm_id,
            twin_version=twin.twin_version,
            state_status=twin.state_status,
            last_synchronized_at=twin.last_synchronized_at,
            completeness_score=twin.completeness_score,
            latest_snapshot=summary_resp,
            active_plots_count=plots_count,
        )
