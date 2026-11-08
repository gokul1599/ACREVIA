# ACREVIA — Nutrient Intelligence and Governance Architecture (Pillar D)

**Project:** ACREVIA — Agricultural Intelligence Platform  
**Stage:** 13 — Climate-Resilient & Sustainable Agriculture  
**Focus:** Soil-Test Interpretation, Crop Nutrient Management, Prescription Safeguards & Agronomist Escalation  
**Target Region:** Telangana-First (PJTSAU Agro-climatic zones)  
**Target Crops:** Cotton (*Gossypium hirsutum*), Rice (*Oryza sativa*), Chilli (*Capsicum annuum*)  

---

## 1. Executive Summary & Principles

Imbalanced chemical fertilizer application in Telangana has led to rampant soil acidification, zinc and boron exhaustion, excessive vegetative growth, pest resurgence (e.g., sucking pests in cotton and chilli), and elevated cultivation costs.

The **ACREVIA Nutrient Intelligence System** pairs accredited laboratory soil test results with authoritative institutional agronomic standards (Professor Jayashankar Telangana State Agricultural University — PJTSAU and ICAR-Indian Institute of Soil Science — IISS).

### Core Governance Guardrails:
1. **Soil-Test Mandatory for Prescriptions:** Chemical fertilizer recommendations are never generated without a verified, accredited soil test result within the last 24 months.
2. **CropVision Boundary:** Visual deficiency detections from computer vision models are classified as **unconfirmed symptomatic observations**. They can suggest targeted testing or mild organic/micronutrient foliar corrections, but *never* trigger large-scale soil fertilizer applications without soil verification.
3. **Hard Rejection of Dangerous Dosages:** Automated safety filters enforce hard upper bounds on nitrogen ($N$), phosphorus ($P_2O_5$), and potassium ($K_2O$) inputs based on PJTSAU recommendations. Any prompt or manual override exceeding safety thresholds is blocked.
4. **Mandatory Expert Agronomist Escalation:** Severe soil anomalies (e.g., $pH < 5.5$ or $> 8.5$, $EC > 2.0\text{ dS/m}$, multi-micronutrient deficiencies) automatically trigger an `ExpertConnect` review.

---

## 2. Soil-Test Interpretation Engine (PJTSAU / ICAR Standards)

ACREVIA categorizes available macronutrients, secondary nutrients, and micronutrients into standardized agronomic sufficiency classes:

```
Available Nutrient Range:   [ LOW ] --------------> [ MEDIUM ] --------------> [ HIGH / EXCESS ]
Fertilizer Dose Adjustment: [+25% of Rec]           [100% Recommended Dose]    [-25% to 0% Dose]
```

### 2.1 Standard Analytical Reference Table (Telangana Soils)

| Analyte | Analytical Method | Low (Deficient) | Medium (Sufficient) | High (Excess) | Unit |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Available Nitrogen ($N$)** | Alkaline Permanganate ($KMnO_4$) | $< 280.0$ | $280.0 - 560.0$ | $> 560.0$ | $\text{kg/ha}$ |
| **Available Phosphorus ($P_2O_5$)** | Olsen's ($0.5\text{M } NaHCO_3, pH 8.5$) | $< 22.0$ | $22.0 - 55.0$ | $> 55.0$ | $\text{kg/ha}$ |
| **Available Potassium ($K_2O$)** | Neutral Normal Ammonium Acetate | $< 140.0$ | $140.0 - 330.0$ | $> 330.0$ | $\text{kg/ha}$ |
| **Organic Carbon (SOC)** | Walkley-Black Wet Oxidation | $< 0.50$ | $0.50 - 0.75$ | $> 0.75$ | $\%$ |
| **Available Sulphur ($S$)** | $0.15\%\text{ } CaCl_2$ Extractable | $< 10.0$ | $10.0 - 20.0$ | $> 20.0$ | $\text{mg/kg (ppm)}$ |
| **Available Zinc ($Zn$)** | DTPA Extractable | $< 0.60$ | $0.60 - 1.50$ | $> 1.50$ | $\text{mg/kg (ppm)}$ |
| **Available Iron ($Fe$)** | DTPA Extractable | $< 4.50$ | $4.50 - 9.00$ | $> 9.00$ | $\text{mg/kg (ppm)}$ |
| **Available Boron ($B$)** | Hot Water Soluble | $< 0.50$ | $0.50 - 1.00$ | $> 1.00$ | $\text{mg/kg (ppm)}$ |

---

## 3. Crop-Specific Nutrient Packs & Split Schedules

All fertilizer dosage packages strictly adhere to PJTSAU Package of Practices:

### 3.1 Cotton (*Gossypium hirsutum*)
- **Standard Recommended Dose:** $120\text{ kg } N - 60\text{ kg } P_2O_5 - 60\text{ kg } K_2O\text{ per hectare}$ (Hybrid/Bt Cotton, irrigated).
- **Split Application Protocol:**
  - *Basal (At sowing):* $20\%\text{ } N + 100\%\text{ } P_2O_5 + 30\%\text{ } K_2O$
  - *Vegetative ($30\text{ DAS}$):* $30\%\text{ } N + 20\%\text{ } K_2O$
  - *Square Formation ($60\text{ DAS}$):* $30\%\text{ } N + 30\%\text{ } K_2O$
  - *Boll Development ($90\text{ DAS}$):* $20\%\text{ } N + 20\%\text{ } K_2O$
