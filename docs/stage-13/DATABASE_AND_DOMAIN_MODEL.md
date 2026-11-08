# ACREVIA — Database and Domain Model Specification (Stage 13)

**Project:** ACREVIA — Agricultural Intelligence Platform  
**Stage:** 13 — Climate-Resilient & Sustainable Agriculture  
**Database:** Neon PostgreSQL 16 + pgvector (Singapore `sin1`)  

---

## 1. Domain Entity Relationship Architecture

Stage 13 introduces six relational model families integrating with existing `farms`, `plots`, `crops`, and `users` tables:

```
                      +-------------------+
                      |      farms        |
                      +-------------------+
                        |               |
       +----------------+               +----------------+
       |                                                 |
       v                                                 v
+------------------+                             +------------------+
|  water_sources   |                             |      plots       |
+------------------+                             +------------------+
       |                                           |         |     |
       |                                           |         |     +------------------+
       v                                           v         v                        v
+--------------------+                     +-------------+ +--------------------+ +-------------------+
| irrigation_events  |                     |soil_profiles| |soil_moisture_obs   | |farm_practice_recs |
+--------------------+                     +-------------+ +--------------------+ +-------------------+
                                                   |
                                                   v
                                           +---------------+
                                           | soil_samples  |
                                           +---------------+
                                                   |
                                                   v
                                           +---------------+
                                           |soil_test_res  |
                                           +---------------+
```

---

## 2. Table Specifications & Column Definitions

### 2.1 Pillar A: Soil Health Intelligence
- **`soil_profiles`**: Represents the historical soil pedon profile for a farm/plot.
  - `id`: UUID (Primary Key)
  - `plot_id`: UUID (Foreign Key $\to$ `plots.id`, Indexed)
  - `soil_order`: String (e.g., `VERTISOL`, `ALFISOL`, `INCEPTISOL`)
  - `soil_series_name`: String (e.g., `WARANGAL_CLAY`)
  - `drainage_class`: String (`WELL_DRAINED`, `MODERATELY_WELL_DRAINED`, `POORLY_DRAINED`)
  - `bulk_density_g_cm3`: Float
  - `effective_soil_depth_cm`: Float
  - `created_at`, `updated_at`: DateTime (UTC)

- **`soil_samples`**: Individual physical soil sampling events.
  - `id`: UUID (PK)
  - `plot_id`: UUID (FK $\to$ `plots.id`, Indexed)
  - `sampled_by_user_id`: UUID (FK $\to$ `users.id`)
  - `sample_code`: String (Unique)
  - `sampling_date`: DateTime
  - `sampling_depth_min_cm`: Float (e.g., `0.0`)
  - `sampling_depth_max_cm`: Float (e.g., `15.0`)
  - `gps_latitude`: Float
  - `gps_longitude`: Float
  - `composite_cores_count`: Integer
  - `status`: String (`COLLECTED`, `DISPATCHED_TO_LAB`, `ANALYZED`, `DISPUTED`)

- **`soil_test_results`**: Accredited analytical laboratory test certificate.
  - `id`: UUID (PK)
  - `soil_sample_id`: UUID (FK $\to$ `soil_samples.id`, Indexed)
  - `laboratory_name`: String
  - `accreditation_number`: String
  - `ph`: Float
  - `electrical_conductivity_ec`: Float ($dS/m$)
  - `organic_carbon_percent`: Float ($\%$)
  - `available_nitrogen_kg_ha`: Float
  - `available_phosphorus_kg_ha`: Float ($P_2O_5$)
  - `available_potassium_kg_ha`: Float ($K_2O$)
  - `available_sulphur_ppm`: Float
  - `available_zinc_ppm`: Float
  - `available_iron_ppm`: Float
  - `available_boron_ppm`: Float
  - `provenance`: JSONB
  - `verified_at`: DateTime

