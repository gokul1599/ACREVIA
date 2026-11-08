# STAGE 02 — DATASET ENGINEERING, 28-CLASS PATHOLOGY TAXONOMY & BASELINE MACHINE LEARNING
## Independent Technical Audit Report

**Audit Target:** Stage 02 — Agricultural Dataset Engineering, 28-Class Taxonomy & Baseline ML  
**Auditor:** Agricultural Computer Vision & Dataset QA Lead  
**Audit Date:** 2026-11-08T18:46:00+05:30  
**Overall Stage Status:** **`PARTIALLY_IMPLEMENTED`**  

---

### Audit objective

Determine whether ACREVIA has a genuine, traceable and scientifically defensible agricultural dataset and baseline ML foundation.

---

### 02.1 Dataset engineering

#### 1. Ingestion, Manifests & Provenance Architecture
- **Code Inspection:** Ingestion schemas and data contracts are defined in [`ml/datasets/manifests/manifest_schema.py`](file:///C:/Users/gokul/OneDrive/Documents/projects/ml/datasets/manifests/manifest_schema.py) via Pydantic model `UnifiedSampleManifest`.
- **Metadata Fields:** Tracks `sample_id`, `dataset_id`, `source_name`, `source_url`, `license_identifier`, `image_path`, `image_hash` (SHA-256), `phash` (perceptual hash), `crop`, `variety`, `original_label`, `normalized_label`, `taxonomy_version`, `annotation_status`, and `consent_status`.
- **Manifest Generator:** Implemented in [`ml/datasets/ingestion/manifest_generator.py`](file:///C:/Users/gokul/OneDrive/Documents/projects/ml/datasets/ingestion/manifest_generator.py), converting raw image directories into structured JSON manifests with cryptographic digests.

#### 2. Deduplication & Data Leakage Prevention
- **Cryptographic & Perceptual Hashing:** [`ml/datasets/deduplication/hash_checker.py`](file:///C:/Users/gokul/OneDrive/Documents/projects/ml/datasets/deduplication/hash_checker.py) implements both exact SHA-256 deduplication and perceptual Hamming distance hashing (threshold $\le 4$ bits) to catch resized or recompressed duplicate images.
- **Group-Based Farm-Disjoint Splitting:** [`ml/datasets/splitting/split_generator.py`](file:///C:/Users/gokul/OneDrive/Documents/projects/ml/datasets/splitting/split_generator.py) implements `GroupSplitter` grouping by `farm_id` or `source_batch_id` to prevent data leakage between train, validation, and test partitions.
- **Leakage Detector:** [`ml/datasets/deduplication/leakage_detector.py`](file:///C:/Users/gokul/OneDrive/Documents/projects/ml/datasets/deduplication/leakage_detector.py) actively cross-checks hashes across splits.

#### 3. Image Quality Filtering
- **Inspection:** [`ml/datasets/quality/quality_validator.py`](file:///C:/Users/gokul/OneDrive/Documents/projects/ml/datasets/quality/quality_validator.py) implements:
  - Laplacian variance blur detection (rejects images with variance $< 100.0$).
  - Overexposure/underexposure analysis via luminance histogram clipping thresholds.
  - Corrupted byte detection via PIL image verification.

#### 4. Critical Finding: Primary Photographic Dataset Storage
- **Inspection of `data/` Directory:**
  ```powershell
  Get-ChildItem -Recurse data
  ```
  The subdirectories `data/raw/`, `data/processed/`, `data/quarantined/`, `data/annotations/`, and `data/splits/` contain **only `.gitkeep` placeholder files**.
- **Audit Conclusion:** The code, tools, schemas, and validators for dataset engineering are fully implemented and tested. However, the physical raw photographic image corpus (e.g., thousands of primary crop leaf photographs) is **not committed to the Git repository**. Training and evaluation pipelines in tests execute on synthetic tensors.

---

### 02.2 Pathology taxonomy

#### 1. Verification of the Claimed 28 Classes
The agricultural pathology taxonomy was inspected across the YAML definition files in [`ml/configs/taxonomy/`](file:///C:/Users/gokul/OneDrive/Documents/projects/ml/configs/taxonomy/):
- [`cotton_taxonomy.yaml`](file:///C:/Users/gokul/OneDrive/Documents/projects/ml/configs/taxonomy/cotton_taxonomy.yaml): 10 classes
- [`rice_taxonomy.yaml`](file:///C:/Users/gokul/OneDrive/Documents/projects/ml/configs/taxonomy/rice_taxonomy.yaml): 10 classes
- [`chilli_taxonomy.yaml`](file:///C:/Users/gokul/OneDrive/Documents/projects/ml/configs/taxonomy/chilli_taxonomy.yaml): 8 classes

**Total Verified Class Count:** Exactly **28 classes** ($10 + 10 + 8 = 28$).

#### 2. Complete 28-Class Enumeration Matrix

| Crop | Class Identifier | Pathology / Condition Name | Category | Agricultural Grounding Source |
|---|---|---|---|---|
| **Cotton** | `COTTON_HEALTHY` | Healthy Cotton Foliage | Healthy | PJTSAU Cotton Production Guide |
| **Cotton** | `COTTON_BACTERIAL_BLIGHT` | Bacterial Blight (*Xanthomonas citri*) | Disease | ICAR-CICR Technical Bulletin No. 24 |
| **Cotton** | `COTTON_GREY_MILDEW` | Grey Mildew (*Ramularia areola*) | Disease | PJTSAU Vyavasaya Panchangam |
| **Cotton** | `COTTON_ALTERNARIA_SPOT` | Alternaria Leaf Spot (*Alternaria macrospora*) | Disease | ICAR-CICR Disease Manual |
| **Cotton** | `COTTON_LEAF_CURL_VIRUS` | Cotton Leaf Curl Virus (CLCuD) | Disease | ICAR-CICR Annual Report |
| **Cotton** | `COTTON_PINK_BOLLWORM` | Pink Bollworm (*Pectinophora gossypiella*) | Pest | ICAR-CICR Pink Bollworm Protocol |
| **Cotton** | `COTTON_JASSID_DAMAGE` | Leafhopper / Jassid Hopper Burn | Pest | PJTSAU Pest Management Guidelines |
| **Cotton** | `COTTON_POTASSIUM_DEF` | Potassium (K) Deficiency | Nutrient | ICAR Soil Science Division |
| **Cotton** | `COTTON_LEAF_REDDENING` | Physiological Leaf Reddening | Abiotic | PJTSAU Agronomy Advisory |
| **Cotton** | `COTTON_UNKNOWN_CONDITION` | Undetermined Foliar Anomaly | Unknown | KisanVision Safety Standard |
| **Rice** | `RICE_HEALTHY` | Healthy Paddy Foliage | Healthy | PJTSAU Rice Knowledge Management Portal |
| **Rice** | `RICE_BLAST_LEAF` | Leaf Blast (*Magnaporthe oryzae*) | Disease | ICAR-IIRR Technical Bulletin No. 89 |
| **Rice** | `RICE_BACTERIAL_BLIGHT` | Bacterial Leaf Blight (*Xanthomonas oryzae*) | Disease | ICAR-IIRR Crop Protection Guide |
| **Rice** | `RICE_SHEATH_BLIGHT` | Sheath Blight (*Rhizoctonia solani*) | Disease | PJTSAU Vyavasaya Panchangam |
| **Rice** | `RICE_BROWN_SPOT` | Brown Spot (*Bipolaris oryzae*) | Disease | ICAR-IIRR Disease Compendium |
| **Rice** | `RICE_FALSE_SMUT` | False Smut (*Ustilaginoidea virens*) | Disease | PJTSAU Rice Advisory |
| **Rice** | `RICE_STEM_BORER_DEADHEART` | Yellow Stem Borer (*Scirpophaga incertulas*) | Pest | ICAR-IIRR Pest Management Handbook |
| **Rice** | `RICE_BPH_HOPPERBURN` | Brown Planthopper (*Nilaparvata lugens*) | Pest | PJTSAU BPH Advisory |
| **Rice** | `RICE_ZINC_DEFICIENCY` | Khaira Disease / Zinc Deficiency | Nutrient | ICAR Soil Micronutrient Division |
| **Rice** | `RICE_UNKNOWN_CONDITION` | Undetermined Rice Anomaly | Unknown | KisanVision Safety Standard |
| **Chilli** | `CHILLI_HEALTHY` | Healthy Chilli Foliage & Fruit | Healthy | IIHR Chilli Cultivation Guide |
| **Chilli** | `CHILLI_ANTHRACNOSE_FRUIT_ROT` | Anthracnose / Dieback (*Colletotrichum*) | Disease | PJTSAU Horticultural Research Station |
| **Chilli** | `CHILLI_LEAF_CURL_VIRUS` | Chilli Leaf Curl Complex (Begomovirus) | Disease | IIHR Viral Disease Manual |
| **Chilli** | `CHILLI_POWDERY_MILDEW` | Powdery Mildew (*Leveillula taurica*) | Disease | PJTSAU Vyavasaya Panchangam |
| **Chilli** | `CHILLI_CERCOSPORA_SPOT` | Cercospora Leaf Spot (*Cercospora capsici*) | Disease | ICAR Horticultural Sciences Bulletin |
| **Chilli** | `CHILLI_BLACK_THRIPS` | Invasive Black Thrips (*Thrips parvispinus*) | Pest | DPPQS Urgent Pest Advisory (Telangana) |
| **Chilli** | `CHILLI_YELLOW_MITE` | Yellow Mite Murda Complex (*Polyphagotarsonemus*) | Pest | PJTSAU Vegetable Protection Guide |
| **Chilli** | `CHILLI_UNKNOWN_CONDITION` | Undetermined Chilli Anomaly | Unknown | KisanVision Safety Standard |

#### 3. Label Normalization & Fallbacks
- Verified in [`ml/datasets/ingestion/manifest_generator.py`](file:///C:/Users/gokul/OneDrive/Documents/projects/ml/datasets/ingestion/manifest_generator.py#L30-L75): `TaxonomyNormalizer` maps standard legacy and external labels (e.g., `pepper__bell___healthy` $\to$ `CHILLI_HEALTHY`, `rice_blast` $\to$ `RICE_BLAST_LEAF`).
- Unrecognized or ambiguous labels strictly fallback to `<CROP>_UNKNOWN_CONDITION`.
- Verified passing in [`tests/ml/test_taxonomy.py`](file:///C:/Users/gokul/OneDrive/Documents/projects/tests/ml/test_taxonomy.py).

---

### 02.3 Baseline ML

#### 1. Architecture Implementation
- [`ml/models/backbones.py`](file:///C:/Users/gokul/OneDrive/Documents/projects/ml/models/backbones.py) supports MobileNetV3-Small, MobileNetV3-Large, ResNet-18, and EfficientNet-B0 with custom classifier heads and temperature-scaled logits.
- [`ml/models/classifier.py`](file:///C:/Users/gokul/OneDrive/Documents/projects/ml/models/classifier.py) implements `KisanVisionClassifier` with dropout regularization ($p=0.2$), batch normalization, and Shannon entropy uncertainty computation.

#### 2. Loss Functions & Schedulers
- Implemented in [`ml/training/losses.py`](file:///C:/Users/gokul/OneDrive/Documents/projects/ml/training/losses.py):
  - `FocalLoss` ($\gamma=2.0, \alpha=0.25$) for severe class imbalance.
  - `ClassBalancedLoss` based on effective number of samples: $E_n = (1 - \beta^n) / (1 - \beta)$.
  - `LabelSmoothingCrossEntropy` ($\epsilon=0.1$) to prevent overconfident output distributions.
- Implemented in [`ml/training/schedulers.py`](file:///C:/Users/gokul/OneDrive/Documents/projects/ml/training/schedulers.py): Cosine annealing with linear warmup.

#### 3. Training Loop & Checkpointing
- [`ml/training/trainer.py`](file:///C:/Users/gokul/OneDrive/Documents/projects/ml/training/trainer.py) implements `KisanVisionTrainer` featuring early stopping, validation Macro-F1 tracking, and checkpoint serialization (`best_model.pt`).
- Verified via [`tests/ml/test_training_smoke.py`](file:///C:/Users/gokul/OneDrive/Documents/projects/tests/ml/test_training_smoke.py) (passes cleanly).

#### 4. Model Artifact Reality Check
- **Finding:** Exported ONNX models exist in [`ml/exports/`](file:///C:/Users/gokul/OneDrive/Documents/projects/ml/exports/):
  - `kisanvision_chilli_mobilenet_v3_small_fp32.onnx` ($4.30\text{ MB}$)
  - `kisanvision_chilli_mobilenet_v3_small_int8.onnx` ($3.86\text{ MB}$)
  - `kisanvision_cotton_mobilenet_v3_small_fp32.onnx` ($4.30\text{ MB}$)
  - `kisanvision_cotton_mobilenet_v3_small_int8.onnx` ($3.86\text{ MB}$)
  - `kisanvision_rice_mobilenet_v3_small_fp32.onnx` ($4.30\text{ MB}$)
  - `kisanvision_rice_mobilenet_v3_small_int8.onnx` ($3.86\text{ MB}$)
- **Gap:** No raw PyTorch training checkpoint files (`.pth` or `.pt`) or full training history logs from real image datasets exist in the repository. The ONNX models exist and load, but their training provenance is not fully traceable to real-world image checkpoints within the repository boundaries.

---

### 02.4 Stage 02 acceptance verification

- [x] Dataset sources documented (`CODE_INSPECTED`, `DOCUMENTATION_ONLY`).
- [x] Dataset versioning implemented in manifest schema (`CODE_INSPECTED`).
- [x] 28-class taxonomy verified across YAML files (`CODE_INSPECTED`, `TEST_EXECUTED`).
- [x] Labels mapped consistently with normalizer fallback (`TEST_EXECUTED`).
- [x] Duplicate and corruption checks implemented and tested (`TEST_EXECUTED`).
- [x] Train/validation/test separation verified with `GroupSplitter` (`TEST_EXECUTED`).
- [x] Leakage risks investigated via hash cross-matching (`TEST_EXECUTED`).
- [x] Baseline training pipeline implemented (`CODE_INSPECTED`, `TEST_EXECUTED`).
- [x] Actual model artifact exists (`ml/exports/*.onnx` verified, size 3.8MB–4.3MB) (`CODE_INSPECTED`).
- [ ] Evaluation results reproducible from raw dataset (`NOT_VERIFIED` — raw image dataset is externalized).
- [x] Limitations documented (`CODE_INSPECTED`).

**Stage 02 Audit Determination:** `PARTIALLY_IMPLEMENTED` (Code, taxonomy, pipeline, and ONNX models exist; primary photographic image dataset is absent from repository).
