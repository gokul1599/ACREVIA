# ACREVIA — PRODUCTION DEPLOYMENT & OPERATION RUNBOOK
## Deployment Architecture, Environment Lifecycle, CI/CD Pipeline & Rollback Protocols

**Document Version:** 1.0.0  
**Status:** Approved Operational Runbook  
**Target Architecture:** Vercel Global Edge (Next.js 16) + Dedicated Container Host (FastAPI + PyTorch Microservice) + Neon PostgreSQL 16 (AWS Singapore `sin1`)

---

### 1. Production Architecture Overview

```
[Client Devices: Mobile Browsers / PWA in Telangana]
       │
       ▼ (HTTPS / DNS / Global Anycast)
[Vercel Global Edge: Next.js 16 App Router]
  │   - Frontend Production URL: https://frontend-omega-two-hijwc54gyy.vercel.app
  │   - Static Pages Prerendered: 13 / 13 (Turbopack)
  │   - PWA Offline Service Worker (IndexedDB OfflineQueue)
  │   - Edge Security Headers (CSP, HSTS, X-Content-Type-Options)
  │
  ├─── API Rewrites (/api/v1/*) ───► [Backend API Gateway: FastAPI]
                                         │  - Port 8000 (ASGI / Uvicorn)
                                         │  - RBAC, JWT (HS256), Tenant Isolation
                                         │  - Correlation Middleware & Structured Logs
                                         │
                                         ├──► [Neon PostgreSQL 16 + pgvector]
                                         │      - AWS Singapore (sin1)
                                         │      - 133 Relational Tables (f4894a11c87d)
                                         │      - 1536d Vector Index (pgvector v0.8.6)
                                         │
                                         └──► [ML Inference Microservice]
                                                - Port 8001 (FastAPI + ONNX Runtime)
                                                - Int8 Quantized MobileNetV3 (<45ms)
                                                - Dual-Tier 8-State Abstention
```

---

### 2. Runtime Compatibility Analysis (Vercel vs Dedicated Host)

#### Frontend (Next.js 16 App Router)
* **Target:** Vercel Global Edge Platform.
* **Compatibility:** 100% Native. Builds with Turbopack, static page prerendering across 13 core views, vernacular localized routing.
* **Live Production Deployment:** Deployed successfully at `https://frontend-omega-two-hijwc54gyy.vercel.app`.

#### Backend API Gateway (FastAPI) & ML Inference Service
* **Constraint:** PyTorch (`torch`), `torchvision`, and `onnxruntime` together exceed 750 MB uncompressed, while Vercel Serverless Functions enforce a strict **250 MB uncompressed limit**.
* **Decision:** 
  1. The Next.js frontend is deployed directly on Vercel.
  2. The FastAPI backend gateway can be hosted either via lightweight Vercel Serverless Functions (excluding PyTorch) or as a containerized service (Docker / AWS ECS / GCP Cloud Run / Fly.io / Railway).
  3. The PyTorch + ONNX ML Inference Service runs as an independent microservice container on port 8001, completely decoupled from the serverless edge.

---

### 3. Step-by-Step Production Release Procedure

#### Pre-Release Verification Checklist
1. All 140 automated tests pass locally:
   * `python -m pytest backend/tests/ -v` (97 passed)
   * `python -m pytest ml/inference_service/tests/ -v` (7 passed)
   * `npm --prefix frontend test` (36 passed)
2. Database migrations stamped and verified:
   * `alembic -c backend/alembic.ini current` $\to$ `f4894a11c87d (head)`
3. Next.js production build succeeds:
   * `npm --prefix frontend run build` $\to$ 13/13 static routes prerendered.

#### Executing Deployment
```powershell
# 1. Deploy Frontend to Vercel
npx vercel --cwd frontend --prod --token $VERCEL_TOKEN

# 2. Deploy Containerized Backend & ML Microservice
docker compose -f docker-compose.yml up -d --build
```

---

### 4. Post-Deployment Smoke Test Protocol

1. **Frontend Availability:**
   * `curl -I https://frontend-omega-two-hijwc54gyy.vercel.app` $\to$ Expect `HTTP/2 200`.
2. **Backend Gateway Health Check:**
   * `curl https://api.acrevia.in/api/v1/system/health` $\to$ Expect `{"status": "healthy", "database": "connected", "migration_head": "f4894a11c87d"}`.
3. **ML Microservice Health Check:**
   * `curl http://localhost:8001/health` $\to$ Expect `{"status": "ok", "crops": ["cotton", "rice", "chilli"]}`.
4. **End-to-End Farmer Flow:**
   * Perform user login $\to$ Create plot $\to$ Upload foliar test image $\to$ Receive diagnosis & KrishiBrain advisory with citations.

---

### 5. Rollback & Disaster Recovery Procedures

#### Instant Frontend Rollback (Vercel)
If a regressions occurs on the frontend:
```bash
# Roll back instantly to previous deployment alias
npx vercel rollback <previous-deployment-id> --token $VERCEL_TOKEN
```

#### Database Point-in-Time Recovery (Neon)
1. Open Neon Cloud Console $\to$ Projects $\to$ ACREVIA Database.
2. Select **Branches / Point-in-Time Restore**.
3. Choose the timestamp prior to the incident (up to 7 days retention in AWS Singapore).
4. Restore branch or repoint connection string in application environment variables.

#### RPO & RTO Targets
* **Recovery Point Objective (RPO):** $< 5 \text{ minutes}$ (continuous Neon WAL replication).
* **Recovery Time Objective (RTO):** $< 15 \text{ minutes}$ (instantaneous branch promotion in Neon).
