# KISANVISION — DATASET AND MODEL STRATEGY

**Document Version:** 1.0.0  
**Status:** Approved for Stage 1 Baseline  
**Scope:** Computer Vision Data Ingestion, Image Collection Protocol, Model Architecture Benchmarking & Evaluation Matrix  
**Host Hardware Constraint Awareness:** AMD Ryzen 5 5500U, 5.86 GB RAM, AMD Radeon Integrated Graphics (No CUDA), 325 GB Free Storage  

---

## 1. Candidate Agricultural Datasets Evaluation

Every candidate dataset is evaluated across real-world field criteria rather than idealized laboratory accuracy.

| Dataset Name | Official Source / Publisher | Crops & Pathologies Covered | Approximate Verified Samples | Image Capture Conditions | Geographic Relevance | License & Permitted Usage | Known Limitations | Field Deployment Suitability |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **PlantVillage** | Hughes & Salathé (Penn State University / EPFL); `https://plantvillage.psu.edu` | Pepper (Chilli), Cotton (Limited), Rice (Not covered) | 54,303 images across 38 crop-disease pairs | Controlled lab setup: detached leaves on uniform plain white/grey cardboard under studio lighting | Global / North American baseline | CC-BY 4.0 (Open academic and commercial attribution) | Complete absence of background clutter, shadows, overlapping leaves, and field weeds. Models trained exclusively on PlantVillage collapse on real-field smartphone photos. | **LOW (Pre-training / Feature Extraction Only)** |
| **PlantDoc** | Singh et al. (IIT Delhi); `https://github.com/pratikkayal/PlantDoc-Dataset` | Rice, Pepper (Bell/Chilli), Cotton (Limited classes) | 2,598 images across 13 plant species, 27 classes | In-field, natural lighting, variable focal distance, background clutter, mobile cameras | India & Global web scrape | MIT License (Permissive commercial & research) | Modest class sample size (~50–150 images per class); contains label noise and web-scraped artifacts that require manual deduplication. | **MEDIUM-HIGH (Fine-tuning & Benchmarking)** |
| **Rice Leaf Diseases Dataset (UCI / Kaggle)** | UCI Machine Learning Repository / Mendeley Data | Rice: Bacterial Leaf Blight, Rice Blast, Brown Spot | ~120 to 1,500 samples (depending on curated variant) | In-field field photography, varying sunlight and leaf orientations | South / Southeast Asia | CC-BY 4.0 / Public Domain | Small dataset size; classes limited to 3 major diseases; lacks rare conditions (False Smut, Tungro). | **MEDIUM (Baseline Evaluation)** |
| **Cotton Weed and Disease Image Set** | Mendeley Data / ICAR Research Archive | Cotton: Bacterial Blight, Grey Mildew, Leaf Reddening, Healthy | ~2,200 curated field photographs | Real agricultural field plots in India (Maharashtra / Telangana) | Central & Southern India | CC-BY 4.0 | Skewed class distribution; requires balancing via albumentations. | **HIGH (Core Training Asset)** |
| **Telangana In-Field Curation (KisanVision Target)** | KisanVision Partnered Extension Collection Protocol | Cotton, Rice, Chilli (Targeting 18 verified local classes including *Thrips parvispinus*) | Target: 6,000 verified images (2,000 per crop) | In-situ smartphone photos taken by extension workers under morning, noon, and overcast lighting | Telangana Agro-Ecological Zones | Proprietary Research Dataset with DPDPA-compliant farmer consent | Progressive collection over 16-week cycle; initially zero baseline samples. | **HIGHEST (Primary Production Target)** |

---

## 2. In-Field Image Collection & Governance Protocol

To overcome laboratory bias and build a research-grade model, KisanVision institutes a standardized collection protocol for field agents and farmers.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                   FIELD IMAGE INGESTION & PIPELINE PROTOCOL                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  [ STEP 1: Consent & Farm Context Capture ]                                 │
│  - Telugu/English explicit consent: Research vs. Diagnostic-only            │
│  - Crop, hybrid/variety name, days after sowing (DAS), Mandal ID            │
│                                      │                                      │
│                                      ▼                                      │
│  [ STEP 2: Client-Side Quality Screening (OpenCV) ]                         │
│  - Laplacian variance > 120 (Blur filter)                                   │
│  - Exposure histogram within [40, 220] (No severe blowout/underexposure)    │
│  - Minimum leaf bounding area > 25% of image frame                          │
│                                      │                                      │
│                                      ▼                                      │
│  [ STEP 3: Cryptographic De-duplication & Metadata Stripping ]              │
│  - Perceptual Hash (pHash) + SHA-256 collision check                        │
│  - EXIF GPS stripped; replaced by anonymized Plot UUID                      │
│                                      │                                      │
│                                      ▼                                      │
│  [ STEP 4: Double-Blind Agronomist Annotation ]                             │
│  - Primary Pathologist Diagnosis + Confidence Rating                        │
│  - Secondary Pathologist Verification (if disagreement -> Senior Panel)     │
│                                      │                                      │
│                                      ▼                                      │
│  [ STEP 5: Farm-Leakage-Free Stratified Data Partitioning ]                 │
│  - Split rule: Partitioning strictly by FARM_ID (Not image ID)              │
│  - Distribution: Train (70%), Validation (15%), Test (15%)                  │
│                                      │                                      │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.1 Critical Invariant: Farm-Level Leakage Prevention
In standard computer vision benchmarks, random image splitting allows multiple photos of the same leaf taken from different angles to leak across both training and test sets, artificially inflating test accuracy by 25–40%.  
**Mandatory KisanVision Rule:** Partitioning must be **Group-Stratified by `farm_id`**. All images originating from Farm $A$ must reside entirely within either the Train, Validation, or Test set.

