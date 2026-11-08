# ACREVIA — Climate Resilience Architecture (Pillar C)

**Project:** ACREVIA — Agricultural Intelligence Platform  
**Stage:** 13 — Climate-Resilient & Sustainable Agriculture  
**Focus:** Multi-Decadal Baselines, Agricultural Hazard Taxonomy, Crop Vulnerability Windows & Adaptation Scenarios  
**Target Region:** Telangana-First (Semi-arid agro-ecological sub-regions: North, Central, and Southern Telangana Zones)  
**Target Crops:** Cotton (*Gossypium hirsutum*), Rice (*Oryza sativa*), Chilli (*Capsicum annuum*)  

---

## 1. Executive Summary & Context

Telangana agriculture is increasingly exposed to compounding agro-climatic extremes: unseasonal torrential downpours during harvest, extended mid-monsoon dry spells (14–21 days) causing root zone moisture depletion, and intense pre-monsoon heatwaves ($T_{max} > 42^\circ\text{C}$). 

The **ACREVIA Climate Resilience Engine** connects long-term multi-decadal climatology (1991–2020 IMD and ERA5-Land baselines) with short-range numerical weather predictions and farm-specific crop phenology. It identifies critical vulnerability windows and models evidence-based adaptation scenarios to reduce crop loss risk.

---

## 2. Multi-Decadal Baseline Data Infrastructure

To objectively evaluate climate anomalies, ACREVIA establishes district-level and sub-district (Mandal) climatological baselines covering a 30-year standard normal period (1991–2020).

```
+-----------------------------------------------------------------------------------------+
|                              Climate Baseline Data Pipeline                             |
+-----------------------------------------------------------------------------------------+
| Sources: India Meteorological Department (IMD) 0.25° Gridded Rainfall & 1.0° Temperature|
| ECMWF ERA5-Land Reanalysis (9km Resolution) for Solar Radiation, Dewpoint & Wind Speed  |
|                                            |                                            |
|                                            v                                            |
|                  District Climatology Engine (Telangana 33 Districts)                   |
| - 30-Year Monthly Means (Tmax, Tmin, Precip, ET0, RH)                                   |
| - Climatological Percentiles (10th, 25th, 50th, 75th, 90th, 99th)                       |
| - Standardized Precipitation-Evapotranspiration Index (SPEI-1, SPEI-3) Base Parameters  |
+-----------------------------------------------------------------------------------------+
```

### 2.1 Baseline Dataset Schema

| Field Name | Type | Description / Standard |
| :--- | :--- | :--- |
| `district_id` | String | Standard Telangana Census/LGD Code (e.g., `TL_WARANGAL`). |
| `baseline_period` | String | Fixed reference window: `"1991-2020"`. |
| `month` | Integer | $1 - 12$ representing calendar months. |
| `normal_rainfall_mm` | Float | 30-year mean monthly cumulative precipitation ($mm$). |
| `normal_tmax_celsius` | Float | 30-year mean daily maximum temperature ($^\circ\text{C}$). |
| `normal_tmin_celsius` | Float | 30-year mean daily minimum temperature ($^\circ\text{C}$). |
| `extreme_heat_days_p90` | Float | Climatological expected count of days with $T_{max} > 90\text{th percentile}$. |
| `dry_spell_frequency` | Float | Historical mean number of dry spells ($\ge 14\text{ days}$) per season. |
| `heavy_rain_days_count`| Float | Mean number of days with precipitation $> 64.5\text{ mm/day}$. |

---

## 3. Agricultural Climate Hazard Taxonomy

ACREVIA categorizes weather anomalies into an actionable 5-tier agricultural hazard taxonomy:

```
                                +-----------------------------+
                                |  Agricultural Climate Hazard|
                                +-----------------------------+
                                               |
        +-------------------+------------------+------------------+-------------------+
        |                   |                  |                  |                   |
+---------------+   +---------------+  +---------------+  +---------------+   +---------------+
| Extreme Heat  |   | Extended Dry  |  | Heavy / Cloud |  | Waterlogging  |   | High Wind /   |
| & Night Warmth|   | Spells        |  | Burst Rain    |  | & Submergence |   | Squalls       |
+---------------+   +---------------+  +---------------+  +---------------+   +---------------+
```

