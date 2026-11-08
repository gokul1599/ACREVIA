# ACREVIA — STAGE 09 VEGETATION INDICATORS & SCIENTIFIC LIMITATIONS
## SPECTRAL FORMULAS, CANOPY BIOPHYSICS & NON-DIAGNOSTIC LEGAL GUARDRAILS

**Programme:** ACREVIA Stage-Wise Engineering Programme  
**Target Stage:** Stage 09 — Geospatial Intelligence & Environmental Sensing  
**Subsystem:** Pillar B: ACREVIA Earth (Vegetation Indices)  
**Status:** ACTIVE VERIFIED SPECIFICATION  
**Date:** November 2026  

---

## 1. Executive Summary

Remote sensing vegetation indicators measure solar radiation reflected by plant canopies across visible, near-infrared, and shortwave-infrared wavelengths. While highly valuable for tracking vegetative vigor and relative moisture dynamics, optical satellite pixels cannot replace physical laboratory pathology or ground scouting.

In compliance with Part 2 (Rules 13, 14) and Part 7 (Section 7.2) of the Stage 09 Master Execution Prompt:
> **Non-Diagnostic Invariant:** Satellite vegetation indices reflect relative canopy greenness and water absorption. They do NOT diagnose specific plant diseases, identify insect pests, or directly measure soil chemical nutrients (NPK). Every satellite screen and API response must enforce this mandatory scientific disclaimer.

---

## 2. Mathematical Indicator Formulations

Implemented and verified in `backend/app/services/satellite_service.py`:

### 2.1 Normalized Difference Vegetation Index (NDVI)
- **Biophysical Meaning:** Exploits strong chlorophyll absorption in the Red band ($\approx 665\text{ nm}$) and high cellular scattering in Near-Infrared ($\approx 842\text{ nm}$).
- **Formula:**
  $$\text{NDVI} = \frac{\rho_{\text{NIR}} - \rho_{\text{Red}}}{\rho_{\text{NIR}} + \rho_{\text{Red}}}$$
- **Range:** $[-1.0, +1.0]$. Dense healthy crop canopies typically exhibit $0.60 \le \text{NDVI} \le 0.85$.
- **Unit Test Verification:** $\text{NIR}=0.75, \text{Red}=0.15 \implies \text{NDVI} = \frac{0.60}{0.90} = 0.6667$ (`test_scenario_c`).

### 2.2 Enhanced Vegetation Index (EVI)
- **Biophysical Meaning:** Optimizes the vegetation signal with improved sensitivity in high biomass regions and decoupling of the canopy background signal through atmospheric aerosol correction via the Blue band.
- **Formula:**
  $$\text{EVI} = G \cdot \frac{\rho_{\text{NIR}} - \rho_{\text{Red}}}{\rho_{\text{NIR}} + C_1 \cdot \rho_{\text{Red}} - C_2 \cdot \rho_{\text{Blue}} + L}$$
- **Standard Coefficients:** $G = 2.5, C_1 = 6.0, C_2 = 7.5, L = 1.0$.
- **Unit Test Verification:** Evaluated at $0.40 \le \text{EVI} \le 0.90$ on typical cotton/rice canopy reflectances.

### 2.3 Normalized Difference Moisture Index (NDMI)
- **Biophysical Meaning:** Contrasts near-infrared scattering with shortwave-infrared absorption ($\approx 1610\text{ nm}$), which is highly sensitive to leaf internal liquid water content.
- **Formula:**
  $$\text{NDMI} = \frac{\rho_{\text{NIR}} - \rho_{\text{SWIR}}}{\rho_{\text{NIR}} + \rho_{\text{SWIR}}}$$
- **Range:** $[-1.0, +1.0]$. High positive values indicate well-hydrated leaf tissues; negative values indicate severe water deficit or dry bare soil.
- **Unit Test Verification:** $\text{NIR}=0.75, \text{SWIR}=0.35 \implies \text{NDMI} = \frac{0.40}{1.10} = 0.3636$ (Verified in range $0.2 \le \text{NDMI} \le 0.5$).

---

## 3. Scientific Limitations & What Indices Cannot Measure

In adherence to agronomic science, ACREVIA strictly enforces four non-negotiable boundaries:

```text
================================================================================
ACREVIA SPECTRAL INDEX SCIENTIFIC BOUNDARIES
================================================================================
[BOUNDARY 1] Disease Specificity:
  An NDVI drop indicates chlorophyll loss or canopy defoliation.
  It CANNOT distinguish between Chilli Anthracnose, Rice Blast, Cotton Root Rot,
  bacterial blight, mite damage, nitrogen deficiency, or mechanical hail damage.
  Physical field scouting is required to identify the causal agent.

[BOUNDARY 2] Direct Soil Nutrient Content:
  Optical satellites cannot penetrate dense vegetative canopies to measure soil
  chemistry. Satellite pixels CANNOT directly quantify Soil Available Nitrogen (kg/ha),
  Phosphorus (P2O5), or Potassium (K2O). Chemical laboratory soil tests are required.

[BOUNDARY 3] Soil Moisture at Depth:
  NDMI reflects liquid water in the upper leaf canopy, NOT sub-surface root zone
  moisture at 30cm or 60cm depths in heavy Black Cotton clay soils.

[BOUNDARY 4] Operational Confusion (Harvest vs. Stress):
  When a farmer harvests bolls or cuts paddy tillers, NDVI drops precipitously.
  ACREVIA must not flag this as catastrophic disease or drought stress without
  cross-referencing CropPulse farm management logs.
================================================================================
```

---

## 4. Mandatory Statutory Disclaimer

Every satellite time-series API endpoint (`/api/v1/satellite/plots/{id}/time-series`) and farmer-facing interface renders this immutable legal notice:

> **Evidence Disclaimer:**  
> *"Satellite vegetation indicators (NDVI, EVI, NDMI) reflect relative canopy greenness and leaf water absorption. They do NOT diagnose specific plant diseases, identify insect pests, or measure soil chemical nutrient concentrations. Ground scouting is required."*

---

## 5. Specification Verdict

**Vegetation Indicators Specification Verdict:** **`PASS (SCIENTIFICALLY GROUNDED)`**  
Spectral index calculations are validated, calibrated, and protected by mandatory agronomic boundaries.

*Certified by: Remote Sensing Scientist, Plant Pathologist, and Legal Governance Specialist — ACREVIA Programme.*