### 2.2 Pillar B: Precision Water Management
- **`water_sources`**: Farm water asset inventory.
  - `id`: UUID (PK)
  - `farm_id`: UUID (FK $\to$ `farms.id`, Indexed)
  - `source_type`: String (`BOREWELL`, `OPEN_WELL`, `CANAL_OUTLET`, `FARM_POND`, `TANKER`)
  - `source_name`: String
  - `depth_meters`: Float
  - `static_water_level_m`: Float
  - `discharge_capacity_lps`: Float
  - `salinity_ec_dsm`: Float
  - `ph`: Float
  - `sar`: Float
  - `seasonal_availability`: JSONB
  - `created_at`, `updated_at`: DateTime

- **`irrigation_events`**: Verifiable irrigation journaling.
  - `id`: UUID (PK)
  - `plot_id`: UUID (FK $\to$ `plots.id`, Indexed)
  - `water_source_id`: UUID (FK $\to$ `water_sources.id`)
  - `event_date`: DateTime
  - `irrigation_method`: String (`DRIP`, `SPRINKLER`, `FLOOD`, `ALTERNATE_FURROW`)
  - `duration_hours`: Float
  - `flow_meter_start_m3`: Float
  - `flow_meter_end_m3`: Float
  - `calculated_volume_m3`: Float
  - `equivalent_depth_mm`: Float
  - `soil_moisture_before`: Float
  - `soil_moisture_after`: Float

- **`soil_moisture_observations`**: In-situ probe telemetry.
  - `id`: UUID (PK)
  - `plot_id`: UUID (FK $\to$ `plots.id`, Indexed)
  - `sensor_id`: String
  - `depth_cm`: Integer ($15$, $30$, $60$)
  - `volumetric_water_content`: Float ($m^3/m^3$ or $\%$)
  - `matric_potential_kpa`: Float
  - `moisture_status`: String (`SATURATED`, `FIELD_CAPACITY`, `DEPLETED`, `WILTING`)
  - `observed_at`: DateTime

- **`water_balance_snapshots`**: Daily root-zone balance logs.
  - `id`: UUID (PK)
  - `plot_id`: UUID (FK $\to$ `plots.id`, Indexed)
  - `snapshot_date`: DateTime
  - `effective_precipitation_mm`: Float
  - `irrigation_applied_mm`: Float
  - `crop_evapotranspiration_mm`: Float
  - `deep_percolation_mm`: Float
  - `runoff_mm`: Float
  - `storage_change_mm`: Float
  - `accounting_status`: String (`COMPLETED_WITH_VALIDATED_INPUTS`, `PARTIALLY_ESTIMATED`, `INSUFFICIENT_DATA`)

### 2.3 Pillar C: Climate Resilience Intelligence
- **`climate_baselines`**: 30-year district normals.
  - `id`: UUID (PK)
  - `district_code`: String (Indexed)
  - `month`: Integer ($1-12$)
  - `normal_rainfall_mm`: Float
  - `normal_tmax_celsius`: Float
  - `normal_tmin_celsius`: Float
  - `extreme_heat_days_p90`: Float
  - `dry_spell_frequency`: Float

- **`climate_exposure_assessments`**: Individualized hazard vulnerability evaluations.
  - `id`: UUID (PK)
  - `plot_id`: UUID (FK $\to$ `plots.id`, Indexed)
  - `hazard_type`: String (`HEAT_STRESS`, `DRY_SPELL`, `EXTREME_RAINFALL`, `WATERLOGGING`, `HIGH_WIND`)
  - `severity_level`: String (`LOW`, `MODERATE`, `HIGH`, `CRITICAL`)
  - `crop_stage`: String
  - `vulnerability_score`: Float ($0.0 - 1.0$)
  - `recommended_adaptation`: Text
  - `assessed_at`: DateTime

