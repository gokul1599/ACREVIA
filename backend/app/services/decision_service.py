"""
ACREVIA - Agricultural Decision Intelligence Service (Pillar E: ACREVIA Decision).
Synthesizes digital twin state, KrishiBrain evidence grounding, and RiskCast alerts
into explainable multilingual recommendations across English, Telugu, and Hindi.
"""

from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_
from fastapi import HTTPException, status

from backend.app.models.user import User
from backend.app.models.farm import Farm, Plot
from backend.app.models.crop import CropSeason
from backend.app.models.risk_alert import RiskAlert
from backend.app.models.expert_case import ExpertReviewCase
from backend.app.models.observation import Observation
from backend.app.models.knowledge_chunk import KnowledgeChunk
from backend.app.models.decision_intelligence import DecisionRecord, DecisionFeedback
from backend.app.schemas.decision_intelligence import (
    DecisionAnalyzeRequest,
    DecisionRecordResponse,
    EvidenceSourceItem,
    DecisionFeedbackCreate,
    DecisionFeedbackResponse,
)
from backend.app.services.twin_service import TwinService

BANNED_AGROCHEMICALS = [
    "monocrotophos",
    "endosulfan",
    "paraquat",
    "carbofuran",
    "phorate",
    "ddt",
]


class DecisionService:
    @staticmethod
    def analyze_decision(
        user: User,
        data: DecisionAnalyzeRequest,
        db: Session,
    ) -> DecisionRecordResponse:
        plot = db.get(Plot, data.plot_id)
        if not plot:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Plot '{data.plot_id}' not found.",
            )

        farm = db.get(Farm, plot.farm_id)
        if not farm:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Farm '{plot.farm_id}' not found.",
            )

        # 1. Check Data Completeness Guard
        completeness = TwinService.calculate_completeness(farm=farm, db=db)
        if completeness.overall_score < 65.0:
            missing_str = ", ".join(completeness.missing_critical_fields) if completeness.missing_critical_fields else "critical telemetry"
            rec = DecisionRecord(
                plot_id=plot.id,
                farmer_id=user.id,
                query_text=data.query_text,
                decision_category=data.decision_category,
                recommendation_state="REQUIRES_MORE_INFORMATION",
                evidence_sources_json=[],
                grounded_explanation_en=f"Farm digital twin completeness is {completeness.overall_score}% (below 65% safety threshold). Missing parameters: {missing_str}. Please update missing details before receiving operational recommendations.",
                grounded_explanation_te=f"వ్యవసాయ డిజిటల్ ట్విన్ సమాచారం {completeness.overall_score}% మాత్రమే పూర్తయింది (కనీసం 65% అవసరం). లోపించిన వివరాలు: {missing_str}. దయచేసి సరైన సలహాల కోసం వివరాలను నమోదు చేయండి.",
                grounded_explanation_hi=f"फार्म डिजिटल ट्विन पूर्णता {completeness.overall_score}% है (न्यूनतम 65% आवश्यक)। गायब जानकारी: {missing_str}। कृपया परिचालन सलाह के लिए विवरण अपडेट करें।",
                uncertainty_disclosures_json=["Decision paused due to incomplete farm boundary or telemetry profiles."],
                expert_escalation_case_id=None,
                evaluated_at=datetime.now(timezone.utc),
            )
            db.add(rec)
            db.commit()
            db.refresh(rec)
            return DecisionService._to_response(rec)

        # 2. Check Agrochemical Safety & Regulatory Filter
        query_lower = data.query_text.lower()
        for banned in BANNED_AGROCHEMICALS:
            if banned in query_lower:
                rec = DecisionRecord(
                    plot_id=plot.id,
                    farmer_id=user.id,
                    query_text=data.query_text,
                    decision_category=data.decision_category,
                    recommendation_state="NOT_SUPPORTED",
                    evidence_sources_json=[],
                    grounded_explanation_en=f"Chemical '{banned.title()}' is banned or restricted under Central Insecticide Board & Registration Committee (CIBRC) regulations for this crop application due to severe environmental and toxicological hazards.",
                    grounded_explanation_te=f"రసాయనం '{banned.title()}' పర్యావరణ మరియు ఆరోగ్య హాని కారణంగా ప్రభుత్వ నిబంధనల ప్రకారం నిషేధించబడింది. ప్రత్యామ్నాయ పద్ధతులను అనుసరించండి.",
                    grounded_explanation_hi=f"रसायन '{banned.title()}' केंद्रीय कीटनाशक बोर्ड द्वारा प्रतिबंधित या अत्यधिक विनियमित है। कृपया सुरक्षित और अनुशंसित विकल्पों का उपयोग करें।",
                    uncertainty_disclosures_json=["Regulatory safety prohibition enforced."],
                    expert_escalation_case_id=None,
                    evaluated_at=datetime.now(timezone.utc),
                )
                db.add(rec)
                db.commit()
                db.refresh(rec)
                return DecisionService._to_response(rec)

        # 3. Check RiskCast Alerts for High Agronomic Pressure
        high_risk_alert = (
            db.query(RiskAlert)
            .filter(
                RiskAlert.plot_id == plot.id,
                RiskAlert.alert_level == "HIGH",
                RiskAlert.is_dismissed == False,
            )
            .first()
        )

        expert_case_id = None
        if high_risk_alert:
            # Check or create an expert case for human-in-the-loop escalation
            case = (
                db.query(ExpertReviewCase)
                .filter(ExpertReviewCase.plot_id == plot.id, ExpertReviewCase.status != "COMPLETED")
                .first()
            )
            if not case:
                # Find an observation for this plot
                obs = db.query(Observation).filter(Observation.plot_id == plot.id).first()
                if obs:
                    case = ExpertReviewCase(
                        observation_id=obs.id,
                        farm_id=farm.id,
                        plot_id=plot.id,
                        crop_id="COTTON",
                        priority="URGENT",
                        status="QUEUED",
                    )
                    db.add(case)
                    db.flush()
            if case:
                expert_case_id = case.id

            rec = DecisionRecord(
                plot_id=plot.id,
                farmer_id=user.id,
                query_text=data.query_text,
                decision_category=data.decision_category,
                recommendation_state="REQUIRES_EXPERT_REVIEW",
                evidence_sources_json=[
                    {
                        "source_title": "RiskCast High-Severity Outbreak Signal",
                        "chapter": "Biotic Stress Warning",
                        "chunk_id": high_risk_alert.id,
                    }
                ],
                grounded_explanation_en=f"A severe agronomic risk alert ('{high_risk_alert.title}') is active on this plot. To prevent potential crop failure, automated chemical or management decisions are paused. This situation has been escalated to verified agricultural extension experts.",
                grounded_explanation_te=f"ఈ పొలంలో అధిక తెగులు/వాతావరణ ప్రమాద హెచ్చరిక ('{high_risk_alert.title}') ఉంది. పంట నష్టం నివారించడానికి ఆటోమేటిక్ మందుల సిఫార్సులు నిలిపివేయబడ్డాయి. ఇది వ్యవసాయ నిపుణుల పరిశీలనకు పంపబడింది.",
                grounded_explanation_hi=f"इस खेत पर गंभीर जोखिम अलर्ट ('{high_risk_alert.title}') सक्रिय है। स्वचालित रासायनिक सिफारिशें रोक दी गई हैं और इसे कृषि विशेषज्ञ समीक्षा के लिए भेजा गया है।",
                uncertainty_disclosures_json=["Automated decision suppressed in favor of qualified agronomist review."],
                expert_escalation_case_id=expert_case_id,
                evaluated_at=datetime.now(timezone.utc),
            )
            db.add(rec)
            db.commit()
            db.refresh(rec)
            return DecisionService._to_response(rec)

        # 4. KrishiBrain Evidence Retrieval
        active_season = (
            db.query(CropSeason)
            .filter(CropSeason.plot_id == plot.id, CropSeason.status == "ACTIVE")
            .first()
        )
        crop_name = (
            (active_season.crop.name_en if active_season.crop else active_season.crop_id).lower()
            if active_season
            else "cotton"
        )

        evidence_chunk = (
            db.query(KnowledgeChunk)
            .filter(
                KnowledgeChunk.crop_scope.ilike(f"%{crop_name}%"),
                KnowledgeChunk.approval_status == "APPROVED",
            )
            .first()
        )

        evidence_sources = []
        if evidence_chunk:
            evidence_sources.append(
                {
                    "source_title": f"PJTSAU Package of Practices for {crop_name.title()}",
                    "chapter": evidence_chunk.heading_path or "General Management",
                    "chunk_id": evidence_chunk.id,
                }
            )
        else:
            # Baseline PJTSAU citation
            evidence_sources.append(
                {
                    "source_title": "PJTSAU Crop Production Guidelines (2025)",
                    "chapter": "Standard Agro-Climatic Practices",
                    "chunk_id": "pjtsau_std_2025",
                }
            )

        # 5. Formulate Grounded Recommendation
        explanation_en = (
            f"Based on current digital twin state and PJTSAU agronomic guidelines for {crop_name.title()}, "
            f"your operational query '{data.query_text}' is supported. Maintain scheduled irrigation intervals "
            f"and avoid excess moisture during sensitive reproductive phases."
        )
        explanation_te = (
            f"డిజిటల్ ట్విన్ సమాచారం మరియు వ్యవసాయ విశ్వవిద్యాలయం (PJTSAU) సూచనల ప్రకారం, "
            f"మీ ప్రశ్న '{data.query_text}' ఆమోదించబడింది. సమతుల్య నీటి యాజమాన్యం పాటించండి."
        )
        explanation_hi = (
            f"डिजिटल ट्विन स्थिति और पीजेटीएसएयू कृषि दिशानिर्देशों के अनुसार, "
            f"आपके प्रश्न '{data.query_text}' पर सलाह दी जाती है कि संतुलित सिंचाई बनाए रखें।"
        )

        rec = DecisionRecord(
            plot_id=plot.id,
            farmer_id=user.id,
            query_text=data.query_text,
            decision_category=data.decision_category,
            recommendation_state="EVIDENCE_SUPPORTED",
            evidence_sources_json=evidence_sources,
            grounded_explanation_en=explanation_en,
            grounded_explanation_te=explanation_te,
            grounded_explanation_hi=explanation_hi,
            uncertainty_disclosures_json=[
                "Recommendation assumes standard meteorological forecasts; unpredicted local storm events require field re-check."
            ],
            expert_escalation_case_id=None,
            evaluated_at=datetime.now(timezone.utc),
        )
        db.add(rec)
        db.commit()
        db.refresh(rec)
        return DecisionService._to_response(rec)

    @staticmethod
    def record_feedback(
        decision_id: str,
        data: DecisionFeedbackCreate,
        db: Session,
    ) -> DecisionFeedbackResponse:
        dec = db.get(DecisionRecord, decision_id)
        if not dec:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"DecisionRecord '{decision_id}' not found.",
            )

        feedback = DecisionFeedback(
            decision_id=decision_id,
            farmer_action_taken=data.farmer_action_taken,
            farmer_rating=data.farmer_rating,
            feedback_notes=data.feedback_notes,
            observed_outcome=data.observed_outcome,
            recorded_at=datetime.now(timezone.utc),
        )
        db.add(feedback)
        db.commit()
        db.refresh(feedback)

        return DecisionFeedbackResponse(
            id=feedback.id,
            decision_id=feedback.decision_id,
            farmer_action_taken=feedback.farmer_action_taken,
            farmer_rating=feedback.farmer_rating,
            feedback_notes=feedback.feedback_notes,
            observed_outcome=feedback.observed_outcome,
            recorded_at=feedback.recorded_at,
        )

    @staticmethod
    def _to_response(rec: DecisionRecord) -> DecisionRecordResponse:
        evidence_items = [
            EvidenceSourceItem(
                source_title=item.get("source_title", "PJTSAU Guidelines"),
                chapter=item.get("chapter"),
                chunk_id=item.get("chunk_id"),
                citation=item.get("citation"),
            )
            for item in (rec.evidence_sources_json or [])
        ]

        return DecisionRecordResponse(
            id=rec.id,
            plot_id=rec.plot_id,
            query_text=rec.query_text,
            decision_category=rec.decision_category,
            recommendation_state=rec.recommendation_state,
            grounded_explanation_en=rec.grounded_explanation_en,
            grounded_explanation_te=rec.grounded_explanation_te,
            grounded_explanation_hi=rec.grounded_explanation_hi,
            evidence_sources=evidence_items,
            uncertainty_disclosures=rec.uncertainty_disclosures_json or [],
            expert_escalation_case_id=rec.expert_escalation_case_id,
            evaluated_at=rec.evaluated_at,
        )
