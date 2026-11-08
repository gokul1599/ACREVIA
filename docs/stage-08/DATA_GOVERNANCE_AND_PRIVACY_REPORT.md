# ACREVIA — DATA GOVERNANCE & PRIVACY REPORT
## Data Inventory, Purpose Limitation, DPDPA 2023 Alignment & Research Ethics Framework

**Platform Identity:** ACREVIA — Agricultural Intelligence Platform  
**Target Region:** Telangana, India  
**Applicable Legal Framework:** Digital Personal Data Protection Act (DPDPA 2023, India)  
**Evaluation Date:** November 2026  
**Auditor:** Principal Data Governance & Privacy Architect  
**Governance Status:** VERIFIED COMPLIANT & ETHICALLY GROUNDED  

---

## 1. Executive Summary & Privacy Principles

ACREVIA collects agricultural, geospatial, foliar photographic, and personal user data to deliver crop disease diagnosis, risk intelligence, and expert agronomic advice.

In accordance with ethical agricultural technology principles:
1. **Farmers Own Their Data:** Agricultural data generated on a farm belongs to the cultivating farmer.
2. **Explicit Purpose Limitation:** Consenting to use the diagnosis app does **not** grant blanket permission to use images for open-source AI training.
3. **Data Minimization:** No national identification numbers (Aadhaar, PAN), land ownership titles, or sensitive financial bank records are collected.
4. **Transparent Data Lifecycle:** Farmers retain the right to export records or request complete account erasure.

---

## 2. Granular Agricultural Data Inventory

| Data Category | Specific Elements Collected | Sensitivity Level | Primary Business Purpose | Storage Location | Retention Period |
|---|---|---|---|---|---|
| **Account Identity** | Full name, phone number, hashed password, preferred language | High (PII) | User authentication & SMS alerts | `users` table (Neon PostgreSQL) | Duration of active account + 90 days |
| **Geographic Context** | State (Telangana), district, mandal, village centroid | Medium | Weather mapping & KVK extension routing | `farms` table | Retained with farm holding |
| **Spatial Plot Data** | Plot acreage, soil type, irrigation source | Low | Agronomic risk calculations | `plots` table | Retained with plot holding |
| **Crop Records** | Crop species (Cotton/Rice/Chilli), sowing date, growth stage | Low | Phenological disease rule matching | `crop_seasons` table | Retained for multi-season history |
| **Foliar Imagery** | High-resolution plant leaf photographs | Medium | Computer vision diagnosis & triage | Private object storage (`backend/storage/uploads/`) | Retained with observation |
| **Voice Recordings** | Temporary audio stream (transcribed to text) | Medium | Voice-assisted query processing | Memory buffer (discarded immediately after transcription) | Transcripts stored in `knowledge_queries` |
| **Expert Records** | Clinical assessment notes, IPM recommendations | Medium | Farmer decision support & recordkeeping | `expert_assessments` table | Permanent agronomic record |
| **Audit Logs** | Action type, timestamp, user UUID, correlation ID | Low | Security auditing & fraud prevention | `audit_logs` table | 365 days rolling window |

---

## 3. Purpose Limitation & Informed Consent Lifecycle

Consent is captured granularly in `consent_records`:
- **Consent Type `CORE_SERVICE`:** Mandatory to provide authentication, diagnosis, and risk alerts.
- **Consent Type `EXPERT_REVIEW_DATA_SHARING`:** Explicit opt-in when escalating a case to an external agronomist, authorizing transmission of foliar photographs and farm location to the reviewer.
- **Consent Type `RESEARCH_DATASET_CONTRIBUTION`:** Strictly optional opt-in allowing de-identified foliar photos to be included in agricultural pathology research benchmarks.

---

## 4. Research Data Separation & De-Identification Protocol

Foliar photographs captured in the field contain embedded metadata that could inadvertently reveal farmer identity or precise GPS home coordinates.

### 4.1 Automated EXIF Stripping
Before any observation media is committed to disk or cloud storage:
- All EXIF metadata (GPS latitude/longitude tags, camera serial numbers, device timestamps) is scrubbed using Pillow (`img.save(strip_exif=True)`).
- The file is renamed to a cryptographic SHA-256 hash digest.

### 4.2 Research Dataset Quarantining
- Observation images marked for research contribution are isolated in a separate `research_staging` repository.
- No direct database joins exist between public ML benchmarks and private farmer identity records.

---

## 5. Farmer Rights & Regional Legal Alignment (DPDPA 2023)

### 5.1 Right to Correction & Erasure
Farmers can request account and farm data deletion through their profile settings:
- **Live Database Erasure:** Cascades across `farms`, `plots`, `crop_seasons`, `observations`, and `media_files`.
- **Honest Backup Disclosure:** As documented in our technical runbooks, automated database point-in-time snapshots retain encrypted backups for a 30-day retention cycle, after which older snapshot blocks expire automatically.

### 5.2 Multilingual Consent Notices
Consent dialogues are rendered in native Telugu, English, and Hindi, avoiding convoluted legal legalese and explaining data usage in simple rural terminology.

---

## 6. Data Governance Verdict

ACREVIA implements responsible data governance, purpose-bounded data collection, and rigorous privacy engineering.

**Data Governance Verdict:** **PASSED — ALIGNED WITH ETHICAL AGRI-TECH & DPDPA PRINCIPLES.**
