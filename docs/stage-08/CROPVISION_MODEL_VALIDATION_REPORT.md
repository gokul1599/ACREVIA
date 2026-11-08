# ACREVIA — CROPVISION MODEL VALIDATION REPORT
## Comprehensive Evaluation, Calibration, Out-of-Distribution Detection & Release Governance

**Platform Identity:** ACREVIA — Agricultural Intelligence Platform  
**Model Family:** CropVision Multi-Crop Foliar Pathology Classifier  
**Architectures Evaluated:** MobileNetV3-Large (4.2M params), MobileNetV3-Small (1.5M params), ONNX INT8 Quantized  
**Evaluation Scope:** Cotton (*Gossypium hirsutum*), Rice (*Oryza sativa*), Chilli (*Capsicum annuum*)  
**Evaluation Date:** November 2026  
**Auditor:** Principal Computer Vision & ML Validation Scientist  
**Validation Status:** VERIFIED IN-DISTRIBUTION / FIELD GENERALIZATION LABELED PENDING  

---

## 1. Executive Summary & Evaluation Scope

CropVision is ACREVIA's custom computer vision engine designed for mobile foliar diagnosis of key smallholder crops in Telangana. This validation report assesses model accuracy, per-class sensitivity, calibration error, out-of-distribution rejection, and inference latency under rigorous statistical evaluation.

In accordance with ACREVIA research principles, we distinguish between **Controlled Dataset Benchmark Performance** and **Uncontrolled Open-Field Generalization**. Models were evaluated on clean test splits where near-duplicate images and single-plant leakage were strictly prevented.

---

## 2. Dataset Engineering & Leakage Prevention Audit

### 2.1 Dataset Composition & Provenance
The model benchmark dataset combines verified open-access agricultural pathology repositories (PlantVillage, Cotton Pathology Repositories, Rice Disease Datasets, and Chilli Leaf Spot collections) scoped to Telangana-priority conditions.

| Crop | Condition / Disease Class | Pathogen / Causative Agent | Total Curated Samples | Train (70%) | Val (15%) | Test (15%) |
|---|---|---|---|---|---|---|
| **Cotton** | Healthy Leaf | Normal physiology | 1,200 | 840 | 180 | 180 |
| **Cotton** | Bacterial Blight | *Xanthomonas citri* pv. *malvacearum* | 980 | 686 | 147 | 147 |
| **Cotton** | Cercospora Leaf Spot | *Cercospora gossypina* | 850 | 595 | 128 | 127 |
| **Cotton** | Alternaria Leaf Spot | *Alternaria macrospora* | 740 | 518 | 111 | 111 |
| **Rice** | Healthy Leaf | Normal physiology | 1,400 | 980 | 210 | 210 |
| **Rice** | Rice Blast | *Magnaporthe oryzae* | 1,150 | 805 | 172 | 173 |
| **Rice** | Brown Spot | *Bipolaris oryzae* | 1,020 | 714 | 153 | 153 |
| **Rice** | Bacterial Leaf Blight | *Xanthomonas oryzae* pv. *oryzae* | 920 | 644 | 138 | 138 |
| **Chilli** | Healthy Leaf | Normal physiology | 1,100 | 770 | 165 | 165 |
| **Chilli** | Anthracnose / Fruit Rot | *Colletotrichum capsici* | 960 | 672 | 144 | 144 |
| **Chilli** | Powdery Mildew | *Leveillula taurica* | 880 | 616 | 132 | 132 |
| **Chilli** | Leaf Curl Virus | Begomovirus (whitefly vector) | 820 | 574 | 123 | 123 |
| **Total** | **12 Target Classes** | — | **12,020** | **8,414** | **1,803** | **1,803** |

### 2.2 Data Leakage Prevention Methodology
In foliar image classification, standard random splitting frequently scatters consecutive photos of the same infected plant across training and test splits, producing artificially inflated test scores.
- **Deduplication:** Perceptual hashing (pHash) with a Hamming distance threshold $\le 4$ removed 284 exact and near-duplicate images prior to splitting.
- **Group Splitting:** Samples were partitioned by source capture session and plant ID using `GroupShuffleSplit` in scikit-learn, ensuring that leaves from the same plant never appear in both training and test partitions.

---

## 3. In-Distribution Benchmark Evaluation

### 3.1 Model Architectures & Parameter Footprint

| Architecture Variant | Precision | Parameter Count | Disk Size | Target Hardware | In-Distribution Accuracy |
|---|---|---|---|---|---|
| **MobileNetV3-Large** | FP32 | 4.22M | 16.4 MB | Cloud / Edge Server | 94.62% |
| **MobileNetV3-Small** | FP32 | 1.53M | 6.1 MB | Mid-range Android | 92.18% |
| **MobileNetV3-Large (ONNX INT8)** | INT8 | 4.22M | 4.82 MB | Mobile PWA Offline | 93.85% |

### 3.2 Granular Per-Class Performance (MobileNetV3-Large Test Split)

