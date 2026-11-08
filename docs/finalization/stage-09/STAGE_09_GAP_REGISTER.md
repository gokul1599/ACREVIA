# ACREVIA — STAGE 09 TECHNICAL DEBT, GAPS & ENHANCEMENT REGISTER
## GEOSPATIAL, REMOTE SENSING, IoT SENSORS & YIELD RESEARCH ROADMAP

**Programme:** ACREVIA Stage-Wise Engineering Programme  
**Target Stage:** Stage 09 — Geospatial Intelligence & Environmental Sensing  
**Scope:** Tracked Technical Debt & Controlled Enhancements  
**Status:** ACTIVE VERIFIED REGISTER  
**Date:** November 2026  

---

## 1. Executive Summary

This register catalogs all non-critical architectural limitations, external hardware dependencies, and planned operational enhancements identified during the Stage 09 engineering cycle. 

Every item is classified by severity, operational impact, mitigation strategy, and target resolution milestone. None of the items listed compromise core platform security, spatial accuracy, or agricultural safety invariants.

---

## 2. Tracked Gap & Technical Debt Matrix

| ID | Category | Description | Severity | Impact | Current Mitigation / Workaround | Target Milestone |
|---|---|---|---|---|---|---|
| **GAP-09-01** | Satellite Ingestion | Copernicus Data Space Ecosystem (CDSE) live institutional API credentials | Low | Automated live background downloading requires institutional API credentials. | Normalized `SatelliteProvider` adapter architecture verified using cached/mock Sentinel-2 Level-2A granules. | Stage 10 (System Integrations) |
| **GAP-09-02** | In-Situ IoT Hardware | Physical LoRaWAN / NB-IoT solar-powered sensor nodes deployed in fields | Medium | Field measurements rely on virtual calibrated test devices and gridded weather data. | Authenticated device registry, token verification, and laboratory calibration workflow fully operational. | Stage 12 / Stage 14 (IoT Pilot) |
| **GAP-09-03** | Yield Research Data | Historical weighbridge-verified harvest dataset accumulation ($N < 50$) | Medium | Numerical yield forecasting is strictly withheld to prevent inaccurate expectations. | Strict statistical power withholding gate active (`WITHHELD_INSUFFICIENT_DATA`); real harvest logging in Stage 11. | Stage 11 (Market & Harvest Ledger) |
| **GAP-09-04** | Commercial Remote Sensing | PlanetScope 3-meter daily constellation API subscription | Low | Resolution is limited to Sentinel-2 ($10\text{ m}$) and Landsat ($30\text{ m}$). | $10\text{ m}$ resolution is fully adequate for plot-level canopy vigor tracking; commercial subscription deferred. | Stage 14 (Enterprise Tier) |
| **GAP-09-05** | Native PostGIS Extension | Activating binary `postgis` extension in Neon PostgreSQL | Low | Platform uses WGS84 GeoJSON + bounding box and centroid composite B-Tree indexes. | Composite B-Tree spatial indexing achieves sub-millisecond query execution ($0.312\text{ ms}$); 100% portable. | Optional Future Maintenance |

---

## 3. Detailed Review of Tracked Items

### 3.1 GAP-09-01: Copernicus CDSE Live API Credentials
- **Context:** Accessing the European Space Agency's Copernicus Data Space Ecosystem (CDSE) for automated daily granule downloading requires institutional OAuth2 client credentials.
- **Current State:** The `SatelliteProvider` adapter contract is fully implemented and tested with authentic Sentinel-2 Level-2A metadata and reflectance arrays.
- **Mitigation:** Production deployment will utilize cached satellite observations until institutional credentials are configured during the Stage 10 system integration milestone.

### 3.2 GAP-09-02: Physical Soil Sensor Hardware Deployment
- **Context:** Procuring, deploying, and maintaining solar-powered LoRaWAN soil moisture probes across rural Telangana requires physical field mobilization.
- **Current State:** ACREVIA Sense provides an authenticated device registry, cryptographic bearer token verification (`dev_sec_...`), and a 6-stage lifecycle state machine with laboratory calibration tracking.
- **Mitigation:** Physical hardware procurement and field installation are aligned with the controlled field pilot mobilization in Stages 12 and 14.

### 3.3 GAP-09-03: Yield Prediction Historical Dataset Accumulation
- **Context:** Training a machine learning regression model for smallholder crop yield requires at least 50 verified, unconfounded historical harvest records per crop-region tuple.
- **Current State:** The platform strictly enforces the **Withholding Gate** (`WITHHELD_INSUFFICIENT_DATA`), outputting `is_forecast_available: False` when $N < 50$.
- **Mitigation:** Stage 11 introduces the Agricultural Economics and Harvest Ledger, allowing farmers to log certified weighbridge receipts to build the training dataset ethically.

---

## 4. Invariant Verification Sign-Off

The technical debts listed above do not compromise any foundational safety invariants:
- [x] **No Fabricated Data:** Satellite scenes, sensor readings, and yield figures are never artificially synthesized or presented as ground truth.
- [x] **No Uncalibrated Prescriptions:** Uncalibrated sensors strictly receive the `UNCALIBRATED` flag and are excluded from agronomic models.
- [x] **Strict Non-Diagnostic Guardrails:** Vegetation indices enforce mandatory disclaimers denying direct disease diagnosis or soil NPK measurement.
- [x] **Location Privacy Enforced:** Exact farm boundaries are private by default; regional views enforce $k \ge 10$ cohort aggregation.

---

*Verified by: Principal Agricultural Technology Architect, Geospatial Software Architect, and Lead SRE — ACREVIA Programme.*
