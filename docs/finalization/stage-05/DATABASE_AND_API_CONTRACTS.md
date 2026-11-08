# ACREVIA — STAGE 05 DATABASE & API CONTRACT SPECIFICATIONS
**Programme:** ACREVIA 14-Stage Finalization Programme  
**Target Stage:** Stage 05 — Farm Action Journal, Observations, Geolocation & Weather  
**Date:** 2026-11-08  
**Status:** SPECIFIED & VERIFIED (`PASS`)

---

## 1. REST API Endpoints Specification

### 1.1 Farm Management (`/api/v1/farms`)

```http
POST /api/v1/farms/
Content-Type: application/json
Authorization: Bearer <farmer_token>

{
  "name": "Nalgonda Chilli Holding",
  "district": "Nalgonda",
  "mandal": "Miryalaguda",
  "village": "Alagadapa",
  "total_acreage": 4.5
}

--> HTTP/1.1 201 Created
{
  "id": "e4b11f32-...",
  "owner_id": "bd0d3037-...",
  "name": "Nalgonda Chilli Holding",
  "state": "Telangana",
  "district": "Nalgonda",
  "mandal": "Miryalaguda",
  "village": "Alagadapa",
  "total_acreage": 4.5,
  "is_archived": false,
  "created_at": "2026-11-08T11:00:00Z",
  "updated_at": "2026-11-08T11:00:00Z"
}
```

---

### 1.2 Plot Management (`/api/v1/farms/{farm_id}/plots`)

```http
POST /api/v1/farms/{farm_id}/plots
Content-Type: application/json
Authorization: Bearer <farmer_token>

{
  "name": "South Parcel",
  "soil_type": "RED_CHALKA",
  "irrigation_source": "DRIP",
  "acreage": 1.5,
  "boundary_geojson": "{\"type\":\"Polygon\",\"coordinates\":[[[79.26,17.05],[79.27,17.05],[79.27,17.06],[79.26,17.06],[79.26,17.05]]]}"
}

--> HTTP/1.1 201 Created
{
  "id": "78a9c211-...",
  "farm_id": "{farm_id}",
  "name": "South Parcel",
  "soil_type": "RED_CHALKA",
  "irrigation_source": "DRIP",
  "acreage": 1.5,
  "boundary_geojson": "...",
  "is_archived": false,
  "created_at": "2026-11-08T11:05:00Z"
}
```

---

### 1.3 Observations & Multi-Image Upload (`/api/v1/observations`)

```http
POST /api/v1/observations/
Content-Type: application/json
Authorization: Bearer <farmer_token>

{
  "farm_id": "{farm_id}",
  "plot_id": "{plot_id}",
  "crop_season_id": "{crop_season_id}",
  "notes": "Red spots observed on lower canopy leaves",
  "symptom_tags": "leaf_spot,chlorosis"
}

--> HTTP/1.1 201 Created
{
  "id": "9a3e4210-...",
  "farm_id": "{farm_id}",
  "plot_id": "{plot_id}",
  "crop_season_id": "{crop_season_id}",
  "observer_id": "bd0d3037-...",
  "notes": "Red spots observed on lower canopy leaves",
  "symptom_tags": "leaf_spot,chlorosis",
  "created_at": "2026-11-08T11:10:00Z",
  "media": []
}

POST /api/v1/observations/{obs_id}/media
Content-Type: multipart/form-data
Authorization: Bearer <farmer_token>

--BOUNDARY
Content-Disposition: form-data; name="file"; filename="cotton_foliar.jpg"
Content-Type: image/jpeg

<binary JPEG bytes>
--BOUNDARY
Content-Disposition: form-data; name="is_primary"

true
--BOUNDARY--

--> HTTP/1.1 201 Created
{
  "id": "c1f88410-...",
  "observation_id": "{obs_id}",
  "storage_path": "a8f3b901_cotton_foliar.jpg",
  "file_size_bytes": 142850,
  "mime_type": "image/jpeg",
  "sha256_hash": "a8f3b901...",
  "is_primary": true,
  "created_at": "2026-11-08T11:10:05Z"
}
```

---

### 1.4 Agrometeorological Context (`/api/v1/farms/{farm_id}/weather`)

```http
GET /api/v1/farms/{farm_id}/weather
Authorization: Bearer <farmer_token>

--> HTTP/1.1 200 OK
{
  "farm_id": "{farm_id}",
  "district": "Warangal",
  "temperature": 28.5,
  "humidity": 68.0,
  "precipitation": 0.0,
  "wind_speed": 8.5,
  "source": "Open-Meteo Historical & Forecast API",
  "pest_risk_level": "MODERATE",
  "weather_risk_level": "LOW",
  "advisory": "Favorable conditions for sucking pests (Thrips, Aphids) and mild foliar spot incidence. Periodic scouting recommended."
}
```

---

## 2. Standardized Error Contract

All error scenarios conform to RFC 7807 problem details:

| Status Code | Scenario | Sample Response Payload |
|---|---|---|
| `400 Bad Request` | Plot does not belong to specified farm | `{"detail": "Specified plot does not belong to this farm."}` |
| `400 Bad Request` | Unsupported file MIME type | `{"detail": "Unsupported image MIME type 'image/bmp'. Allowed: ['image/jpeg', 'image/png', 'image/webp']"}` |
| `401 Unauthorized` | Missing / expired JWT Bearer token | `{"detail": "Could not validate credentials."}` |
| `403 Forbidden` | Access to another tenant's farm or media | `{"detail": "Unauthorized: User does not have access permissions for this farm holding."}` |
| `404 Not Found` | Farm / observation does not exist | `{"detail": "Observation '{id}' not found."}` |
| `413 Payload Too Large` | Image upload exceeds 10 MB ceiling | `{"detail": "File exceeds maximum allowed size of 10485760 bytes."}` |
