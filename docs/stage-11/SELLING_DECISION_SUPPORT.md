# ACREVIA — Selling Decision Support & Insurance Evidence Package
**Focus:** Comparative Mandi Scenario Modeling and Verified Crop Loss Documentation

---

## 1. Selling Decision Support Workflow

ACREVIA provides comparative economic clarity without making speculative or illegal price guarantees:

### Decision Comparison Factors:
1. **Local Farm-Gate vs. Primary Mandi vs. Secondary Hub:**
   - *Farm Gate:* Zero transport cost, but typically 10–15% discount to mandi modal price; risk of inaccurate local trader weights.
   - *Nearby Mandi (e.g. Suryapet, 25 km):* Moderate transport cost (₹35/Qtl), standard mandi cess (1%), lower transit loss.
   - *Major Hub (e.g. Warangal Enumamula, 95 km):* Higher modal price, higher buyer competition, but higher transport (₹110/Qtl), higher hamali, and risk of delay.
2. **Net Realization Matrix:**
   $$\text{Estimated Net Inflow} = (\text{Quantity} \times \text{Expected Mandi Price}) - \text{Total Transport Cost} - \text{Mandi Cess} - \text{Weighing/Hamali}$$
3. **Moisture Dockage Penalty Estimation:**
   - Mandis deduct weight or bid price for moisture above statutory thresholds (e.g., Rice $>17\%$, Cotton $>9\%$).
   - ACREVIA displays the estimated dockage cost vs. the cost of 1-day drying.

---

## 2. Insurance Evidence Package (PMFBY / Relief Support)

When adverse weather (hail, unseasonal rainfall, localized flooding) damages crops during harvest or late season, farmers need audit-proof records for PMFBY (Pradhan Mantri Fasal Bima Yojana) and state disaster relief:

### Structured Evidence Package Components:
1. **Farm & Plot Identifiers:** GeoJSON polygon, survey/khata number, crop season, sowing date.
2. **Recorded Weather Anomaly:** Time-stamped precipitation, temperature, wind gusts from RiskCast / Open-Meteo.
3. **Field Observations:** CropVision diagnostic scans, expert review records from ExpertConnect.
4. **Estimated Loss Quantity:** Planned yield vs. actual harvested yield from HarvestSessions.
5. **Cryptographic Integrity Hash:** SHA-256 hash across the JSON evidence bundle to verify it has not been modified post-generation.
