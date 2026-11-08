# ACREVIA STAGE 10: REST API CONTRACTS & OPENAPI SPECIFICATION

---

## 1. Overview & Architecture

All Stage 10 endpoints are registered under `/api/v1` and enforce:
- **Authentication:** Bearer JWT in the `Authorization` header (`Bearer <token>`).
- **Tenant Isolation:** Access strictly restricted to resources owned by the authenticated farmer, or assigned extension workers/experts with verified role permissions.
- **Content Type:** `application/json` for requests and responses.
- **Error Standard:** Standardized error format matching ACREVIA core exception structure (`{"detail": "...", "code": "...", "status_code": 4xx/5xx}`).

---

## 2. Digital Twin Endpoints (`/api/v1/twin`)

### 2.1 Get Current Farm Digital Twin
- **Method:** `GET`
- **Path:** `/api/v1/twin/farms/{farm_id}`
- **Security:** Authenticated user with farm ownership or extension access.
- **Response `200 OK`:**
```json
{
  "id": "twin_uuid",
  "farm_id": "farm_uuid",
  "twin_version": 4,
  "state_status": "SYNCHRONIZED",
  "completeness_score": 87.5,
  "last_synchronized_at": "2026-11-08T06:00:00Z",
  "plots": [
    {
      "plot_id": "plot_uuid",
      "plot_name": "East Cotton Field",
      "area_hectares": 1.8,
      "soil_type": "BLACK_COTTON",
      "current_season": {
        "season_id": "season_uuid",
        "crop_name": "Cotton",
        "variety": "RCH-659 BG II",
        "sowing_date": "2026-07-01",
        "growth_stage": "BOLL_DEVELOPMENT",
        "gdd_accumulated": 1420.5
      },
      "latest_measurements": {
        "ndvi": {"value": 0.68, "provenance": "PROVIDER_OBSERVATION", "date": "2026-11-05"},
        "soil_moisture_pct": {"value": 24.2, "provenance": "MEASURED", "date": "2026-11-07"}
      }
    }
  ]
}
```

### 2.2 List Farm Twin Snapshots
- **Method:** `GET`
- **Path:** `/api/v1/twin/farms/{farm_id}/snapshots`
- **Query Params:** `limit` (default: 10), `offset` (default: 0)
- **Response `200 OK`:**
```json
{
  "items": [
    {
      "id": "snapshot_uuid",
      "twin_id": "twin_uuid",
      "snapshot_version": 4,
      "data_completeness_pct": 87.5,
      "generated_at": "2026-11-08T06:00:00Z",
      "source_manifest": {
        "iot_readings_count": 14,
        "satellite_scenes_count": 2,
        "diagnoses_count": 1
      }
    }
  ],
  "total": 12
}
```

### 2.3 Get Farm Data Completeness Vector
- **Method:** `GET`
- **Path:** `/api/v1/twin/farms/{farm_id}/completeness`
- **Response `200 OK`:**
```json
{
  "farm_id": "farm_uuid",
  "overall_score": 87.5,
  "dimensions": {
    "cadastral_boundary": 100.0,
    "soil_profile": 100.0,
    "crop_season_active": 100.0,
    "sowing_date": 100.0,
    "iot_telemetry": 75.0,
    "satellite_coverage": 80.0,
    "pest_scouting": 70.0
  },
  "missing_critical_fields": [],
  "recommendations": [
    "Upload recent soil moisture sensor calibration"
  ]
}
```

### 2.4 Trigger Farm Twin Reconciliation
- **Method:** `POST`
- **Path:** `/api/v1/twin/farms/{farm_id}/reconcile`
- **Response `200 OK`:**
```json
{
  "twin_id": "twin_uuid",
  "farm_id": "farm_uuid",
  "reconciled_events_count": 5,
  "previous_version": 3,
  "current_version": 4,
  "status": "SYNCHRONIZED",
  "timestamp": "2026-11-08T10:35:00Z"
}
```

---

## 3. Simulation Endpoints (`/api/v1/simulations`)

### 3.1 Create and Run Simulation Scenario
- **Method:** `POST`
- **Path:** `/api/v1/simulations`
- **Request Body:**
```json
{
  "plot_id": "plot_uuid",
  "crop_season_id": "season_uuid",
  "scenario_name": "Delayed Irrigation 5 Days",
  "scenario_type": "IRRIGATION_WATER_BALANCE",
  "input_parameters": {
    "irrigation_depth_mm": 35.0,
    "days_offset": 5,
    "efficiency": 0.85
  },
  "farmer_assumptions": {
    "weather_condition": "DRY_SPELL",
    "pump_availability_hours": 6
  }
}
```
- **Response `201 Created`:**
```json
{
  "id": "scenario_uuid",
  "scenario_name": "Delayed Irrigation 5 Days",
  "scenario_type": "IRRIGATION_WATER_BALANCE",
  "status": "COMPLETED",
  "result": {
    "model_name": "FAO-56_DUAL_KC",
    "model_version": "v1.4",
    "outputs": {
      "root_zone_depletion_mm": 48.2,
      "relative_transpiration_ratio": 0.82,
      "water_stress_index": 0.35,
      "waterlogging_risk_pct": 0.0,
      "depletion_trajectory_7d": [28.0, 32.5, 37.1, 41.8, 46.4, 48.2, 51.0]
    },
    "uncertainty_metadata": {
      "confidence_band_lower": 0.28,
      "confidence_band_upper": 0.42,
      "p_value": 0.02
    },
    "execution_duration_ms": 42.5
  }
}
```

