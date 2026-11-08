# ACREVIA — RiskCast Architecture Specification
## Climate & Agrometeorological Risk Intelligence Engine

---

## 1. System Vision & Objective

RiskCast is ACREVIA's agrometeorological risk intelligence sub-system. It transforms raw weather observations and multi-day meteorological forecasts into actionable, crop-specific agro-climatic risk indicators for smallholder farmers in Telangana.

Rather than providing generic weather forecasts (e.g., "30°C and 70% humidity"), RiskCast interprets atmospheric dynamics through the lens of plant pathology, entomology, and phenological vulnerability.

```
+-----------------------------------------------------------------------------------+
|                              AGROMETEOROLOGICAL DATA                              |
|   +----------------------------------+     +----------------------------------+   |
|   |       Weather Observations       |     |        Weather Forecasts         |   |
|   |  - Historical & Ground Stations  |     |  - 1 to 7 Day Horizon            |   |
|   |  - Hourly Temp, Humidity, Precip |     |  - Hourly & Daily Aggregations   |   |
|   +-----------------+----------------+     +----------------+-----------------+   |
+---------------------|---------------------------------------|---------------------+
                      |                                       |
                      +-------------------+-------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
|                           RISKCAST RULE & CONTEXT ENGINE                          |
|   +---------------------------------------------------------------------------+   |
|   | Plot & Crop Context: Crop (Cotton/Rice/Chilli), Growth Stage, Soil Type   |   |
|   +---------------------------------------------------------------------------+   |
|   | Evidence-Backed Agronomic Rules (University & CIBRC Literature)            |   |
|   |   - Rice Blast Risk Window: Temp 20-28°C, RH >= 90%, Wetness >= 10h       |   |
|   |   - Cotton Bollworm Risk: Vegetative-Boll, Temp 26-34°C, Intermittent Rain|   |
|   |   - Chilli Powdery Mildew: Moderate Temp 22-30°C, RH 70-85%               |   |
|   +---------------------------------------------------------------------------+   |
+-----------------------------------------+-----------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
|                             RISKCAST OUTPUT & DELIVERY                            |
|   +---------------------------------------------------------------------------+   |
|   | Risk Level: LOW | MODERATE | HIGH | INSUFFICIENT_DATA                     |   |
|   | Specific Pathogen / Pest Warnings & Phenological Susceptibility           |   |
|   | Actionable Preventive Scouting & Cultural Monitoring Advice               |   |
|   | Idempotent Risk Alert Drawer & Notification Push                          |   |
|   | Explicit Disclaimer: Favorable Conditions != Confirmed Disease Infection  |   |
|   +---------------------------------------------------------------------------+   |
+-----------------------------------------------------------------------------------+
```

---

## 2. Fundamental Distinctions & Domain Integrity

### 2.1 Weather Observations vs. Weather Forecasts
1. **Observation Data:**
   - **Data Origin:** Ground automated weather stations (AWS), gridded reanalysis, and satellite observations.
   - **Semantics:** Confirmed historical and near-real-time atmospheric conditions.
   - **Storage:** Persisted with `is_forecast = false` and `observation_time`.
2. **Forecast Data:**
   - **Data Origin:** High-resolution numerical weather prediction models (e.g., ECMWF, GFS, Open-Meteo downscaled models).
   - **Semantics:** Future projections with increasing uncertainty over 24h, 48h, 72h, and 7-day horizons.
   - **Storage:** Persisted with `is_forecast = true`, `forecast_issued_time`, and `target_time`.

### 2.2 Environmental Predisposition vs. Biological Infection
- **The Pitfall:** Inexperienced agricultural software often alerts farmers that their crop *has* Rice Blast or Powdery Mildew solely because the weather is warm and humid. This causes panic, leads to unnecessary chemical pesticide spraying, and destroys farmer trust.
- **The Rule:** RiskCast measures *climatic predisposition* (abiotic favorability for biotic stress).
- **Mandatory Safeguard:** All RiskCast alerts and API responses must explicitly state:
  > *"Risk indicators reflect micro-climatic favorability for disease emergence or pest proliferation. This is NOT a confirmed diagnosis. Inspect your field visually and record CropPulse observations before considering interventions."*

---

## 3. Data Schema & Core Agrometeorological Variables

| Parameter | Unit | Detection Method | Agronomic Significance |
|:---|:---|:---|:---|
| `temperature_celsius` | °C | Hourly 2m air temp | Pathogen germination thresholds & insect metabolic rates |
| `relative_humidity_percent` | % | Hourly 2m RH | Fungal spore germination (>85-90% triggers fungal risks) |
| `precipitation_mm` | mm | Hourly / daily accumulated | Soil saturation, splash dispersal of bacterial spores |
| `wind_speed_kmh` | km/h | 10m wind speed | Sucking pest migration (Aphids, Whiteflies) and droplet drift |
| `leaf_wetness_hours` | hours | Derived (RH > 90% or rain) | Critical prerequisite for foliar fungal infection (e.g., *Pyricularia oryzae*) |
| `consecutive_wet_days` | count | Rolling 7-day window | Disease incubation trigger |

---

## 4. Evaluation Workflow & Alert Deduplication

1. **Triggering Evaluation:**
   - On-demand via `POST /api/v1/riskcast/evaluate/{plot_id}`.
   - Batch evaluation during daily scheduled processing.
2. **Matching Rules:**
   - Identifies active crop and current phenological stage on the plot (e.g., Cotton at Squaring stage).
   - Evaluates ambient conditions against active `RiskRule` criteria.
3. **Calculating Risk Index:**
   - Severity is computed based on matched thresholds:
     - `HIGH`: Meets all temperature, humidity, and duration criteria for high-threat pathogens/pests.
     - `MODERATE`: Partial threshold matches or borderline humidity levels.
     - `LOW`: Environmental conditions unfavorable for monitored pests/pathogens.
     - `INSUFFICIENT_DATA`: Missing weather data or plot context.
4. **Idempotent Alerting:**
   - Uses a deduplication key: `hash(farm_id + plot_id + target_threat + date + severity)`.
   - Prevents duplicate alerts from spamming the farmer for identical ongoing weather events.
   - Farmer can acknowledge or dismiss alerts with full audit logging.
