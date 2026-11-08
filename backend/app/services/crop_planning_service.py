"""
ACREVIA - Crop Planning & Operations Service (Pillar D: ACREVIA Plan).
Provides PJTSAU-grounded crop calendars, dynamic task scheduling,
weather conflict evaluation, and operational task execution tracking.
"""

from datetime import datetime, date, timedelta, timezone
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from backend.app.models.user import User
from backend.app.models.farm import Plot
from backend.app.models.crop import CropSeason
from backend.app.models.weather_data import WeatherData
from backend.app.models.operation import FarmOperation
from backend.app.models.crop_planning import CropCalendarDefinition, CropTask
from backend.app.schemas.crop_planning import (
    CropTaskCreate,
    CropTaskUpdate,
    CropTaskCompleteRequest,
    CropTaskResponse,
    CropCalendarDefinitionResponse,
)

PJTSAU_BASELINE_CALENDARS = [
    {
        "crop_id": "COTTON",
        "variety_id": "RCH-659 BG II / Hybrid",
        "agro_climatic_zone": "TELANGANA_NORTH_EASTERN",
        "growth_stage": "EMERGENCE_AND_SQUARE_INITIATION",
        "typical_duration_days": 45,
        "source_citation": "PJTSAU Cotton Production Technology Manual (2025)",
        "version": "1.0",
        "recommended_tasks": [
            {"task_name": "Deep Summer Ploughing & FYM Application", "category": "LAND_PREP", "offset_days": -15},
            {"task_name": "Basal DAP & MOP Soil Application", "category": "FERTILIZATION", "offset_days": 0},
            {"task_name": "Sowing with Trichoderma seed treatment", "category": "SOWING", "offset_days": 1},
            {"task_name": "Gap filling and thinning to single plant", "category": "LAND_PREP", "offset_days": 15},
            {"task_name": "First top-dressing with Urea (split 1)", "category": "FERTILIZATION", "offset_days": 30},
            {"task_name": "Sucking pest scouting (Jassids & Aphids)", "category": "PLANT_PROTECTION", "offset_days": 35},
        ],
    },
    {
        "crop_id": "COTTON",
        "variety_id": "RCH-659 BG II / Hybrid",
        "agro_climatic_zone": "TELANGANA_NORTH_EASTERN",
        "growth_stage": "FLOWERING_AND_BOLL_DEVELOPMENT",
        "typical_duration_days": 60,
        "source_citation": "PJTSAU Cotton Production Technology Manual (2025)",
        "version": "1.0",
        "recommended_tasks": [
            {"task_name": "Second split Nitrogen & Potash top dressing", "category": "FERTILIZATION", "offset_days": 60},
            {"task_name": "Pink Bollworm pheromone trap installation", "category": "PLANT_PROTECTION", "offset_days": 65},
            {"task_name": "Critical boll development furrow irrigation", "category": "IRRIGATION", "offset_days": 75},
            {"task_name": "1% MgSO4 + 1% 19-19-19 foliar spray against leaf reddening", "category": "FERTILIZATION", "offset_days": 90},
        ],
    },
    {
        "crop_id": "RICE",
        "variety_id": "Telangana Sona (RNR 15048)",
        "agro_climatic_zone": "TELANGANA_SOUTHERN",
        "growth_stage": "TRANSPLANTING_AND_TILLERING",
        "typical_duration_days": 55,
        "source_citation": "PJTSAU Rice Package of Practices (2025)",
        "version": "1.0",
        "recommended_tasks": [
            {"task_name": "Puddling and basal complex fertilizer incorporation", "category": "LAND_PREP", "offset_days": -2},
            {"task_name": "Transplanting 2-3 seedlings per hill at 15x15 cm", "category": "SOWING", "offset_days": 0},
            {"task_name": "Pre-emergence herbicide application (Pretilachlor)", "category": "PLANT_PROTECTION", "offset_days": 3},
            {"task_name": "First top dressing with Urea + Zinc Sulphate", "category": "FERTILIZATION", "offset_days": 21},
            {"task_name": "Stem borer and leaf folder scouting", "category": "PLANT_PROTECTION", "offset_days": 35},
        ],
    },
    {
        "crop_id": "CHILLI",
        "variety_id": "Teja / G4 Local Selection",
        "agro_climatic_zone": "TELANGANA_CENTRAL",
        "growth_stage": "FLOWERING_AND_FRUIT_SET",
        "typical_duration_days": 60,
        "source_citation": "PJTSAU Chilli Production Technology (2025)",
        "version": "1.0",
        "recommended_tasks": [
            {"task_name": "Drip fertigation with 13-0-45 (Potassium Nitrate)", "category": "FERTILIZATION", "offset_days": 45},
            {"task_name": "Thrips and Mites yellow/blue sticky trap placement", "category": "PLANT_PROTECTION", "offset_days": 50},
            {"task_name": "Neem oil 10000 ppm preventive botanical spray", "category": "PLANT_PROTECTION", "offset_days": 60},
            {"task_name": "First picking of mature green chillies", "category": "HARVEST", "offset_days": 75},
        ],
    },
]