### 2.4 Pillar D: Nutrient Intelligence & Governance
- **`nutrient_assessments`**: Soil-test driven nutrient evaluation.
  - `id`: UUID (PK)
  - `soil_test_result_id`: UUID (FK $\to$ `soil_test_results.id`, Indexed)
  - `crop_id`: UUID (FK $\to$ `crops.id`)
  - `nitrogen_status`: String (`DEFICIENT`, `SUFFICIENT`, `EXCESS`)
  - `phosphorus_status`: String
  - `potassium_status`: String
  - `zinc_status`: String
  - `boron_status`: String
  - `recommended_n_kg_ha`: Float
  - `recommended_p2o5_kg_ha`: Float
  - `recommended_k2o_kg_ha`: Float
  - `split_application_schedule`: JSONB
  - `safeguard_checks_passed`: Boolean
  - `institutional_citation`: String

- **`nutrient_expert_reviews`**: Agronomist review tickets.
  - `id`: UUID (PK)
  - `nutrient_assessment_id`: UUID (FK $\to$ `nutrient_assessments.id`)
  - `expert_user_id`: UUID (FK $\to$ `users.id`)
  - `review_status`: String (`PENDING`, `APPROVED`, `MODIFIED`, `REJECTED`)
  - `agronomist_notes`: Text
  - `revised_prescription`: JSONB
  - `reviewed_at`: DateTime

### 2.5 Pillar E: Sustainable Agriculture Intelligence
- **`agricultural_practice_definitions`**: Canonical library of sustainable practices.
  - `id`: UUID (PK)
  - `code`: String (Unique)
  - `category`: String (`SOIL_COVER`, `RESIDUE_MGMT`, `CROP_DIVERSITY`, `IPM`, `SOIL_WATER`)
  - `title_en`: String
  - `title_te`: String
  - `title_hi`: String
  - `description_en`: Text
  - `specification`: JSONB

- **`farm_practice_records`**: Verified implementation of practices on plots.
  - `id`: UUID (PK)
  - `plot_id`: UUID (FK $\to$ `plots.id`, Indexed)
  - `practice_code`: String
  - `implementation_date`: DateTime
  - `area_covered_acres`: Float
  - `verification_method`: String (`FARMER_LOG`, `EXPERT_VERIFIED`, `GEO_TAGGED_IMAGE`)
  - `status`: String (`ACTIVE`, `COMPLETED`, `DISCONTINUED`)

- **`soil_carbon_measurements`**: Empirical SOC time-series.
  - `id`: UUID (PK)
  - `plot_id`: UUID (FK $\to$ `plots.id`, Indexed)
  - `sample_date`: DateTime
  - `depth_cm`: Float
  - `soc_percent`: Float
  - `bulk_density`: Float
  - `method`: String (`WALKLEY_BLACK`, `DRY_COMBUSTION`)
  - `lab_accreditation`: String

- **`environmental_accounting_estimates`**: Research-grade GHG emissions.
  - `id`: UUID (PK)
  - `plot_id`: UUID (FK $\to$ `plots.id`, Indexed)
  - `season`: String
  - `year`: Integer
  - `fertilizer_n2o_kg_co2e`: Float
  - `paddy_ch4_kg_co2e`: Float
  - `fuel_combustion_kg_co2e`: Float
  - `total_emissions_kg_co2e`: Float
  - `emission_intensity_kg_co2e_per_kg`: Float
  - `is_certified`: Boolean (Always `False`)
  - `scientific_disclaimer`: Text

### 2.6 Pillar F: Agricultural Resilience Engine
- **`resilience_assessments`**: Multi-dimensional farm resilience score.
  - `id`: UUID (PK)
  - `plot_id`: UUID (FK $\to$ `plots.id`, Indexed)
  - `overall_resilience_score`: Float ($0.0 - 100.0$)
  - `soil_score`: Float
  - `water_score`: Float
  - `climate_score`: Float
  - `nutrient_score`: Float
  - `practice_score`: Float
  - `evidence_quality_score`: Float ($0.0 - 1.0$)
  - `confidence_category`: String (`HIGH_CONFIDENCE_EMPIRICAL`, `MODERATE_CONFIDENCE_HYBRID`, `LOW_CONFIDENCE_INSUFFICIENT_DATA`)
  - `top_vulnerabilities`: JSONB
  - `adaptation_recommendations`: JSONB
  - `evaluated_at`: DateTime
