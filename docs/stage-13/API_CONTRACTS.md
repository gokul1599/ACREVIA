# ACREVIA — API Contracts Specification (Stage 13)

**Project:** ACREVIA — Agricultural Intelligence Platform  
**Stage:** 13 — Climate-Resilient & Sustainable Agriculture  
**Protocol:** RESTful HTTPS JSON  
**Base URL:** `/api/v1`  
**Authentication:** Bearer JWT Header (`Authorization: Bearer <token>`)  

---

## 1. Soil Health Intelligence Endpoints (`/api/v1/soil`)

### 1.1 Log Soil Sample
- **Endpoint:** `POST /api/v1/soil/samples`
- **Roles:** `FARMER`, `AGRONOMIST`, `ADMIN`
- **Request Body:**
```json
{
  "plot_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "sample_code": "WAR-PLT1-2026-01",
  "sampling_date": "2026-10-15T08:00:00Z",
  "sampling_depth_min_cm": 0.0,
  "sampling_depth_max_cm": 15.0,
  "gps_latitude": 17.9689,
  "gps_longitude": 79.5941,
  "composite_cores_count": 8
}
```
- **Response (201 Created):** Returns created `SoilSampleResponse`.

### 1.2 Ingest Accredited Lab Test Result
- **Endpoint:** `POST /api/v1/soil/lab-results`
- **Roles:** `AGRONOMIST`, `ADMIN`, `LAB_ANALYST`
- **Request Body:**
```json
{
  "soil_sample_id": "7fa85f64-5717-4562-b3fc-2c963f66afa6",
  "laboratory_name": "PJTSAU Regional Soil Testing Laboratory, Warangal",
  "accreditation_number": "NABL-TC-8912",
  "ph": 7.4,
  "electrical_conductivity_ec": 0.65,
  "organic_carbon_percent": 0.58,
  "available_nitrogen_kg_ha": 240.0,
  "available_phosphorus_kg_ha": 18.5,
  "available_potassium_kg_ha": 310.0,
  "available_zinc_ppm": 0.52,
  "available_boron_ppm": 0.45,
  "provenance": {
    "method_nitrogen": "ALKALINE_PERMANGANATE",
    "method_phosphorus": "OLSEN_BICARBONATE",
    "analyst_id": "TECH_402"
  }
}
```
- **Response (201 Created):** Returns `SoilTestResultResponse`.

### 1.3 Query Plot Soil History
- **Endpoint:** `GET /api/v1/soil/plot/{plot_id}/history`
- **Roles:** `FARMER`, `AGRONOMIST`, `ADMIN`
- **Response (200 OK):** Array of historical tests with longitudinal delta.

---

## 2. Precision Water Management Endpoints (`/api/v1/water`)

### 2.1 Register Farm Water Source
- **Endpoint:** `POST /api/v1/water/sources`
- **Roles:** `FARMER`, `ADMIN`
- **Request Body:**
```json
{
  "farm_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "source_type": "BOREWELL",
  "source_name": "North Field Borewell #1",
  "depth_meters": 120.0,
  "static_water_level_m": 42.5,
  "discharge_capacity_lps": 3.5,
  "salinity_ec_dsm": 0.85,
  "ph": 7.2,
  "sar": 2.1,
  "seasonal_availability": {"kharif": true, "rabi": true, "summer": false}
}
```
- **Response (201 Created):** Returns `WaterSourceResponse`.

### 2.2 Record Irrigation Event
- **Endpoint:** `POST /api/v1/water/irrigation-events`
- **Roles:** `FARMER`, `ADMIN`
- **Request Body:**
```json
{
  "plot_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "water_source_id": "2fa85f64-5717-4562-b3fc-2c963f66afa6",
  "event_date": "2026-10-18T06:00:00Z",
  "irrigation_method": "DRIP",
  "duration_hours": 3.5,
  "flow_meter_start_m3": 1420.0,
  "flow_meter_end_m3": 1464.0,
  "soil_moisture_before": 18.5,
  "soil_moisture_after": 28.2
}
```
- **Response (201 Created):** Returns `IrrigationEventResponse` with computed volume ($44.0\text{ m}^3$) and equivalent depth ($mm$).

### 2.3 Query Water Balance Snapshot
- **Endpoint:** `GET /api/v1/water/plot/{plot_id}/balance`
- **Response (200 OK):**
```json
{
  "plot_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "snapshot_date": "2026-10-18T00:00:00Z",
  "effective_precipitation_mm": 0.0,
  "irrigation_applied_mm": 11.0,
  "crop_evapotranspiration_mm": 4.8,
  "deep_percolation_mm": 0.5,
  "runoff_mm": 0.0,
  "storage_change_mm": 5.7,
  "accounting_status": "COMPLETED_WITH_VALIDATED_INPUTS",
  "management_allowed_depletion_percent": 45.0,
  "current_depletion_percent": 22.0
}
```

---

## 3. Climate Resilience Endpoints (`/api/v1/climate`)

### 3.1 Get District 30-Year Baseline Normals
- **Endpoint:** `GET /api/v1/climate/baselines/{district_code}`
- **Response (200 OK):** Array of monthly climatological normals ($1-12$).

### 3.2 Evaluate Climate Exposure Assessment
- **Endpoint:** `POST /api/v1/climate/assess-exposure`
- **Request Body:**
```json
{
  "plot_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "crop_id": "4fa85f64-5717-4562-b3fc-2c963f66afa6",
  "crop_stage": "FLOWERING_BOLL_FORMATION",
  "forecast_tmax": 39.5,
  "forecast_rainfall_next_7_days": 0.0,
  "consecutive_rainless_days": 16
}
```
- **Response (200 OK):**
```json
{
  "hazard_type": "DRY_SPELL",
  "severity_level": "HIGH",
  "vulnerability_score": 0.78,
  "recommended_adaptation": "Foliar spray of 1% KNO3 to protect squares from shedding; implement alternate-furrow life-saving irrigation.",
  "institutional_citation": "PJTSAU Kharif Contingency Plan 2026 / ICAR-CRIDA"
}
```

