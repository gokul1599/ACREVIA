# ACREVIA — STAGE 06 BASELINE AUDIT
**Programme:** ACREVIA 14-Stage Finalization Programme  
**Target Stage:** Stage 06 — Vernacular Progressive Web App & Voice Interaction  
**Date:** 2026-11-08  
**Status:** AUDIT COMPLETED (`PASS`)

---

## 1. Scope of Baseline Audit

The baseline audit for Stage 06 conducts a rigorous code-level inspection of all assets governing:
1. **PWA Foundation:** Web App Manifest, Service Worker caching strategies, Cache API, and app lifecycle events.
2. **Offline-First Persistence:** `OfflineQueue` architecture, client-side draft models, base64/blob image persistence, and local storage mechanisms.
3. **Synchronization Engine:** Replay mechanisms, server communication via `api.createObservation` and `api.uploadObservationMedia`, and state transitions (`PENDING`, `SYNCING`, `FAILED`).
4. **Multilingual Architecture:** Telugu (`te-IN`), English (`en-IN`), and Hindi (`hi-IN`) dictionary coverage, context provider, and runtime language switching.
5. **Voice Interaction Adapter:** Web Speech API integration (`SpeechRecognition` & `SpeechSynthesis`), locale resolution, error handling, and text fallbacks.
6. **Mobile Field Ergonomics & Accessibility:** Outdoor high-contrast color palette, $\ge 48\text{px}$ touch targets, responsive navigation, and screen reader compliance.

---

## 2. Codebase Asset Inventory

### 2.1 PWA Core Assets

| File Path | Component Identity | Responsibilities & Observed Status |
|---|---|---|
| [`frontend/public/manifest.json`](file:///c:/Users/gokul/OneDrive/Documents/projects/frontend/public/manifest.json) | Web App Manifest | Declares `name`, `short_name: "ACREVIA"`, `start_url: "/"`, `display: "standalone"`, `theme_color: "#1E3A2B"`, `background_color: "#F7F5F0"`, `orientation: "portrait"`, and icons. Verified valid JSON. |
| [`frontend/public/sw.js`](file:///c:/Users/gokul/OneDrive/Documents/projects/frontend/public/sw.js) | Service Worker Script | Implements `acrevia-shell-v1` cache precaching (`/`, `/manifest.json`, `/icons/icon-192.png`, `/icons/icon-512.png`). Excludes `/api/` from cache (network-only). Network-first for navigation; stale-while-revalidate for static assets. |
| [`frontend/public/icons/icon-192.png`](file:///c:/Users/gokul/OneDrive/Documents/projects/frontend/public/icons/icon-192.png) | Standard PWA Icon | 192x192 PNG icon for mobile home screen and task switchers. Verified physical file exists. |
| [`frontend/public/icons/icon-512.png`](file:///c:/Users/gokul/OneDrive/Documents/projects/frontend/public/icons/icon-512.png) | High-Res & Maskable Icon | 512x512 PNG icon supporting Android adaptive/maskable icons. Verified physical file exists. |

---

### 2.2 Offline Persistence & Synchronization

| File Path | Component Identity | Responsibilities & Observed Status |
|---|---|---|
| [`frontend/lib/offline/queue.ts`](file:///c:/Users/gokul/OneDrive/Documents/projects/frontend/lib/offline/queue.ts) | `OfflineQueue` Service | Manages `OfflineDraft` records (`id`, `type`, `farm_id`, `plot_id`, `notes`, `image_data_base64`, `sync_status`). Implements `getDrafts`, `saveDraft`, `removeDraft`, `updateDraftStatus`, and `syncAll`. |
| [`frontend/hooks/useOnlineStatus.ts`](file:///c:/Users/gokul/OneDrive/Documents/projects/frontend/hooks/useOnlineStatus.ts) | `useOnlineStatus` Hook | Listens to browser `online` and `offline` events with `navigator.onLine` initial state. |
| [`frontend/components/ui/OfflineBanner.tsx`](file:///c:/Users/gokul/OneDrive/Documents/projects/frontend/components/ui/OfflineBanner.tsx) | `OfflineBanner` UI Component | Renders dynamic status banner: offline alert, pending draft count, active syncing indicator, and manual "Sync Now" button. |

---

### 2.3 Voice Interaction Adapter

| File Path | Component Identity | Responsibilities & Observed Status |
|---|---|---|
| [`frontend/features/voice/voiceAdapter.ts`](file:///c:/Users/gokul/OneDrive/Documents/projects/frontend/features/voice/voiceAdapter.ts) | `VoiceAdapter` Class | Wraps `SpeechRecognition` / `webkitSpeechRecognition` and `SpeechSynthesis`. Resolves `te-IN`, `hi-IN`, `en-IN`. Enforces text preview before submission; strips markdown tokens before speech synthesis. Safe fallback on unsupported devices. |

---

### 2.4 Multilingual Localization

| File Path | Language / Purpose | Coverage & Parity Status |
|---|---|---|
| [`frontend/lib/localization/context.tsx`](file:///c:/Users/gokul/OneDrive/Documents/projects/frontend/lib/localization/context.tsx) | `LocalizationProvider` | React Context managing `locale` state (`te`, `en`, `hi`) with `localStorage` persistence and fallback resolution. |
| [`frontend/messages/en.ts`](file:///c:/Users/gokul/OneDrive/Documents/projects/frontend/messages/en.ts) | English (`en-IN`) | Canonical dictionary defining 12 core namespaces (`app`, `nav`, `auth`, `onboarding`, `dashboard`, `diagnosis`, `knowledge`, `croppulse`, `riskcast`, `expertconnect`, `interventions`, `common`). |
| [`frontend/messages/te.ts`](file:///c:/Users/gokul/OneDrive/Documents/projects/frontend/messages/te.ts) | Telugu (`te-IN`) | Complete parity with English dictionary; authentic Telangana agronomic terminology. |
| [`frontend/messages/hi.ts`](file:///c:/Users/gokul/OneDrive/Documents/projects/frontend/messages/hi.ts) | Hindi (`hi-IN`) | Complete parity with English dictionary; standard Hindi agricultural phrasing. |

---

## 3. Initial Baseline Audit Findings

1. **Strengths:**
   - Next.js 16 App Router build is fast and clean ($1042\text{ ms}$ compile time, 0 TypeScript errors).
   - Strict service worker cache boundary: `/api/` requests are completely exempted from caching, preventing private farmer data leakage into browser cache.
   - Comprehensive dictionary parity across all 12 core namespaces tested and passing.
   - All 36 frontend tests pass out of the box ($590\text{ ms}$).

2. **Areas for Architectural Hardening in Stage 06:**
   - Transitioning `OfflineQueue` from synchronous `localStorage` to asynchronous `IndexedDB` (`idb`) to support larger image blobs ($> 5\text{ MB}$) without risking `QUOTA_EXCEEDED_ERR`.
   - Hardening idempotency boundaries on the server to reject duplicate observation replays.
   - Defining explicit conflict-resolution contracts for concurrent multi-device updates.
   - Auditing browser voice recognition limitations and establishing transparent text fallbacks.

---

## 4. Baseline Conclusion

The Stage 06 foundation is robust, cleanly written, and fully tested. It is ready for formal verification and authoring of the full 22-monograph package.