class CropPlanningService:
    @staticmethod
    def seed_crop_calendars(db: Session) -> int:
        count = 0
        for cal in PJTSAU_BASELINE_CALENDARS:
            existing = (
                db.query(CropCalendarDefinition)
                .filter(
                    CropCalendarDefinition.crop_id == cal["crop_id"],
                    CropCalendarDefinition.growth_stage == cal["growth_stage"],
                    CropCalendarDefinition.agro_climatic_zone == cal["agro_climatic_zone"],
                )
                .first()
            )
            if not existing:
                row = CropCalendarDefinition(
                    crop_id=cal["crop_id"],
                    variety_id=cal.get("variety_id"),
                    agro_climatic_zone=cal["agro_climatic_zone"],
                    growth_stage=cal["growth_stage"],
                    typical_duration_days=cal["typical_duration_days"],
                    recommended_tasks_json=cal["recommended_tasks"],
                    source_citation=cal["source_citation"],
                    version=cal["version"],
                )
                db.add(row)
                count += 1
        db.commit()
        return count

    @staticmethod
    def list_calendars(
        crop_name: Optional[str],
        zone: Optional[str],
        db: Session,
    ) -> List[CropCalendarDefinition]:
        CropPlanningService.seed_crop_calendars(db)
        query = db.query(CropCalendarDefinition)
        if crop_name:
            query = query.filter(CropCalendarDefinition.crop_id == crop_name.upper())
        if zone:
            query = query.filter(CropCalendarDefinition.agro_climatic_zone == zone)
        return query.all()

    @staticmethod
    def create_task(
        user: User,
        data: CropTaskCreate,
        db: Session,
    ) -> CropTask:
        plot = db.get(Plot, data.plot_id)
        if not plot:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Plot '{data.plot_id}' not found.",
            )

        conflict_flag, conflict_reason = CropPlanningService.detect_weather_conflict(
            plot=plot,
            category=data.task_category,
            task_date=data.due_date,
            db=db,
        )

        task = CropTask(
            crop_season_id=data.crop_season_id,
            plot_id=data.plot_id,
            calendar_def_id=data.calendar_def_id,
            task_name=data.task_name,
            task_category=data.task_category,
            due_date=data.due_date,
            status="PLANNED",
            weather_conflict_flag=conflict_flag,
            conflict_reason=conflict_reason,
            notes=data.notes,
        )
        db.add(task)
        db.commit()
        db.refresh(task)
        return task

    @staticmethod
    def detect_weather_conflict(
        plot: Plot,
        category: str,
        task_date: date,
        db: Session,
    ) -> tuple[bool, Optional[str]]:
        # Evaluate weather conflict for spray/fertilization
        if category not in ["PLANT_PROTECTION", "FERTILIZATION"]:
            return False, None

        # Check latest weather data recorded for this farm/district
        threshold_dt = datetime.combine(task_date - timedelta(days=1), datetime.min.time(), tzinfo=timezone.utc)
        weather = (
            db.query(WeatherData)
            .filter(WeatherData.observation_time >= threshold_dt)
            .first()
        )

        if weather:
            if weather.precipitation_mm and weather.precipitation_mm > 15.0:
                return True, f"Rainfall forecast of {weather.precipitation_mm}mm will cause chemical wash-off and leaching."
            if weather.wind_speed_kmh and weather.wind_speed_kmh > 22.0:
                return True, f"High wind speed ({weather.wind_speed_kmh} km/h) exceeds safe spray drift limits (>20 km/h)."

        return False, None

    @staticmethod
    def complete_task(
        task_id: str,
        data: CropTaskCompleteRequest,
        user: User,
        db: Session,
    ) -> CropTask:
        task = db.get(CropTask, task_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"CropTask '{task_id}' not found.",
            )

        actual_date = data.actual_date or date.today()
        task.status = "COMPLETED"
        task.completed_date = actual_date
        task.execution_details_json = {
            "labor_hours": data.labor_hours,
            "materials_used": data.materials_used,
            "observations": data.observations,
            "completed_by_user_id": user.id,
        }

        # Log as an immutable FarmOperation for auditability
        operation = FarmOperation(
            plot_id=task.plot_id,
            operation_type=task.task_category,
            execution_date=actual_date,
            details_json=str(task.execution_details_json),
        )
        db.add(operation)

        db.commit()
        db.refresh(task)
        return task
