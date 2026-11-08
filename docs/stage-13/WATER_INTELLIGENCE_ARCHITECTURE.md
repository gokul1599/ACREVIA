# ACREVIA — Water Intelligence Architecture (Pillar B)

**Project:** ACREVIA — Agricultural Intelligence Platform  
**Stage:** 13 — Climate-Resilient & Sustainable Agriculture  
**Focus:** Precision Water Management, Source Inventory, Irrigation Accounting & Water Productivity  
**Target Region:** Telangana-First (Semi-arid Deccan Plateau: Warangal, Khammam, Suryapet, Karimnagar, Adilabad, Nalgonda)  
**Target Crops:** Cotton (*Gossypium hirsutum*), Rice (*Oryza sativa*), Chilli (*Capsicum annuum*)  

---

## 1. Executive Summary & Purpose

Agricultural water management in semi-arid southern India is characterized by severe seasonal groundwater overdraft, erratic monsoon precipitation, and high evaporative demand. The **ACREVIA Water Intelligence Engine** provides an evidence-based, transparent water accounting and decision-support architecture.

### Core Non-Negotiable Invariants:
1. **Zero Hallucinated Water Availability:** Ground and surface water reserves are never fabricated. If borehole recharge or canal release dates are unverified, they are explicitly flagged as unverified estimates or `INSUFFICIENT_DATA`.
2. **Strict Provenance on Pump & Flow Records:** Pump run durations are never converted to volumetric abstractions ($m^3$) without verified pump horsepower (HP), head, and calibrated discharge curves, or physical inline flow-meter records.
3. **Transparent Water Accounting:** Every component in the farm hydrological water balance explicitly identifies whether it was **directly measured** (in-situ telemetry/meter), **modeled** (FAO-56 dual crop coefficient $ET_c$), or **regionally estimated** (IMD gridded rainfall).
4. **No Automated Mechanical Valve Actuation:** ACREVIA provides decision support, audit logs, and scenario simulations; it does not trigger unattended irrigation valve commands that could waterlog crops or burn pumps.

---

## 2. Water Source Inventory & Hydrogeological Schema

Telangana farms typically rely on conjunctive water use spanning deep borewells (tapping fractured granitic and basaltic aquifers), local minor irrigation tanks (*Cheruvulu* under Mission Kakatiya), canal lift irrigation, and on-farm rainwater harvesting ponds (*Panta Kuntalu*).

```
                      +---------------------------------------+
                      |       ACREVIA Farm Water Source       |
                      +---------------------------------------+
                                          |
        +------------------+--------------+-------------+------------------+
        |                  |                            |                  |
+---------------+  +---------------+            +---------------+  +---------------+
|   Borewell    |  |  Canal Minor  |            |   Farm Pond   |  |   Open Well   |
| (Deep Aquifer)|  |  (Command Area|            | (Runoff Catch)|  | (Shallow Dug) |
+---------------+  +---------------+            +---------------+  +---------------+
        |                  |                            |                  |
        v                  v                            v                  v
  Static Water Lvl   Rotational Canal              Storage Capacity    Seasonal Water
  Discharge (LPS)    Release Schedule             Current Water Depth  Table Depth
  Water Quality (EC) Supply Reliability           Evaporation Loss     Recharge Yield
```

### 2.1 Water Source Attributes

| Field Name | Type / Units | Valid Range / Classification | Provenance & Validation Rules |
| :--- | :--- | :--- | :--- |
| `source_type` | Enum | `BOREWELL`, `OPEN_WELL`, `CANAL_OUTLET`, `FARM_POND`, `WATER_TANKER` | Must correspond to verified farm infrastructure. |
| `source_name` | String | Descriptive (e.g., "North Borewell #2") | Mandatory farm-level identifier. |
| `depth_meters` | Float ($m$) | $5.0 - 250.0$ | Required for borewells and open wells; derived from driller log or sounder measurement. |
| `current_static_water_level_m` | Float ($m$) | $0.0 - 250.0$ | Depth from surface to water table. Measured via piezometer or acoustic sensor. |
| `recharge_rate_lpm` | Float ($L/\min$) | $0.0 - 2000.0$ | Yield test recovery rate. If unmeasured, marked `ESTIMATED_REGIONAL_AQUIFER`. |
| `discharge_capacity_lps` | Float ($L/s$) | $0.5 - 50.0$ | Rated discharge under operational pump head. |
| `salinity_ec_dsm` | Float ($dS/m$) | $0.05 - 15.0$ | Measured electrical conductivity. $<0.75$ Good, $0.75-2.0$ Moderate, $>2.0$ High Salinity. |
| `ph` | Float | $4.0 - 10.0$ | Laboratory or calibrated benchtop probe reading. |
| `sodium_adsorption_ratio_sar` | Float | $0.0 - 30.0$ | Computed from $Na^+ / \sqrt{(Ca^{2+} + Mg^{2+})/2}$ to assess sodicity risk. |
| `seasonal_availability` | JSON Object | Monthly boolean map `{"jan": true, ..., "may": false}` | Derived from farmer interview or historical monitoring. |

