"""
ACREVIA - RiskCast Agronomic Rule Evaluation Engine.
Evaluates crop-specific risk thresholds against phenology and agrometeorological parameters.
"""

import json
from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import select

from backend.app.models.risk_rule import RiskRule
from backend.app.models.weather_data import WeatherData


class RuleEvaluationEngine:
    @classmethod
    def evaluate_rules(
        cls,
        crop: str,
        growth_stage: str,
        weather: WeatherData,
        db: Session
    ) -> Tuple[str, List[Dict[str, Any]], Dict[str, str]]:
        """
        Evaluates active risk rules for a given crop, phenological stage, and weather data.
        Returns:
            - overall_risk_level: "LOW" | "MODERATE" | "HIGH" | "INSUFFICIENT_DATA"
            - triggered_rules: list of matched rule details with citations
            - composite_advisory: localized summaries in en, te, hi
        """
        crop_clean = crop.lower().strip()
        stmt = (
            select(RiskRule)
            .filter_by(is_active=True)
            .filter(RiskRule.crop == crop_clean)
        )
        rules = db.scalars(stmt).all()

        if not rules:
            return (
                "LOW",
                [],
                {
                    "en": f"No active disease risks identified under current conditions for {crop}.",
                    "te": f"{crop} పంటకు ప్రస్తుత వాతావరణంలో ఎలాంటి తీవ్రమైన తెగులు సూచనలు లేవు.",
                    "hi": f"{crop} की फसल के लिए वर्तमान मौसम में किसी गंभीर रोग का जोखिम नहीं है।"
                }
            )

        triggered = []
        highest_severity = "LOW"
        severity_rank = {"LOW": 1, "MODERATE": 2, "HIGH": 3}

        for rule in rules:
            # Check growth stage applicability if specified
            if rule.applicable_growth_stages:
                stages = [s.strip().lower() for s in rule.applicable_growth_stages.split(",")]
                stage_match = any(st in growth_stage.lower() for st in stages) if growth_stage else True
                if not stage_match:
                    continue

            # Evaluate Temperature Criteria
            temp_match = True
            if rule.min_temp is not None and weather.temperature_celsius < rule.min_temp:
                temp_match = False
            if rule.max_temp is not None and weather.temperature_celsius > rule.max_temp:
                temp_match = False

            # Evaluate Humidity Criteria
            humidity_match = True
            if rule.min_humidity is not None and weather.relative_humidity < rule.min_humidity:
                humidity_match = False

            # Evaluate Leaf Wetness Hours Criteria
            wetness_match = True
            if rule.min_leaf_wetness_hours is not None and weather.leaf_wetness_hours < rule.min_leaf_wetness_hours:
                wetness_match = False

            # Determine match
            if temp_match and humidity_match and wetness_match:
                citations = []
                try:
                    citations = json.loads(rule.evidence_citations_json)
                except Exception:
                    citations = []

                triggered.append({
                    "rule_code": rule.rule_code,
                    "target_threat": rule.target_threat,
                    "severity_level": rule.severity_level,
                    "advisory_en": rule.advisory_en,
                    "advisory_te": rule.advisory_te,
                    "advisory_hi": rule.advisory_hi,
                    "citations": citations
                })

                if severity_rank.get(rule.severity_level, 1) > severity_rank.get(highest_severity, 1):
                    highest_severity = rule.severity_level

        if not triggered:
            return (
                "LOW",
                [],
                {
                    "en": f"Agrometeorological conditions remain within safe baseline tolerances for {crop}. Routine monitoring advised.",
                    "te": f"{crop} పంటకు వాతావరణ పరిస్థితులు అనుకూలంగా ఉన్నాయి. సాధారణ పరిశీలన సరిపోతుంది.",
                    "hi": f"{crop} की फसल के लिए मौसम सामान्य है। नियमित निगरानी रखें।"
                }
            )

        # Composite advisory text from top triggered rule
        top_rule = triggered[0]
        composite_advisory = {
            "en": f"[{highest_severity} RISK] {top_rule['target_threat']}: {top_rule['advisory_en']}",
            "te": f"[{highest_severity} రిస్క్] {top_rule['target_threat']}: {top_rule['advisory_te']}",
            "hi": f"[{highest_severity} जोखिम] {top_rule['target_threat']}: {top_rule['advisory_hi']}"
        }

        return highest_severity, triggered, composite_advisory
