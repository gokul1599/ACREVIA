# ACREVIA — Agricultural Source and Method Governance

**Project:** ACREVIA — Agricultural Intelligence Platform  
**Stage:** 13 — Climate-Resilient & Sustainable Agriculture  
**Focus:** Institutional Authority Registry, Provenance Verification, Usage Permissions & Scientific Dispute Escalation  
**Geographic Priority:** Telangana, India  

---

## 1. Institutional Source Registry

ACREVIA anchors every agronomic algorithm, nutrient threshold, water requirement parameter, and climate baseline to recognized public agricultural research institutions.

```
+-----------------------------------------------------------------------------------------+
|                         Institutional Source Hierarchy                                  |
+-----------------------------------------------------------------------------------------+
| Tier 1: State Agricultural University (Primary Regional Authority)                      |
|         - Professor Jayashankar Telangana State Agricultural University (PJTSAU)        |
|                                            |                                            |
| Tier 2: National Apex Research Councils (Methodological Standards)                      |
|         - Indian Council of Agricultural Research (ICAR)                                |
|         - ICAR-Central Research Institute for Dryland Agriculture (CRIDA, Hyderabad)    |
|         - ICAR-Indian Institute of Rice Research (IIRR, Rajendranagar)                  |
|         - ICAR-Central Institute for Cotton Research (CICR, Nagpur)                     |
|         - ICAR-Indian Institute of Soil Science (IISS, Bhopal)                          |
|         - ICAR-National Bureau of Soil Survey and Land Use Planning (NBSS&LUP)          |
|                                            |                                            |
| Tier 3: National Geospatial & Hydro-Meteorological Authorities                          |
|         - India Meteorological Department (IMD) / Pune Climate Data Services            |
|         - Central Ground Water Board (CGWB) & Telangana State Ground Water Dept         |
|         - Central Water Commission (CWC)                                                |
+-----------------------------------------------------------------------------------------+
```

### 1.1 Registered Institutional Authorities

| Authority Code | Organization Name | Domain of Authority | Key Documents Referenced |
| :--- | :--- | :--- | :--- |
| `PJTSAU` | Prof. Jayashankar Telangana State Agricultural University | Crop Package of Practices, Local Varieties, Telangana Critical Nutrient Levels | *Vyavasaya Panchangam (Annual Farm Almanac)*, *Package of Practices for Kharif/Rabi Crops* |
| `ICAR_CRIDA` | Central Research Institute for Dryland Agriculture | Contingency Crop Planning, Drought Adaptation, Moisture Conservation | *District Agriculture Contingency Plans for Telangana (33 Districts)* |
| `ICAR_IIRR` | Indian Institute of Rice Research | Rice Agronomy, Alternate Wetting & Drying, Salinity Tolerance | *Rice Production Technology Compendium* |
| `ICAR_CICR` | Central Institute for Cotton Research | Cotton High-Density Planting (HDPS), Pink Bollworm IPM | *CICR Technical Bulletins on Rainfed and Irrigated Cotton* |
| `ICAR_IISS` | Indian Institute of Soil Science | Standard Soil Analytical Procedures, Micronutrient Assessment | *Methods of Soil Analysis for Soil Health Card Scheme* |
| `IMD` | India Meteorological Department | Climatological Normals, Gridded Weather Data, Agro-Advisory | *30-Year Climatological Tables (1991-2020)*, *Agromet Field Unit (AMFU) Advisories* |
| `CGWB` | Central Ground Water Board | Aquifer Geometry, Ground Water Assessment, Dynamic Resources | *Ground Water Resources of Telangana State*, *Aquifer Mapping (NAQUIM) Reports* |

---

## 2. Measurement Provenance & Method Validation Rules

Every numerical record in the system carries an explicit `MeasurementProvenance` metadata block:

```json
{
  "source_type": "ACCREDITED_LABORATORY",
  "organization_code": "PJTSAU_SOIL_LAB",
  "certificate_number": "SL-HYD-2026-0941",
  "method_standard": "WALKLEY_BLACK_1934",
  "analyst_id": "TECH_4102",
  "verification_status": "VERIFIED_OFFICIAL",
  "measured_at": "2026-10-15T09:30:00Z"
}
```

### Analytical Method Standardization Rules:
- **Soil Organic Carbon:** Must specify `WALKLEY_BLACK` or `DRY_COMBUSTION_ELEMENTAL`. Remote sensing approximations are prohibited from entering soil measurement tables.
- **Available Phosphorus:** Must specify `OLSEN_BICARBONATE` for neutral/alkaline soils ($pH \ge 6.5$) or `BRAY_KURTZ_NO1` for acid soils ($pH < 6.5$).
- **Available Potassium:** Must specify `AMMONIUM_ACETATE_FLAME_PHOTOMETRY`.
- **Soil Moisture Telemetry:** Must specify sensor model, frequency, factory calibration curve vs soil-specific calibration curve.

---

## 3. Handling Scientific Conflicts & Precedence Rules

When institutional recommendations differ (e.g., national ICAR guideline vs state PJTSAU guideline):

1. **Precedence Rule:** State Agricultural University (`PJTSAU`) recommendations supersede national guidelines for crop varieties, sowing windows, and fertilizer split schedules in Telangana.
2. **Conservative Safeguard Rule:** If one institution recommends a higher chemical pesticide/fertilizer dose and another recommends a lower dose, ACREVIA defaults to the **lower, environmentally conservative dose** pending human agronomist review.
3. **Transparent Divergence Citation:** Where significant divergence exists, the system notes the alternative view with explicit citations in the KrishiBrain knowledge retrieval card.

---

## 4. Scientific Dispute Escalation Protocol

If an accredited laboratory result, soil analysis, or agronomic prescription is disputed by a farmer, certified advisor, or institutional researcher:

1. **Dispute Filing:** User submits an escalation via `POST /api/v1/nutrient/dispute` or `POST /api/v1/soil/dispute` attaching supporting evidence.
2. **Automated Audit Freezing:** The disputed record is marked `UNDER_INVESTIGATION` and excluded from algorithmic baseline computations.
3. **Expert Agronomist Panel Routing:** The ticket is routed through `ExpertConnect` to an agronomist panel with verified PJTSAU/ICAR credentials.
4. **Resolution Audit Trail:** The panel issues an approval, modification, or invalidation with signed rationale. The full audit trail is preserved in the database.