---

## 3. Irrigation Event Journaling & Metering

Irrigation logs record water application at the individual plot or irrigation zone level.

```
+---------------------------------------------------------------------------------------+
|                              Irrigation Event Pipeline                                |
+---------------------------------------------------------------------------------------+
| 1. Initiation: Date, Start Time, Target Plot, Irrigation Method (Drip/Sprinkler/Flood)|
| 2. Execution Logging: Duration (Hours), In-line Meter Delta (m3) OR Pump Rating (HP)  |
| 3. Sensor Ground-Truth: Soil Moisture @ 15cm & 30cm (Pre-Irrigation vs Post-Irrig)   |
| 4. Volumetric Computation: Total Volume (m3), Equivalent Depth (mm = m3 / Area / 10)  |
| 5. Quality Gate: Validates pump discharge curve vs line pressure; flags anomalies     |
+---------------------------------------------------------------------------------------+
```

### Irrigation Application Methods & Efficiencies:
- **Drip Irrigation (`DRIP`):** Typical application efficiency $\eta_a = 0.85 - 0.95$. Wetted area fraction $f_w \approx 0.3 - 0.5$.
- **Sprinkler Irrigation (`SPRINKLER`):** Application efficiency $\eta_a = 0.70 - 0.80$. Wind drift loss accounted for if wind speed $> 15\text{ km/h}$.
- **Alternate Furrow (`ALTERNATE_FURROW`):** Efficiency $\eta_a = 0.60 - 0.70$. Standard water-saving technique for cotton and chilli.
- **Surface Flood / Basin (`FLOOD`):** Efficiency $\eta_a = 0.45 - 0.60$. Conventional rice paddy or furrow flooding.

---

## 4. Soil Moisture Sensor Telemetry

ACREVIA integrates telemetry from multi-depth capacitive or TDR/FDR soil moisture sensors deployed at three agronomic tiers:

1. **Surface Layer ($15\text{ cm}$):** Rapid evaporation and seed germination zone. High diurnal oscillation.
2. **Active Root Zone ($30\text{ cm}$):** Primary nutrient and moisture uptake zone for Cotton, Rice, and Chilli root masses.
3. **Subsoil / Buffer Zone ($60\text{ cm}$):** Deep percolation reservoir, groundwater recharge interface, and subsoil moisture storage.

```
       Soil Surface
        +-------------------------------------------------------+
        |                0 - 15 cm: Surface Layer               |  <-- Sensor 1 (Diurnal ET, crusting)
        +-------------------------------------------------------+
        |               15 - 30 cm: Active Root Zone            |  <-- Sensor 2 (Primary Water Uptake)
        +-------------------------------------------------------+
        |               30 - 60 cm: Deep Root / Subsoil Buffer  |  <-- Sensor 3 (Percolation / Drought Reserve)
        +-------------------------------------------------------+
```

### Soil Moisture Status Thresholds:
- **Saturation ($\theta_{sat}$):** Pores fully water-filled. Risk of root hypoxia in cotton and chilli; required for flooded lowland rice.
- **Field Capacity ($\theta_{fc}$):** Water held against gravitational drainage ($24-48\text{ h}$ post-saturation). Optimal condition for aerobic crops.
- **Management Allowed Depletion (MAD):** Critical trigger threshold.
  - Cotton: $\text{MAD} = 0.50$ (50% of Total Available Water depleted).
  - Chilli: $\text{MAD} = 0.35$ (Sensitive to moisture stress during flowering/fruit set).
  - Rice (AWD - Alternate Wetting & Drying): Water level drops $15\text{ cm}$ below soil surface before re-flooding.
- **Permanent Wilting Point ($\theta_{pwp}$):** Plants can no longer extract water; permanent cell turgor loss.

---

## 5. Transparent Farm Hydrological Water Balance

The dynamic root-zone water balance is modeled following FAO-56 dual crop coefficient methodology:

$$\Delta S = P_{eff} + I_{net} + CR - ET_c - DP - RO$$

