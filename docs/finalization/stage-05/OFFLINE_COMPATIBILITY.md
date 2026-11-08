# ACREVIA — OFFLINE COMPATIBILITY & STAGE 06 INTERFACE CONTRACT
**Programme:** ACREVIA 14-Stage Finalization Programme  
**Target Stage:** Stage 05 — Farm Action Journal, Observations, Geolocation & Weather  
**Date:** 2026-11-08  
**Status:** ARCHITECTED & CONTRACT VERIFIED (`PASS`)

---

## 1. Upstream Readiness for Stage 06

In rural Telangana, smallholder fields frequently sit in cellular dead zones where 4G/5G signal drops completely. While Stage 06 formally delivers the Offline-First PWA and service worker synchronization engine, Stage 05 must establish stable data contracts, idempotent endpoints, and conflict-free data structures that guarantee seamless offline operation.

---

## 2. Client-Side Offline Schema (IndexedDB Contract)

During offline scouting walks, mobile clients persist observation records to browser IndexedDB before synchronization:

```typescript
// Stage 06 Offline Ingestion Contract
interface OfflineObservationRecord {
  client_id: string;             // Client-generated UUIDv4
  farm_id: string;               // Target farm holding ID
  plot_id?: string;              // Target plot parcel ID
  crop_season_id?: string;       // Active season ID
  captured_at: string;           // ISO 8601 UTC timestamp
  notes: string;                 // Farmer observations / notes
  symptom_tags: string[];        // Selected tags (e.g. ['leaf_spot', 'chlorosis'])
  geolocation?: {
    lat: number;
    lon: number;
    accuracy_meters: number;
    provenance: 'DEVICE_GPS_CONSENTED' | 'FARMER_ENTERED';
  };
  media_blobs: {
    blob_id: string;
    blob: Blob;
    mime_type: string;
    view_type: 'WHOLE_PLANT' | 'UPPER_LEAF' | 'LOWER_LEAF' | 'STEM' | 'FRUIT';
    is_primary: boolean;
  }[];
  sync_status: 'PENDING_UPLOAD' | 'SYNCING' | 'SYNCED' | 'CONFLICT';
}
```

---

## 3. Idempotent Synchronization & Replay Safety

To prevent duplicate records when intermittent connections drop mid-upload:
1. **Client-Generated UUIDs:** The client generates a persistent `client_id` (UUIDv4). If a POST request times out but was partially received by the server, subsequent replays identify the existing record and update rather than duplicate.
2. **SHA-256 Deduplication on Media:** The server computes `SHA-256` of incoming binary streams. If a foliar image was already persisted during an interrupted attempt, the server returns the existing media reference immediately.

---

## 4. Conflict Resolution Strategy

When multiple devices or offline drafts update the same entity:

| Scenario | Resolution Rule | Agronomic Justification |
|---|---|---|
| **Field Notes Edit** | Last-Write-Wins (LWW) based on client timestamp | Farmer's latest observation note reflects updated field perception. |
| **Observation Creation** | Additive (New Timeline Node) | Every scouting walk represents a distinct temporal event; never merge observations. |
| **Pathology Diagnosis** | Server-Authoritative Override | Edge ONNX predictions are preliminary; certified agronomist or server ensemble models hold canonical authority. |

---

## 5. Mobile Storage Budget Management

Mobile browsers enforce strict storage quotas on IndexedDB (often bounded to 100 MB before prompting user permission).
- Stage 05 images captured in the field are compressed on the client before queuing:
  - Max dimension: $1600\text{px} \times 1600\text{px}$.
  - JPEG Quality: $85\%$.
  - Target size per image: $250\text{ KB} - 450\text{ KB}$.
- Maximum offline queue ceiling: 100 pending observations (~40 MB total storage), safely below browser quota limits.
