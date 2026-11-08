# ACREVIA — Security and Privacy Review (Stage 13)

**Project:** ACREVIA — Agricultural Intelligence Platform  
**Stage:** 13 — Climate-Resilient & Sustainable Agriculture  
**Focus:** Data Protection, Tenant Isolation, Hydrogeological Privacy & Access Control  

---

## 1. Threat Modeling & Sensitive Agricultural Data Assets

Agricultural sustainability and resource management involve sensitive farm assets and commercial privacy risks:

1. **Hydrogeological Privacy (High Sensitivity):**
   - *Risk:* Public exposure of borewell locations, static water levels, and discharge yields can trigger competitive groundwater drilling by neighbors, depleting shared fractured-rock aquifers.
   - *Control:* Borehole geographic coordinates, yield rates, and water level measurements are strictly restricted to the registered farm owner and assigned certified agronomists.
2. **Soil Health Laboratory Reports (Medium Sensitivity):**
   - *Risk:* Commercial exploitation by chemical fertilizer vendors targeting farmers with depleted soils.
   - *Control:* Soil test results are sandboxed within the farm tenant domain. Third-party vendor integration requires explicit, granular, time-bound farmer consent.
3. **Environmental & Sustainability Disclaimers (Regulatory & Legal):**
   - *Risk:* Misrepresentation of research-grade greenhouse gas estimates as tradable carbon credits (greenwashing liability).
   - *Control:* Programmatic injection of immutable scientific disclaimers in all API payloads and reports. The database explicitly marks `is_certified = False`.

---

## 2. Role-Based Access Control (RBAC) Matrix

| Endpoint Group | `FARMER` (Owner) | `AGRONOMIST` (Assigned) | `RESEARCHER` (Consented) | `COMMUNITY_USER` | `ADMIN` |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Soil Sampling & Tests** | Full Access (Own Plots) | Read + Lab Ingest | Anonymized Aggregates | No Access | Full Administrative |
| **Water Asset & Telemetry** | Full Access (Own Plots) | Read-Only | Anonymized Watershed | No Access | Full Administrative |
| **Nutrient Prescriptions** | Read (Own Plots) | Review, Modify, Approve| Anonymized Rates | No Access | Full Administrative |
| **Practice Records** | Full Access (Own Plots) | Verify Practices | Anonymized Adoption | View Shared Public | Full Administrative |
| **Resilience Assessments** | Read (Own Plots) | Full Analysis Access | Aggregate Risk Models | No Access | Full Administrative |

---

## 3. Location Minimization & Geospatial Privacy

When research projects or regional watershed dashboards query farm sustainability metrics:
- Coordinates are perturbed using differential privacy spatial jittering ($500\text{ m}$ Gaussian radius).
- Farm boundaries are dissolved into sub-district (Mandal) or watershed hydrological polygons.
- Survey numbers and land revenue identifiers are stripped before ingestion into analytical warehouses.

---

## 4. Input Validation & Defense-in-Depth

- **Pydantic Validation:** All numerical inputs (pH, EC, N-P-K, flow meter deltas) are bounded by physical and physiological realities (e.g., $0.0 \le pH \le 14.0$, $0.0 \le \text{Rainfall} \le 1000\text{ mm}$).
- **SQL Injection Prevention:** SQLAlchemy 2.0 type-safe ORM parameterized queries across all database drivers.
- **Audit Logging:** Every modification to soil tests, water logs, or nutrient prescriptions creates an immutable audit row recording `user_id`, `timestamp`, `ip_address`, and `delta_json`.