| Crop | Class Name | Precision | Recall | F1-Score | Support ($N$) |
|---|---|---|---|---|---|
| Cotton | Healthy Leaf | 0.962 | 0.978 | 0.970 | 180 |
| Cotton | Bacterial Blight | 0.931 | 0.918 | 0.924 | 147 |
| Cotton | Cercospora Leaf Spot | 0.924 | 0.906 | 0.915 | 127 |
| Cotton | Alternaria Leaf Spot | 0.898 | 0.910 | 0.904 | 111 |
| Rice | Healthy Leaf | 0.976 | 0.986 | 0.981 | 210 |
| Rice | Rice Blast | 0.941 | 0.936 | 0.938 | 173 |
| Rice | Brown Spot | 0.919 | 0.928 | 0.923 | 153 |
| Rice | Bacterial Leaf Blight | 0.956 | 0.942 | 0.949 | 138 |
| Chilli | Healthy Leaf | 0.982 | 0.970 | 0.976 | 165 |
| Chilli | Anthracnose | 0.929 | 0.938 | 0.933 | 144 |
| Chilli | Powdery Mildew | 0.961 | 0.947 | 0.954 | 132 |
| Chilli | Leaf Curl Virus | 0.949 | 0.935 | 0.942 | 123 |
| **Overall (Macro Avg)** | **12 Classes** | **0.944** | **0.941** | **0.942** | **1,803** |

---

## 4. Model Calibration & Probability Reliability

Raw deep learning softmax outputs typically exhibit overconfidence. CropVision applies post-hoc Temperature Scaling on the validation partition to minimize Expected Calibration Error ($ECE$).

$$ECE = \sum_{m=1}^{M} \frac{|B_m|}{N} \left| \text{acc}(B_m) - \text{conf}(B_m) \right|$$

- **Uncalibrated Model (Raw Softmax):** $ECE = 0.0894$ (Noticeable overconfidence in the 0.80–0.95 confidence range).
- **Calibrated Model (Temperature Scaling $T=1.34$):** $ECE = 0.0218$ (True class probabilities closely track observed empirical accuracy).

---

## 5. Out-of-Distribution (OOD) Detection & Quality Gates

CropVision must never produce an agricultural disease prediction when presented with non-crop imagery or degraded photographs.

### 5.1 Laplacian Variance Blur Detection
- **Mechanism:** Computes the variance of the 2D Laplacian operator over the green foliar channel.
- **Threshold:** $\text{Var}(\nabla^2 I) < 100.0$ triggers immediate rejection before inference.
- **Test Set Performance:** 100% rejection of synthetic Gaussian blurred images ($\sigma \ge 3.0$).

### 5.2 Exposure & Luminance Validator
- **Mechanism:** Evaluates mean pixel intensity $Y = 0.299R + 0.587G + 0.114B$.
- **Rejection Boundaries:** Mean luminance $< 30$ (severe underexposure) or $> 225$ (severe overexposure/glare) rejected with user guidance.

### 5.3 Semantic OOD Detector (Mahalanobis Distance on Embeddings)
Tested against 500 non-agricultural distractors (human faces, indoor rooms, vehicles, animals):
- **OOD Rejection Rate:** **98.4%** correctly rejected as `OUT_OF_DISTRIBUTION` without forcing a crop disease class.
- **False Negative OOD Rate:** 1.6% (primarily extreme close-ups of green fabrics or artificial green leaves).

---

## 6. Uncertainty & Clinical Abstention Gate

When the calibrated top-1 softmax probability is below 0.65, or the difference between top-1 and top-2 candidates ($\Delta_{1-2}$) is $\le 0.15$:
- The model transitions to status `NEEDS_REVIEW`.
- An explanatory disclaimer is returned to the farmer in their selected language.
- A clinical case is queued for human verification in ExpertConnect.

---

## 7. Model Release Governance & Known Limitations

### 7.1 Production Model Card Summary
- **Model Identifier:** `acrevia-cropvision-mobilenetv3-v1.0.0`
- **Supported Crops:** Cotton (*G. hirsutum*), Rice (*O. sativa*), Chilli (*C. annuum*)
- **Input Resolution:** $224 \times 224 \times 3$ RGB
- **Quantization:** INT8 Dynamic Quantization for mobile execution.
- **Rollback Snapshot:** `ml/models/weights/baseline_mobilenet_v3_large.pt`

### 7.2 Field Generalization Statement (Non-Negotiable)
> [!WARNING]
> While CropVision achieves **94.2% Macro F1** on in-distribution test splits, **open-field generalization under uncontrolled Indian monsoon conditions remains officially classified as `FIELD_GENERALIZATION_NOT_VALIDATED`**. Field conditions involving severe rain wash, pesticide chemical residue, dust coating, multiple simultaneous co-infections, and unusual smartphone sensors require on-farm empirical validation before automated autonomous treatment recommendations can be safely made.

**Model Validation Verdict:** **PASSED IN-DISTRIBUTION — APPROVED FOR ASSISTED PILOT DEPLOYMENT WITH EXPERT ESCALATION.**
