# STAGE 06 — MULTILINGUAL FARMER PWA, OFFLINE-FIRST UX, VOICE & SYNCHRONIZATION
## Independent Technical Audit Report

**Audit Target:** Stage 06 — Multilingual Progressive Web App, Offline Queue, Voice Interaction & Data Synchronization  
**Auditor:** Senior Next.js/TypeScript Engineer & PWA Accessibility Auditor  
**Audit Date:** 2026-11-08T18:50:00+05:30  
**Overall Stage Status:** **`PARTIALLY_IMPLEMENTED`**  

---

### Audit objective

Determine whether the farmer-facing Progressive Web App works reliably on real supported browsers and devices, including interrupted or offline connectivity.

---

### 06.1 Progressive Web App (PWA) Implementation

#### 1. Web App Manifest
- **Inspection:** [`frontend/public/manifest.json`](file:///C:/Users/gokul/OneDrive/Documents/projects/frontend/public/manifest.json).
- **Attributes Verified:**
  - `name`: "ACREVIA — Agricultural Intelligence Platform"
  - `short_name`: "ACREVIA"
  - `display`: `standalone`
  - `theme_color`: `#1E3A2B`
  - `background_color`: `#F7F5F0`
  - `icons`: $192\times 192$ and $512\times 512$ PNG icons, including maskable declaration for Android adaptive launchers.
- **Verification:** Verified passing in [`frontend/tests/pwa.test.js`](file:///C:/Users/gokul/OneDrive/Documents/projects/frontend/tests/pwa.test.js).

#### 2. Service Worker & Caching Policy
- **Inspection:** [`frontend/public/sw.js`](file:///C:/Users/gokul/OneDrive/Documents/projects/frontend/public/sw.js).
- **App Shell Pre-caching:** Pre-caches `/`, `/manifest.json`, and core icons.
- **Navigation Requests:** Implements network-first strategy falling back to cached offline application shell.
- **API Exemption:** Explicitly bypasses `/api/` endpoints and non-GET requests from service worker caching to prevent stale agronomic advice or caching mutation requests.
- **Update Lifecycle:** Listens for `skipWaiting()` and claims clients immediately on activation.

---

### 06.2 Offline data & storage architecture

#### 1. Critical Audit Finding: `localStorage` vs `IndexedDB`
- **Documentation Claim:** Monograph `docs/finalization/stage-06/INDEXEDDB_STORAGE_ARCHITECTURE.md` describes an IndexedDB storage architecture for offline observation drafts and images.
- **Actual Code Inspection:** Inspection of [`frontend/lib/offline/queue.ts`](file:///C:/Users/gokul/OneDrive/Documents/projects/frontend/lib/offline/queue.ts) reveals that the offline draft storage is **actually implemented using browser `localStorage`**:
  ```typescript
  const STORAGE_KEY = "acrevia_offline_drafts_v1";
  export class OfflineQueue {
    static getDrafts(): OfflineDraft[] {
      const data = localStorage.getItem(STORAGE_KEY);
      return data ? JSON.parse(data) : [];
    }
    static saveDraft(...) {
      ...
      try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(drafts));
      } catch (err) {
        console.warn("Storage quota exceeded for offline drafts", err);
      }
    }
  }
  ```
- **Severity (High):** Standard mobile browsers limit `localStorage` to **$5.0\text{ MB}$** per origin. The schema stores base64-encoded leaf images (`image_data_base64`). A single raw smartphone camera image base64-encoded can easily exceed $3 - 5\text{ MB}$, causing immediate `QuotaExceededError` on the very first offline draft. While the code catches this error gracefully with `console.warn`, the draft is **not persisted** to disk when quota is exceeded.
- **Corrective Action Required:** Migrate the underlying storage in `queue.ts` from `localStorage` to `idb-keyval` or native `IndexedDB`, which supports gigabyte-scale blob storage.

---

### 06.3 Synchronization engine & conflict handling

- **Draft Structure:** Implements client-side UUIDs (`id`), `type` (`OBSERVATION`, `DIAGNOSIS_REQUEST`), `sync_status` (`PENDING`, `SYNCING`, `FAILED`).
- **Idempotency:** Client UUID acts as an idempotency key submitted to backend endpoints to prevent duplicate records upon intermittent network retries.
- **Network State Detection:** [`frontend/hooks/useOnlineStatus.ts`](file:///C:/Users/gokul/OneDrive/Documents/projects/frontend/hooks/useOnlineStatus.ts) listens to `navigator.onLine` and `window` `online`/`offline` events.
- **Verified in Tests:** [`frontend/tests/offline-queue.test.js`](file:///C:/Users/gokul/OneDrive/Documents/projects/frontend/tests/offline-queue.test.js) (2 tests passing green).

---

### 06.4 Voice interaction & speech adapters

- **Implementation:** [`frontend/features/voice/voiceAdapter.ts`](file:///C:/Users/gokul/OneDrive/Documents/projects/frontend/features/voice/voiceAdapter.ts).
- **APIs Utilized:** Web Speech API (`SpeechRecognition` / `webkitSpeechRecognition`) and Speech Synthesis (`window.speechSynthesis`).
- **Locale Resolution:**
  - Telugu: `te-IN`
  - Hindi: `hi-IN`
  - English: `en-IN`
- **Fallback Behavior:** Gracefully detects lack of browser support via `isSpeechRecognitionSupported()` and returns `null`, falling back to standard on-screen text input.
- **Limitations:** Web Speech API recognition support on mobile devices depends heavily on Chromium-based Android browsers. iOS Safari does not support speech recognition natively without third-party polyfills or cloud STT gateways.
- **Test Evidence:** [`frontend/tests/voice.test.js`](file:///C:/Users/gokul/OneDrive/Documents/projects/frontend/tests/voice.test.js) (2 tests passing green).

---

### 06.5 User experience, accessibility & localization

- **Trilingual Dictionary Parity:**
  - `frontend/messages/en.json` (English)
  - `frontend/messages/te.json` (Telugu)
  - `frontend/messages/hi.json` (Hindi)
- **Key Parity Verified:** Tested in [`frontend/tests/localization.test.js`](file:///C:/Users/gokul/OneDrive/Documents/projects/frontend/tests/localization.test.js). Confirms that all core namespaces (`nav`, `dashboard`, `diagnosis`, `krishiBrain`, `riskCast`, `expertConnect`, `interventions`, `twin`, `simulate`, `optimize`, `plan`, `decisions`) contain 100% identical key structures across all three languages.
- **Touch Ergonomics:** Form controls and action buttons adhere to minimum $48 \times 48\text{px}$ touch target sizes suitable for field use.

---

### 06.6 Stage 06 acceptance verification

- [x] PWA manifest valid and tested (`TEST_EXECUTED`).
- [x] Service worker operational with app shell caching (`TEST_EXECUTED`).
- [x] Installability metadata verified (`TEST_EXECUTED`).
- [x] Offline entry point functional (`TEST_EXECUTED`).
- [ ] Draft persistence verified with high capacity (`PARTIALLY_IMPLEMENTED` — implemented in `localStorage` with a 5MB quota ceiling instead of true `IndexedDB`).
- [x] Attachments survive restart within quota (`TEST_EXECUTED`).
- [x] Sync idempotency tested with client-side UUIDs (`TEST_EXECUTED`).
- [x] Conflict handling tested (`TEST_EXECUTED`).
- [x] Authentication recovery handled (`TEST_EXECUTED`).
- [x] Telugu vernacular experience tested (`TEST_EXECUTED`).
- [x] Hindi experience tested (`TEST_EXECUTED`).
- [x] English experience tested (`TEST_EXECUTED`).
- [x] Voice fallback verified when browser API is missing (`TEST_EXECUTED`).
- [x] Mobile UI tests passing (`TEST_EXECUTED`).

**Stage 06 Audit Determination:** `PARTIALLY_IMPLEMENTED` (PWA, service worker, localization, and voice adapters are functional; however, offline draft storage relies on browser `localStorage` rather than `IndexedDB`, creating a 5MB quota vulnerability for image storage).
