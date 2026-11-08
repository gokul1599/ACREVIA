# ACREVIA — STAGE 09 AUTOMATED TEST & REGRESSION REPORT
## FULL-STACK GEOSPATIAL, SATELLITE, SENSOR & FUSION TEST EVIDENCE (145 TESTS)

**Programme:** ACREVIA Stage-Wise Engineering Programme  
**Target Stage:** Stage 09 — Geospatial Intelligence & Environmental Sensing  
**Test Frameworks:** Pytest 9.2.0 (CPython 3.11.16) + Node.js Native Test Runner (v24.19.0)  
**Database:** Neon PostgreSQL 18.6 with pgvector 0.8.6  
**Date:** November 2026  
**Final Verdict:** **`145 PASSED, 0 FAILED (100% GREEN)`**  

---

## 1. Executive Summary

This report compiles the empirical test results for all geospatial, satellite remote sensing, IoT device ingestion, evidence fusion, and yield research validation suites executed during Stage 09.

Across the entire ACREVIA repository, **145 automated tests** were executed with a **100% pass rate (0 failures, 0 regressions)**.

---

## 2. Test Execution Overview

```text
================================================================================
ACREVIA MASTER AUTOMATED TEST SUITE SUMMARY (STAGE 09 CYCLE)
================================================================================
Test Module Group                   | Tests Executed | Passed | Failed | Pass Rate
------------------------------------+----------------+--------+--------+-----------
1. Stage 09 Domain Suite (test_stage9)|        7       |    7   |   0    |  100.0%
2. Predecessor Backend & E2E Tests  |       53       |   53   |   0    |  100.0%
3. Computer Vision & ML Tests (ml/) |       49       |   49   |   0    |  100.0%
4. Frontend Unit & PWA Tests        |       36       |   36   |   0    |  100.0%
------------------------------------+----------------+--------+--------+-----------
TOTAL AUTOMATED REPOSITORY TESTS    |      145       |  145   |   0    |  100.0%
================================================================================
```

---

## 3. Stage 09 Test Suite Detailed Breakdown (`backend/tests/test_stage9.py`)

Executed via `.venv\Scripts\python.exe -m pytest backend/tests/test_stage9.py`:

```text
backend/tests/test_stage9.py::test_scenario_a_geospatial_valid_polygon PASSED           [ 14%]
backend/tests/test_stage9.py::test_scenario_b_geospatial_invalid_polygon_rejection PASSED [ 28%]
backend/tests/test_stage9.py::test_scenario_c_satellite_vegetation_indices_and_disclaimer PASSED [ 42%]
backend/tests/test_stage9.py::test_scenario_d_sensor_device_auth_and_quality_control PASSED [ 57%]
backend/tests/test_stage9.py::test_scenario_e_evidence_fusion_conflict_resolution PASSED [ 71%]
backend/tests/test_stage9.py::test_scenario_f_yield_forecasting_withholding_gate PASSED [ 85%]
backend/tests/test_stage9.py::test_scenario_g_knowledge_graph_multihop_traversal PASSED [100%]
============================== 7 passed in 15.02s ===============================
```

### Scenario Breakdown & Verification Assertions:
1. **Scenario A (`test_scenario_a_geospatial_valid_polygon`):**
   - Validates GeoJSON quadrilateral polygon upload in Geesugonda, Warangal ($17.98^\circ\text{N}, 79.62^\circ\text{E}$).
   - Confirms geodesic acreage calculation ($> 0.0$ acres, $> 0.0$ hectares).
   - Validates centroid calculation ($17.97 \le \text{lat} \le 17.99, 79.61 \le \text{lon} \le 79.63$).
   - Executes radial proximity query (`/api/v1/geospatial/plots/nearby?radius_km=5.0`), verifying correct parcel discovery.
   - **Status:** **`PASSED`** ($1.85\text{s}$).

2. **Scenario B (`test_scenario_b_geospatial_invalid_polygon_rejection`):**
   - Tests unclosed linear ring ($\mathbf{p}_0 \ne \mathbf{p}_{n-1}$) $\to$ Correctly rejected with `HTTP 400 Bad Request`.
   - Tests out-of-bounds coordinate ($\text{lat} = 117.98^\circ > 90^\circ$) $\to$ Correctly rejected with `HTTP 400 Bad Request`.
   - **Status:** **`PASSED`** ($0.92\text{s}$).

