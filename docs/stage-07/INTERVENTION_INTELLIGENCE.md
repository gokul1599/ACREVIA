# ACREVIA — Intervention Intelligence & Outcome Tracking
## Traceable Farm Action Journaling & Longitudinal Crop Health Monitoring

---

## 1. System Vision & Objective

Intervention Intelligence closes the loop between diagnostic detection and real-world farm outcomes. It provides smallholder farmers with a structured, digital action logbook to record inputs and operations, subsequently evaluating visual and physiological changes over time.

```
+-----------------------------------------------------------------------------------+
|                        1. DIAGNOSIS OR RISKCAST ALERT                             |
|   - CropPulse AI or Expert confirms e.g., Chilli Leaf Curl / Thrips               |
+-----------------------------------------+-----------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
|                         2. FARMER INTERVENTION RECORD                             |
|   - Category: BIOLOGICAL | CHEMICAL | CULTURAL | IRRIGATION | FERTILIZER          |
|   - Trade Name & Active Ingredient (e.g., Neem Oil 1500ppm / Spinosad 45% SC)     |
|   - Application Dosage & Dilution Rate per Acre                                   |
|   - Application Method (Foliar Spray, Soil Drench, Pheromone Trap, Pruning)       |
|   - Pre-Harvest Interval (PHI) & Re-Entry Interval (REI) Guidance                 |
+-----------------------------------------+-----------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
|                  3. FOLLOW-UP OBSERVATION & VISUAL COMPARISON                     |
|   - Day +3 to Day +14: Farmer captures new foliar images with CropPulse           |
|   - High-resolution side-by-side visual progression                               |
|   - Image Quality verification (Sharpness, Illumination consistency)              |
+-----------------------------------------+-----------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
|                         4. OUTCOME EVALUATION ENGINE                              |
|   - Status: IMPROVING | STABLE | WORSENING | INCONCLUSIVE                         |
|   - Confounding Variables Documented (Rain washout, Heatwave, Nitrogen surge)     |
|   - Correlation vs. Causation Guardrail: Prevents False "Cure" Claims             |
+-----------------------------------------------------------------------------------+
```

---

## 2. The Correlation vs. Causation Guardrail

A fundamental danger in agricultural software is claiming that a pesticide or biostimulant "cured" a crop issue simply because symptoms improved 5 days later. In open-field ecosystems, dozens of confounding variables govern crop health:
- A sudden drop in humidity may halt fungal sporulation regardless of the spray.
- Natural predator populations (e.g., ladybird beetles, parasitoid wasps) may have collapsed the pest population.
- Rainfall immediately following application may have washed off the formulation.
- Incomplete coverage may have left untreated pest reservoirs on lower leaf surfaces.

### Scientific Guardrail Policy
ACREVIA enforces strict semantic integrity:
1. The platform **never** displays statements such as: *"Product X cured your Rice Blast."*
2. The platform reports observed temporal progression:
   > *"Follow-up observation on Plot [Plot Name] indicates disease lesion stagnation and healthy new vegetative growth. Note: Environmental factors (reduced rainfall and lower relative humidity) and soil moisture conditions also contributed to changing field pressure."*
3. Every outcome report includes an explicit breakdown of **Confounding Variables**.

---

## 3. Intervention Categorization & Data Model

| Category | Typical Telangana Actions | Required Tracking Fields |
|:---|:---|:---|
| `BIOLOGICAL` | *Trichoderma viride*, *Pseudomonas fluorescens*, Neem oil, Beauveria bassiana | Agent name, CFU/concentration, preparation time, expiry date |
| `CHEMICAL` | CIBRC registered insecticides, fungicides, bactericides | Trade name, active ingredient, dosage per acre, spray volume (litres), PHI days |
| `CULTURAL` | Hand weeding, removal of infected shoots (rogueing), sticky traps, mulching | Operation type, labour hours, disposal method of infected material |
| `IRRIGATION` | Drip fertigation, flood irrigation, furrow drainage | Source (borewell/canal), duration, depth/volume |
| `FERTILIZER` | Urea, DAP, MOP, micronutrient zinc/boron foliar spray | Formulation, quantity (kg/acre), basal vs. top-dressing |

---

## 4. Outcome Status Definitions

- `IMPROVING`: New leaf emergence is symptom-free; existing necrotic lesions have dried, stabilized margins; insect counts decreased below ETL.
- `STABLE`: Lesions have not expanded, but no vigorous new growth is observed; pest counts static.
- `WORSENING`: Lesions expanded into systemic blight; chlorosis or wilting spreading; pest infestation moved from vegetative to reproductive organs.
- `INCONCLUSIVE`: Follow-up image has inconsistent lighting/angle, or interval too brief (< 48 hours) to observe physiological plant response.
