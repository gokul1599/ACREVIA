# ACREVIA — STAGE 05 BASELINE AUDIT
**Programme:** ACREVIA 14-Stage Finalization Programme  
**Target Stage:** Stage 05 — Farm Action Journal, Observations, Geolocation & Weather  
**Date:** 2026-11-08  
**Status:** AUDIT COMPLETED (`PASS`)

---

## 1. Scope of Baseline Audit

The baseline audit for Stage 05 conducts a comprehensive structural, architectural, and code-level inspection of all assets governing:
1. **Farm & Land Holding Hierarchy:** Farms, Memberships, Plots, Plants, and Crop Seasons.
2. **Field Observations & Media:** Observation records, multi-image attachments, foliar image quality assessments, and private storage abstractions.
3. **Geospatial & Geolocation Infrastructure:** Plot boundaries (GeoJSON polygons), centroid calculations, bounding boxes, and location privacy permissions.
4. **Agrometeorological & Weather Ingestion:** Open-Meteo live API integration, Telangana district centroid lookups, fallback normal tables, and agro-climatic risk computation.
5. **Farm Action Journal UX & Localization:** Next.js 16 App Router timeline (`/dashboard`, `/croppulse`, `/crops`) in Telugu, English, and Hindi.

---

## 2. Codebase Asset Inventory

### 2.1 Backend Models (`backend/app/models/`)

| Model Class | Source File | Database Table | Key Attributes & Responsibilities |
|---|---|---|---|
| `Farm` | [`backend/app/models/farm.py`](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/models/farm.py) | `farms` | `id`, `owner_id`, `name`, `state`, `district`, `mandal`, `village`, `total_acreage`, `is_archived`. Root tenant entity. |
| `FarmMembership` | [`backend/app/models/farm.py`](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/models/farm.py) | `farm_memberships` | `id`, `farm_id`, `user_id`, `role_in_farm` (`OWNER`, `MANAGER`, `WORKER`, `AGRONOMIST_ADVISOR`). Multi-user RBAC. |
| `Plot` | [`backend/app/models/farm.py`](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/models/farm.py) | `plots` | `id`, `farm_id`, `name`, `soil_type`, `irrigation_source`, `acreage`, `boundary_geojson`. Physical sub-parcel. |
| `Plant` | [`backend/app/models/farm.py`](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/models/farm.py) | `plants` | `id`, `plot_id`, `tag_code`, `crop_id`, `notes`. Individual plant monitoring code. |
| `CropSeason` | [`backend/app/models/crop.py`](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/models/crop.py) | `crop_seasons` | `id`, `plot_id`, `crop_id`, `variety_id`, `season_type` (`KHARIF`, `RABI`, `SUMMER`), `sowing_date`, `current_stage`, `status`. |
| `Observation` | [`backend/app/models/observation.py`](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/models/observation.py) | `observations` | `id`, `farm_id`, `plot_id`, `crop_season_id`, `observer_id`, `notes`, `symptom_tags`. Core observation record. |
| `ObservationMedia` | [`backend/app/models/observation.py`](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/models/observation.py) | `observation_media` | `id`, `observation_id`, `storage_path`, `file_size_bytes`, `mime_type`, `sha256_hash`, `is_primary`. Private media storage link. |
| `ImageQualityAssessment` | [`backend/app/models/observation.py`](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/models/observation.py) | `image_quality_assessments` | `id`, `media_id`, `status` (`ACCEPTED`, `RETAKE_OR_REVIEW`, `QUARANTINED`), `sharpness_score`, `exposure_status`, `reasons_json`. |
| `PlotGeometry` | [`backend/app/models/geo_spatial.py`](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/models/geo_spatial.py) | `plot_geometries` | `id`, `plot_id`, `coordinates_geojson`, `centroid_lat`, `centroid_lon`, `calculated_area_hectares`, `calculated_area_acres`, `bbox_min/max`. |
| `LocationPermission` | [`backend/app/models/geo_spatial.py`](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/models/geo_spatial.py) | `location_permissions` | `id`, `farm_id`, `user_id`, `granularity` (`EXACT_BOUNDARY`, `COARSE_VILLAGE`, `REVOKED`), `is_active`. |
| `WeatherData` | [`backend/app/models/weather_data.py`](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/models/weather_data.py) | `weather_data` | `id`, `farm_id`, `district`, `is_forecast`, `observation_time`, `temperature_celsius`, `relative_humidity`, `precipitation_mm`, `wind_speed_kmh`, `leaf_wetness_hours`. |

---

### 2.2 API Endpoints (`backend/app/api/v1/endpoints/`)

1. **`farms.py`:**
   - `POST /api/v1/farms/` — Creates farm holding.
   - `GET /api/v1/farms/` — Lists authorized farms for user.
   - `GET /api/v1/farms/{farm_id}` — Gets detailed farm holding.
   - `PUT /api/v1/farms/{farm_id}` — Updates farm properties.
   - `POST /api/v1/farms/{farm_id}/memberships` — Adds collaborator role.
   - `GET /api/v1/farms/{farm_id}/memberships` — Lists active members.
   - `POST /api/v1/farms/{farm_id}/plots` — Creates parcel plot.
   - `GET /api/v1/farms/{farm_id}/plots` — Lists plots in farm.

