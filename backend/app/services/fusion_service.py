"""
ACREVIA - Multi-Source Evidence Fusion Service (Pillar D: Acrevia Fusion).
Aligns satellite remote sensing, IoT sensor streams, CropVision photos,
weather conditions, and operational logs to detect contradictions and produce
traceable multilingual agronomic explanations.
"""

from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, and_, desc

from backend.app.models.evidence_fusion import FusionExplanation
from backend.app.models.satellite import SatelliteObservation
from backend.app.models.sensor import SensorMeasurement
from backend.app.models.intervention import InterventionRecord
from backend.app.models.operation import FarmOperation
from backend.app.models.diagnosis import DiagnosisRequest
from backend.app.models.farm import Plot
from backend.app.core.exceptions import NotFoundError


class FusionService:
    @staticmethod
    def evaluate_plot_fusion(db: Session, plot_id: str) -> FusionExplanation:
        """Synthesizes all evidence streams for a plot into a unified qualified assessment."""
        plot = db.get(Plot, plot_id)
        if not plot or plot.is_archived:
            raise NotFoundError("Plot not found.")

        now = datetime.now(timezone.utc)
        recent_window_days = 14
        cutoff_date = now - timedelta(days=recent_window_days)

        # 1. Gather Satellite Stream
        latest_sat = db.execute(
            select(SatelliteObservation).where(
                SatelliteObservation.plot_id == plot_id
            ).order_by(desc(SatelliteObservation.observation_date)).limit(1)
        ).scalar_one_or_none()

        # 2. Gather Ground Sensor Stream
        latest_sensor = db.execute(
            select(SensorMeasurement).where(
                SensorMeasurement.plot_id == plot_id
            ).order_by(desc(SensorMeasurement.timestamp)).limit(1)
        ).scalar_one_or_none()

        # 3. Gather Recent Interventions & Farm Operations
        recent_interventions = list(db.execute(
            select(InterventionRecord).where(
                and_(
                    InterventionRecord.plot_id == plot_id,
                    InterventionRecord.application_date >= cutoff_date.date()
                )
            )
        ).scalars().all())

        recent_operations = list(db.execute(
            select(FarmOperation).where(
                and_(
                    FarmOperation.plot_id == plot_id,
                    FarmOperation.execution_date >= cutoff_date.date()
                )
            )
        ).scalars().all())

        # 4. Gather Recent Visual Diagnoses
        from backend.app.models.observation import Observation
        recent_diagnosis = db.execute(
            select(DiagnosisRequest)
            .join(Observation, DiagnosisRequest.observation_id == Observation.id)
            .where(Observation.plot_id == plot_id)
            .order_by(desc(DiagnosisRequest.created_at))
            .limit(1)
        ).scalar_one_or_none()

        # Build Evidence Corpus
        evidence_sources: Dict[str, Any] = {}
        contradictions: List[Dict[str, str]] = []

        if latest_sat:
            evidence_sources["satellite"] = {
                "observation_date": latest_sat.observation_date.isoformat(),
                "mean_ndvi": latest_sat.mean_ndvi,
                "mean_ndmi": latest_sat.mean_ndmi,
                "trend": latest_sat.trend_classification
            }

        if latest_sensor:
            evidence_sources["sensor"] = {
                "timestamp": latest_sensor.timestamp.isoformat(),
                "soil_moisture_pct": latest_sensor.soil_moisture_pct,
                "ambient_temp_c": latest_sensor.ambient_temperature_c,
                "leaf_wetness_pct": latest_sensor.leaf_wetness_pct,
                "quality_flag": latest_sensor.data_quality_flag
            }

        if recent_interventions:
            evidence_sources["interventions"] = [
                {"category": i.category, "trade_name": i.trade_name, "date": i.application_date.isoformat()}
                for i in recent_interventions
            ]

        if recent_operations:
            evidence_sources["operations"] = [
                {"operation_type": o.operation_type, "date": o.execution_date.isoformat()}
                for o in recent_operations
            ]

        # 5. Conflict & Contradiction Detection Rules
        overall_vigor = "OPTIMAL"
        primary_driver = "NONE"

        has_harvest_op = any(
            o.operation_type in ["HARVEST", "PRUNING", "TOPPING"]
            for o in recent_operations
        )

        sat_declining = latest_sat and (
            latest_sat.trend_classification in ["DECLINING_STRESS", "HARVEST_CLEARING"]
            or latest_sat.mean_ndvi < 0.45
        )

        # Contradiction Rule 1: Satellite drop vs Recent Harvest/Pruning
        if sat_declining and has_harvest_op:
            contradictions.append({
                "conflict_type": "CANOPY_DROP_VS_MANAGEMENT_ACTION",
                "description": "Satellite optical vigor shows canopy reduction, but field operation logs indicate deliberate harvesting or pruning.",
                "resolution": "Suppressed disease alarm. Canopy decline classified as intentional management activity rather than pest or pathogen stress."
            })
            overall_vigor = "VEGETATIVE_CLEARING"
            primary_driver = "OPERATIONAL_CLEARING"

        # Contradiction Rule 2: Soil moisture deficit with high satellite vigor
        elif latest_sensor and latest_sensor.soil_moisture_pct is not None and latest_sensor.soil_moisture_pct < 18.0:
            primary_driver = "MOISTURE_DEFICIT"
            overall_vigor = "MODERATE_STRESS"
            if latest_sat and latest_sat.mean_ndvi > 0.65:
                contradictions.append({
                    "conflict_type": "LATENT_SOIL_DEFICIT",
                    "description": "Root-zone soil moisture is critically low (<18%) while satellite canopy greenness remains temporarily elevated.",
                    "resolution": "Canopy greenness lags root-zone stress by 5-8 days. Flagged early moisture deficit before visual wilting manifests."
                })

        # Contradiction Rule 3: High fungal disease risk with healthy canopy
        elif latest_sensor and latest_sensor.leaf_wetness_pct is not None and latest_sensor.leaf_wetness_pct > 70.0:
            primary_driver = "PEST_DISEASE_SUSPECT"
            overall_vigor = "MODERATE_STRESS"
            contradictions.append({
                "conflict_type": "PRE_SYMPTOMATIC_DISEASE_PRESSURE",
                "description": "Extended canopy wetness (>70%) creates ideal fungal spore germination conditions despite high current satellite vigor.",
                "resolution": "Issued pre-symptomatic preventive alert for foliar blight/blast."
            })

        elif sat_declining and not has_harvest_op:
            primary_driver = "PEST_DISEASE_SUSPECT"
            overall_vigor = "MODERATE_STRESS"

        # 6. Generate Multilingual Explanations
        if primary_driver == "OPERATIONAL_CLEARING":
            explanation_en = (
                "Canopy decline observed on satellite imagery is consistent with your recently logged harvesting or pruning. "
                "No adverse biological stress or disease outbreak is indicated."
            )
            explanation_te = (
                "శాటిలైట్ చిత్రాలలో కనిపించిన ఆకుల తగ్గుదల మీరు ఇటీవల నమోదు చేసిన కోత లేదా కత్తిరింపుకు అనుగుణంగా ఉంది. "
                "ఎటువంటి తెగులు లేదా వ్యాధి సంకేతాలు లేవు."
            )
            explanation_hi = (
                "उपग्रह चित्रों में दिखाई देने वाली पत्तियों की कमी आपके हाल ही में दर्ज किए गए कटाई या छंटाई के काम के अनुरूप है। "
                "किसी बीमारी या कीट के प्रकोप का कोई संकेत नहीं है।"
            )
        elif primary_driver == "MOISTURE_DEFICIT":
            explanation_en = (
                "Root-zone soil moisture probe indicates moisture stress (<18% VWC). "
                "Canopy greenness currently appears normal on satellite, but irrigation is recommended within 48 hours to prevent wilting."
            )
            explanation_te = (
                "నేల తేమ మీటరు వేర్ల వద్ద తీవ్రమైన తేమ కొరతను చూపుతోంది (<18%). "
                "శాటిలైట్‌లో పంట ఇంకా పచ్చగా ఉన్నప్పటికీ, పైరు వాడకుండా ఉండటానికి 48 గంటల్లో నీటి తడి ఇవ్వండి."
            )
            explanation_hi = (
                "मिट्टी का नमी सेंसर जड़ क्षेत्र में नमी की कमी दिखा रहा है (<18%)। "
                "उपग्रह पर फसल अभी भी हरी दिख रही है, लेकिन मुरझाने से बचाने के लिए 48 घंटों के भीतर सिंचाई की सलाह दी जाती है।"
            )
        elif primary_driver == "PEST_DISEASE_SUSPECT":
            explanation_en = (
                "High leaf wetness and canopy humidity create favorable conditions for fungal germination. "
                "Inspect the underside of leaves for early lesions using CropVision."
            )
            explanation_te = (
                "ఆకులపై ఎక్కువ సమయం తేమ ఉండటం వల్ల శిలీంధ్ర తెగుళ్లు ఆశించే అవకాశం ఉంది. "
                "క్రాప్‌విజన్ ద్వారా ఆకుల కింద మచ్చలు ఉన్నాయేమో పరిశీలించండి."
            )
            explanation_hi = (
                "पत्तियों पर नमी और अधिक आर्द्रता के कारण फंगल रोग पनपने के अनुकूल परिस्थितियाँ हैं। "
                "क्रॉपविज़न के माध्यम से पत्तियों की जांच करें।"
            )
        else:
            explanation_en = (
                "Plot environmental indicators, satellite canopy vigor, and ground telemetry are optimal and in alignment. "
                "Crop progression is healthy."
            )
            explanation_te = (
                "పొలం వాతావరణం, శాటిలైట్ పంట పచ్చదనం మరియు గ్రౌండ్ సెన్సార్లు అన్నీ అనుకూలంగా ఉన్నాయి. "
                "పైరు పెరుగుదల ఆరోగ్యంగా ఉంది."
            )
            explanation_hi = (
                "खेत के पर्यावरणीय संकेतक, उपग्रह कैनोपी स्वास्थ्य और ग्राउंड सेंसर सभी अनुकूल और सामान्य हैं। "
                "फसल की प्रगति स्वस्थ है।"
            )

        epistemic_qualifications = {
            "satellite_nature": "Remote proxy of canopy vigor, not a biological disease diagnosis.",
            "sensor_nature": "In-situ micro-probe measurement of root-zone and canopy vicinity.",
            "conflict_status": "CONTRADICTIONS_RESOLVED" if contradictions else "NO_CONFLICTS"
        }

        explanation = FusionExplanation(
            plot_id=plot_id,
            evaluation_timestamp=now,
            overall_vigor_status=overall_vigor,
            primary_stress_driver=primary_driver,
            evidence_sources_json=evidence_sources,
            contradictions_detected_json=contradictions,
            farmer_explanation_en=explanation_en,
            farmer_explanation_te=explanation_te,
            farmer_explanation_hi=explanation_hi,
            epistemic_qualifications_json=epistemic_qualifications
        )
        db.add(explanation)
        db.commit()
        db.refresh(explanation)
        return explanation
