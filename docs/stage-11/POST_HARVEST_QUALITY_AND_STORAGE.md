# ACREVIA — Post-Harvest Quality & Storage Architecture
**Subsystem:** Pillar D — ACREVIA Quality  
**Primary Objective:** Standardized quality grading, moisture measurement provenance, and storage lot tracking.

---

## 1. Crop-Specific Quality Parameters

Grading standards in ACREVIA conform to AGMARK and BIS standards:

### 1. Cotton:
- **Staple Length (mm):** Short (<24.5 mm), Medium (25–27 mm), Long (27.5–32 mm), Extra Long (>32 mm).
- **Micronaire (fineness):** Premium range 3.8 – 4.2. Low micronaire indicates immature bolls.
- **Trash Content (%):** High trash lowers ginning turnout and market price.
- **Moisture Content (%):** Baseline standard is 8–9%. Above 10% incurs dockage at procurement centers.

### 2. Rice / Paddy:
- **Moisture Content (%):** Procurement standard $\le 17\%$ moisture. Above $17\%$ requires mechanical/sun drying.
- **Foreign Matter (%):** Chaff, weed seeds, stones (max 1–2%).
- **Damaged / Discolored Grains (%):** Affects milling grade and head rice recovery (HRR).
- **Broken Grain Ratio (%):** Critical for market value of premium varieties (e.g. BPT-5204 Samba Mahsuri).

### 3. Red Chilli:
- **Moisture Content (%):** Optimal dry pod moisture is 10–11%. $>12\%$ risks aflatoxin and fungal decay in storage.
- **Color Value (ASTA units):** Higher ASTA reflects deep uniform red pigment.
- **Capsaicin / Pungency (SHU):** E.g., *Teja* variety commands 70,000–90,000 SHU.
- **Pod Damage & Stalk Presence (%):** *Fatki* (white/yellow discolored diseased pods) commands significantly lower rates.

---

## 2. Measurement Provenance & Storage Management

1. **`QualityMeasurement` Entity:**
   - Captures parameter, numeric value, unit, and method:
     - `MEASURED_DIGITAL_SENSOR` (e.g., calibrated pin moisture meter).
     - `VERIFIED_LAB_ASSAY` (e.g., APMC laboratory certificate).
     - `FARMER_VISUAL_ESTIMATE` (self-reported assessment).
   - Prevents unverified visual estimates from being masqueraded as certified lab tests.
2. **`StorageLocation` & `StorageLot`:**
   - Supports:
     - `FARM_ON_PREMISE`: Traditional shed, hermetic bag, or grain bin.
     - `COMMERCIAL_COLD_STORAGE`: Critical for Chilli storage across Warangal and Khammam to preserve color value over 6–10 months.
     - `STATE_WAREHOUSE_CWC_TSWC`: Regulated warehouses issuing negotiable warehouse receipts (e-NWR).
   - Tracks incoming quantity, exit quantity, storage temperature/humidity log, and pest monitoring events.