### 3.2 Compare Simulation Scenarios
- **Method:** `POST`
- **Path:** `/api/v1/simulations/compare`
- **Request Body:**
```json
{
  "scenario_ids": ["scenario_uuid_1", "scenario_uuid_2"]
}
```
- **Response `200 OK`:** Returns side-by-side metric comparison, difference vectors, and trade-off analysis.

---

## 4. Resource Optimization Endpoints (`/api/v1/optimization`)

### 4.1 Create and Solve Resource Optimization Problem
- **Method:** `POST`
- **Path:** `/api/v1/optimization/problems`
- **Request Body:**
```json
{
  "farm_id": "farm_uuid",
  "problem_type": "WATER_ALLOCATION",
  "objective_type": "MAXIMIZE_WATER_PRODUCTIVITY",
  "decision_variables": {
    "plots": ["plot_uuid_1", "plot_uuid_2"]
  },
  "hard_constraints": {
    "max_water_volume_m3": 120.0,
    "pump_hours_available": 8.0,
    "flow_rate_lps": 4.2
  },
  "soft_constraints": {
    "target_uniformity_pct": 85.0
  }
}
```
- **Response `201 Created`:**
```json
{
  "id": "opt_uuid",
  "farm_id": "farm_uuid",
  "problem_type": "WATER_ALLOCATION",
  "status": "SOLVED",
  "result": {
    "feasibility_status": "FEASIBLE",
    "selected_solution": {
      "allocated_depths_mm": {
        "plot_uuid_1": 25.0,
        "plot_uuid_2": 30.0
      },
      "total_water_used_m3": 105.4,
      "pump_hours_required": 7.1
    },
    "conflicting_constraints": [],
    "trade_off_analysis": {
      "water_saved_pct": 12.1,
      "stress_mitigated_pct": 94.0
    },
    "solver_name": "SIMPLEX_BOUNDED_LP",
    "solved_at": "2026-11-08T10:36:00Z"
  }
}
```

---

## 5. Crop Planning Endpoints (`/api/v1/planning`)

### 5.1 List Recommended Crop Calendars
- **Method:** `GET`
- **Path:** `/api/v1/planning/calendars`
- **Query Params:** `crop_name`, `agro_climatic_zone` (e.g. `TELANGANA_NORTH_EASTERN`)
- **Response `200 OK`:** Returns official PJTSAU package of practice milestones and scheduled operations.

### 5.2 Create Operations Task
- **Method:** `POST`
- **Path:** `/api/v1/planning/tasks`
- **Request Body:**
```json
{
  "crop_season_id": "season_uuid",
  "plot_id": "plot_uuid",
  "task_name": "Post-Emergence Herbicide Spray",
  "task_category": "PLANT_PROTECTION",
  "due_date": "2026-11-10",
  "notes": "Apply recommended dosage as per PJTSAU advisory"
}
```

### 5.3 Complete Operations Task
- **Method:** `POST`
- **Path:** `/api/v1/planning/tasks/{id}/complete`
- **Request Body:**
```json
{
  "actual_date": "2026-11-10",
  "labor_hours": 4.5,
  "materials_used": [{"item": "Pyrithiobac sodium", "quantity_ml": 250}],
  "observations": "Clean weed knockdown observed"
}
```

---

## 6. Decision Intelligence Endpoints (`/api/v1/decisions`)

### 6.1 Analyze Farm Query & Generate Grounded Decision
- **Method:** `POST`
- **Path:** `/api/v1/decisions/analyze`
- **Request Body:**
```json
{
  "plot_id": "plot_uuid",
  "query_text": "Should I irrigate my chilli crop tomorrow given the high wind alert?",
  "decision_category": "IRRIGATION_SCHEDULING"
}
```
- **Response `200 OK`:**
```json
{
  "id": "dec_uuid",
  "plot_id": "plot_uuid",
  "decision_category": "IRRIGATION_SCHEDULING",
  "recommendation_state": "EVIDENCE_SUPPORTED",
  "grounded_explanation_en": "Irrigation should be postponed by 24 hours. Forecast wind gusts exceed 25 km/h, which reduces sprinkler distribution uniformity below 60% and increases drift losses. Soil moisture is currently adequate (26% volumetric content).",
  "grounded_explanation_te": "రేపటి నీటి పారుదలని 24 గంటలు వాయిదా వేయడం మంచిది. గాలి వేగం గంటకు 25 కి.మీ మించి ఉన్నందున నీటి నష్టం ఎక్కువగా ఉంటుంది. నేలలో ప్రస్తుతం సరిపడా తేమ (26%) ఉంది.",
  "grounded_explanation_hi": "कल की सिंचाई को 24 घंटे के लिए स्थगित करने की सलाह दी जाती है। हवा की गति 25 किमी/घंटा से अधिक होने के कारण छिड़काव एकसमान नहीं होगा। मिट्टी में वर्तमान में पर्याप्त नमी (26%) मौजूद है।",
  "evidence_sources": [
    {
      "source_title": "PJTSAU Chilli Water Management Guidelines (2025)",
      "chapter": "Sprinkler Operation Constraints",
      "chunk_id": "kb_chunk_8412"
    }
  ],
  "uncertainty_disclosures": [
    "Weather forecast certainty decreases beyond 48 hours."
  ],
  "expert_escalation_required": false
}
```
