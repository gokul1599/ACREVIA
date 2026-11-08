# KISANVISION — FIELD ROBUSTNESS & GENERALIZATION EVALUATION

**Document Version:** 1.0.0  
**Effective Date:** November 7, 2026  
**Auditor:** Principal Computer Vision Research Scientist & Agricultural AI Specialist  
**Status:** Approved Research Framework  

---

## 1. The Real-World Agricultural Generalization Gap

A pervasive flaw in academic agricultural vision literature is evaluating models exclusively on sanitized datasets with plain gray, white, or black backgrounds (e.g. PlantVillage) and claiming $>98\%$ field readiness.

When such models encounter authentic Telangana smallholder field conditions, accuracy regularly drops by $30\text{--}50\%$ due to:
1. **Intense Tropical Solar Glare:** Mid-day sunlight causes specular reflection on waxy cotton leaves, washing out yellow vein chlorosis.
2. **Dense Canopy Shadows:** Lower leaves suffer from steep illumination gradients and partial occlusion by adjacent weeds.
3. **Severe Motion Blur:** Farmers operating under wind gusts often take blurry hand-held shots.
4. **Bandwidth Compression:** Transmitting photos over 2G/3G rural networks introduces severe 8x8 block DCT compression artifacts.
5. **Varying Camera Sensors:** $50 smartphone camera sensors exhibit chromatic aberration and CMOS thermal sensor noise.

---

## 2. Systematic Perturbation Protocol

The KisanVision Robustness Harness (`ml/evaluation/robustness.py`) defines 6 standardized stress tests:

| Perturbation Benchmark | Physical Field Mechanism | Simulation Methodology | Critical Failure Risk |
| :--- | :--- | :--- | :--- |
| **`direct_solar_glare`** | High-noon direct tropical sunlight (100,000+ lux). | Scaled brightness ($+50\%$) and contrast clipping. | Washes out faint foliar mildew and chlorotic mosaics. |
| **`canopy_shadow`** | Dense inter-row shade and cloud cover. | Non-linear brightness reduction ($-50\%$). | Misclassified as necrotic fungal blight. |
| **`camera_blur`** | Wind gusts and hand tremor during capture. | Gaussian spatial convolution ($r = 2.5\text{ px}$). | Suppresses high-frequency pustules and mites. |
| **`jpeg_compression`** | Low-bandwidth rural network upload (WhatsApp compression). | Re-quantized discrete cosine transform ($Q = 25$). | Introduces block boundary noise masquerading as lesions. |
| **`sensor_noise`** | Low-cost smartphone CMOS sensors at dusk. | Additive zero-mean Gaussian noise ($\sigma = 20$). | Degrades subtle color gradients in nutrient deficiencies. |
| **`leaf_rotation`** | Random leaf angles in field canopy. | Arbitrary in-plane rotation ($45^\circ\text{--}270^\circ$). | Tests rotational invariance of convolutional kernels. |

---

## 3. Strict Scientific Integrity Rules

1. **Synthetic vs Real Field Evidence:**
   Simulated robustness testing must never be equated with genuine in-field clinical trials.
2. **Controlled Background Separation:**
   Any model trained exclusively on laboratory or controlled-background imagery is flagged as:
   `VALIDATED_IN_VITRO_ONLY — UNVERIFIED_IN_FIELD`.
3. **Robustness Threshold for Pilot Deployment:**
   To qualify for Telangana field pilot trials, a model candidate must maintain:
   $$\frac{\text{Perturbed Accuracy}}{\text{Clean Accuracy}} \ge 0.80$$
   across all 6 standardized perturbation benchmarks.
