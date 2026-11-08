# ACREVIA — Agronomic Risk Rule Governance & Rule Catalogue
## Evidence-Backed Agro-Climatic Models for Telangana Target Crops

---

## 1. Rule Governance Framework

Every risk rule executed by RiskCast must adhere to strict scientific governance:
1. **Literature Provenance:** Every rule must trace directly to published research from PJTSAU (Professor Jayashankar Telangana State Agricultural University), ICAR, or CIBRC guidelines.
2. **Phenological Mapping:** Rules do not apply uniformly throughout the crop year; they only trigger during biologically susceptible growth stages.
3. **Compound Environmental Conditions:** Single-variable alerts (e.g., purely high temperature) are avoided. Pathogens require specific confluence of moisture, temperature, and host tissue maturity.
4. **Version Control:** Rules are immutable once versioned (e.g., `COTTON-BLL-v1.0`). If thresholds are refined, a new version is created.
5. **Multilingual Advisories:** Explanations and scouting actions must be pre-translated into Telugu, English, and Hindi.

---

## 2. Target Crop Risk Rule Catalogue

### 2.1 Cotton (*Gossypium hirsutum*)

| Rule Code | Target Pathogen / Pest | Susceptible Growth Stages | Agrometeorological Trigger Criteria | Risk Level | Evidence Citation |
|:---|:---|:---|:---|:---|:---|
| `COT-CLSP-01` | Cercospora Leaf Spot (*Cercospora gossypina*) | Vegetative, Flowering & Squaring, Boll Formation | Temp: 24°C–32°C, RH $\ge 85\%$, Leaf Wetness $\ge 8\text{ h}$, or $\ge 2$ consecutive wet days | `HIGH` | PJTSAU Cotton Disease Management Compendium (2022) |
| `COT-BLW-01` | American / Pink Bollworm (*Helicoverpa armigera* / *Pectinophora*) | Squaring, Boll Formation | Temp: 25°C–34°C, RH: 60%–80%, Intermittent dry spell after rain | `HIGH` | ICAR-CICR Nagpur Technical Bulletin on Bollworm Dynamics |
| `COT-WFL-01` | Whitefly (*Bemisia tabaci*) & Sucking Pests | Vegetative, Squaring | Dry weather, Temp > 32°C, Low RH (< 60%), Wind speed < 12 km/h | `MODERATE` | PJTSAU Integrated Pest Management Bulletin (2023) |

### 2.2 Rice (*Oryza sativa*)

| Rule Code | Target Pathogen / Pest | Susceptible Growth Stages | Agrometeorological Trigger Criteria | Risk Level | Evidence Citation |
|:---|:---|:---|:---|:---|:---|
| `RIC-BLST-01` | Rice Blast (*Magnaporthe oryzae* / *Pyricularia*) | Tillering, Panicle Initiation, Flowering | Temp: 20°C–28°C, RH $\ge 90\%$, Leaf Wetness $\ge 10\text{ h}$, cloudy days | `HIGH` | PJTSAU Rice Disease Guide & ICAR-IIRR Hyderabad Blast Advisory |
| `RIC-SHBL-01` | Sheath Blight (*Rhizoctonia solani*) | Maximum Tillering, Heading | Temp: 28°C–34°C, High RH $\ge 85\%$, high plant density, prolonged water stagnation | `HIGH` | ICAR-NRRI Cuttack Sheath Blight Epidemiology (2021) |
| `RIC-BPH-01` | Brown Plant Hopper (BPH - *Nilaparvata lugens*) | Tillering, Booting, Milking | High humidity (> 80%), Temp 25°C–31°C, warm sultry nights, dense canopy | `HIGH` | PJTSAU BPH Surveillance & ETL Guidelines |

### 2.3 Chilli (*Capsicum annuum*)

| Rule Code | Target Pathogen / Pest | Susceptible Growth Stages | Agrometeorological Trigger Criteria | Risk Level | Evidence Citation |
|:---|:---|:---|:---|:---|:---|
| `CHL-ANTH-01` | Anthracnose / Dieback (*Colletotrichum capsici*) | Flowering, Fruit Set, Ripening | Temp: 26°C–32°C, RH $\ge 80\%$, frequent rain showers or heavy morning dew | `HIGH` | PJTSAU Chilli Production Technology & ICAR-IIHR Bangalore |
| `CHL-PWM-01` | Powdery Mildew (*Leveillula taurica*) | Vegetative, Flowering, Fruiting | Warm dry days (26°C–32°C) followed by humid nights (RH $\ge 70\%$) | `MODERATE` | PJTSAU Plant Pathology Field Bulletin |
| `CHL-THRP-01` | Chilli Thrips (*Scirtothrips dorsalis*) & Leaf Curl | Nursery, Vegetative, Flowering | Extended dry spells, Temp 28°C–35°C, RH < 65% | `HIGH` | ICAR-IIHR Thrips and Murda Disease Management |

---

## 3. Rule Evaluation Logic & Output Contract

When a plot is evaluated:
1. Active season and crop stage are fetched from the database.
2. If crop stage is unknown, rules applicable to general vegetative/flowering stages are evaluated with a qualifying note.
3. Each rule evaluates atmospheric conditions across the past 24 hours (observations) and the upcoming 72 hours (forecasts).
4. For triggered rules, RiskCast compiles:
   - Overall risk level (maximum severity among triggered rules).
   - Specific pathogen/pest predispositions.
   - Preventive, non-chemical scouting guidelines (e.g., "Check lower canopy leaves for water-soaked lesions; avoid excessive nitrogen fertilizer application").
   - Approved KrishiBrain knowledge source references for transparent farmer auditing.
