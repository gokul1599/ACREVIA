# ACREVIA — STAGE 07 TECHNICAL DEBT, GAPS & ENHANCEMENT REGISTER
## AGRICULTURAL RISK INTELLIGENCE, EXPERTCONNECT & INTERVENTION OUTCOME JOURNAL

**Product:** ACREVIA — Enterprise Agricultural Intelligence Platform  
**Stage:** Stage 07 — RiskCast Engine, ExpertConnect & Intervention Outcome Management  
**Geography:** Telangana, India (Warangal, Khammam, Karimnagar, Nalgonda, Suryapet, Adilabad)  
**Target Crops:** Cotton (*Gossypium hirsutum*), Rice (*Oryza sativa*), Chilli (*Capsicum annuum*)  
**Status:** ACTIVE VERIFIED REGISTER  
**Date:** November 2026  

---

## 1. Executive Summary

This register catalogs all tracked technical debt, non-critical architectural limitations, and operational roadmap items identified during the formal Stage 07 verification and testing cycle. Stage 07 successfully verified and operationalized:
1. **RiskCast Engine:** Deterministic rule evaluation using PJTSAU thresholds, derived leaf wetness hours, multi-factor environmental indices, and discrete risk scoring (`LOW`, `MODERATE`, `HIGH`, `CRITICAL`, `INSUFFICIENT_EVIDENCE`).
2. **Alert Management:** State machine transitions, in-app alert generation, and strict 72-hour deduplication keys (`farm:plot:rule:date`).
3. **ExpertConnect:** Agronomist registry, administrative credential verification (`APPLICATION_SUBMITTED` $\to$ `APPROVED`), multi-stream evidence dossiers, differential diagnoses, IPM strategy, CIBRC label compliance, and immutable revision history.
4. **Intervention Outcome Journal:** Chemical, biological, cultural, mechanical, and nutrient intervention logging, PHI/REI safety countdowns, follow-up photo comparisons, and legally binding non-causal agronomic disclaimers.

Every item in this register is categorized by severity, impact, mitigation strategy, and target resolution stage. None of the listed items block production readiness or violate core architectural invariants.

---

## 2. Tracked Gap & Debt Matrix

| ID | Category | Description | Severity | Impact | Current Mitigation / Workaround | Target Milestone |
|---|---|---|---|---|---|---|
| **GAP-07-01** | Micro-climate Ingestion | Canopy-level microclimate sensor integration (physical leaf wetness sensors, Campbell Scientific/Decagon) | Low | Weather risk relies on 1-km gridded Open-Meteo model and mathematical LWH derivation | High-precision mathematical LWH derivation using Campbell & Norman dewpoint depression model + relative humidity $\ge 90\%$ threshold | Stage 12 / Stage 14 (IoT Pilot) |
| **GAP-07-02** | External Notifications | Push notification / SMS gateway (Govt. e-Kisan / CDAC) and WhatsApp Business API delivery | Medium | Risk alerts are currently delivered via in-app notification center and dashboard streams | In-app alerts with persistent database records, unread badge counters, and 72-hour deduplication keys | Stage 10 (System Integrations) |
| **GAP-07-03** | Tele-Consultation | Synchronous real-time WebRTC audio/video consultations between farmer and agronomist | Low | Consultations are asynchronous structured dossiers with photos, telemetry, and audio notes | High-fidelity asynchronous multi-stream evidence dossiers with voice note playback and annotated image carousels | Stage 11 (Farmer Engagement) |
| **GAP-07-04** | Regulatory Compliance Sync | Automated real-time scraper/sync with CIBRC official gazette for newly banned/restricted formulations | Low | Chemical safety rules are periodically seeded from official CIBRC & PJTSAU packages of practices | Versioned database tables with strict non-zero PHI/REI safety defaults and administrative update tools | Annual Regulatory Review |
| **GAP-07-05** | Image Comparison Vision | Automated computer vision diffing for before/after intervention foliar damage segmentation | Low | Visual comparison is currently presented side-by-side with slider and manual agronomist scoring | High-resolution side-by-side comparison slider with metadata timestamping and zoom controls | Stage 09 / Future ML Sprint |
| **GAP-07-06** | Soil Sensor Integration | Real-time soil moisture and electrical conductivity (EC) telemetry ingestion | Low | Nutrient and moisture interventions rely on farmer-reported observations and gridded soil data | Farmer-logged journal entries with soil texture selection and manual test report uploads | Stage 12 (Sensor Hardware) |

---

## 3. Detailed Analysis of Tracked Items

