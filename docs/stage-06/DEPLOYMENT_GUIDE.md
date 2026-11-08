# ACREVIA Frontend Vercel Deployment & Infrastructure Guide
**Stage 06: Farmer Experience & Mobile-First Progressive Web App**  
*Document Version:* 1.0.0  
*Target Hosting:* Vercel Platform (Edge Network & Serverless Compute)  
*Primary Compute Region:* `sin1` (Singapore)  
*Regional Alignment:* Aligned with Neon PostgreSQL in `ap-southeast-1` (Singapore)

---

## 1. Vercel Project Configuration

The ACREVIA farmer frontend deploys to Vercel as a standard Next.js App Router project:

### 1.1 Project Settings
- **Framework Preset:** Next.js
- **Root Directory:** `frontend`
- **Build Command:** `next build`
- **Output Directory:** `.next`
- **Install Command:** `npm install`
- **Node.js Version:** 20.x or 22.x+ (Node 24 supported)

### 1.2 Environment Variables (Vercel Dashboard)

| Variable Name | Environment | Value Description | Example Value |
| :--- | :--- | :--- | :--- |
| `NEXT_PUBLIC_API_URL` | Production & Preview | Public URL of the FastAPI Backend | `https://api.acrevia.in` |
| `BACKEND_INTERNAL_URL` | Production & Preview | Internal backend URL for reverse proxying | `http://api.acrevia.internal:8000` |
| `VERCEL_REGION` | Production | Compute execution region | `sin1` |

> [!IMPORTANT]
> Never define database credentials (`DATABASE_URL`), JWT secret keys, or cloud AI keys in the frontend Vercel environment. All database operations are restricted to backend APIs.

---

## 2. HTTPS & Progressive Web App Requirements

1. **Mandatory HTTPS:**
   - Both the **Service Worker API** (`sw.js`) and the **Web Speech API** (`SpeechRecognition`, `speechSynthesis`) strictly require a secure TLS/HTTPS origin. Vercel automatically provisions SSL certificates on all preview and production domains.
2. **PWA Asset Cache Control:**
   - Static assets in `/public` (`manifest.json`, `/icons/*`, `/sw.js`) are served with appropriate caching headers.
   - `/sw.js` must be served with `Cache-Control: no-cache, no-store, must-revalidate` to ensure service worker updates take effect immediately on farmer devices.

---

## 3. Local Development & End-to-End Orchestration

To run the complete platform locally:

```powershell
# Terminal 1: Start ML Inference Service (Port 8001)
uvicorn ml.inference_service.app.main:app --port 8001 --reload

# Terminal 2: Start ACREVIA Enterprise Backend Gateway (Port 8000)
uvicorn backend.app.main:app --port 8000 --reload

# Terminal 3: Start Farmer Next.js Progressive Web App (Port 3000)
cd frontend
npm run dev
```

Open `http://localhost:3000` in Google Chrome or Android Emulator. The Next.js reverse proxy automatically routes `/api/v1/*` requests to the FastAPI backend on port 8000 without CORS configuration issues.
