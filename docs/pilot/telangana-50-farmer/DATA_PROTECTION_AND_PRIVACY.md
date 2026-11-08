# ACREVIA Data Protection & Privacy Governance Framework
## Operationalizing India's Digital Personal Data Protection Act (DPDP Act, 2023)
**Target Stage:** Stage 08 Remediation (`TASK-S08-01`)  
**Scope:** 50-Farmer Telangana Pilot (Warangal & Nalgonda)  
**Applicable Legislation:** Digital Personal Data Protection Act 2023 (Act No. 22 of 2023), Information Technology Act 2000  

---

## 1. Regulatory Roles & Legal Basis

Under the DPDP Act 2023:
- **Data Fiduciary:** ACREVIA Agricultural Intelligence Platform (Research & Operations Division).
- **Data Principal:** The individual participating smallholder farmer.
- **Data Processor:** Neon Database Inc. (PostgreSQL hosting), Vercel Inc. (Application delivery), AWS (S3 storage).
- **Consent Manager / Facilitator:** Local KVK Extension Personnel and ACREVIA Village Field Assistants.
- **Legal Basis for Processing:** Explicit, affirmative, informed, and unbundled consent under Section 6 of the DPDP Act 2023, delivered in 8th Schedule languages (Telugu, Hindi, and English).

---

## 2. Principle of Data Minimization

ACREVIA collects **only** the data strictly necessary for agricultural decision support and model calibration.

### 2.1 Permitted Data Items
1. **Personal Identity:** Full Name, Phone Number (for OTP authentication & critical disease alerts), Village, Mandal, District.
2. **Agronomic Data:** Plot acreage, crop variety, sowing/transplanting date, soil texture, irrigation type.
3. **Observation Data:** Leaf photographs, symptom descriptions, audio notes, disease severity ratings.
4. **Coarse Geolocation:** Truncated/dithered latitude and longitude for weather forecast retrieval.

### 2.2 Prohibited Data Items (Strictly Disallowed)
- **Aadhaar Numbers:** Never requested, collected, or stored.
- **Bank Account / Credit Details:** Never requested.
- **Land Ownership Title Deeds / Passbook Scans:** Never collected.
- **Facial Images / Biometrics:** Field staff are instructed that photos must contain only plant parts; any accidental human face detected is auto-blurred or rejected.

---

## 3. Geolocation Dithering & Farm Boundary Privacy

Precise farm GPS boundaries could expose smallholder farmers to predatory input dealers or speculative land acquisition. To prevent this:
- **Dithering Transformation:** Raw device GPS coordinates $(\text{Lat}_{\text{raw}}, \text{Lon}_{\text{raw}})$ are truncated to 2 decimal places:
  $$\text{Lat}_{\text{stored}} = \text{round}(\text{Lat}_{\text{raw}}, 2), \quad \text{Lon}_{\text{stored}} = \text{round}(\text{Lon}_{\text{raw}}, 2)$$
- This provides an accuracy radius of $\approx 1.1\text{ km}$—sufficient for Open-Meteo 1-km weather grids and district disease epidemiology while preventing pinpoint identification of the farmer's private plot.

---

## 4. Encryption & Technical Security Controls

1. **In-Transit Protection:** All communications between client PWAs, Vercel edge functions, and backend APIs are enforced via HTTPS using TLS 1.3 with HSTS headers.
2. **At-Rest Protection:**
   - PostgreSQL database tables are encrypted using AES-256 (storage level) and column-level encryption for participant phone numbers.
   - S3 image storage enforces server-side encryption (`AES256` or `aws:kms`).
3. **Multi-Tenant Row-Level Security:** Verified in `backend/tests/test_authorization.py`; farmers are restricted to querying only their own farm records, while KVK scientists are restricted to their assigned district tenant (`warangal-pilot` or `nalgonda-pilot`).
4. **Rate Limiting Anonymization:** Rate limit tracking keys in Redis use SHA-256 hashed identifiers (`rl:acrevia:warangal:ai:anon:<hash[:12]>`), preventing IP address persistence in memory caches.

---

## 5. Farmer Rights & Consent Life-Cycle Management

```
[Consent Granted]  ──> Digital Consent Log Created (Timestamp, Version, Language)
         │
         ├──> [Access Request]   ──> Provide JSON/PDF export of all records
         │
         ├──> [Correction]       ──> Update inaccurate phone number or crop variety
         │
         └──> [Consent Revoked]  ──> Trigger 72-Hour Cascading Data Purge Protocol
```

### 5.1 Right to Withdraw Consent & Cascading Purge Protocol
When a participant requests withdrawal:
1. **Immediate Deactivation:** The participant's credentials are revoked immediately.
2. **Cascading Database Purge:** A background job executes within 72 hours:
   - Deletes personal identifiers from `users` and `farms`.
   - Deletes leaf images from object storage (`s3://acrevia-pilot/observations/*`).
   - Removes queued records from the local PWA IndexedDB via an administrative tombstone event.
3. **Research Anonymization:** Any previously aggregated pathology training statistics (e.g., "Cotton leaf spot confirmed in Warangal") retain no link to the individual.

---

## 6. Grievance Redressal & Contact

The designated Data Protection Officer (DPO) oversees pilot compliance:
- **Data Protection Officer:** ACREVIA Compliance Directorate  
- **Email:** `dpo@acrevia.app`  
- **Postal Address:** ACREVIA Research Foundation, Hyderabad / Warangal, Telangana, India  
- **Statutory Response Time:** Within 48 hours for preliminary response; within 7 business days for resolution.