### 3.1 GAP-07-01: Canopy Micro-climate vs. Derived Gridded Meteorological Data
- **Context:** Plant pathologies such as Chilli Anthracnose (*Colletotrichum capsici*) and Rice Blast (*Magnaporthe oryzae*) depend on micro-scale free moisture on leaf cuticles (Leaf Wetness Duration).
- **Current State:** ACREVIA calculates LWH dynamically from hourly Open-Meteo temperature and relative humidity streams using the peer-reviewed Campbell & Norman dewpoint depression threshold model:
  $$\text{LWH} = \sum_{t=1}^{24} \mathbb{I}\left(\text{RH}_t \ge 90\% \lor (T_t - T_{d,t}) \le 1.8^\circ\text{C}\right)$$
- **Residual Risk:** In densely planted chilli or flood-irrigated rice canopies, canopy humidity can remain higher than 2-meter ambient weather predictions by 10–15%, potentially leading to slight underestimation during marginal transition periods.
- **Safety Margin:** ACREVIA applies conservative safety padding: if ambient RH exceeds 85% for more than 4 consecutive hours during flowering/pod development, the risk score is elevated to `MODERATE` with an advisory note instructing ground scouting.

### 3.2 GAP-07-02: Multi-Channel Alert Dispatch (SMS & WhatsApp)
- **Context:** Smallholder farmers in rural Telangana may not have continuous 4G data coverage or may not open the PWA application daily.
- **Current State:** Alerts are generated and persisted in Neon PostgreSQL (`risk_alerts` table) with deduplication hashing (`farm:plot:rule:date`), surfaced on the farmer dashboard, CropPulse timeline, and offline IndexedDB cache upon network sync.
- **Planned Enhancement:** In Stage 10, an asynchronous background task queue (Celery/Redis or serverless event bridge) will dispatch high-priority and critical alerts via Telco SMS (CDAC / Sandes / MSG91) and WhatsApp Business Cloud API in Telugu and Hindi.

### 3.3 GAP-07-03: Asynchronous Dossiers vs. Synchronous Tele-Consultations
- **Context:** Farmers occasionally request direct voice/video interaction with university experts.
- **Evaluation:** Asynchronous structured dossiers were deliberately chosen as the primary architecture for three scientific reasons:
  1. *Connectivity Resilience:* 2G/3G network conditions in rural agricultural mandals frequently drop synchronous WebRTC video streams.
  2. *Agronomist Bandwidth:* Telangana extension officers and university agronomists manage hundreds of plot cases; asynchronous review allows batched triage, deep literature cross-referencing, and differential diagnosis formulation.
  3. *Auditability & Liability:* Real-time unrecorded phone advice creates liability risks; asynchronous signed assessment records provide an immutable legal audit trail.
- **Roadmap:** Audio voice notes are fully supported in Stage 07 dossiers; live video scheduled appointments will be introduced in Stage 11 as an optional secondary tier.

### 3.4 GAP-07-04: CIBRC Pesticide Gazette Automated Updates
- **Context:** The Central Insecticide Board & Registration Committee (CIBRC) periodically updates banned, restricted, and approved chemical formulations under the Insecticides Act, 1968.
- **Current State:** ACREVIA implements a static, curated, and versioned database of CIBRC-approved formulations specific to Cotton, Rice, and Chilli in Telangana, cross-verified with PJTSAU Vyavasaya Panchangam (2024–2025). Missing PHI/REI values strictly reject zero-defaults and trigger mandatory human safety review.
- **Planned Enhancement:** Development of a scheduled ingestion worker that parses weekly CIBRC gazette publications and flags updated maximum residue limits (MRL) or revised label restrictions for agronomist confirmation.

---

## 4. Invariant Verification Sign-Off

The technical debts listed above do not compromise the foundational safety invariants verified in Stage 07:
- [x] **No Unverified Chemical Prescriptions:** No automated AI engine ever writes a pesticide dosage without human agronomist certification.
- [x] **No False Safety Defaults:** Missing Pre-Harvest or Re-Entry Intervals are never defaulted to 0 days.
- [x] **Strict Non-Causal Ground Tracking:** Crop recovery observations explicitly display statutory multi-factorial disclaimers.
- [x] **Zero Alert Storms:** 72-hour deduplication keys strictly prevent repeated identical warnings.
- [x] **Full Tenant Isolation:** Farm, plot, and expert consult records are partitioned by tenant with role-based access control.

---

*Verified by Principal Agricultural Software Architect, Senior Plant Pathologist, and Lead Backend Engineer — ACREVIA Programme, November 2026.*