### 3.1 Taxonomy Criteria & Agronomic Thresholds

1. **Extreme Heat Stress (`HEAT_STRESS`):**
   - *Severe Day Heat:* Daily maximum temperature $T_{max} \ge 40.0^\circ\text{C}$ (or $\ge 38.0^\circ\text{C}$ during reproductive stages).
   - *Nocturnal Heat:* Night minimum temperature $T_{min} \ge 26.0^\circ\text{C}$, elevating dark respiration and draining carbohydrate reserves.
2. **Extended Dry Spell (`DRY_SPELL`):**
   - $\ge 14$ consecutive days during Kharif/Rabi with daily rainfall $< 2.5\text{ mm}$ and root zone available soil moisture $< 40\%$.
3. **Heavy / Extreme Precipitation (`EXTREME_RAINFALL`):**
   - *Heavy:* $64.5 - 115.5\text{ mm}$ in 24 hours.
   - *Very Heavy:* $115.6 - 204.4\text{ mm}$ in 24 hours.
   - *Extremely Heavy:* $\ge 204.5\text{ mm}$ in 24 hours (flash flood trigger).
4. **Waterlogging & Submergence (`WATERLOGGING`):**
   - Free-standing surface ponding on upland soils (Vertisols/Alfisols) lasting $> 24\text{ hours}$, creating anoxic root-zone conditions.
5. **High Wind / Squalls (`HIGH_WIND`):**
   - Sustained winds $> 40\text{ km/h}$ or gusts $> 55\text{ km/h}$ associated with tropical depressions or convective storms, inducing mechanical lodging.

---

## 4. Crop-Stage Vulnerability Windows

The agro-climatic impact of any hazard depends heavily on crop phenology. ACREVIA maps dynamic susceptibility matrices across growth phases:

```
Growth Stages:      Vegetative       Reproductive (Flowering/Anthesis)    Maturity / Harvest
Cotton:         [Low Moisture Risk] --------> [CRITICAL: Boll Shedding] ------> [Boll Rot / Lint Spoilage]
Rice:           [Submergence Tolerant] ----> [CRITICAL: Pollen Sterility] ----> [Lodging / Grain Shatter]
Chilli:         [Moderate Tolerance] -------> [CRITICAL: Blossom Drop] -------> [Ripe Fruit Anthracnose]
```

### 4.1 Detailed Crop Vulnerability Matrix

| Crop | Phenological Stage | Vulnerable Hazard | Physiological Impact | Actionable RiskCast Severity |
| :--- | :--- | :--- | :--- | :--- |
| **Cotton** | Square & Boll Formation ($60-100\text{ DAS}$) | Extreme Heat ($>38^\circ\text{C}$) | Square abortion, poor pollen viability, excessive shedding of young bolls. | **CRITICAL** |
| **Cotton** | Peak Vegetative to Flowering | Waterlogging ($>48\text{ h}$) | Taproot suffocation, parawilt symptom onset, yellowing, leaf reddening. | **HIGH** |
| **Cotton** | Boll Bursting to Harvest ($120-160\text{ DAS}$) | Unseasonal Rain ($>30\text{ mm}$) | Discoloration of lint, fiber degradation, sprouting of seeds inside open bolls. | **HIGH** |
| **Rice** | Panicle Initiation to Anthesis | Daytime Heat ($>35^\circ\text{C}$) | Anther indehiscence, non-fertilization, spikelet sterility, chaffy grain formation. | **CRITICAL** |
| **Rice** | Vegetative Tillering | Submergence ($>5\text{ days}$) | Complete foliar decay in non-Sub1 varieties; severe stand thinning. | **HIGH** |
| **Rice** | Grain Filling to Maturity | High Winds & Cyclone Rain | Plant lodging, contact of panicles with mud/water, grain discoloration, sprouting. | **HIGH** |
| **Chilli** | Flowering & Fruit Set ($45-90\text{ DAT}$) | Sudden Wetting / High RH ($>85\%$) | Immediate blossom and pinhead drop; explosive outbreak of Anthracnose (*Colletotrichum*). | **CRITICAL** |
| **Chilli** | Mid-Season Vegetative / Reproductive | Extended Dry Spell ($>15\text{ days}$) | Stunted bushy growth, small fruit size, severe flower drop, thrips/mite infestation. | **HIGH** |
| **Chilli** | Red Ripe Stage / Solar Drying | Unseasonal Showers | Fruit rot, aflatoxin contamination during drying yard stage, loss of capsaicin quality. | **CRITICAL** |

