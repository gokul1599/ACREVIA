# ACREVIA Frontend API Integration Report
**Stage 06: Farmer Experience & Mobile-First Progressive Web App**  
*Document Version:* 1.0.0  
*Backend Protocol:* REST / JSON over TLS  
*Base URL Path:* `/api/v1`  
*Authorization:* Bearer JWT (`Authorization: Bearer <token>`)

---

## 1. Integration Scope & Verification Matrix

The frontend integrates directly with the verified FastAPI backend services developed in Stages 4 and 5. Every client method in `frontend/lib/api/client.ts` maps to an authorized backend route:

| API Domain | HTTP Method | Endpoint | Frontend Client Method | Verified Status |
| :--- | :---: | :--- | :--- | :---: |
| **Auth** | `POST` | `/api/v1/auth/register` | `api.register()` | VERIFIED |
| **Auth** | `POST` | `/api/v1/auth/login` | `api.login()` | VERIFIED |
| **Auth** | `GET` | `/api/v1/auth/me` | `api.getCurrentUser()` | VERIFIED |
| **Farms** | `GET` | `/api/v1/farms/` | `api.listFarms()` | VERIFIED |
| **Farms** | `POST` | `/api/v1/farms/` | `api.createFarm()` | VERIFIED |
| **Plots** | `GET` | `/api/v1/farms/{farm_id}/plots` | `api.listPlots()` | VERIFIED |
| **Plots** | `POST` | `/api/v1/farms/{farm_id}/plots` | `api.createPlot()` | VERIFIED |
| **Seasons** | `GET` | `/api/v1/plots/{plot_id}/seasons` | `api.listCropSeasons()` | VERIFIED |
| **Seasons** | `POST` | `/api/v1/plots/{plot_id}/seasons` | `api.createCropSeason()` | VERIFIED |
| **Observations** | `GET` | `/api/v1/observations/?farm_id=...` | `api.listObservations()` | VERIFIED |
| **Observations** | `POST` | `/api/v1/observations/` | `api.createObservation()` | VERIFIED |
| **Media** | `POST` | `/api/v1/observations/{id}/media` | `api.uploadObservationMedia()` | VERIFIED |
| **Media Stream** | `GET` | `/api/v1/observations/{id}/media/{mid}/file` | `api.getMediaFileUrl()` | VERIFIED |
| **Diagnosis** | `POST` | `/api/v1/diagnoses/` | `api.requestDiagnosis()` | VERIFIED |
| **Diagnosis** | `GET` | `/api/v1/diagnoses/{id}` | `api.getDiagnosis()` | VERIFIED |
| **Knowledge** | `POST` | `/api/v1/knowledge/query` | `api.queryKnowledge()` | VERIFIED |
| **Knowledge** | `POST` | `/api/v1/knowledge/feedback` | `api.submitKnowledgeFeedback()` | VERIFIED |
| **Weather** | `GET` | `/api/v1/farms/{farm_id}/weather` | `api.getFarmWeather()` | VERIFIED |

---

## 2. Foliar Media Upload & Quality Verification

Foliar photos captured via mobile camera or photo picker are submitted using `multipart/form-data`:
1. Client passes binary file to `POST /api/v1/observations/{id}/media`.
2. Backend runs image quality checks (blur detection, resolution, exposure).
3. If acceptable, file is stored in private object storage, and a structured `ObservationMediaResponse` is returned.
4. Images are displayed using private streaming endpoints (`/media/{media_id}/file`) requiring valid session authorization.

---

## 3. CropVision Diagnosis Inference Pipeline

When a diagnosis is requested:
1. Client submits `{ observation_id, media_id, crop_type, language }`.
2. Backend calls the Stage 3 PyTorch inference engine on port 8001.
3. Response includes calibrated probabilities, decision state (`CONFIDENT_PREDICTION`, `LOW_CONFIDENCE`, `OUT_OF_DISTRIBUTION`), normalized entropy, and CIBRC advisory.
4. Client renders candidate conditions with native Telugu, Hindi, and English translations.

---

## 4. Security & Error Handling

- **Automatic 401 Interception:** If a JWT token expires while browsing, the API client clears local credentials and routes the farmer to `/login?expired=1`.
- **Zero Client Credentials:** Database connection strings (Neon PostgreSQL) and cloud AI keys remain strictly server-side. No `NEXT_PUBLIC_*` credentials exist in browser bundles.
- **Tenant Isolation:** All farm, plot, and observation queries require farm membership authorization. Any cross-tenant access attempt returns HTTP 403 Forbidden.
