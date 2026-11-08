# ACREVIA — Performance and Cost Report (Stage 13)

**Project:** ACREVIA — Agricultural Intelligence Platform  
**Stage:** 13 — Climate-Resilient & Sustainable Agriculture  
**Infrastructure:** Neon PostgreSQL 16 Serverless (Singapore `sin1`) + Vercel Global Edge & Functions  

---

## 1. Latency & Throughput Targets

All Stage 13 endpoints are engineered to meet strict low-latency budgets to guarantee fluid mobile PWA performance over rural 4G cellular connections in Telangana.

| Operation / Endpoint | Target $P_{50}$ | Target $P_{95}$ | Max Acceptable | Optimization Strategy |
| :--- | :--- | :--- | :--- | :--- |
| `GET /api/v1/soil/plot/{id}/history` | $22\text{ ms}$ | $38\text{ ms}$ | $100\text{ ms}$ | Index on `(plot_id, sampling_date DESC)` |
| `POST /api/v1/water/irrigation-events` | $28\text{ ms}$ | $45\text{ ms}$ | $120\text{ ms}$ | Single-transaction insert with pre-computed depth |
| `GET /api/v1/water/plot/{id}/balance` | $35\text{ ms}$ | $60\text{ ms}$ | $150\text{ ms}$ | Aggregation over indexed daily snapshots |
| `GET /api/v1/climate/baselines/{code}` | $10\text{ ms}$ | $18\text{ ms}$ | $50\text{ ms}$ | In-memory LRU cache of 30-year monthly normals |
| `POST /api/v1/climate/assess-exposure` | $32\text{ ms}$ | $52\text{ ms}$ | $150\text{ ms}$ | Rule-engine matrix evaluation without heavy DB joins |
| `POST /api/v1/nutrient/prescribe` | $40\text{ ms}$ | $70\text{ ms}$ | $200\text{ ms}$ | In-memory agronomic rule engine with DB lookup |
| `POST /api/v1/resilience/assess` | $65\text{ ms}$ | $110\text{ ms}$ | $300\text{ ms}$ | Parallel gathering of 5 dimensional scores |

---

## 2. Neon PostgreSQL Indexing Strategy

To eliminate full table scans across high-volume sensor telemetry and event logs:

```sql
-- Soil Indexes
CREATE INDEX idx_soil_samples_plot_date ON soil_samples (plot_id, sampling_date DESC);
CREATE INDEX idx_soil_test_results_sample ON soil_test_results (soil_sample_id);

-- Water Indexes
CREATE INDEX idx_water_sources_farm ON water_sources (farm_id);
CREATE INDEX idx_irrigation_events_plot_date ON irrigation_events (plot_id, event_date DESC);
CREATE INDEX idx_soil_moisture_plot_depth_time ON soil_moisture_observations (plot_id, depth_cm, observed_at DESC);
CREATE INDEX idx_water_balance_plot_date ON water_balance_snapshots (plot_id, snapshot_date DESC);

-- Climate & Resilience Indexes
CREATE INDEX idx_climate_baselines_district ON climate_baselines (district_code, month);
CREATE INDEX idx_climate_exposure_plot ON climate_exposure_assessments (plot_id, assessed_at DESC);
CREATE INDEX idx_resilience_assessments_plot ON resilience_assessments (plot_id, evaluated_at DESC);

-- Sustainable Practices Indexes
CREATE INDEX idx_farm_practices_plot ON farm_practice_records (plot_id, implementation_date DESC);
CREATE INDEX idx_soil_carbon_plot ON soil_carbon_measurements (plot_id, sample_date DESC);
```

---

## 3. Infrastructure Cost Analysis & Neon Serverless Budget

Stage 13 introduces minimal cloud hosting overhead by leveraging serverless connection pooling:

- **Neon Compute Units (CU):** Baseline $0.25\text{ CU}$, autoscaling to $2\text{ CU}$ during peak morning advisory hours ($6\text{ AM} - 9\text{ AM IST}$).
- **Neon Storage:** Projected $1.2\text{ GB}$ incremental storage for 10,000 plots over 2 seasons.
- **Vercel Serverless Functions:** Lightweight Python runtime ($<250\text{ MB}$ memory footprint), sub-second execution duration.
- **Estimated Cost per 1,000 Active Farmers:** $<\$0.85\text{ USD / month}$.