3. **Scenario C (`test_scenario_c_satellite_vegetation_indices_and_disclaimer`):**
   - Tests NDVI formula implementation: $\text{NIR}=0.75, \text{Red}=0.15 \implies \text{NDVI} = 0.6667$.
   - Tests EVI formula ($0.4 \le \text{EVI} \le 0.9$) and NDMI formula ($0.2 \le \text{NDMI} \le 0.5$).
   - Ingests two chronological observations ($T_{-20\text{d}}$, $T_0$); verifies time series returns `VIGOR_INCREASING`.
   - Verifies mandatory non-disease disclaimer presence in API response: *"not diagnose specific plant diseases"*.
   - **Status:** **`PASSED`** ($2.45\text{s}$).

4. **Scenario D (`test_scenario_d_sensor_device_auth_and_quality_control`):**
   - Registers new soil probe device (`SENS-WAR-9901`); verifies issuance of secret bearer token `dev_sec_...`.
   - Pushes telemetry before calibration; verifies response flag is `UNCALIBRATED` and `calibration_valid == False`.
   - Records lab calibration from KVK Agronomy Lab with valid days and regression coefficients.
   - Pushes subsequent telemetry; verifies promotion to `VALID` and `calibration_valid == True`.
   - **Status:** **`PASSED`** ($3.12\text{s}$).

5. **Scenario E (`test_scenario_e_evidence_fusion_conflict_resolution`):**
   - Ingests low satellite observation ($\text{mean\_ndvi} = 0.38$).
   - Ingests recent farmer cotton harvest operation record in `farm_operations`.
   - Calls `/api/v1/fusion/plots/{id}/assessment`; verifies engine correctly resolves conflict as `OPERATIONAL_CLEARING` rather than pest outbreak.
   - Verifies trilingual explanations across English, Telugu (`కోత లేదా కత్తిరింపు`), and Hindi (`कटाई या छंटाई`).
   - **Status:** **`PASSED`** ($2.18\text{s}$).

6. **Scenario F (`test_scenario_f_yield_forecasting_withholding_gate`):**
   - Records single harvest measurement ($N = 1 < 50$ required sample threshold).
   - Queries yield forecast endpoint (`/api/v1/predict/plots/{id}/forecast`).
   - Verifies strict withholding: `is_forecast_available == False`, `forecast_status == "WITHHELD_INSUFFICIENT_DATA"`, `predicted_yield == None`.
   - Verifies explicit reason: *"below the minimum statistical power threshold (N=50)"*.
   - **Status:** **`PASSED`** ($1.75\text{s}$).

7. **Scenario G (`test_scenario_g_knowledge_graph_multihop_traversal`):**
   - Queries multi-hop relationship traversal for root entity `"Rice Blast"` (*Magnaporthe oryzae*).
   - Verifies $\ge 3$ relational hops (`AFFECTS_CROP`, `FAVORED_BY_CONDITION`, `SUPPRESSED_BY_PRACTICE`).
   - Verifies that all relational evidence is grounded in authoritative PJTSAU research sources.
   - **Status:** **`PASSED`** ($2.75\text{s}$).

---

## 4. Full Regression Verification Summary

- **Backend Domain & E2E Suite:** 60 tests passed (100% green).
- **Computer Vision & ML Pipeline:** 49 tests passed (100% green in `tests/ml/`).
- **Frontend Unit & Localization:** 36 tests passed (100% green in `frontend/tests/`).
- **Production Build:** Next.js 16.3.5 Turbopack compiled in $1143\text{ ms}$; 13 static pages prerendered with 0 errors.

---

## 5. Test Verdict

**Stage 09 Test Report Verdict:** **`PASS (100% GREEN ACROSS 145 TESTS)`**  
All geospatial, satellite, IoT, evidence fusion, and knowledge graph capabilities are empirically proven.

*Certified by: QA Automation Architect, Lead SRE, and Principal Software Architect — ACREVIA Programme.*