Where:
- $\Delta S$: Change in root zone soil water storage ($mm$).
- $P_{eff}$: Effective rainfall ($mm$) computed via USDA Soil Conservation Service method:
  $$P_{eff} = \begin{cases} \frac{P \times (125 - 0.2 \times P)}{125} & \text{if } P \le 250\text{ mm} \\ 125 + 0.1 \times P & \text{if } P > 250\text{ mm} \end{cases}$$
- $I_{net}$: Net irrigation applied ($mm$) = $I_{gross} \times \eta_a$.
- $CR$: Capillary rise from shallow water tables ($mm$).
- $ET_c$: Crop evapotranspiration under standard conditions ($mm/day$) = $(K_{cb} \times K_s + K_e) \times ET_0$.
- $DP$: Deep percolation beyond effective root zone ($mm$).
- $RO$: Surface runoff ($mm$) computed via SCS Curve Number method based on soil hydrologic group and antecedent moisture condition (AMC II).

### Water Balance Transparency Categorization:
Every water balance snapshot emitted by ACREVIA is assigned a data completeness state:
- `COMPLETED_WITH_VALIDATED_INPUTS`: Direct inline flow meter readings + in-situ soil moisture sensor telemetry + local calibrated weather station data.
- `PARTIALLY_ESTIMATED`: Verified pump runtime with calibrated discharge rating curve + IMD $0.25^\circ$ gridded rainfall + FAO-56 modeled $ET_c$.
- `INSUFFICIENT_DATA`: Missing pump characteristics or lack of rainfall records. The system refuses to output an unverified water balance and demands user input.

---

## 6. Irrigation Scenario Comparison & Simulation

Farmers and agronomists can evaluate water-saving scenarios against current practices:

| Scenario | Water Application Strategy | Projected Water Saving (%) | Projected Yield Impact (%) | Energy / Diesel Saving (INR) |
| :--- | :--- | :--- | :--- | :--- |
| **Baseline (Flood)** | Continuous flooding (Rice) or broad furrow (Cotton/Chilli) | $0.0\%$ | Baseline ($100\%$) | Baseline |
| **Scenario A: Alternate Wetting & Drying (AWD)** | Intermittent flooding in Rice: irrigate when ponded depth drops to $-15\text{ cm}$ | $22\% - 30\%$ | $+1\% \text{ to } -3\%$ (Negligible) | $1,800 - 2,500\text{ /acre}$ |
| **Scenario B: Alternate Furrow Drip** | Drip fertigation at 80% $ET_c$ replenishment (Cotton / Chilli) | $35\% - 45\%$ | $+12\% \text{ to } +18\%$ | $3,200 - 4,500\text{ /acre}$ |
| **Scenario C: Regulated Deficit Irrigation (RDI)** | Mild deficit (60% $ET_c$) during cotton vegetative phase, full replenishment at boll formation | $18\% - 24\%$ | $+2\% \text{ to } +5\%$ (Controlled vegetative vigor) | $1,500 - 2,100\text{ /acre}$ |

---

## 7. Water Productivity & Resource Efficiency Metrics

ACREVIA computes three standardized water productivity indicators:

1. **Physical Water Productivity ($WP_{phys}$):**
   $$WP_{phys} = \frac{Y_{total}\text{ (kg)}}{\text{Total Consumptive Water Use } (m^3)}$$
   - *Target Telangana Benchmarks:*
     - Rice: $0.35 - 0.70\text{ kg}/m^3$
     - Seed Cotton: $0.40 - 0.85\text{ kg}/m^3$
     - Dry Chilli: $0.25 - 0.55\text{ kg}/m^3$

2. **Economic Water Productivity ($WP_{econ}$):**
   $$WP_{econ} = \frac{\text{Gross Revenue (INR)} - \text{Irrigation Operational Costs (INR)}}{\text{Total Consumptive Water Use } (m^3)}$$
   Expressed in $\text{INR}/m^3$.

3. **Irrigation Water Use Efficiency (IWUE):**
   $$IWUE = \frac{Y_{irrigated} - Y_{rainfed}\text{ (kg)}}{\text{Total Irrigation Water Applied } (m^3)}$$

---

## 8. Integration Interfaces & Architectural Boundaries

- **ACREVIA Twin Integration:** Synchronizes real-time soil water depletion ($D_r$) to update root zone moisture state in the digital twin.
- **RiskCast Integration:** Triggers moisture stress and terminal drought alerts when $D_r > \text{MAD}$ during critical crop stages (e.g., flowering/boll filling).
- **Security & Privacy:** Water source locations, static water levels, and borehole capacities are restricted to authorized farm owners and verified advisory staff. Regional water aggregates are strictly anonymized.
