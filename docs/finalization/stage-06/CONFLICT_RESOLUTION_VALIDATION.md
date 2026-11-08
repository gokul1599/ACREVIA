# ACREVIA — CONFLICT DETECTION & RESOLUTION FRAMEWORK
**Programme:** ACREVIA 14-Stage Finalization Programme  
**Target Stage:** Stage 06 — Vernacular Progressive Web App & Voice Interaction  
**Date:** 2026-11-08  
**Status:** SPECIFIED & VALIDATED (`PASS`)

---

## 1. Multi-Device Agricultural Scenarios

In commercial or collective farming holdings across Telangana, multiple actors frequently interact with the same farm entity:
- **Scenario A:** The farm owner in Warangal updates plot boundary and soil classifications via the web desktop dashboard. Simultaneously, a field worker in the plot records foliar observations offline.
- **Scenario B:** An agronomist advisor reviews an observation and certifies a diagnosis of Rice Blast. Meanwhile, the farmer edits their field notes locally to add symptoms noticed during an evening inspection.

ACREVIA guarantees that concurrent offline work never silently destroys or overwrites verified agronomic records.

---

## 2. Optimistic Concurrency Control (OCC) Architecture

Entity models enforce versioning using monotonic update timestamps:

```mermaid
sequenceDiagram
    participant DeviceA as "Worker Mobile (Offline)"
    participant Server as "ACREVIA Server (Neon DB)"
    participant DeviceB as "Owner Desktop (Online)"

    DeviceA->>DeviceA: Fetch Plot (Version: t1)
    DeviceB->>Server: Update Plot Name (New Version: t2)
    Server-->>DeviceB: Plot Updated to t2
    DeviceA->>DeviceA: Network Disconnects; Record Observations
    DeviceA->>Server: Sync Draft referencing Plot (Expects: t1)
    Server->>Server: Detect Version Mismatch (t2 > t1)
    alt Non-Conflicting Change (Additive Observation)
        Server-->>DeviceA: Auto-Merge: Accept Observation & Re-parent to t2
    else Conflicting Entity Mutation
        Server-->>DeviceA: 409 Conflict: Require User Resolution
    end
```

---

## 3. Conflict Categories & Resolution Policies

| Conflict Scenario | Resolution Rule | Agronomic Justification |
|---|---|---|
| **Additive Field Observations** | **Auto-Merge (No Conflict)** | Observations are chronological timeline nodes; adding a new observation never conflicts with parent plot name updates. |
| **Simultaneous Field Notes Edit** | **Last-Write-Wins (LWW) with Diff Preservation** | Client's latest field observation is preserved; previous text is retained in audit history. |
| **Server Archived / Deleted Plot** | **Orphan Prevention (Attach to Farm Root)** | If a plot was archived while the worker was offline, the observation is automatically re-anchored to `farm_id` with a warning flag: `PLOT_ARCHIVED_FALLBACK`. |
| **Expert Diagnosis Override** | **Server-Authoritative Override** | A certified human agronomist's laboratory diagnosis cannot be overwritten by an offline client draft. |
| **Revoked Farm Permission** | **Quarantine Draft Locally** | If farm membership was revoked while offline, the draft is locked in IndexedDB with an explanation, preventing unauthorized server writes. |

---

## 4. Multilingual User Resolution Prompts

When a conflict requires farmer input, ACREVIA presents an accessible modal in the user's selected language:

- **Telugu (`te`):**  
  *"ఈ క్షేత్ర వివరాలు సర్వర్‌లో మార్చబడ్డాయి. మీ కొత్త పరిశీలనను భద్రపరచడానికి నిర్ధారించండి."*  
  [నా వివరాలను ఉంచు] [సర్వర్ మార్పులను అంగీకరించు]
- **Hindi (`hi`):**  
  *"इस खेत का विवरण सर्वर पर बदल दिया गया है। अपने नए अवलोकन को सुरक्षित करने के लिए पुष्टि करें।"*  
  [मेरा विवरण रखें] [सर्वर परिवर्तन स्वीकारें]
- **English (`en`):**  
  *"This field holding was updated on the server. Confirm to preserve your local observation."*  
  [Keep My Local Version] [Accept Server Updates]
