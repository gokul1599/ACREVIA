# ACREVIA — YIELD FORECASTING RESEARCH (PILLAR E: ACREVIA PREDICT)
## Governed Feasibility Framework, Leakage-Free Feature Engineering & Withholding Policies

---

## 1. Research Overview & Problem Statement
Predicting smallholder crop yield (quintals per acre) in Telangana involves significant variance driven by sowing date, seed quality, micro-irrigation management, fertilizer splits, and sudden pest attacks (e.g., Pink Bollworm in cotton, Brown Planthopper in rice).

Commercial AI platforms often fabricate ungrounded yield predictions using naive NDVI regressions. Such predictions mislead farmers, misinform credit scoring, and damage institutional trust.

> [!CAUTION]
> **GOVERNED WITHHOLDING SAFEGUARD (NON-NEGOTIABLE):**
> Acrevia Predict operates under a strict scientific withholding rule:
> **If historical ground-truth harvest records for a crop and agro-climatic zone fall below minimum sample thresholds ($N < 50$ verified seasons), or if the model's prediction error interval exceeds $\pm 35\%$, the system MUST withhold production yield forecasts and return `NOT_READY / RESEARCH_ONLY` with an explicit scientific justification.**
> Under no circumstances may artificial yield numbers be output to farmers or financial partners.

---

## 2. Historical Harvest Data Provenance & Audit

Yield models require rigorous ground-truth data verification:
1. **Provenance Tiers:**
   - **Tier 1 (Highest):** Verified weighbridge receipt or agricultural market committee (AMC) sale bill with matching plot ID.
   - **Tier 2 (High):** Standardized crop cutting experiment (CCE) conducted by an agronomist or field extension officer.
   - **Tier 3 (Unverified):** Farmer self-reported verbal estimate at season end.
2. **Audit Rule:** Tier 3 self-reports are excluded from primary model training sets or down-weighted by $70\%$ unless corroborated by village-level historical benchmarks.

---

## 3. Leakage-Free Feature Engineering Pipeline

To prevent temporal and spatial data leakage:
1. **Temporal Split:** Models are trained strictly on historical seasons ($t < t_{\text{target}}$) and evaluated on forward out-of-time seasons ($t \ge t_{\text{target}}$).
2. **Spatial Holdout:** Validation folds hold out entire mandals to prevent spatial autocorrelation leakage.
3. **Causal Pre-Harvest Features:** Only features known prior to harvest window are included:
   - **Thermal & Weather Aggregates:** Growing Degree Days ($\sum GDD_{10}$), seasonal cumulative rainfall, maximum heat stress days ($T_{\max} > 38^\circ\text{C}$).
   - **Satellite Vegetation Trajectory:** Peak vegetative NDVI, Integrated Seasonal NDVI (Area Under Curve), Mid-season NDMI moisture deficit.
   - **Soil & Management Factors:** Soil texture group (Black Cotton, Red Chalka), irrigation mode (Rainfed vs Drip/Borewell), cultivar maturity class.

---

## 4. Model Benchmarking & Feasibility Gate

| Crop | Verified Historical Sample Size ($N$) | Baseline Model | Holdout $R^2$ | Mean Absolute Error (MAE) | Feasibility Decision |
|---|---|---|---|---|---|
| **Cotton** | $N = 18$ (Preliminary) | Ridge / LightGBM | $0.29$ | $\pm 42\%$ | **WITHHELD (`NOT_READY / RESEARCH_ONLY`)** |
| **Rice** | $N = 24$ (Preliminary) | Random Forest / GBDT | $0.34$ | $\pm 38\%$ | **WITHHELD (`NOT_READY / RESEARCH_ONLY`)** |
| **Chilli** | $N = 12$ (Preliminary) | Ridge Regression | $0.21$ | $\pm 47\%$ | **WITHHELD (`NOT_READY / RESEARCH_ONLY`)** |

### Feasibility Conclusion:
At Stage 09, harvest ground-truth sample sizes are still in the initial pilot collection phase across Telangana partner farms. The system correctly exercises epistemic integrity: **Yield predictions remain in research phase with explicit disclosure.**
