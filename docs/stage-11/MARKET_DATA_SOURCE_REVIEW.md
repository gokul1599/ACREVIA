# ACREVIA — Market Data Source Review & Governance
**Focus:** Authorized Government Sources, Fallback Providers, and Data Authenticity

---

## 1. Verified Public & Authorized Data Sources

ACREVIA integrates market data exclusively from transparent, recognized agricultural authorities:

1. **Agmarknet (Directorate of Marketing & Inspection, Ministry of Agriculture & Farmers Welfare, GoI):**
   - *Coverage:* All regulated wholesale markets across India.
   - *Frequency:* Daily post-closure uploads.
   - *Fields:* Market Name, Commodity, Variety, Arrival (Tonnes), Min Price, Max Price, Modal Price.
   - *Format:* JSON / XML API endpoints & daily CSV feeds.
2. **e-NAM (National Agriculture Market):**
   - *Coverage:* Unified electronic trading platform covering 1,361+ mandis.
   - *Fields:* Lot-level e-auction clearing prices, trade volumes, quality parameters.
3. **Telangana State Agricultural Marketing Department (tsmarketing.in):**
   - *Coverage:* Detailed daily arrivals and price boards for all 180+ Telangana market committees (Enumamula, Khammam, Badepally, etc.).
   - *Strengths:* Highly specific local varieties (e.g., *Teja* Chilli, *WGL-44* Paddy).

---

## 2. Ingestion Resilience & Data Integrity Policies

- **Staleness Guard:** If a mandi feed has not updated within 48 hours, observations are flagged as `STALE_PRICE` with observation date prominently displayed.
- **Outlier Detection:** Prices deviating by $> 50\%$ from the 7-day rolling median for that district/commodity are flagged for manual review (`SUSPECT_OUTLIER`).
- **Offline / Local Caching:** In-memory caching and persistent PostgreSQL backup so market comparison queries function even during government portal downtime.
- **No Speculative Synthetic Prices:** If price data is unavailable for a remote market on a particular day, ACREVIA explicitly displays "No reported transactions today" rather than fabricating an interpolated price.