---

## 5. Farm-Level Exposure Assessment Engine

When an agro-climatic hazard is forecast or observed, ACREVIA generates an individualized `ClimateExposureAssessment`:

1. **Spatial Overlay:** Matches plot polygon with gridded weather forecasts (NCMRWF/IMD) and digital elevation model (DEM slope and flow accumulation).
2. **Phenological Intersect:** Reads current plot crop and days after sowing/transplanting from `CropPulse` and `ACREVIA Twin`.
3. **Soil Texture Moderation:**
   - Deep Vertisols (Black Cotton Soils): High waterlogging vulnerability; high resilience to short dry spells.
   - Shallow Alfisols (Red Sandy Loams): Low waterlogging vulnerability; very high susceptibility to dry spells.
4. **Calculated Vulnerability Index:**
   $$\text{VulnerabilityScore} = \text{HazardMagnitude} \times \text{CropStageSensitivity} \times \text{SoilVulnerabilityFactor}$$
   Normalized to $0.0 - 1.0$.

---

## 6. Climate Adaptation Scenarios & Mitigation Recommendations

ACREVIA formulates proactive adaptation packages following validated PJTSAU and ICAR protocols:

| Hazard & Crop | Adaptation Alternative | Mechanism & Evidence Base | Projected Loss Reduction |
| :--- | :--- | :--- | :--- |
| **Heat Wave during Cotton Flowering** | Foliar spray of $1\%$ Potassium Nitrate ($KNO_3$) or $2\%$ DAP $+ 1\%\text{ Urea}$. | Maintains cellular osmotic balance, improves stomatal regulation, and suppresses abscisic acid accumulation. | $35\% - 50\%$ lower boll shedding. |
| **Severe Dry Spell in Kharif Cotton/Chilli** | In-situ soil moisture conservation: inter-row dust mulch or biomass residue mulching; emergency life-saving drip. | Breaks soil capillary pores, retarding evaporation by up to $40\%$. | Prevents permanent wilting; safeguards basal yield. |
| **Excess Rainfall & Waterlogging in Vertisols** | Broad Bed and Furrow (BBF) drainage, dead furrow clearance, foliar application of $0.5\%\text{ Zinc Sulphate} + 1\%\text{ Urea}$. | Evacuates gravitational water within $12\text{ hours}$; restores rhizosphere nitrogen assimilation. | $60\% - 75\%$ reduction in parawilt occurrence. |
| **Pollen Heat Stress in Rabi Rice** | Maintain $5-7\text{ cm}$ standing water depth in paddy field during morning anthesis ($9\text{ AM} - 11\text{ AM}$). | Microclimate evaporative cooling reduces canopy temperature by $1.5^\circ - 2.5^\circ\text{C}$. | $20\% - 30\%$ decrease in spikelet sterility. |
| **Pre-Harvest Cyclone Wind in Rice** | Controlled drainage 10 days before harvest; avoid excessive late nitrogen top-dressing. | Stiffens culms and lowers center of gravity, resisting lodging. | Mitigates up to $80\%$ mechanical lodging risk. |

---

## 7. Interfaces & Governance

- **RiskCast Synchronization:** Emits high-priority climate advisory webhooks when compound hazards are detected.
- **Scientifically Grounded Advisory Content:** All agronomic interventions cite PJTSAU Crop Production Guidelines or ICAR-CRIDA contingency plans.
- **Farmer Explainability:** Alerts are rendered in Telugu, English, and Hindi using plain vernacular terms (e.g., Telugu: *తేమ కొరత* for moisture stress, *నీరు నిలబడటం* for waterlogging).
