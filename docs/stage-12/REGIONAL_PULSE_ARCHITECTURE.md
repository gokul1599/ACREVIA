# ACREVIA — Regional Pulse Architecture (Regional Agricultural Intelligence)
**Subsystem:** Pillar F — ACREVIA Regional Pulse  
**Primary Objective:** A privacy-preserving regional agricultural information system organizing community observations, environmental context, and expert reports into qualified regional signals with zero unsupported outbreak claims.

---

## 1. Domain Purpose & Evidence-Based Philosophy

Regional Pulse provides early awareness of emerging agricultural trends (weather risks, pest inquiries, phenology stages) across Telangana districts (Warangal, Khammam, Suryapet, Karimnagar, Adilabad).

### Anti-Panic & Outbreak Governance Invariants:
1. **Never Make Unsupported Outbreak Claims:** Unverified community chatter, social rumors, or isolated single-farm reports are **strictly prohibited** from being labelled as "outbreaks" or "epidemics".
2. **Confidence Tiers:**
   - `FARMER_REPORT`: Isolated self-reported observation from a single grower.
   - `MULTIPLE_INDEPENDENT`: Confirmed observations from multiple distinct farms ($\ge 3$) within a mandal or district.
   - `AI_ASSISTED`: Multiple CropVision leaf scans corroborating symptom class with high diagnostic confidence.
   - `EXPERT_REVIEWED`: Validated by an ExpertConnect certified agronomist via physical field visit or diagnostic dossier.
   - `OFFICIAL_ADVISORY`: Formally declared by the State Department of Agriculture or PJTSAU.
3. **Outbreak Claim Suppression:**
   - If an unverified user submits a report claiming a "Severe Pest Epidemic" or "Total Crop Failure Outbreak", the text is automatically cleansed/suppressed, and the signal is categorized as `UNVALIDATED_OBSERVATION` until formal expert adjudication.

---

## 2. Privacy-Preserving Geographic Aggregation

```
[Raw Observations & Scans] ──> [Filter & De-duplicate] ──> [Minimum Cohort Check (≥ 3 Farms)] ──> [District / Mandal Signal]
```

### Privacy Rules:
- **No Farm Pinpointing:** Regional Pulse signals are published at the **Mandal** or **District** level. Exact plot GPS boundaries, survey numbers, and farm names are **never** displayed on regional maps.
- **Minimum Farm Threshold:** At least 3 independent farms must report corroborating symptoms within a 14-day rolling window before an aggregate signal is surfaced. Single-farm observations remain private.
