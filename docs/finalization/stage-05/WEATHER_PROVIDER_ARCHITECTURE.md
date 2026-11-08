# ACREVIA — WEATHER PROVIDER ARCHITECTURE & OPEN-METEO INTEGRATION
**Programme:** ACREVIA 14-Stage Finalization Programme  
**Target Stage:** Stage 05 — Farm Action Journal, Observations, Geolocation & Weather  
**Date:** 2026-11-08  
**Status:** VERIFIED & VALIDATED (`PASS`)

---

## 1. Agrometeorological Provider Selection

ACREVIA integrates **Open-Meteo** (`https://api.open-meteo.com/v1/forecast`) as its primary agrometeorological data provider. Open-Meteo was chosen for its open-access scientific reanalysis models, high temporal resolution (hourly), zero-authentication friction, and rapid latency (< 400 ms globally).

---

## 2. API Contract & Parameter Specification

Implemented in [`backend/app/integrations/weather_client.py`](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/integrations/weather_client.py) and [`backend/app/services/riskcast/weather_service.py`](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/services/riskcast/weather_service.py):

### 2.1 Request Schema
```http
GET https://api.open-meteo.com/v1/forecast
  ?latitude={lat}
  &longitude={lon}
  &current=temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m
  &hourly=temperature_2m,relative_humidity_2m,precipitation
  &forecast_days=3
  &timezone=Asia/Kolkata
```

### 2.2 Canonical Unit Normalization

| Variable | Raw Provider Key | Canonical ACREVIA Key | Unit | Normalization Rule |
|---|---|---|---|---|
| Temperature | `temperature_2m` | `temperature_celsius` | Celsius (°C) | Strict float, rounded to 1 decimal place. |
| Relative Humidity | `relative_humidity_2m` | `relative_humidity` | Percentage (%) | Bounded between $0.0\%$ and $100.0\%$. |
| Precipitation | `precipitation` | `precipitation_mm` | Millimeters (mm) | Bounded $\ge 0.0\text{ mm}$; sum of liquid rainfall. |
| Wind Speed | `wind_speed_10m` | `wind_speed_kmh` | km/h | 10-meter surface wind speed. |
| Leaf Wetness | Derived from hourly RH | `leaf_wetness_hours` | Hours (h) | Derived duration where foliar fungal spores germinate. |

---

## 3. Epistemic Separation: Observations vs. Forecasts vs. Reanalysis

In agronomic research, confusing a modeled forecast with an observed ground reality produces invalid disease spread simulations.

ACREVIA enforces strict tagging:
1. `is_forecast = False`: Data corresponding to elapsed or current hours. Represents atmospheric assimilation / reanalysis.
2. `is_forecast = True`: Data corresponding to future hours ($t > t_{\text{current}}$). Includes target timestamp `forecast_target_time`.
3. `source_provider`: Declares data provenance:
   - `"Open-Meteo Live API"`
   - `"PJTSAU Historical Agro-Climatic Normal (Fallback)"`
   - `"On-Field IoT AgroStation (Stage 07)"`

---

## 4. Agronomic Leaf Wetness Derivation

Fungal spore germination (e.g. *Magnaporthe oryzae* Rice Blast, *Cercospora* Leaf Spot) requires free moisture on the leaf surface or ambient relative humidity exceeding 88% for a prolonged window (typically 6–10 consecutive hours).

### 4.1 Derivation Algorithm
In [`backend/app/services/riskcast/weather_service.py`](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/services/riskcast/weather_service.py):
```python
# Evaluates past 24 hours of hourly agrometeorological readings
hourly = payload.get("hourly", {})
rh_series = hourly.get("relative_humidity_2m", [])[:24]
p_series = hourly.get("precipitation", [])[:24]

wet_hours = 0
for rh, p in zip(rh_series, p_series):
    # Leaf surface is deemed wet if rainfall occurred or ambient RH exceeds 88%
    if (rh and rh >= 88.0) or (p and p > 0.1):
        wet_hours += 1

leaf_wetness_hours = float(wet_hours)
```
This derived index directly feeds the Stage 05 agro-climatic disease risk rules.
