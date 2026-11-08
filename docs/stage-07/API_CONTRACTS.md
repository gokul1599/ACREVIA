# ACREVIA — Stage 7 API Contracts Specification
## RiskCast, ExpertConnect & Intervention Outcome Tracking Endpoints

---

## 1. Overview & Base Configuration

- **API Base URL:** `/api/v1`
- **Authentication:** Bearer JWT in `Authorization` header.
- **Content-Type:** `application/json` (except media streams: `multipart/form-data` or `image/jpeg`).
- **Telemetry:** Injects `X-Correlation-ID` and `X-Response-Time-Ms` in all responses.

---

## 2. RiskCast Endpoints

### 2.1 Get Farm Agrometeorological & Risk Overview
- **Path:** `GET /api/v1/riskcast/farms/{farm_id}/overview`
- **Permissions:** `FARMER` (Farm owner/member), `AGRICULTURAL_EXPERT`, `ADMIN`.
- **Response:** `200 OK`
```json
{
  "farm_id": "9ac1646c-6a2b-4eaa-83fd-5512961816c9",
  "district": "Warangal",
  "current_weather": {
    "temperature_celsius": 28.5,
    "relative_humidity": 82.0,
    "precipitation_mm": 4.2,
    "wind_speed_kmh": 11.0,
    "leaf_wetness_hours": 7.5,
    "source_provider": "Open-Meteo Live API",
    "observation_time": "2026-11-08T09:30:00Z"
  },
  "plots_risk_summary": [
    {
      "plot_id": "cbe856a6-4735-484c-94ce-5ff66a617dc8",
      "plot_name": "South Plot - Cotton",
      "crop_id": "cotton",
      "growth_stage": "VEGETATIVE",
      "current_risk_level": "HIGH",
      "top_threat": "Cercospora Leaf Spot (Cercospora gossypina)",
      "advisory": "[HIGH RISK] Cercospora Leaf Spot: Humid spells favor fungal spots. Practice clean cultivation.",
      "active_alerts_count": 1
    }
  ],
  "active_alerts": []
}
```

### 2.2 Trigger Plot Risk Evaluation
- **Path:** `POST /api/v1/riskcast/evaluate/{plot_id}`
- **Permissions:** Farm Owner / Worker / Agronomist / Admin.
- **Response:** `201 Created`
```json
{
  "id": "b1a2c3d4-e5f6-7890-abcd-ef1234567890",
  "plot_id": "cbe856a6-4735-484c-94ce-5ff66a617dc8",
  "farm_id": "9ac1646c-6a2b-4eaa-83fd-5512961816c9",
  "crop_season_id": "s1a2b3c4-d5e6-7890-abcd-ef1234567890",
  "evaluation_timestamp": "2026-11-08T09:30:58Z",
  "overall_risk_level": "HIGH",
  "weather_data_id": "w1a2b3c4-d5e6-7890-abcd-ef1234567890",
  "weather_summary": {
    "temperature_celsius": 28.5,
    "relative_humidity": 82.0,
    "precipitation_mm": 4.2,
    "leaf_wetness_hours": 7.5,
    "source_provider": "Open-Meteo Live API"
  },
  "rules_triggered": [
    {
      "rule_code": "COT-CLSP-01",
      "target_threat": "Cercospora Leaf Spot (Cercospora gossypina)",
      "severity_level": "HIGH",
      "advisory_en": "Humid spells and moderate temperatures favor fungal leaf spots. Monitor lower canopy for circular brown spots with purple margins. Practice clean cultivation.",
      "advisory_te": "తేమతో కూడిన వాతావరణం వల్ల పత్తిలో ఆకుమచ్చ తెగులు వ్యాప్తి చెందే అవకాశం ఉంది.",
      "advisory_hi": "आर्द्र मौसम कपास में पत्ती धब्बा रोग के अनुकूल है।",
      "citations": ["PJTSAU Cotton Advisory (2023)", "ICAR-CICR Nagpur Bulletin"]
    }
  ],
  "advisory_en": "[HIGH RISK] Cercospora Leaf Spot: Humid spells and moderate temperatures favor fungal leaf spots.",
  "advisory_te": "[HIGH రిస్క్] ఆకుమచ్చ తెగులు: తేమతో కూడిన వాతావరణం వల్ల పత్తిలో ఆకుమచ్చ తెగులు వ్యాప్తి చెందే అవకాశం ఉంది.",
  "advisory_hi": "[HIGH जोखिम] पत्ती धब्बा रोग: आर्द्र मौसम कपास में पत्ती धब्बा रोग के अनुकूल है।",
  "limitations_notice": "High environmental risk denotes favorable climatic conditions for pathogen proliferation, NOT confirmed disease outbreak. Physical scouting required."
}
```

