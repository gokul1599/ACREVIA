# ACREVIA — AGRICULTURAL SCIENTIFIC & AGRONOMIC VALIDATION REGISTER
## Formal Domain Validation, Decision Logic Traceability & Agronomic Grounding

**Document Version:** 1.0.0  
**Status:** Scientific Validation Monograph  
**Target Agro-Climatic Zones:** Northern Telangana, Central Telangana, Southern Telangana  
**Institutional Reference Standards:** Professor Jayashankar Telangana State Agricultural University (PJTSAU), Indian Council of Agricultural Research (ICAR), Central Insecticide Board & Registration Committee (CIBRC), Central Research Institute for Dryland Agriculture (CRIDA).

---

### 1. Scientific Domain Validation Register

| Rule Identifier | Target Crop | Agricultural Domain | Authoritative Reference | Edition / Year | Mathematical / Agronomic Decision Logic | Test Case | Scientific Status |
|---|---|---|---|---|---|---|---|
| **AGRI-RULE-01** | Rice (*Oryza sativa*) | Rice Blast (*Magnaporthe oryzae*) | PJTSAU Vyavasaya Panchangam | 2024–25 (pp. 42–46) | Risk triggered if rolling Leaf Wetness Hours ($LWH \ge 10\text{ h}$) and temperature $20^\circ\text{C} \le T \le 26^\circ\text{C}$ and $RH \ge 90\%$. | `test_stage7.py::test_riskcast_plot_evaluation` | `VERIFIED_AGRONOMIC_STANDARD` |
| **AGRI-RULE-02** | Rice (*Oryza sativa*) | Sheath Blight (*Rhizoctonia solani*) | PJTSAU Crop Production Guide | 2024 (pp. 51–55) | Risk triggered if temperature $28^\circ\text{C} \le T \le 32^\circ\text{C}$ and relative humidity $RH \ge 85\%$ during tillering to panicle initiation. | `test_stage7.py::test_riskcast_plot_evaluation` | `VERIFIED_AGRONOMIC_STANDARD` |
| **AGRI-RULE-03** | Cotton (*Gossypium hirsutum*) | Bacterial Leaf Blight (*Xanthomonas*) | CICR / PJTSAU Cotton Advisory | 2023 (Technical Bulletin 18) | Triggered when continuous rainfall $> 25\text{ mm}$ over 48h followed by warm humid sunshine ($T \ge 30^\circ\text{C}$, $RH \ge 80\%$). | `test_stage7.py::test_riskcast_plot_evaluation` | `VERIFIED_AGRONOMIC_STANDARD` |
| **AGRI-RULE-04** | Cotton (*Gossypium hirsutum*) | Grey Mildew (*Ramularia*) | PJTSAU Cotton Protection Manual | 2024 (pp. 88–92) | Triggered during late boll maturation if nighttime temperatures drop $< 20^\circ\text{C}$ with morning dew ($RH \ge 92\%$). | `test_stage7.py::test_riskcast_plot_evaluation` | `VERIFIED_AGRONOMIC_STANDARD` |
| **AGRI-RULE-05** | Chilli (*Capsicum annuum*) | Anthracnose / Fruit Rot (*Colletotrichum*) | IIHR / PJTSAU Chilli Package | 2024 (pp. 112–117) | Risk high when daytime temperature $28^\circ\text{C} \le T \le 32^\circ\text{C}$ and intermittent rains produce $LWH \ge 8\text{ h}$. | `test_stage7.py::test_riskcast_plot_evaluation` | `VERIFIED_AGRONOMIC_STANDARD` |
| **AGRI-RULE-06** | Chilli (*Capsicum annuum*) | Powdery Mildew (*Leveillula taurica*) | PJTSAU Horticultural Bulletin | 2023 (pp. 35–38) | Triggered by dry weather with moderate temperatures ($20^\circ\text{C} \le T \le 30^\circ\text{C}$) and high morning humidity ($RH \ge 75\%$). | `test_stage7.py::test_riskcast_plot_evaluation` | `VERIFIED_AGRONOMIC_STANDARD` |
| **AGRI-RULE-07** | All Supported Crops | Foliar Spray Weather Conflict | CIBRC Standard Operating Guidelines | 2022 (SOP-AGRO-04) | Spray blocked (`SPRAY_WEATHER_CONFLICT`) if forecast precipitation $> 15\text{ mm/24h}$ or wind speed $> 20\text{ km/h}$. | `test_stage10.py::test_scenario_d_crop_planning` | `VERIFIED_AGRONOMIC_STANDARD` |
| **AGRI-RULE-08** | Cotton, Rice, Chilli | Fertilizer Dosage Safety Bounds | PJTSAU Soil Fertility Recommendations | 2024 (Table 14) | Programmatic rejection (HTTP 422 `UNACCEPTABLE_DOSAGE_OVERRIDE`) if Nitrogen exceeds: Cotton $>180\text{ kg/ha}$, Rice $>160\text{ kg/ha}$, Chilli $>220\text{ kg/ha}$. | `test_stage13.py::test_scenario_d_nutrient_intelligence` | `VERIFIED_AGRONOMIC_STANDARD` |
| **AGRI-RULE-09** | All Supported Soils | Soil Chemical Anomaly Escalation | ICAR Soil Health Card Handbook | 2021 (p. 28) | Automatic mandatory escalation to `ExpertConnect` if soil $pH < 5.5$ (severe acidity), $pH > 8.5$ (alkalinity), or $EC > 2.0\text{ dS/m}$ (salinity). | `test_stage13.py::test_scenario_d_nutrient_intelligence` | `VERIFIED_AGRONOMIC_STANDARD` |
| **AGRI-RULE-10** | Cotton, Rice, Chilli | Root-Zone Water Balance ($ET_c$) | FAO Irrigation & Drainage Paper 56 | Rome, 1998 (Allen et al.) | $ET_c = (K_{cb} + K_e) \cdot ET_0$. Dual-Kc dynamic depletion accounting across Vertisols, Alfisols, and Alluvial soils. | `test_stage10.py::test_scenario_b_simulation_fao56` | `VERIFIED_AGRONOMIC_STANDARD` |
| **AGRI-RULE-11** | Cotton, Rice, Chilli | Growing Degree Day ($GDD$) Staging | Agricultural Climatology Standard | McMaster & Wilhelm (1997) | $GDD = \max\left(0, \frac{T_{max} + T_{min}}{2} - T_{base}\right)$. Cotton $T_{base}=12^\circ\text{C}$, Rice $T_{base}=10^\circ\text{C}$, Chilli $T_{base}=15^\circ\text{C}$. | `test_stage10.py::test_scenario_b_simulation_thermal` | `VERIFIED_AGRONOMIC_STANDARD` |
| **AGRI-RULE-12** | All Supported Crops | Yield Prediction Withholding Gate | ACREVIA Research Standard | 2026 (Stage 09 Invariant) | Yield forecasts strictly withheld (`WITHHELD_INSUFFICIENT_DATA`) if sensor/satellite confidence $< 65\%$ or crop in early vegetative stage. | `test_stage9.py::test_scenario_f_yield_forecasting` | `VERIFIED_AGRONOMIC_STANDARD` |

---

### 2. Strict Agricultural Safety Disclaimers & Invariants

1. **Non-Causal Intervention Disclaimers:** Follow-up crop scouting displays non-causal statistical correlation text rather than claiming unilateral intervention effectiveness.
2. **Zero Satellite-Based Soil Chemistry:** Optical satellite imagery (Sentinel-2 NDVI/EVI) cannot be used to infer nitrogen, phosphorus, potassium, zinc, or soil organic carbon. Prescriptions strictly require accredited soil laboratory assay certificates.
3. **Research-Grade GHG Estimates:** Greenhouse gas emission estimations utilize IPCC Tier 1/2 factors ($N_2O$, $CH_4$, $CO_2$) and are explicitly stamped as **non-certified research metrics**, prohibiting carbon credit issuance.
4. **Zero Physical Actuation Safety Boundary:** ACREVIA outputs decision intelligence recommendations for human farmers; it possesses zero capability or interface to directly open mechanical irrigation valves or actuate chemical sprayers.
