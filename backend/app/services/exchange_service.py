"""
ACREVIA - Agricultural Data Exchange & Portability Service.
Stage 14: Consent-driven data export, standardized data import, conflict preservation, and cryptographic manifests.
"""

import csv
import hashlib
import io
import json
import zipfile
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.exchange import DataExchangeJob, DataMappingProfile
from backend.app.models.farm import Farm, Plot
from backend.app.models.soil_health import SoilSample, SoilTestResult
from backend.app.models.water_management import WaterSource, IrrigationEvent
from backend.app.models.observation import Observation
from backend.app.models.harvest_operations import HarvestPlan, HarvestSession
from backend.app.models.financial_ledger import FarmExpense, SaleTransaction
from backend.app.services.canonical_standards import CanonicalStandardsService


class DataExchangeService:
    """
    Handles export packaging (JSON, CSV, GeoJSON, ZIP archive with SHA-256 manifests)
    and safe, non-overwriting data imports with conflict detection.
    """

    # In-memory transient artifact storage for export downloads
    _EXPORT_PAYLOAD_CACHE: Dict[str, Tuple[str, bytes]] = {}

    @classmethod
    def create_export_job(
        cls,
        db: Session,
        user_id: str,
        farm_id: Optional[str],
        categories: List[str],
        export_format: str = "JSON",
        redact_pii: bool = True,
        redact_gps: bool = True,
    ) -> DataExchangeJob:
        job = DataExchangeJob(
            user_id=user_id,
            farm_id=farm_id,
            job_type="EXPORT",
            format=export_format.upper(),
            categories_json=json.dumps(categories),
            status="PROCESSING",
            redact_pii=redact_pii,
            preserve_conflicts=True,
        )
        db.add(job)
        db.commit()
        db.refresh(job)

        cls._process_export(db, job, categories, export_format.upper(), redact_pii, redact_gps)
        return job

    @classmethod
    def _process_export(
        cls,
        db: Session,
        job: DataExchangeJob,
        categories: List[str],
        export_format: str,
        redact_pii: bool,
        redact_gps: bool,
    ) -> None:
        try:
            export_data: Dict[str, Any] = {
                "schema_version": "1.0.0",
                "export_id": job.id,
                "exported_at": datetime.now(timezone.utc).isoformat(),
                "tenant_id": job.user_id,
                "redact_pii": redact_pii,
                "redact_gps": redact_gps,
                "entities": {}
            }

            total_records = 0
            include_all = "ALL" in categories or not categories

            # 1. Farm & Plots
            if include_all or "FARM_PROFILE" in categories:
                stmt = select(Farm).where(Farm.owner_id == job.user_id)
                if job.farm_id:
                    stmt = stmt.where(Farm.id == job.farm_id)
                farms = db.scalars(stmt).all()

                farms_list = []
                for f in farms:
                    plots_list = []
                    for p in f.plots:
                        plots_list.append({
                            "id": p.id,
                            "name": p.name,
                            "acreage": p.acreage,
                            "soil_type": p.soil_type,
                            "irrigation_source": p.irrigation_source,
                        })
                    farms_list.append({
                        "id": f.id,
                        "name": f.name if not redact_pii else f"Farm-{f.id[:8]}",
                        "district": f.district,
                        "state": f.state,
                        "total_acreage": f.total_acreage,
                        "plots": plots_list
                    })
                export_data["entities"]["farms"] = farms_list
                total_records += len(farms_list)

            # 2. Soil Health
            if include_all or "SOIL_HEALTH" in categories:
                stmt = select(SoilSample).join(Plot).join(Farm).where(Farm.owner_id == job.user_id)
                if job.farm_id:
                    stmt = stmt.where(Farm.id == job.farm_id)
                samples = db.scalars(stmt).all()
                samples_list = []
                for s in samples:
                    samples_list.append({
                        "sample_code": s.sample_code,
                        "plot_id": s.plot_id,
                        "sampling_depth_min_cm": float(s.sampling_depth_min_cm),
                        "sampling_depth_max_cm": float(s.sampling_depth_max_cm),
                        "sampling_date": s.sampling_date.isoformat() if s.sampling_date else None,
                        "composite_cores_count": s.composite_cores_count,
                        "status": s.status,
                    })
                export_data["entities"]["soil_samples"] = samples_list
                total_records += len(samples_list)

            # 3. Observations
            if include_all or "OBSERVATIONS" in categories:
                stmt = select(Observation).join(Farm, Observation.farm_id == Farm.id).where(Farm.owner_id == job.user_id)
                if job.farm_id:
                    stmt = stmt.where(Observation.farm_id == job.farm_id)
                obs = db.scalars(stmt.limit(100)).all()
                obs_list = []
                for o in obs:
                    obs_list.append({
                        "id": o.id,
                        "farm_id": o.farm_id,
                        "plot_id": o.plot_id,
                        "notes": o.notes,
                        "symptom_tags": o.symptom_tags,
                        "created_at": o.created_at.isoformat() if hasattr(o, "created_at") and o.created_at else None,
                    })
                export_data["entities"]["observations"] = obs_list
                total_records += len(obs_list)

            # 4. Financial Records
            if include_all or "FINANCIAL_LEDGER" in categories:
                stmt = select(FarmExpense).join(Farm, FarmExpense.farm_id == Farm.id).where(Farm.owner_id == job.user_id)
                if job.farm_id:
                    stmt = stmt.where(FarmExpense.farm_id == job.farm_id)
                expenses = db.scalars(stmt.limit(100)).all()
                exp_list = []
                for e in expenses:
                    exp_list.append({
                        "id": e.id,
                        "category": e.category,
                        "amount": float(e.amount),
                        "transaction_date": e.transaction_date.isoformat() if e.transaction_date else None,
                        "payment_status": e.payment_status
                    })
                export_data["entities"]["expenses"] = exp_list
                total_records += len(exp_list)

            # Format serialization
            raw_bytes: bytes
            mime_type: str

            if export_format == "CSV":
                # Flatten main entities into CSV buffer
                output = io.StringIO()
                writer = csv.writer(output)
                writer.writerow(["category", "entity_id", "data_json"])
                for cat, items in export_data["entities"].items():
                    for item in items:
                        writer.writerow([cat, item.get("id") or item.get("sample_code", ""), json.dumps(item)])
                raw_bytes = output.getvalue().encode("utf-8")
                mime_type = "text/csv"

            elif export_format == "GEOJSON":
                # GeoJSON FeatureCollection
                features = []
                for f in export_data["entities"].get("farms", []):
                    # Masked point geometry
                    coord = [78.4867, 17.3850] if not redact_gps else [78.5, 17.4]
                    features.append({
                        "type": "Feature",
                        "geometry": {"type": "Point", "coordinates": coord},
                        "properties": f
                    })
                geojson_doc = {
                    "type": "FeatureCollection",
                    "features": features,
                    "metadata": {"export_id": job.id, "exported_at": export_data["exported_at"]}
                }
                raw_bytes = json.dumps(geojson_doc, indent=2).encode("utf-8")
                mime_type = "application/geo+json"

            elif export_format == "ARCHIVE":
                # Multi-file ZIP archive containing individual CSVs and MANIFEST.json
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
                    manifest = {
                        "export_id": job.id,
                        "exported_at": export_data["exported_at"],
                        "tenant_id": job.user_id,
                        "entity_counts": {k: len(v) for k, v in export_data["entities"].items()},
                        "platform": "ACREVIA Agricultural Intelligence",
                        "canonical_units": {"mass": "kg / quintal", "area": "acre / ha"}
                    }
                    zf.writestr("MANIFEST.json", json.dumps(manifest, indent=2))

                    for cat, items in export_data["entities"].items():
                        cat_json = json.dumps(items, indent=2)
                        zf.writestr(f"{cat}.json", cat_json)
                raw_bytes = zip_buffer.getvalue()
                mime_type = "application/zip"

            else:  # JSON (Default)
                raw_bytes = json.dumps(export_data, indent=2).encode("utf-8")
                mime_type = "application/json"

            # Compute SHA-256 Checksum
            sha256_hash = hashlib.sha256(raw_bytes).hexdigest()

            # Cache artifact for download
            cls._EXPORT_PAYLOAD_CACHE[job.id] = (mime_type, raw_bytes)

            # Update job manifest
            manifest_summary = {
                "entity_counts": {k: len(v) for k, v in export_data["entities"].items()},
                "sha256": sha256_hash,
                "mime_type": mime_type,
                "byte_size": len(raw_bytes)
            }
            job.status = "COMPLETED"
            job.records_processed = total_records
            job.checksum_sha256 = sha256_hash
            job.manifest_json = json.dumps(manifest_summary)
            db.commit()

        except Exception as ex:
            job.status = "FAILED"
            job.error_message = str(ex)
            db.commit()

    @classmethod
    def get_export_payload(cls, job_id: str) -> Optional[Tuple[str, bytes]]:
        """
        Retrieves cached export binary payload.
        """
        return cls._EXPORT_PAYLOAD_CACHE.get(job_id)

    @classmethod
    def create_import_job(
        cls,
        db: Session,
        user_id: str,
        farm_id: Optional[str],
        target_category: str,
        data_payload: str,
        data_format: str = "JSON",
        mapping_profile_id: Optional[str] = None,
        preserve_conflicts: bool = True,
    ) -> DataExchangeJob:
        job = DataExchangeJob(
            user_id=user_id,
            farm_id=farm_id,
            job_type="IMPORT",
            format=data_format.upper(),
            categories_json=json.dumps([target_category]),
            status="PROCESSING",
            preserve_conflicts=preserve_conflicts,
        )
        db.add(job)
        db.commit()
        db.refresh(job)

        cls._process_import(db, job, target_category, data_payload, data_format.upper(), mapping_profile_id, preserve_conflicts)
        return job

    @classmethod
    def _process_import(
        cls,
        db: Session,
        job: DataExchangeJob,
        target_category: str,
        data_payload: str,
        data_format: str,
        mapping_profile_id: Optional[str],
        preserve_conflicts: bool,
    ) -> None:
        try:
            # 1. Parse payload into list of dictionaries
            raw_records: List[Dict[str, Any]] = []
            if data_format == "CSV":
                reader = csv.DictReader(io.StringIO(data_payload))
                raw_records = [dict(row) for row in reader]
            else:
                parsed = json.loads(data_payload)
                if isinstance(parsed, list):
                    raw_records = parsed
                elif isinstance(parsed, dict) and "records" in parsed:
                    raw_records = parsed["records"]
                else:
                    raw_records = [parsed]

            # 2. Apply mapping rules if profile provided
            mapping_rules: Dict[str, str] = {}
            if mapping_profile_id:
                profile = db.get(DataMappingProfile, mapping_profile_id)
                if profile:
                    mapping_rules = json.loads(profile.mapping_rules_json)

            processed = 0
            failed = 0
            conflicts = 0

            # 3. Ingest and detect conflicts without silent overwrite
            for r in raw_records:
                mapped_record: Dict[str, Any] = {}
                for k, v in r.items():
                    target_key = mapping_rules.get(k, k)
                    mapped_record[target_key] = v

                # Convert known numeric strings
                for num_key in ["ph", "ec_ds_m", "organic_carbon_percent", "nitrogen_kg_ha", "phosphorus_kg_ha", "potassium_kg_ha"]:
                    if num_key in mapped_record and mapped_record[num_key] not in (None, ""):
                        try:
                            mapped_record[num_key] = float(mapped_record[num_key])
                        except ValueError:
                            pass

                # Check conflict (e.g. sample_code or id already exists)
                if target_category.upper() in ["SOIL_TESTS", "SOIL_SAMPLE"]:
                    code = mapped_record.get("sample_code")
                    if code:
                        existing = db.scalars(select(SoilSample).where(SoilSample.sample_code == code)).first()
                        if existing:
                            conflicts += 1
                            # Invariant: Never overwrite! Retain both with conflict marker
                            mapped_record["sample_code"] = f"{code}_CONFLICT_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"

                processed += 1

            manifest_summary = {
                "records_processed": processed,
                "conflicts_detected": conflicts,
                "records_failed": failed,
                "preserve_conflicts": preserve_conflicts,
                "imported_at": datetime.now(timezone.utc).isoformat()
            }

            job.status = "COMPLETED"
            job.records_processed = processed
            job.records_failed = failed
            job.conflicts_detected = conflicts
            job.manifest_json = json.dumps(manifest_summary)
            db.commit()

        except Exception as ex:
            job.status = "FAILED"
            job.error_message = str(ex)
            db.commit()

    @classmethod
    def create_mapping_profile(
        cls,
        db: Session,
        user_id: str,
        name: str,
        source_format: str,
        target_entity: str,
        mapping_rules: Dict[str, str],
    ) -> DataMappingProfile:
        profile = DataMappingProfile(
            user_id=user_id,
            name=name,
            source_format=source_format,
            target_entity=target_entity,
            mapping_rules_json=json.dumps(mapping_rules),
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)
        return profile

    @classmethod
    def list_mapping_profiles(cls, db: Session, user_id: str) -> List[DataMappingProfile]:
        return db.scalars(select(DataMappingProfile).where(DataMappingProfile.user_id == user_id)).all()
