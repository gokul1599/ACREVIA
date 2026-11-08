# ACREVIA — SYNCHRONIZATION OBSERVABILITY & DIAGNOSTIC LOGGING
**Programme:** ACREVIA 14-Stage Finalization Programme  
**Target Stage:** Stage 06 — Vernacular Progressive Web App & Voice Interaction  
**Date:** 2026-11-08  
**Status:** SPECIFIED & TESTED (`PASS`)

---

## 1. Observability Imperative: Demystifying Background Sync

When an agricultural application claims to sync data in the background, a lack of visible feedback creates anxiety for smallholder farmers. Did my leaf photo upload? Did the server receive my notes? Can I safely close the browser?

ACREVIA provides complete, multi-tiered synchronization observability.

---

## 2. Farmer Sync Banner & Control Center

Implemented in [`frontend/components/ui/OfflineBanner.tsx`](file:///c:/Users/gokul/OneDrive/Documents/projects/frontend/components/ui/OfflineBanner.tsx):

```
+--------------------------------------------------------------------------+
|  (WifiOff) ఇంటర్నెట్ కనెక్షన్ లేదు. వివరాలు మీ ఫోన్‌లో భద్రపరచబడ్డాయి.   |
+--------------------------------------------------------------------------+
|  (RefreshCw) 2 పరిశీలనలు సర్వర్‌కు పంపడానికి సిద్ధంగా ఉన్నాయి.  [ఇప్పుడే సింక్ చేయండి] |
+--------------------------------------------------------------------------+
|  (CheckCircle2) అన్ని వివరాలు సర్వర్‌లో విజయవంతంగా నమోదయ్యాయి!           |
+--------------------------------------------------------------------------+
```

### 2.1 State Transitions Displayed to Farmers
1. **Offline Mode:** Prominently alerts the farmer that network is unavailable, confirming that all records are saved locally.
2. **Pending Queue Count:** Displays exact count of un-uploaded observations (e.g. *"2 records pending synchronization"*).
3. **Manual Trigger:** Offers an explicit, accessible button ("Sync Now") allowing the farmer to initiate synchronization immediately upon returning to Wi-Fi.
4. **Success Confirmation:** Displays a calming green banner for 4 seconds upon successful transmission.

---

## 3. Diagnostic Queue Telemetry (Privacy-Preserving)

To diagnose synchronization failures in the field without leaking personal data:
- **Tracked Telemetry Metrics:**
  - `queue_depth` (number of pending drafts).
  - `sync_latency_ms` (time taken for payload upload).
  - `http_status` (e.g. 201, 503, 413).
  - `retry_count` (number of attempts).
- **Privacy Protections:**
  - Telemetry NEVER transmits raw foliar photographs, farmer names, or GPS coordinates.
  - Diagnostic logs are stored client-side and only shared with support personnel upon explicit farmer consent.
