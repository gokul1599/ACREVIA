# ACREVIA Progressive Web App & Offline Data Architecture
**Stage 06: Farmer Experience & Mobile-First Progressive Web App**  
*Document Version:* 1.0.0  
*Standards:* W3C Web App Manifest, Service Workers Level 1, IndexedDB API  
*Core Target:* Intermittent 3G/4G connectivity in rural Telangana

---

## 1. PWA Fundamentals & Manifest Specification

ACREVIA is configured as an installable Progressive Web App (PWA) operating seamlessly on Android (Chrome, Edge) and iOS (Safari):

### 1.1 Web App Manifest (`frontend/public/manifest.json`)
```json
{
  "name": "ACREVIA — Agricultural Intelligence Platform",
  "short_name": "ACREVIA",
  "description": "Foliar crop disease diagnostics, KrishiBrain agricultural knowledge, and plant health monitoring for Cotton, Rice, and Chilli farmers.",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#F7F5F0",
  "theme_color": "#1E3A2B",
  "orientation": "portrait",
  "icons": [
    { "src": "/icons/icon-192.png", "sizes": "192x192", "type": "image/png" },
    { "src": "/icons/icon-512.png", "sizes": "512x512", "type": "image/png" },
    { "src": "/icons/icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable" }
  ]
}
```

### 1.2 Standalone Display Mode
When installed to the Android home screen:
- Removes the browser URL bar, providing a native application experience.
- Persists theme color (`#1E3A2B`) on Android system status and navigation bars.
- Launches directly into the farmer's active dashboard shell.

---

## 2. Service Worker & Caching Policy (`frontend/public/sw.js`)

The service worker implements safe, versioned caching (`acrevia-shell-v1`):

1. **Pre-Cached Static Assets:**
   - Application shell root (`/`), `manifest.json`, icon assets (`/icons/icon-192.png`, `/icons/icon-512.png`).
2. **Stale-While-Revalidate for Static Content:**
   - CSS stylesheets, JavaScript chunks, and static branding assets are served immediately from cache while fetching updates in the background.
3. **Explicit Exclusion of Private APIs & Dynamic Mutations:**
   - Requests matching `/api/` or HTTP methods `POST`, `PUT`, `DELETE` are **never cached** in the service worker. This ensures sensitive farm observations, diagnoses, and authentication tokens are never leaked into shared browser caches.
4. **Offline Navigation Fallback:**
   - When a farmer navigates to an uncached route while offline, the service worker serves the pre-cached static shell rather than the browser's default connection error screen.

---

## 3. Offline Draft Queue & Data Integrity (`frontend/lib/offline/queue.ts`)

Field scouting often takes place in deep field plots where cellular reception drops completely. ACREVIA ensures no farmer data or foliar photograph is lost:

```
    [Farmer Submits Observation / Diagnosis in Field]
                            │
                            ▼
                  [Is Device Online?]
                  ├── YES ──► [Submit Directly to FastAPI Backend]
                  │
                  └── NO ───► [Save to OfflineQueue (IndexedDB / LocalStorage)]
                                    │
                                    ├── Assign Client UUID Idempotency Key
                                    ├── Convert Foliar Photo to Base64 String
                                    ├── Store Timestamps and Notes
                                    │
                                    ▼
                          [Display Yellow Notice: "Saved as Local Draft"]
```

### 3.1 Idempotency & Conflict Prevention
- Each offline draft generates a unique idempotency key (`draft-<timestamp>-<random_id>`).
- When connectivity returns, `OfflineQueue.syncAll()` submits the drafts sequentially:
  1. Creates server observation via `POST /api/v1/observations/`.
  2. Converts base64 image back to a binary Blob and uploads via `POST /api/v1/observations/{id}/media`.
  3. If a diagnosis was requested, triggers inference via `POST /api/v1/diagnoses/`.
  4. On server confirmation, the draft is deleted from local storage, preventing duplicate submissions.

### 3.2 Honest AI Representation
ACREVIA never fabricates an offline diagnosis prediction. The UI explicitly informs the farmer:
> *"You are currently offline. Changes are saved as local drafts and will sync when reconnected."*
Offline storage is never misrepresented as an on-device AI inference engine.
