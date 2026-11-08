# ACREVIA — Weather Provider Review & Integration Architecture
## Agrometeorological Data Ingestion, Freshness & Resilience

---

## 1. Provider Evaluation Matrix

To provide reliable climate and risk intelligence for smallholder farmers across all 33 districts of Telangana, ACREVIA evaluated multiple weather data providers.

| Provider | Geographical Resolution | Hourly Agrometeorological Variables | Free Tier / Licensing | Latency & Reliability | Evaluation & Role in ACREVIA |
|:---|:---|:---|:---|:---|:---|
| **Open-Meteo** | ~1 to 5 km (Seamless multi-model: ECMWF, DWD, GFS) | Temperature, RH, Precipitation, Wind, Dew Point, Soil Moisture | Free non-commercial / Open data; Commercial API tier available | < 150 ms response time; 99.9% uptime | **Primary Live Provider**. Excellent documentation, no strict rate limits for development, hourly agrometeorological outputs. |
| **India Meteorological Department (IMD) / Mausam API** | Block / District level (5-10 km) | District forecasts, seasonal advisories, rainfall | Government open data, rate-limited, irregular JSON schemas | Variable latency (300ms - 2s), occasional downtime | **Secondary / Ground Truth Cross-Check**. Used for official district agro-advisories and monsoon forecasts. |
| **NASA POWER / ERA5 Reanalysis** | 0.5° x 0.5° (~50 km) | Solar radiation, historical hourly reanalysis, agroclimatology | Open access | High latency (batch query preferred), 2-3 day lag for reanalysis | **Historical Baseline / Offline Research**. Excellent for historical epidemiological studies, not for 24h real-time alerts. |
| **ACREVIA Simulated Agro-Weather Fallback** | District-calibrated synthetic generator | Complete agrometeorological hourly & 7-day forecast packet | Built-in zero-dependency fallback | Instant (< 5 ms), 100% deterministic | **Mandatory Offline & Test Adapter**. Ensures zero disruption during external API outages or isolated test environments. |

---

## 2. Selected Ingestion Pipeline Architecture

```
                                  +------------------------------+
                                  | Open-Meteo REST API Client   |
                                  +--------------+---------------+
                                                 |
                                  (HTTP 200)     | (Timeout / HTTP 5xx)
                                                 v
                               +-----------------+-----------------+
                               | ACREVIA Ingestion Normalizer      |
                               +-----------------+-----------------+
                                                 | (If API unreachable)
                                                 v
                               +-----------------+-----------------+
                               | Telangana District Climatology   |
                               | Fallback Engine (Warangal, etc.)  |
                               +-----------------+-----------------+
                                                 |
                                                 v
+-----------------------------------------------------------------------------------+
|                           NORMALIZED WEATHER DATA ENTITY                          |
|  - observation_time vs. forecast_horizon_time                                      |
|  - temperature_celsius, relative_humidity, precipitation_mm, wind_speed_kmh        |
|  - estimated_leaf_wetness_hours (calculated from RH >= 90% and rain duration)     |
|  - source_provider ("Open-Meteo", "IMD-Sync", "ACREVIA-Climatology-Fallback")     |
|  - fetched_at_utc, is_stale (< 3 hours old = fresh; > 6 hours old = stale)        |
+-----------------------------------------------------------------------------------+
```

---

## 3. Freshness & Staleness Governance

1. **Freshness Windows:**
   - **Fresh:** Data fetched within the last 3 hours (`freshness_status = "FRESH"`).
   - **Aging:** Data between 3 and 6 hours old (`freshness_status = "AGING"`). Still usable for rule evaluation with a low-confidence flag.
   - **Stale:** Data older than 6 hours (`freshness_status = "STALE"`). The system triggers an immediate re-fetch. If the provider is unreachable, the system generates an `INSUFFICIENT_DATA` risk assessment rather than issuing false alerts based on obsolete weather.
2. **Rate-Limiting & Caching:**
   - In-memory or database caching keyed by `(district, round(lat, 2), round(lon, 2), hour)`.
   - Caching interval: 60 minutes for current observations; 3 hours for 7-day forecasts.

---

## 4. Calculated Agrometeorological Parameters

Many critical agricultural disease triggers depend on parameters not directly output as single numbers by standard commercial weather endpoints. ACREVIA derives these using validated biophysical formulas:

1. **Leaf Wetness Hours ($LWH$):**
   $$LWH \approx \sum_{t \in 24h} \mathbb{I}(RH_t \ge 90\% \lor Precip_t > 0.1\text{ mm})$$
   Spore germination for *Pyricularia oryzae* (Rice Blast) and *Colletotrichum capsici* (Chilli Anthracnose) requires continuous leaf surface moisture for $\ge 8\text{ to }12$ hours.
2. **Vapor Pressure Deficit ($VPD$):**
   Derived from saturated vapor pressure ($e_s$) and actual vapor pressure ($e_a$). Low VPD indicates high humidity and sluggish crop transpiration, increasing guttation droplets where bacteria enter hydathodes.
3. **Consecutive Wet Days:**
   Rolling count of consecutive days with precipitation $\ge 2.5\text{ mm}$ or mean $RH \ge 80\%$.
