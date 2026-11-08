# ACREVIA — STAGE 08 STRIDE SECURITY THREAT MODEL

**Programme:** ACREVIA Stage-Wise Finalization Programme  
**Target Stage:** Stage 08 — Production Hardening, End-to-End Validation & Observability  
**Methodology:** Microsoft STRIDE Threat Modeling Framework  
**Scope:** Full Stack (PWA Client, Edge CDN, FastAPI ASGI, Neon PostgreSQL, ML Engine, S3 Media)  
**Status:** ACTIVE VERIFIED THREAT MODEL  
**Date:** November 2026  

---

## 1. Executive Summary

ACREVIA operates in rural and smallholder agricultural environments where mobile devices may be shared among family members, network connectivity is intermittent, and land parcel data represents proprietary farmer assets. 

This document articulates a formal threat model based on the STRIDE framework (Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, Elevation of Privilege) covering all application tiers, external integrations, and data boundaries.

---

## 2. System Decomposition & Attack Surface

The platform presents six distinct attack surfaces:
1. **Public Web & Edge Surface:** Vercel Edge CDN, Next.js routing, reverse proxy `/api/v1` rewrites.
2. **API & Authentication Surface:** FastAPI endpoints, JWT bearer token validation, password reset flows.
3. **Data Ingestion Surface:** Foliar image uploads, EXIF metadata parsing, CSV/JSON bulk imports.
4. **Database & Vector Surface:** Neon PostgreSQL relational tables, pgvector cosine search embeddings.
5. **Inference & Intelligence Surface:** ONNX Runtime MobileNetV3 classifier, KrishiBrain RAG queries.
6. **Third-Party Integration Surface:** Open-Meteo weather API, S3-compatible cloud object storage.

---

## 3. STRIDE Threat Analysis & Countermeasure Matrix

### 3.1 Spoofing (Identity Deception)
| Threat ID | Threat Description | Attack Vector | Severity | Implemented Countermeasure | Verification Status |
|---|---|---|---|---|---|
| **THR-S-01** | Farmer Account Impersonation | Brute-forcing phone number credentials or intercepting SMS | High | Bcrypt salted password hashing (work factor 12), rate-limiting login attempts, short-lived JWTs (15 min). | **VERIFIED** |
| **THR-S-02** | Fraudulent Agronomist Registration | Unqualified individual claiming expert status to advise farmers | High | Mandatory administrative verification gate (`APPLICATION_SUBMITTED` $\to$ `APPROVED`) requiring university credentials. | **VERIFIED** |
| **THR-S-03** | Weather Provider Spoofing | Man-in-the-middle forging fake weather telemetry to induce false risk alerts | Medium | Outbound HTTPS/TLS 1.3 to verified Open-Meteo API domains; cryptographic payload integrity checks. | **VERIFIED** |

### 3.2 Tampering (Data Modification)
| Threat ID | Threat Description | Attack Vector | Severity | Implemented Countermeasure | Verification Status |
|---|---|---|---|---|---|
| **THR-T-01** | Foliar Image Modification in Transit | Altering disease symptom photos to manipulate ML diagnosis | Medium | SHA-256 cryptographic hash calculated immediately upon receipt and recorded in `observation_media`. | **VERIFIED** |
| **THR-T-02** | Chemical Safety Interval Tampering | Changing Pre-Harvest Interval (PHI) or Re-Entry Interval (REI) | Critical | Hardcoded, versioned CIBRC label database; non-zero validation rules reject unsafe zero-defaults. | **VERIFIED** |
| **THR-T-03** | Silent Alteration of Expert Assessments | Overwriting agronomist diagnosis to avoid liability | Critical | Immutable revision history in `expert_assessment_revisions`; in-place updates strictly prohibited. | **VERIFIED** |

### 3.3 Repudiation (Action Denial)
| Threat ID | Threat Description | Attack Vector | Severity | Implemented Countermeasure | Verification Status |
|---|---|---|---|---|---|
| **THR-R-01** | Denying Expert Diagnosis or Advisory | Agronomist denying they prescribed a hazardous chemical | High | Digital signature with authenticated expert UUID, exact timestamp, and mandatory written rationale. | **VERIFIED** |
| **THR-R-02** | Denying Ground Chemical Application | Farmer denying application date when harvest residue is detected | Medium | Immutable `intervention_records` with timestamp, plot ID, operator identity, and spray equipment log. | **VERIFIED** |
| **THR-R-03** | Denying Consent Revocation | Researcher utilizing data after farmer has revoked consent | High | Centralized `consent_records` table queried dynamically on every research API invocation. | **VERIFIED** |

### 3.4 Information Disclosure (Data Leakage)
| Threat ID | Threat Description | Attack Vector | Severity | Implemented Countermeasure | Verification Status |
|---|---|---|---|---|---|
| **THR-I-01** | Multi-Tenant Cross-Farmer Data Leak | Insecure Direct Object References (IDOR) on farm/plot endpoints | Critical | Server-side ownership verification middleware; attempts return `403 Forbidden` with zero record metadata. | **VERIFIED** |
| **THR-I-02** | Private Plot Coordinate Harvesting | Scraping plot geocoordinates and boundary polygons | High | GPS coordinates strictly withheld from public APIs; researcher exports require anonymization and centroid fuzzing. | **VERIFIED** |
| **THR-I-03** | Secret Key / Token Leakage via Logs | Logging passwords, JWTs, or database credentials in application logs | Critical | Structured logging filters explicitly redact Authorization headers, passwords, and sensitive coordinates. | **VERIFIED** |

### 3.5 Denial of Service (Service Disruption)
| Threat ID | Threat Description | Attack Vector | Severity | Implemented Countermeasure | Verification Status |
|---|---|---|---|---|---|
| **THR-D-01** | Image Decompression Bomb (Pixel Bomb) | Uploading highly compressed multi-gigapixel images to crash memory | High | Strict byte limits (15 MB max), PIL decompressed size checks, Laplacian quality filter aborts invalid files. | **VERIFIED** |
| **THR-D-02** | Database Connection Exhaustion | Flooding endpoints to saturate Neon PostgreSQL connections | High | Neon managed connection pooling (PgBouncer), SQLAlchemy pool pre-ping and bounded queue sizing. | **VERIFIED** |
| **THR-D-03** | ML Inference Overload | Bombarding CPU inference with continuous invalid image payloads | Medium | Fast input validation and Laplacian blur variance filtering reject unprocessable images before model execution. | **VERIFIED** |

### 3.6 Elevation of Privilege (Unauthorized Escalation)
| Threat ID | Threat Description | Attack Vector | Severity | Implemented Countermeasure | Verification Status |
|---|---|---|---|---|---|
| **THR-E-01** | Farmer Escalation to Platform Admin | Modifying JWT payload or role claim in API requests | Critical | Cryptographic HMAC-SHA256 signature validation; server re-verifies user role in database for sensitive routes. | **VERIFIED** |
| **THR-E-02** | Unverified User Claiming Agronomist Cases | Bypassing expert registration gate to claim consult dossiers | Critical | Strict RBAC dependency checking both role membership and `verification_status == 'APPROVED'`. | **VERIFIED** |

---

## 4. Threat Model Sign-Off

All identified STRIDE threat categories are addressed through defense-in-depth controls across client, network, application, and database tiers.

*Reviewed and approved by: Principal Application Security Engineer, DevSecOps Lead, and Lead Architect — ACREVIA Programme.*
