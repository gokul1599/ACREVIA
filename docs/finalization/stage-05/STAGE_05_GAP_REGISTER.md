# ACREVIA — STAGE 05 TECHNICAL GAP & DEBT REGISTER
**Programme:** ACREVIA 14-Stage Finalization Programme  
**Target Stage:** Stage 05 — Farm Action Journal, Observations, Geolocation & Weather  
**Date:** 2026-11-08  
**Status:** MONITORED & MANAGED

---

## 1. Register Overview & Tracking Policy

This register documents all known limitations, architectural trade-offs, external API dependencies, and deferred enhancements identified during Stage 05 verification. Each entry is classified by severity, tracked with concrete mitigations, and mapped to downstream resolution milestones.

---

## 2. Identified Technical Debt & Mitigation Matrix

| Gap ID | Subsystem | Description & Impact | Severity | Current Mitigation | Target Stage for Closure |
|---|---|---|---|---|---|
| **GAP-05-01** | Weather Provider | Open-Meteo free tier imposes a daily ceiling of 10,000 calls. Uncontrolled farm-level polling could exhaust quotas during peak morning advisory hours. | **MEDIUM** | Ingested weather is cached per district for 60 minutes. Multiple farmers within Warangal or Khammam share the same cached hourly reading. | **Stage 07** (IoT & Weather Station Integration) |
| **GAP-05-02** | Geolocation | Some low-cost Android OEM camera apps (e.g., Xiaomi MIUI, Realme) strip EXIF metadata when saving photos to conserve space or enforce device-level privacy. | **LOW** | 5-tier location fallback gracefully steps down to HTML5 browser Geolocation API (`DEVICE_GPS_CONSENTED`) or plot centroid (`PLOT_CENTROID_FALLBACK`). | **Stage 06** (Native PWA Geolocation Capture) |
| **GAP-05-03** | Storage | `LocalStorageProvider` stores images on the local filesystem. While ideal for development and single-server deployments, multi-region horizontal scaling requires cloud bucket replication. | **LOW** | Abstract `StorageProvider` interface is isolated; dropping in S3 or Cloudflare R2 requires updating only configuration settings without code refactoring. | **Stage 11** (DevOps & Multi-Region Cloud Deployment) |
| **GAP-05-04** | Scouting | Multi-image dossiers are currently uploaded sequentially via multipart requests rather than a single atomic batch payload. | **LOW** | Observation entity is created first (`DRAFT` / `SUBMITTED`), and images are attached with transactional integrity; partial failures allow retry without data loss. | **Stage 06** (Offline Batch Sync Queue) |
| **GAP-05-05** | Field Validation | Usability metrics on mud-spattered screens under intense 42°C summer heat in Adilabad require live smallholder field testing. | **LOW** | High-contrast UI ($8.7:1$ contrast) and $48\text{px}$ touch targets deployed; live testing scheduled under Stage 14 field protocol. | **Stage 14** (Real-World Smallholder Validation) |

---

## 3. Residual Risk Assessment

None of the tracked gaps compromise core application security, tenant isolation, or data integrity. The system functions reliably and safely within design parameters.
