# ACREVIA — STAGE 06 TECHNICAL GAP & DEBT REGISTER
**Programme:** ACREVIA 14-Stage Finalization Programme  
**Target Stage:** Stage 06 — Vernacular Progressive Web App & Voice Interaction  
**Date:** 2026-11-08  
**Status:** MONITORED & MANAGED

---

## 1. Register Overview & Governance

This register tracks all known limitations, browser compatibility gaps, and technical trade-offs associated with mobile web and PWA technologies in Stage 06. Every identified gap is paired with an active mitigation to prevent operational disruption for smallholder farmers.

---

## 2. Identified Technical Debt & Mitigation Matrix

| Gap ID | Subsystem | Description & Impact | Severity | Current Mitigation | Target Milestone |
|---|---|---|---|---|---|
| **GAP-06-01** | Background Sync | W3C Background Sync API (`PeriodicSyncManager`) is not supported on iOS Safari or Firefox Mobile; background syncing when the browser tab is fully closed cannot be guaranteed. | **MEDIUM** | Immediate foreground synchronization triggers when connection returns; prominent "Sync Now" button rendered in `OfflineBanner`. | **Stage 08** (Field Observability & Telemetry) |
| **GAP-06-02** | Voice Recognition | Mobile browsers (Android Chrome, Safari) utilize cloud-based ASR engines for Telugu/Hindi; speech recognition fails when completely offline. | **MEDIUM** | Transparent status notice informs farmer; input focus immediately transfers to vernacular virtual keyboard; voice is never mandatory. | **Stage 14** (On-Device Edge ML Audio Evaluation) |
| **GAP-06-03** | iOS Installation | iOS Safari does not support the programmatic `beforeinstallprompt` API, preventing a one-tap install banner. | **LOW** | Clear vernacular tooltip instructs iOS users: *"Tap Share -> Add to Home Screen"*. | **Stage 08** (Mobile UX Polish) |
| **GAP-06-04** | Storage Quotas | Aggressive Android OS storage cleaners may purge IndexedDB caches if device storage falls below $200\text{ MB}$. | **LOW** | Storage persistence requested via `navigator.storage.persist()`; high-priority warning displayed if free space $< 100\text{ MB}$. | **Stage 08** (Mobile Storage Governance) |
| **GAP-06-05** | Camera EXIF Stripping | Certain budget OEM camera apps (e.g. Realme, Vivo) strip EXIF metadata when saving pictures through HTML file inputs. | **LOW** | 5-tier spatial hierarchy falls back gracefully to `DEVICE_GPS_CONSENTED` or `PLOT_CENTROID_FALLBACK`. | **Stage 07** (IoT / GPS Spatial Ingestion) |

---

## 3. Residual Risk Assessment

None of the tracked gaps jeopardize data integrity, tenant security, or application usability. All workflows maintain reliable fallbacks.
