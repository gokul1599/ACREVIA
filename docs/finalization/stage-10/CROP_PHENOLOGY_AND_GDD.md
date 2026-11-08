# ACREVIA — CROP PHENOLOGY & GROWING DEGREE DAYS (GDD) SPECIFICATION
## Thermal Time Modeling, Phenological Stage Transitions & Telangana Triad Parameters

**Document Identifier:** ACREVIA-SPEC-ST10-004  
**Target Subsystem:** ACREVIA Simulate / Phenology Engine  
**Classification:** Agronomic Process Model Specification  
**Status:** Implemented & Verified in Production  

---

### 1. Mathematical Formulation of Thermal Time

Crop development is driven primarily by accumulated thermal energy rather than calendar days. ACREVIA employs the standard modified sinusoidal Growing Degree Day (GDD) formulation bounded by lower base temperatures and upper biological cutoff temperatures:

$$GDD = \max\left(0, \frac{T^*_{\max} + T^*_{\min}}{2} - T_{\text{base}}\right)$$

Where:
- $T^*_{\max} = \min\left(T_{\text{observed\_max}}, T_{\text{upper}}\right)$
- $T^*_{\min} = \max\left(T_{\text{observed\_min}}, T_{\text{base}}\right)$
- If $T^*_{\max} < T_{\text{base}}$, then $GDD = 0$.

Cumulative thermal accumulation from sowing date $t_0$ to current time $t_n$ is:

$$\text{Cumulative GDD} = \sum_{t=t_0}^{t_n} GDD_t$$

---

### 2. Telangana Triad Crop Parameters & Phenological Stages

The thermal parameters and stage transition thresholds are calibrated specifically for Telangana agro-climatic conditions in consultation with Professor Jayashankar Telangana State Agricultural University (PJTSAU) recommendations:

#### A. Cotton (*Gossypium hirsutum*)
- **Base Temperature ($T_{\text{base}}$):** $12.0^\circ\text{C}$
- **Upper Temperature Threshold ($T_{\text{upper}}$):** $35.0^\circ\text{C}$
- **Phenological Stages & GDD Thresholds:**

| Stage Index | Phenological Stage | Cumulative GDD Range ($^\circ\text{C}\cdot\text{d}$) | Typical Duration (Telangana Kharif) | Key Agronomic Vulnerabilities |
|---|---|---|---|---|
| **C1** | Emergence & Seedling | $0 - 120$ | $5 - 10$ days | Damping off, sucking pests (Thrips) |
| **C2** | Square Formation (Squaring) | $121 - 500$ | $35 - 45$ days | Square shedding due to moisture stress |
| **C3** | Flowering (Bloom) | $501 - 950$ | $55 - 75$ days | High water requirement, Whitefly/Aphids |
| **C4** | Boll Formation & Filling | $951 - 1600$ | $80 - 120$ days | Bollworm attack, severe drought sensitivity |
| **C5** | Boll Opening & Bursting | $1601 - 2100$ | $125 - 150$ days | Rain-induced fiber discolouration |
| **C6** | Senescence & Termination | $> 2100$ | $155 - 180$ days | Stalk residue management |

#### B. Rice (*Oryza sativa* — Medium Duration Cultivars, e.g., Telangana Sona RNR 15048)
- **Base Temperature ($T_{\text{base}}$):** $10.0^\circ\text{C}$
- **Upper Temperature Threshold ($T_{\text{upper}}$):** $35.0^\circ\text{C}$
- **Phenological Stages & GDD Thresholds:**

| Stage Index | Phenological Stage | Cumulative GDD Range ($^\circ\text{C}\cdot\text{d}$) | Typical Duration | Key Agronomic Vulnerabilities |
|---|---|---|---|---|
| **R1** | Nursery & Transplanting | $0 - 250$ | $20 - 25$ days | Submergence mortality, root shock |
| **R2** | Active Tillering | $251 - 650$ | $25 - 45$ DAT | Stem borer, blast, zinc deficiency |
| **R3** | Panicle Initiation & Booting | $651 - 1100$ | $50 - 75$ DAT | Water deficit causing spikelet reduction |
| **R4** | Anthesis & Flowering | $1101 - 1450$ | $80 - 95$ DAT | Floret sterility if $T_{\max} > 35^\circ\text{C}$ |
| **R5** | Grain Filling (Milky / Dough) | $1451 - 1900$ | $100 - 120$ DAT | Brown planthopper (BPH), neck blast |
| **R6** | Physiological Maturity | $> 1900$ | $125 - 135$ DAT | Lodging, pre-harvest grain sprouting |

#### C. Chilli (*Capsicum annuum* — e.g., Teja, Byadgi types in Khammam/Warangal)
- **Base Temperature ($T_{\text{base}}$):** $15.0^\circ\text{C}$
- **Upper Temperature Threshold ($T_{\text{upper}}$):** $35.0^\circ\text{C}$
- **Phenological Stages & GDD Thresholds:**

| Stage Index | Phenological Stage | Cumulative GDD Range ($^\circ\text{C}\cdot\text{d}$) | Typical Duration | Key Agronomic Vulnerabilities |
|---|---|---|---|---|
| **P1** | Nursery & Seedling | $0 - 220$ | $30 - 35$ days | Damping off, viral vectors |
| **P2** | Vegetative Establishment | $221 - 600$ | $20 - 40$ DAT | Thrips, mites, root rot in heavy black soil |
| **P3** | Flower Bud & Flowering | $601 - 1050$ | $45 - 75$ DAT | Severe blossom drop if $T_{\max} > 35^\circ\text{C}$ or dry wind |
| **P4** | Fruit Set & Development | $1051 - 1650$ | $80 - 120$ DAT | Anthracnose / Dieback (*Colletotrichum*) |
| **P5** | Fruit Ripening & Flush 1 | $1651 - 2150$ | $125 - 150$ DAT | Sunscald, fruit borer |
| **P6** | Subsequent Flush Pickings | $> 2150$ | $155 - 210$ DAT | Soil exhaustion, secondary mite flare-up |

---

### 3. Thermal Stress Warning Triggers

When observed or forecasted temperatures exceed crop physiological tolerances, the phenology engine triggers immediate risk flags to prevent irreversible yield loss:

1. **Cotton High-Temperature Shedding Alert:**
   - *Condition:* $T_{\max} \ge 38.0^\circ\text{C}$ for $\ge 3$ consecutive days during Flowering/Boll development.
   - *Advisory:* Maintain light, frequent irrigation to facilitate canopy evaporative cooling; inspect for early square drop.

2. **Rice Anthesis Sterility Alert:**
   - *Condition:* $T_{\max} \ge 35.0^\circ\text{C}$ during Flowering stage (10:00 to 14:00 window).
   - *Advisory:* Maintain 3–5 cm water ponding depth in paddy field to buffer microclimate temperatures and protect pollen viability.

3. **Chilli Blossom Drop Alert:**
   - *Condition:* Daily diurnal variation $\Delta T = (T_{\max} - T_{\min}) > 18^\circ\text{C}$ combined with $RH_{\min} < 30\%$ during flowering.
   - *Advisory:* Irrigate immediately in early morning; avoid excessive nitrogen application during peak heat flushes.
