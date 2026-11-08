# ACREVIA — FRONTEND-TO-BACKEND API CONTRACT SPECIFICATION
## Comprehensive OpenAPI v3 Protocol, Authentication Headers, Request Payloads, and Response Schemas

---

## 1. Protocol & Communication Standards

- **Base URL:** `/api/v1`
- **Protocol:** HTTPS / JSON (Multipart for foliar image uploads; Binary stream for media retrieval)
- **Authentication:** HTTP Bearer Header: `Authorization: Bearer <JWT_ACCESS_TOKEN>`
- **Correlation Header:** Clients should provide `X-Correlation-ID: <UUIDv4>`. The backend returns the identical correlation ID in response headers.
- **Latency Tracking:** Backend returns execution duration via `X-Response-Time-Ms`.
- **Standardized Error Envelope:**
```json
{
  "error_type": "AuthorizationException",
  "detail": "Access to requested farm is forbidden: you are not an owner or member.",
  "details": {},
  "correlation_id": "c1f72a44-8bc9-4b89-a2ea-9e7674251234"
}
```

---

## 2. Authentication & Identity Endpoints (`/api/v1/auth`)

### 2.1 Register User
- **Method:** `POST /api/v1/auth/register`
- **Status:** `201 Created` / `409 Conflict` (Duplicate phone/email) / `422 Unprocessable Entity`
- **Request Body:**
```json
{
  "phone": "+919876543210",
  "full_name": "Ramesh Goud",
  "password": "SecurePassword123!",
  "email": "ramesh@acrevia.com",
  "language_preference": "te",
  "role": "FARMER"
}
```
- **Response Body:**
```json
{
  "id": "c4f236c8-603f-4932-ab54-e13f5e256420",
  "phone": "+919876543210",
  "email": "ramesh@acrevia.com",
  "full_name": "Ramesh Goud",
  "language_preference": "te",
  "is_active": true,
  "is_verified": false,
  "roles": ["FARMER"]
}
```