- **Micro/Secondary Nutrient Safeguards:**
  - In zinc-deficient soils: Soil application of $ZnSO_4 @ 25\text{ kg/ha}$ once every 3 seasons.
  - Cotton Leaf Reddening Prevention: Foliar spray of $1\%\text{ } MgSO_4 + 1\%\text{ Urea}$ at $60\text{ DAS}$ and $90\text{ DAS}$.
  - Boron Deficiency (hard unopened bolls): Foliar spray of Solubor ($0.15\%$) at flowering.

### 3.2 Rice (*Oryza sativa*)
- **Standard Recommended Dose:** $120\text{ kg } N - 60\text{ kg } P_2O_5 - 40\text{ kg } K_2O\text{ per hectare}$ (Medium duration varieties, Kharif).
- **Split Application Protocol:**
  - *Basal (Final puddling):* $33\%\text{ } N + 100\%\text{ } P_2O_5 + 50\%\text{ } K_2O$
  - *Active Tillering ($20-25\text{ DAT}$):* $34\%\text{ } N$
  - *Panicle Initiation ($40-45\text{ DAT}$):* $33\%\text{ } N + 50\%\text{ } K_2O$
- **Micro/Secondary Nutrient Safeguards:**
  - Zinc Khaira Disease Mitigation: In submerged soils with $Zn < 0.60\text{ ppm}$, apply $ZnSO_4 @ 50\text{ kg/ha}$ to soil or foliar spray $0.2\%\text{ } ZnSO_4$ with $1\%\text{ Urea}$ twice at weekly intervals.

### 3.3 Chilli (*Capsicum annuum*)
- **Standard Recommended Dose:** $150\text{ kg } N - 60\text{ kg } P_2O_5 - 120\text{ kg } K_2O\text{ per hectare}$ (Irrigated Commercial Hybrids).
- **Split Application / Fertigation Protocol:**
  - *Basal:* $20\%\text{ } N + 100\%\text{ } P_2O_5 + 20\%\text{ } K_2O$
  - *Vegetative ($30\text{ DAT}$):* $20\%\text{ } N + 20\%\text{ } K_2O$
  - *Flowering & Initial Fruit Set ($60\text{ DAT}$):* $30\%\text{ } N + 30\%\text{ } K_2O$
  - *Multi-Picking Phase ($90-120\text{ DAT}$):* $30\%\text{ } N + 30\%\text{ } K_2O$ split evenly across pickings.
- **Micro/Secondary Nutrient Safeguards:**
  - Blossom End Rot Mitigation: Calcium deficiency corrected via foliar Calcium Nitrate ($0.5\%$) during active fruit development.
  - Flower Drop Prevention: Foliar micronutrient cocktail ($Zn + B + Fe$) at peak flowering.

---

## 4. Prescription Safeguards & Dosage Upper Bounds

ACREVIA implements programmatic validation gates that reject any prescription violating institutional maximums:

```
[Prescription Request] 
         |
         v
+-----------------------------------------------------------+
|               Dose Upper-Bound Check                      |
| Cotton: Max N <= 180 kg/ha | P2O5 <= 90 | K2O <= 90       |
| Rice:   Max N <= 160 kg/ha | P2O5 <= 80 | K2O <= 60       |
| Chilli: Max N <= 220 kg/ha | P2O5 <= 90 | K2O <= 180      |
+-----------------------------------------------------------+
         |
         +---- [Exceeds Limit?] ----> [HTTP 422: UNACCEPTABLE_DOSAGE_OVERRIDE]
         |
         v
+-----------------------------------------------------------+
|              CropVision / Visual Symptom Gate             |
| Is Soil Test Available?                                   |
|   YES -> Generate Split Schedule with PJTSAU Citation     |
|   NO  -> Classify as UNCONFIRMED_OBSERVATION; recommend   |
|          targeted soil testing + organic/foliar booster   |
+-----------------------------------------------------------+
```

---

## 5. Agronomist Review & Escalation Workflow

When an anomalous soil sample or conflicting advisory request is detected, ACREVIA creates an `ExpertConnect` review ticket:

### Escalation Triggers:
1. **Soil Acidity Anomaly:** Soil $pH < 5.5$ (Requires specialized agricultural lime / dolomite calculation).
2. **Soil Alkalinity & Sodicity Anomaly:** Soil $pH > 8.5$ or $\text{SAR} > 15.0$ (Requires gypsum requirement testing).
3. **Severe Salinity:** Electrical Conductivity $EC > 2.0\text{ dS/m}$ (Risk of seedling mortality; leaching requirement evaluation).
4. **Extreme Single-Element Deficiency:** DTPA $Zn < 0.3\text{ ppm}$ or Hot Water $B < 0.2\text{ ppm}$.
5. **Crop Failure Reports:** Repeated visual distress logs following fertilizer application.

The agronomist can review the full laboratory analysis, field photographs from `CropPulse`, crop phenology, and approve, modify, or reject the proposed nutrient schedule.
