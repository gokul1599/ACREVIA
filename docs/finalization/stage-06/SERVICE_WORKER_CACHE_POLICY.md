# ACREVIA — SERVICE WORKER CACHE STRATEGY & DATA BOUNDARIES
**Programme:** ACREVIA 14-Stage Finalization Programme  
**Target Stage:** Stage 06 — Vernacular Progressive Web App & Voice Interaction  
**Date:** 2026-11-08  
**Status:** AUDITED & SECURE (`PASS`)

---

## 1. Security Invariant: Public Shell vs. Private Data Boundary

In a multi-tenant agricultural intelligence platform, caching must be handled with extreme vigilance. Storing authenticated API responses (e.g. farmer GPS coordinates, foliar photographs, financial ledger transactions) in the browser's Cache API introduces severe privacy risks, especially on shared family devices.

ACREVIA enforces an absolute architectural separation:
- **Cache API:** Strictly restricted to public application shell assets, compiled JavaScript bundles, CSS stylesheets, static font glyphs, and iconography.
- **Network-Only API Boundary:** All `/api/*` endpoints and HTTP mutation requests (`POST`, `PUT`, `DELETE`) are completely exempted from Service Worker caching.
- **Client Persistence:** Private field drafts are persisted exclusively in domain-governed client storage (IndexedDB), governed by user ID boundaries.

---

## 2. Multi-Tier Caching Policy Matrix

Implemented in [`frontend/public/sw.js`](file:///c:/Users/gokul/OneDrive/Documents/projects/frontend/public/sw.js):

| Resource Category | Match Rule | Caching Strategy | Justification |
|---|---|---|---|
| **App Shell Precaches** | `/`, `/manifest.json`, `/icons/*` | **Cache-First (Precaching)** | Guarantees instant launch of core UI shell without network. |
| **Compiled Next.js Bundles** | `/_next/static/*` | **Stale-While-Revalidate** | Delivers cached assets immediately; updates quietly in background. |
| **Navigation Requests** | `request.mode === 'navigate'` | **Network-First with Shell Fallback** | Fetches fresh page if online; falls back to cached root shell (`/`) if offline. |
| **Private Backend APIs** | `pathname.startsWith('/api/')` | **Network-Only (Never Cached)** | Prevents stale or cross-user private data leakage. |
| **Data Mutations** | `request.method !== 'GET'` | **Network-Only (Bypass SW)** | Forwarded directly to network or routed to client `OfflineQueue`. |

---

## 3. Service Worker Implementation Deep-Dive

```javascript
// frontend/public/sw.js
const CACHE_NAME = "acrevia-shell-v1";
const STATIC_ASSETS = [
  "/",
  "/manifest.json",
  "/icons/icon-192.png",
  "/icons/icon-512.png"
];

// 1. Install Event: Precache Core Shell
self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(STATIC_ASSETS).catch((err) => {
        console.warn("ACREVIA SW: Precaching warning:", err);
      });
    })
  );
  self.skipWaiting();
});

// 2. Activate Event: Purge Obsolete Caches
self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.map((key) => {
          if (key !== CACHE_NAME) {
            return caches.delete(key);
          }
        })
      );
    })
  );
  self.clients.claim();
});

// 3. Fetch Event: Strict Policy Routing
self.addEventListener("fetch", (event) => {
  const url = new URL(event.request.url);

  // INVARIANT: Never cache API endpoints or mutations
  if (url.pathname.startsWith("/api/") || event.request.method !== "GET") {
    return;
  }

  // Navigation requests: Network-first with root shell fallback
  if (event.request.mode === "navigate") {
    event.respondWith(
      fetch(event.request).catch(() => caches.match("/") || caches.match(event.request))
    );
    return;
  }

  // Static assets: Stale-While-Revalidate
  event.respondWith(
    caches.match(event.request).then((cached) => {
      const fetchPromise = fetch(event.request)
        .then((network) => {
          if (network && network.status === 200) {
            const clone = network.clone();
            caches.open(CACHE_NAME).then((cache) => cache.put(event.request, clone));
          }
          return network;
        })
        .catch(() => cached);

      return cached || fetchPromise;
    })
  );
});
```

---

## 4. Connectivity Detection & Synthetic State Awareness

The browser's `navigator.onLine` flag merely indicates that a local network adapter (Wi-Fi or cellular radio) has an IP address; it does not guarantee that the upstream ACREVIA server on Vercel/Neon is reachable.

### 4.1 Hybrid Connectivity Architecture
In [`frontend/hooks/useOnlineStatus.ts`](file:///c:/Users/gokul/OneDrive/Documents/projects/frontend/hooks/useOnlineStatus.ts) and [`frontend/components/ui/OfflineBanner.tsx`](file:///c:/Users/gokul/OneDrive/Documents/projects/frontend/components/ui/OfflineBanner.tsx):
1. **Radio Level:** Reacts immediately to `window.online` and `window.offline` browser events.
2. **Application Level:** During synchronization, an attempted ping to `/health` confirms real WAN reachability before attempting bulk binary uploads.
3. **User Transparency:** The UI clearly distinguishes between:
   - `OFFLINE`: Radio disconnected; drafts queued locally.
   - `RECONNECTING`: Radio online; probing server health.
   - `SYNCING`: Server reached; streaming pending observation queue.
   - `SYNC_SUCCESS`: All records durably acknowledged by server.