---

## 3. Computer Vision Model Architecture Strategy

### 3.1 Model Candidate Evaluation Under Host Hardware Constraints

*Audited Environment:* AMD Ryzen 5 5500U (6 Cores / 12 Threads), 5.86 GB RAM (~1 GB Free), Integrated GPU (No CUDA).

| Architecture | Model Size (MB) | Theoretical MACs (GFLOPs) | Cloud Training Cost / Feasibility | Local Host CPU Inference Latency (ONNX INT8) | Mobile / Edge Deployment Viability | Architectural Recommendation |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **MobileNetV3-Small / Large** | ~11 MB (Small)<br>~21 MB (Large) | ~0.06 GFLOPs (Small)<br>~0.22 GFLOPs (Large) | Minimal; fast convergence in <2h on free Google Colab T4 | **~35–55 ms** | Excellent; zero latency barrier | **PRIMARY BASELINE CANDIDATE (P0)** |
| **EfficientNet-B0 / B1** | ~21 MB (B0)<br>~31 MB (B1) | ~0.39 GFLOPs (B0)<br>~0.70 GFLOPs (B1) | Low; trains in <4h on Colab T4 / Hugging Face Jobs | **~75–110 ms** | High; optimal accuracy-to-compute ratio | **PRIMARY PRODUCTION CANDIDATE (P0)** |
| **ResNet-18 / ResNet-50** | ~45 MB (Res18)<br>~98 MB (Res50) | ~1.82 GFLOPs (Res18)<br>~4.12 GFLOPs (Res50) | Moderate; requires 8 GB+ VRAM for batch size 32 | **~140–280 ms** | Moderate; higher memory consumption | **COMPARATIVE CONTROL BASELINE (P1)** |
| **Vision Transformer (ViT-B/16 / Swin-T)** | ~340 MB (ViT)<br>~110 MB (Swin-T)| ~17.6 GFLOPs (ViT)<br>~4.5 GFLOPs (Swin) | High; prone to overfitting on datasets <100k without massive self-supervised pretraining | **~650–1200 ms** (Exceeds CPU SLA) | Poor on edge CPU; severe memory consumption | **DISQUALIFIED FOR LOCAL INFERENCE; RESEARCH BENCHMARK ONLY** |

### 3.2 Chosen Comparison Strategy
1. **Backbone Benchmarking:** Benchmark **MobileNetV3-Large** versus **EfficientNet-B0** using transfer learning from ImageNet-1k weights.
2. **Quantization Pipeline:** Export fine-tuned PyTorch checkpoints to ONNX; apply Post-Training Dynamic INT8 Quantization using ONNX Runtime. This reduces model size by 65% (down to ~8–12 MB) and doubles CPU inference throughput on AMD Ryzen.
3. **Multimodal LLM Arbiter (Tier 2):** Use Gemini 1.5 Flash as an asynchronous verification tier only when the local quantized model yields an entropy confidence score $< 0.85$ or flags an Out-Of-Distribution sample.

---

## 4. Model Evaluation & Uncertainty Requirements

*Strict Rule: No accuracy, F1, or latency claims will be cited without documented experimental execution logs.*

Every model experiment logged in KisanVision must report the following metrics:
1. **Macro-Averaged F1 Score:** Harmonic mean of precision and recall calculated across all classes independently to prevent majority-class bias (e.g., preventing high accuracy on Healthy leaves from masking low recall on rare False Smut).
2. **Per-Class Precision, Recall, and PR-AUC Curves:** Specifically tracking high-risk false-negative rates for quarantine-grade pests like *Thrips parvispinus*.
3. **Confusion Matrix Analysis:** Highlighting structural confusions between visual look-alikes (e.g., Chilli Anthracnose vs. Sunscald; Rice Bacterial Leaf Blight vs. Leaf Scald).
4. **Model Calibration via Expected Calibration Error (ECE):**
   $$\text{ECE} = \sum_{m=1}^{M} \frac{|B_m|}{N} \left| \text{acc}(B_m) - \text{conf}(B_m) \right|$$
   A model that outputs 90% confidence must be correct 90% of the time. Temperature scaling will be applied to align softmax scores with empirical probabilities.
5. **Out-of-Distribution (OOD) Detection:**
   - Detect non-crop images (human faces, soil, weeds, cattle, tractors).
   - Evaluate energy-based OOD scoring and Mahalanobis distance in the pen-ultimate feature embedding space.
6. **Robustness Stress Tests:**
   - Synthetic perturbation benchmarks: Gaussian blur, exposure shifts ($\pm 2.0$ EV), shadows, random occlusion masks (10–30% leaf surface).