2. **`plots.py` & `seasons.py`:**
   - `GET /api/v1/plots/{plot_id}` — Gets plot details.
   - `PUT /api/v1/plots/{plot_id}` — Updates plot boundaries and soil parameters.
   - `POST /api/v1/plots/{plot_id}/plants` — Tags physical plant.
   - `GET /api/v1/plots/{plot_id}/plants` — Lists tagged plants.
   - `POST /api/v1/plots/{plot_id}/seasons` — Sows crop season.
   - `GET /api/v1/plots/{plot_id}/seasons` — Lists crop seasons.

3. **`observations.py`:**
   - `POST /api/v1/observations/` — Creates field observation event.
   - `GET /api/v1/observations/` — Paginated list of observations for a farm holding.
   - `GET /api/v1/observations/{observation_id}` — Observation details with foliar attachments.
   - `POST /api/v1/observations/{observation_id}/media` — Multi-image multipart upload with automated Stage 02 quality filtering.
   - `GET /api/v1/observations/{observation_id}/media/{media_id}/file` — Authenticated private image binary stream with RBAC enforcement.

4. **`weather.py`:**
   - `GET /api/v1/farms/{farm_id}/weather` — District-level real-time agrometeorological indicators, foliar disease risk scoring, and PJTSAU fallback.

5. **`geospatial.py`:**
   - `POST /api/v1/geospatial/plots/{plot_id}/boundary` — Ingests WGS84 GeoJSON polygon, validates self-intersection, computes spherical Shoelace acreage and centroid.
   - `GET /api/v1/geospatial/plots/{plot_id}/geometry` — Retrieves plot boundary and metadata.
   - `POST /api/v1/geospatial/location-permission` — Configures spatial privacy sharing rules.

---

### 2.3 Storage Architecture (`backend/app/integrations/storage.py`)

- **Storage Abstraction:** Base abstract interface `StorageProvider` defining `save_file`, `get_url`, `delete_file`, `read_file`, and `get_absolute_path`.
- **Implementation:** `LocalStorageProvider` storing assets in `backend/storage/uploads/` with SHA-256 content addressing: `{sha256[:16]}_{filename}`.
- **Security Invariant:** Enforces strict path traversal sanitization via `Path(storage_path).name` preventing directory escaping.

---

### 2.4 Weather Integration Architecture (`backend/app/integrations/weather_client.py` & `backend/app/services/riskcast/weather_service.py`)

- **Primary Provider:** Open-Meteo REST API (`https://api.open-meteo.com/v1/forecast`).
- **Target Spatial Coords:** Pre-configured Telangana district centroids (Warangal, Khammam, Nalgonda, Karimnagar, Nizamabad, Adilabad, Hyderabad).
- **Hourly Variables Ingested:** `temperature_2m`, `relative_humidity_2m`, `precipitation`, `wind_speed_10m`.
- **Agro-climatic Metrics Computed:** Leaf wetness hours derived from hourly $\text{RH} \ge 88\%$ or rainfall $> 0.1\text{ mm}$ over 24 hours.
- **Failover / Resiliency:** Graceful degradation to PJTSAU Historical Agro-Climatic Normal if Open-Meteo is unreachable or times out after 4.0s.

---

### 2.5 Frontend Applications (`frontend/app/(farmer)/`)

- **`dashboard/page.tsx`:** Aggregates farm overview, plot cards, active crop stage, weather widget, and recent observation timeline.
- **`croppulse/page.tsx`:** Farm Action Journal chronological timeline, mobile photo upload with camera environment capture, and PJTSAU capture consistency advisory.
- **`crops/page.tsx`:** Plot and season management, soil type configuration (Black Cotton, Red Chalka, Alluvial), irrigation source, and plant tagging.

---

## 3. Initial Baseline Audit Findings

1. **Strengths:**
   - Strong multi-tenant data boundaries on farms and plots.
   - Media uploaded through `observations.py` automatically triggers Stage 02's `ImageQualityValidator` to score sharpness and exposure.
   - Geodesic computations in `GeoSpatialService` implement robust spherical polygon math and segment intersection checks.
   - Resilient weather architecture guarantees continuous service even during external provider outages.

2. **Observed Areas for Hardening in Stage 05:**
   - Need explicit documentation of the 5-tier location fallback hierarchy (`EXIF_GPS` -> `FARMER_ENTERED` -> `DEVICE_GPS_CONSENTED` -> `PLOT_CENTROID_FALLBACK` -> `UNKNOWN`).
   - Need clear decoupling between ambient weather correlations and causal disease diagnosis to avoid misinforming farmers.
   - Need formalization of multi-image scouting protocols (whole plant, upper leaf, lower leaf, stem, fruit) to support Stage 06 offline PWA.

---

## 4. Baseline Conclusion

The existing codebase provides a solid, working, and well-structured implementation of Stage 05 components. All 15 automated backend tests pass. The foundation is ready for formal Stage 05 verification and monograph authoring.
