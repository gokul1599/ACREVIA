# ACREVIA — Testing and Scientific Validation Plan (Stage 13)

**Project:** ACREVIA — Agricultural Intelligence Platform  
**Stage:** 13 — Climate-Resilient & Sustainable Agriculture  
**Focus:** Scientific Soundness, Algorithmic Accuracy, Edge-Case Verification & Security Integrity  

---

## 1. Test Architecture & Validation Framework

Stage 13 verification follows a six-scenario scientific test harness executed via `pytest` and `Node.js`:

```
+-----------------------------------------------------------------------------------------+
|                              Stage 13 Scientific Test Suite                             |
+-----------------------------------------------------------------------------------------+
| Scenario A: Soil Health & Laboratory Provenance Verification                            |
| Scenario B: Water Resource Inventory & Dual-Crop Coefficient Water Balance              |
| Scenario C: Climate Hazard Exposure & Phenological Vulnerability Window                 |
| Scenario D: Governed Nutrient Prescriptions & Dosage Safeguard Rejections               |
| Scenario E: Sustainable Practice Tracking & Research-Grade GHG Accounting               |
| Scenario F: Multi-Dimensional Resilience Assessment & Evidence Quality Score            |
| Security Suite: Tenant Boundary Isolation, Coordinate Privacy, RBAC Safeguards         |
+-----------------------------------------------------------------------------------------+
```

---

## 2. Test Scenario Details & Acceptance Criteria

### 2.1 Scenario A: Soil Health & Analytical Provenance
- **Test Objective:** Verify accredited soil sample ingestion, laboratory metadata validation, and spatial sampling density warnings.
- **Inputs:** Soil sample taken from a 5-acre plot with 2 composite cores ($<1$ core per 2.5 acres).
- **Expected Results:**
  - Soil sample created with valid unique `sample_code`.
  - System flags `INSUFFICIENT_SPATIAL_COVERAGE` warning due to low sampling density.
  - Lab test result stored with full `MeasurementProvenance` JSONB object.
  - Longitudinal delta correctly calculates SOC difference between consecutive tests.

### 2.2 Scenario B: Precision Water Management & Telemetry
- **Test Objective:** Verify water source registration, volumetric flow meter conversion, and transparent water balance accounting.
- **Inputs:** Borewell source ($120\text{ m}$ depth), drip irrigation event ($44\text{ m}^3$ applied over 1.0 acre), in-situ moisture sensor reading at $15\text{ cm}$ and $30\text{ cm}$.
- **Expected Results:**
  - Computed depth equals $10.87\text{ mm}$ ($44\text{ m}^3 / 4046.86\text{ m}^2 \times 1000$).
  - Water balance snapshot correctly balances inputs and outputs.
  - Accounting status marked `COMPLETED_WITH_VALIDATED_INPUTS`.

### 2.3 Scenario C: Climate Hazard Exposure & Vulnerability
- **Test Objective:** Test climatological baseline retrieval and phenological vulnerability scoring during reproductive phases.
- **Inputs:** Cotton crop at $75\text{ DAS}$ (Flowering/Boll formation) facing forecast $T_{max} = 39.5^\circ\text{C}$ and 16 consecutive rainless days.
- **Expected Results:**
  - Hazard detected: `DRY_SPELL` and `HEAT_STRESS`.
  - Severity level: `CRITICAL`.
  - Vulnerability score $\ge 0.75$.
  - Recommended intervention matches PJTSAU protocol (1% $KNO_3$ foliar spray).

### 2.4 Scenario D: Governed Nutrient Prescriptions & Safeguards
- **Test Objective:** Validate soil-test-driven N-P-K split scheduling and programmatic rejection of excessive fertilizer dosages.
- **Inputs:** Soil test showing low N ($210\text{ kg/ha}$), low P ($14\text{ kg/ha}$), medium K ($220\text{ kg/ha}$).
- **Expected Results:**
  - Recommended rates adjusted upward by 25% for N and P.
  - Generated split schedule conforms to PJTSAU 4-stage split for cotton.
  - Malicious / erroneous attempt to prescribe $300\text{ kg } N/\text{ha}$ is rejected with HTTP 422 `UNACCEPTABLE_DOSAGE_OVERRIDE`.
  - Anomaly soil sample ($pH = 4.8$) automatically generates an `ExpertConnect` review ticket.

### 2.5 Scenario E: Sustainable Practices & Research GHG Accounting
- **Test Objective:** Validate farm practice logging, empirical SOC record keeping, and IPCC Tier 1/2 emissions calculation.
- **Inputs:** Rice paddy with 2.0 acres under Alternate Wetting & Drying (AWD) with $100\text{ kg}$ applied synthetic N and $40\text{ L}$ diesel pump consumption.
- **Expected Results:**
  - Practice record logged with `GREEN_MANURE` or `AWD_IRRIGATION`.
  - Empirical SOC stored; satellite or synthetic estimation rejected.
  - GHG calculation returns $CH_4$, $N_2O$, and $CO_2$ breakdown with AWD scaling factor ($SF_w = 0.52$).
  - Scientific disclaimer banner present in output payload; `is_certified` is strictly `False`.

### 2.6 Scenario F: Agricultural Resilience Engine
- **Test Objective:** Verify multi-dimensional scoring, evidence quality metric calculation, and scenario simulation.
- **Inputs:** Farm plot with verified soil test ($C_1 = 1.0$), verified water metering ($C_2 = 1.0$), AWS climate telemetry ($C_3 = 1.0$), verified practices ($C_4 = 1.0$), and balanced nutrition ($C_5 = 1.0$).
- **Expected Results:**
  - $EQS \ge 0.85$, category: `HIGH_CONFIDENCE_EMPIRICAL`.
  - Overall resilience score computed as weighted sum of 5 dimensions.
  - Scenario simulation of regenerative package demonstrates $+25\text{ to }+40$ point resilience improvement.

### 2.7 Security & Tenant Isolation Tests
- **Test Objective:** Confirm cross-farmer unauthorized data tampering is blocked with HTTP 403 / 404.
- **Expected Results:** User A cannot view or log soil samples, irrigation events, or borewell details for User B's plot.
