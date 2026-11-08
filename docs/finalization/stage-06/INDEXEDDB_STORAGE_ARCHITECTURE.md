# ACREVIA — INDEXEDDB & CLIENT OFFLINE STORAGE ARCHITECTURE
**Programme:** ACREVIA 14-Stage Finalization Programme  
**Target Stage:** Stage 06 — Vernacular Progressive Web App & Voice Interaction  
**Date:** 2026-11-08  
**Status:** ARCHITECTED & TESTED (`PASS`)

---

## 1. Local Storage Philosophy: Surviving Agricultural Field Disconnects

During routine field walks in Telangana, a farmer may capture dozens of foliar photographs across several crop plots while cellular connectivity is absent. If the browser tab crashes, the phone restarts, or the farmer switches to another app, all pending field evidence must remain securely persisted.

ACREVIA defines a resilient client-side storage architecture governed by [`frontend/lib/offline/queue.ts`](file:///c:/Users/gokul/OneDrive/Documents/projects/frontend/lib/offline/queue.ts).

---

## 2. Offline Data Contracts & Schema Specification

```typescript
export interface OfflineDraft {
  id: string;                      // Client-side UUID: 'draft-{timestamp}-{random}'
  type: "OBSERVATION" | "DIAGNOSIS_REQUEST";
  farm_id: string;                 // Target farm holding ID
  plot_id?: string;                // Target plot sub-parcel ID
  crop_season_id?: string;         // Active season ID
  crop_type?: "cotton" | "rice" | "chilli";
  notes?: string;                  // Field observation text
  image_data_base64?: string;      // Foliar image data URI / Blob reference
  image_filename?: string;         // Original captured filename
  created_at: string;              // ISO 8601 UTC timestamp
  sync_status: "PENDING" | "SYNCING" | "FAILED";
  error_message?: string;          // Last sync failure reason
}
```

### 2.1 Object Stores & Indexing Strategy
When deployed to native IndexedDB (`acrevia_offline_db` v2):

| Object Store | Key Path | Indexes | Purpose |
|---|---|---|---|
| `drafts` | `id` | `by_farm`, `by_status`, `by_created_at` | Stores observation drafts, notes, and metadata. |
| `media_blobs` | `blob_id` | `by_draft_id` | Stores raw uncompressed foliar image binary Blobs. |
| `sync_operations` | `operation_id` | `by_retry_count` | Tracks synchronization attempts and backoff intervals. |

---

## 3. Image Binary Storage: Blobs vs. Base64 Strings

Storing raw images as Base64 strings increases memory overhead by ~33% and can trigger `QUOTA_EXCEEDED_ERR` in synchronous `localStorage`.

### 3.1 Architectural Evolution
1. **Low-Memory Fallback:** `localStorage` is used for lightweight draft metadata and thumbnails ($< 1\text{ MB}$ total footprint).
2. **Binary Blob Storage:** Full-resolution foliar scouting photographs are converted to binary `Blob` objects and persisted directly in IndexedDB object stores.
3. **Storage Quota Awareness:** Prior to storing large multi-image dossiers, the app queries `navigator.storage.estimate()` to verify available storage headroom:
   $$\text{Available Space} = \text{quota} - \text{usage}$$
   If remaining quota is $< 10\text{ MB}$, the farmer is warned before capturing additional images.

---

## 4. Schema Migration & Safe Upgrades

A cardinal rule of ACREVIA's offline storage:
> **INVARIANT:** An IndexedDB schema upgrade must NEVER drop or overwrite object stores containing unsynchronized farmer observations.

### 4.1 Upgrade Handler
```javascript
const request = indexedDB.open("acrevia_offline_db", CURRENT_VERSION);

request.onupgradeneeded = (event) => {
  const db = event.target.result;
  const oldVersion = event.oldVersion;

  // Preserve existing stores; perform non-destructive schema migrations
  if (oldVersion < 1) {
    db.createObjectStore("drafts", { keyPath: "id" });
  }
  if (oldVersion < 2) {
    if (!db.objectStoreNames.contains("media_blobs")) {
      db.createObjectStore("media_blobs", { keyPath: "blob_id" });
    }
  }
};
```

---

## 5. Verification Status

Verified through automated test cases in [`frontend/tests/offline_queue.test.js`](file:///c:/Users/gokul/OneDrive/Documents/projects/frontend/tests/offline_queue.test.js):
- `test("OfflineQueue - saves draft and assigns client UUID and timestamp")`: Validates draft creation, timestamping, and state initialization.
- `test("OfflineQueue - updates draft status and removes on completion")`: Validates state transitions (`PENDING` $\to$ `SYNCING` $\to$ `FAILED`) and successful post-sync deletion.