### 2.2 Login User
- **Method:** `POST /api/v1/auth/login`
- **Status:** `200 OK` / `401 Unauthorized`
- **Request Body:**
```json
{
  "phone": "+919876543210",
  "password": "SecurePassword123!"
}
```
- **Response Body:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsIn...",
  "token_type": "bearer",
  "expires_in_seconds": 86400,
  "user": {
    "id": "c4f236c8-603f-4932-ab54-e13f5e256420",
    "phone": "+919876543210",
    "full_name": "Ramesh Goud",
    "roles": ["FARMER"]
  }
}
```

### 2.3 Get Current User Profile
- **Method:** `GET /api/v1/auth/me`
- **Status:** `200 OK` / `401 Unauthorized`
- **Headers:** `Authorization: Bearer <token>`

---

## 3. Farm & Plot Management Endpoints (`/api/v1/farms`, `/api/v1/plots`)

### 3.1 Create Farm Holding
- **Method:** `POST /api/v1/farms/`
- **Status:** `201 Created`
- **Request Body:**
```json
{
  "name": "Ramesh Warangal Farm",
  "district": "Warangal",
  "mandal": "Geesugonda",
  "village": "Dharmaram",
  "total_acreage": 3.5
}
```

### 3.2 List Accessible Farms
- **Method:** `GET /api/v1/farms/`
- **Response Body:** List of farms owned by or shared with the authenticated user.

### 3.3 Add Farm Collaborator
- **Method:** `POST /api/v1/farms/{farm_id}/memberships`
- **Status:** `201 Created` / `403 Forbidden` / `409 Conflict`
- **Request Body:**
```json
{
  "user_id": "758f6233-0c46-44b2-9aa8-261545620948",
  "role_in_farm": "WORKER"
}
```

### 3.4 Create Plot in Farm
- **Method:** `POST /api/v1/farms/{farm_id}/plots`
- **Request Body:**
```json
{
  "name": "North Plot - Cotton",
  "soil_type": "BLACK_COTTON",
  "irrigation_source": "BOREWELL",
  "acreage": 2.0
}
```

---

## 4. Observations & Foliar Photographs (`/api/v1/observations`)

### 4.1 Create Observation
- **Method:** `POST /api/v1/observations/`
- **Status:** `201 Created` / `403 Forbidden`
- **Request Body:**
```json
{
  "farm_id": "425f2b52-2469-4009-8a9b-d176fbf19f4b",
  "plot_id": "a91b4028-ef22-4a5c-89a1-8d2645167091",
  "crop_season_id": "90e1c482-1bf7-4220-8025-01e441865912",
  "notes": "Red spots observed on lower canopy leaves",
  "symptom_tags": "leaf_spot,chlorosis"
}
```

### 4.2 Upload Foliar Media (Multipart)
- **Method:** `POST /api/v1/observations/{observation_id}/media`
- **Status:** `201 Created` / `400 Bad Request` (Invalid MIME) / `413 Entity Too Large`
- **Content-Type:** `multipart/form-data`
- **Form Fields:** `file: <binary>`, `is_primary: true`
- **Response Body:**
```json
{
  "id": "51b2e6aa-d129-4560-b631-08579bf68291",
  "observation_id": "bb9650ef-a30f-47b3-9b05-fea2851c84ac",
  "storage_path": "a82b9c011e48f729_leaf.jpg",
  "file_size_bytes": 1048576,
  "mime_type": "image/jpeg",
  "sha256_hash": "a82b9c011e48f7293b4f620e9871abf9584c310243e8d22384a2bce430291abc",
  "is_primary": true,
  "created_at": "2026-11-08T08:25:00Z"
}
```

### 4.3 Secure Foliar Media Stream
- **Method:** `GET /api/v1/observations/{observation_id}/media/{media_id}/file`
- **Status:** `200 OK` (Streams raw bytes) / `403 Forbidden` (Cross-farm access blocked) / `404 Not Found`

---

## 5. AI Diagnoses & Expert Reviews (`/api/v1/diagnoses`)

### 5.1 Request AI Diagnosis
- **Method:** `POST /api/v1/diagnoses/`
- **Status:** `201 Created`
- **Request Body:**
```json
{
  "observation_id": "bb9650ef-a30f-47b3-9b05-fea2851c84ac",
  "crop_type": "cotton",
  "language": "te"
}
```
- **Response Body:**
```json
{
  "id": "e458e0a1-4328-4ef8-a1bf-894285160911",
  "observation_id": "bb9650ef-a30f-47b3-9b05-fea2851c84ac",
  "status": "COMPLETED",
  "requested_at": "2026-11-08T08:26:00Z",
  "completed_at": "2026-11-08T08:26:02Z",
  "prediction": {
    "model_version": "MobileNetV3-Stage3-v1.0",
    "decision_state": "HIGH_CONFIDENCE_DIAGNOSIS",
    "top_confidence": 0.942,
    "normalized_entropy": 0.182,
    "prediction_margin": 0.812,
    "cibrc_advisory": "Follow CIBRC approved IPM protocol for Cotton Cercospora Leaf Spot.",
    "candidates": [
      {
        "rank": 1,
        "class_id": "cotton_cercospora_leaf_spot",
        "display_name_en": "Cercospora Leaf Spot",
        "display_name_te": "సెర్కోస్పోరా ఆకుమచ్చ తెగులు",
        "display_name_hi": "सर्कोस्पोरा पत्ती धब्बा रोग",
        "pathogen_or_cause": "Cercospora gossypina",
        "calibrated_prob": 0.942
      }
    ]
  },
  "expert_review": null
}
```

### 5.2 Submit Certified Expert Review
- **Method:** `POST /api/v1/diagnoses/{diagnosis_id}/expert-review`
- **Status:** `201 Created` / `403 Forbidden` (Restricted to `AGRICULTURAL_EXPERT` / `ADMIN`)
- **Request Body:**
```json
{
  "status": "CONFIRMED",
  "verified_class_id": "cotton_cercospora_leaf_spot",
  "expert_notes": "Clinical foliar symptoms confirmed. Recommend improving field drainage."
}
```

---

## 6. Weather & Agrometeorological Risk (`/api/v1/farms/{id}/weather`)

- **Method:** `GET /api/v1/farms/{farm_id}/weather`
- **Status:** `200 OK`
- **Response Body:**
```json
{
  "farm_id": "425f2b52-2469-4009-8a9b-d176fbf19f4b",
  "district": "Warangal",
  "temperature": 29.5,
  "humidity": 82.0,
  "precipitation": 2.4,
  "wind_speed": 7.5,
  "source": "Open-Meteo Historical & Forecast API",
  "pest_risk_level": "HIGH",
  "weather_risk_level": "LOW",
  "advisory": "High relative humidity combined with moderate temperature elevates risk of foliar fungal pathogens (e.g., Rice Blast, Cotton Cercospora Leaf Spot). Maintain field drainage and monitor lower canopy."
}
```

---

## 7. Data Governance & Consent (`/api/v1/consent`)

- **Method:** `POST /api/v1/consent/`
- **Request Body:**
```json
{
  "consent_type": "CORE_SERVICE",
  "is_granted": true,
  "policy_version": "1.0.0"
}
```
- **Method:** `GET /api/v1/consent/` (Returns list of active consent declarations for the authenticated user).