---

## 4. Nutrient Intelligence Endpoints (`/api/v1/nutrient`)

### 4.1 Generate Soil-Test Based Nutrient Prescription
- **Endpoint:** `POST /api/v1/nutrient/prescribe`
- **Request Body:**
```json
{
  "soil_test_result_id": "7fa85f64-5717-4562-b3fc-2c963f66afa6",
  "crop_id": "4fa85f64-5717-4562-b3fc-2c963f66afa6",
  "yield_target_quintals_per_acre": 12.0
}
```
- **Response (200 OK):**
```json
{
  "id": "8fa85f64-5717-4562-b3fc-2c963f66afa6",
  "crop_name": "Cotton",
  "nitrogen_status": "DEFICIENT",
  "phosphorus_status": "DEFICIENT",
  "potassium_status": "SUFFICIENT",
  "zinc_status": "DEFICIENT",
  "boron_status": "DEFICIENT",
  "recommended_n_kg_ha": 144.0,
  "recommended_p2o5_kg_ha": 72.0,
  "recommended_k2o_kg_ha": 48.0,
  "split_application_schedule": [
    {"stage": "BASAL", "n_kg": 28.8, "p2o5_kg": 72.0, "k2o_kg": 14.4, "timing": "At sowing"},
    {"stage": "VEGETATIVE", "n_kg": 43.2, "p2o5_kg": 0.0, "k2o_kg": 9.6, "timing": "30 DAS"},
    {"stage": "SQUARE_FORMATION", "n_kg": 43.2, "p2o5_kg": 0.0, "k2o_kg": 14.4, "timing": "60 DAS"},
    {"stage": "BOLL_DEVELOPMENT", "n_kg": 28.8, "p2o5_kg": 0.0, "k2o_kg": 9.6, "timing": "90 DAS"}
  ],
  "micronutrient_recommendations": [
    "Apply Zinc Sulphate @ 25 kg/ha to soil basally due to DTPA-Zn < 0.6 ppm",
    "Foliar spray Borax @ 1.5 g/L at peak flowering"
  ],
  "safeguard_checks_passed": true,
  "institutional_citation": "PJTSAU Vyavasaya Panchangam 2026 Cotton Protocol"
}
```

### 4.2 Submit Expert Agronomist Review
- **Endpoint:** `POST /api/v1/nutrient/expert-review`
- **Roles:** `AGRONOMIST`, `ADMIN`
- **Request Body:**
```json
{
  "nutrient_assessment_id": "8fa85f64-5717-4562-b3fc-2c963f66afa6",
  "review_status": "APPROVED",
  "agronomist_notes": "Prescription verified against local Vertisol characteristics. Advise farmer not to mix ZnSO4 with DAP."
}
```

---

## 5. Sustainable Agriculture Endpoints (`/api/v1/sustain`)

### 5.1 Query Canonical Sustainable Practices
- **Endpoint:** `GET /api/v1/sustain/practices`
- **Response (200 OK):** List of practice definitions with multilingual titles.

### 5.2 Log Farm Practice
- **Endpoint:** `POST /api/v1/sustain/records`
- **Request Body:**
```json
{
  "plot_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "practice_code": "GREEN_MANURE",
  "implementation_date": "2026-06-12T00:00:00Z",
  "area_covered_acres": 2.5,
  "verification_method": "FARMER_LOG"
}
```

### 5.3 Record Empirical Soil Organic Carbon
- **Endpoint:** `POST /api/v1/sustain/carbon-measurement`
- **Request Body:**
```json
{
  "plot_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "sample_date": "2026-10-15T00:00:00Z",
  "depth_cm": 15.0,
  "soc_percent": 0.58,
  "bulk_density": 1.32,
  "method": "WALKLEY_BLACK",
  "lab_accreditation": "NABL-TC-8912"
}
```

### 5.4 Research-Grade Greenhouse Gas Emissions
- **Endpoint:** `GET /api/v1/sustain/plot/{plot_id}/emissions?season=Kharif&year=2026`
- **Response (200 OK):** Returns emission breakdown with mandatory disclaimer: `"ACREVIA GHG estimations are research-grade indicative metrics based on IPCC Tier 1/2 factors. They do not constitute certified carbon credits or tradable offsets."`

---

## 6. Agricultural Resilience Engine Endpoints (`/api/v1/resilience`)

### 6.1 Evaluate Plot Resilience Assessment
- **Endpoint:** `POST /api/v1/resilience/assess`
- **Request Body:**
```json
{
  "plot_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6"
}
```
- **Response (200 OK):**
```json
{
  "id": "9fa85f64-5717-4562-b3fc-2c963f66afa6",
  "plot_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "overall_resilience_score": 72.4,
  "soil_score": 68.0,
  "water_score": 75.0,
  "climate_score": 62.0,
  "nutrient_score": 80.0,
  "practice_score": 77.0,
  "evidence_quality_score": 0.88,
  "confidence_category": "HIGH_CONFIDENCE_EMPIRICAL",
  "top_vulnerabilities": [
    "Extended dry spell risk during flowering stage",
    "Subsoil compaction at 25cm restricting root penetration"
  ],
  "adaptation_recommendations": [
    "Adopt alternate furrow irrigation to stretch available borewell volume by 35%",
    "Maintain residue mulch to buffer soil temperature"
  ],
  "evaluated_at": "2026-10-18T12:00:00Z"
}
```