### 2.3 List, Acknowledge & Dismiss Alerts
- `GET /api/v1/riskcast/alerts?farm_id={farm_id}`: Lists alerts.
- `POST /api/v1/riskcast/alerts/{alert_id}/acknowledge`: Sets `is_acknowledged = true`, `acknowledged_at = now()`.
- `POST /api/v1/riskcast/alerts/{alert_id}/dismiss`: Sets `is_dismissed = true`, `dismissed_at = now()`.

---

## 3. ExpertConnect Endpoints

### 3.1 Apply for Expert Certification
- **Path:** `POST /api/v1/expertconnect/apply`
- **Body:**
```json
{
  "registration_number": "PJTSAU-AGRO-2026-089",
  "highest_degree": "Ph.D. in Plant Pathology",
  "institution": "PJTSAU Hyderabad",
  "specializations": ["COTTON", "CHILLI"],
  "districts_covered": ["Warangal", "Khammam", "Karimnagar"]
}
```
- **Response:** `201 Created` (`verification_status = "APPLICATION_SUBMITTED"`).

### 3.2 Admin Verification
- **Path:** `POST /api/v1/expertconnect/admin/verify/{profile_id}`
- **Permissions:** `ADMIN` role required.
- **Body:** `{"decision": "APPROVED"}`
- **Response:** `200 OK` (User granted `AGRICULTURAL_EXPERT` role).

### 3.3 Clinical Case Dossier
- **Path:** `GET /api/v1/expertconnect/cases/{case_id}`
- **Response:** `200 OK` (Includes farmer notes, foliar images, AI prediction with entropy/margin, KrishiBrain citations, and weather context).

### 3.4 Submit Certified Assessment
- **Path:** `POST /api/v1/expertconnect/cases/{case_id}/assess`
- **Permissions:** `AGRICULTURAL_EXPERT` or `ADMIN`.
- **Body:**
```json
{
  "confirmed_crop": "cotton",
  "primary_condition": "Cercospora Leaf Spot (Cercospora gossypina)",
  "differential_diagnoses": ["Alternaria Leaf Spot", "Bacterial Blight"],
  "confidence_rating": 4,
  "urgency_level": "ROUTINE",
  "management_plan": "Improve drainage, remove heavily infected lower leaves, and spray Copper Oxychloride 50% WP if progression exceeds 5% leaf area.",
  "ipm_strategy": "Cultural sanitation first. Clear crop residues and maintain proper plant spacing for aeration.",
  "cibrc_advisories": "Copper Oxychloride 50% WP @ 2.5-3.0 g/litre of water. Pre-Harvest Interval (PHI): 14 days."
}
```
- **Response:** `201 Created` (`revision_count = 0`).

### 3.5 Revise Assessment & Audit Log
- `PUT /api/v1/expertconnect/cases/{case_id}/assess`: Requires `revision_reason`. Creates `ExpertAssessmentRevision` preserving previous assessment JSON immutably.
- `GET /api/v1/expertconnect/cases/{case_id}/revisions`: Lists all prior revisions with timestamps, reasons, and author metadata.

---

## 4. Intervention Intelligence Endpoints

### 4.1 Record Field Intervention
- **Path:** `POST /api/v1/interventions/`
- **Permissions:** Farm Owner / Worker.
- **Body:**
```json
{
  "plot_id": "cbe856a6-4735-484c-94ce-5ff66a617dc8",
  "category": "BIOLOGICAL",
  "trade_name": "Neem Baan 1500 ppm",
  "active_ingredient": "Azadirachtin 0.15% EC",
  "dosage": 500.0,
  "unit": "ml/acre",
  "application_method": "FOLIAR_SPRAY",
  "application_date": "2026-11-08",
  "target_condition": "Sucking pests (Whitefly)",
  "phi_days": 3,
  "rei_hours": 12,
  "notes": "Applied early morning foliar spray with knapsack sprayer."
}
```
- **Response:** `201 Created`

### 4.2 Link Outcome Observation
- **Path:** `POST /api/v1/interventions/{intervention_id}/outcomes`
- **Body:**
```json
{
  "follow_up_observation_id": "03fc5184-5232-47b9-a44c-64135ce76221",
  "evaluation_date": "2026-11-13",
  "observed_status": "IMPROVING",
  "visual_change_notes": "Whitefly counts reduced from 8/leaf to 2/leaf; no phytotoxicity symptoms.",
  "confounding_factors": "Light intermittent shower 2 days ago; beneficial predator ladybird beetles spotted.",
  "farmer_assessment": "Satisfied with organic bio-repellent outcome."
}
```
- **Response:** `201 Created` (`days_post_intervention = 5`).

### 4.3 Get Comparative Timeline
- **Path:** `GET /api/v1/interventions/{intervention_id}/timeline`
- **Response:** `200 OK` (Returns initial foliar media, follow-up outcome media, and the mandatory non-causal disclaimer).
