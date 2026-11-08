# ACREVIA — API CONTRACTS SPECIFICATION
## REST Endpoints for Geospatial, Satellite, IoT Telemetry, Multi-Source Fusion, Yield Feasibility & Knowledge Graph

---

## 1. Domain Endpoint Summary

All routes are mounted under `/api/v1` and protected by standard JWT Bearer authentication or dedicated Device Tokens.

| Domain | Route | Method | Description | Auth Required |
|---|---|---|---|---|
| **Acrevia Geo** | `/geospatial/plots/{plot_id}/geometry` | `POST` | Upload & validate plot polygon boundary | Farmer / Manager |
| **Acrevia Geo** | `/geospatial/plots/{plot_id}/geometry` | `GET` | Retrieve plot boundary, centroid, and area | Plot Member |
| **Acrevia Geo** | `/geospatial/permissions` | `POST` | Update location privacy granularity | Farm Owner |
| **Acrevia Earth** | `/satellite/plots/{plot_id}/time-series` | `GET` | Retrieve NDVI/EVI/NDMI history & trend | Plot Member |
| **Acrevia Earth** | `/satellite/plots/{plot_id}/latest` | `GET` | Get latest clear-sky satellite observation | Plot Member |
| **Acrevia Sense** | `/sense/devices` | `POST` | Register field IoT sensor device | Farm Manager |
| **Acrevia Sense** | `/sense/devices` | `GET` | List registered farm sensor devices | Farm Member |
| **Acrevia Sense** | `/sense/telemetry` | `POST` | Ingest sensor telemetry stream | Device Token |
| **Acrevia Sense** | `/sense/plots/{plot_id}/telemetry` | `GET` | Retrieve plot micro-climate readings | Plot Member |
| **Acrevia Sense** | `/sense/devices/{device_id}/calibration` | `POST` | Record calibration ledger entry | Technician / Manager |
| **Acrevia Fusion** | `/fusion/plots/{plot_id}/assessment` | `GET` | Multi-source evidence fusion & explanation | Plot Member |
| **Acrevia Predict** | `/predict/harvests` | `POST` | Log ground-truth harvest yield record | Farm Manager |
| **Acrevia Predict** | `/predict/plots/{plot_id}/forecast` | `GET` | Retrieve yield prediction or withholding notice | Plot Member |
| **Knowledge Graph** | `/knowledge-graph/entities` | `GET` | Query agricultural entities & taxonomy | Authenticated |
| **Knowledge Graph** | `/knowledge-graph/traverse` | `GET` | Multi-hop causal graph traversal | Authenticated |

---

## 2. Selected Request & Response Payloads

### 2.1 Acrevia Geo: Plot Geometry Upload
`POST /api/v1/geospatial/plots/{plot_id}/geometry`
```json
{
  "type": "Polygon",
  "coordinates": [
    [
      [79.5812, 17.9854],
      [79.5845, 17.9854],
      [79.5845, 17.9821],
      [79.5812, 17.9821],
      [79.5812, 17.9854]
    ]
  ]
}
```

Response:
```json
{
  "plot_id": "plot-cotton-01",
  "is_valid": true,
  "centroid": { "latitude": 17.98375, "longitude": 79.58285 },
  "calculated_area_hectares": 1.18,
  "calculated_area_acres": 2.92,
  "bbox": [79.5812, 17.9821, 79.5845, 17.9854]
}
```

### 2.2 Acrevia Earth: Satellite Time-Series
`GET /api/v1/satellite/plots/{plot_id}/time-series`
```json
{
  "plot_id": "plot-cotton-01",
  "trend_summary": "STABLE_VIGOR",
  "observations_count": 4,
  "evidence_disclaimer": "Satellite observations reflect broad canopy vigor and surface moisture; they do not diagnose specific plant diseases or pathogens.",
  "time_series": [
    {
      "observation_date": "2026-10-15T05:30:00Z",
      "mean_ndvi": 0.68,
      "mean_evi": 0.52,
      "mean_ndmi": 0.31,
      "cloud_masked_pixel_ratio": 0.05
    },
    {
      "observation_date": "2026-10-25T05:30:00Z",
      "mean_ndvi": 0.72,
      "mean_evi": 0.56,
      "mean_ndmi": 0.34,
      "cloud_masked_pixel_ratio": 0.02
    }
  ]
}
```

### 2.3 Acrevia Predict: Yield Feasibility Withholding Notice
`GET /api/v1/predict/plots/{plot_id}/forecast`
```json
{
  "plot_id": "plot-cotton-01",
  "crop_name": "Cotton",
  "forecast_status": "WITHHELD_INSUFFICIENT_DATA",
  "is_forecast_available": false,
  "sample_count_available": 18,
  "minimum_sample_threshold_required": 50,
  "withholding_reason": "Historical verified harvest records for this agro-climatic zone are below statistical significance threshold (18 < 50). Yield predictions are withheld to prevent ungrounded estimates.",
  "research_experimental_baseline": null
}
```
