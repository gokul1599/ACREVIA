# ACREVIA — COMPLETE RAW TRAINING DATASET INVENTORY
## REPRODUCIBLE CORPUS REGISTRY, PROVENANCE & ARCHIVAL METADATA (TASK-S02-01)
**Document:** `DATASET_ARCHIVAL_INVENTORY.md`  
**Classification:** ML Engineering & Data Governance Registry  
**Date:** 2026-11-08  
**Component:** `ml/data/archival_manager.py` & `scripts/sync_training_corpus.py`  
**Status:** `COMPLETE_VERIFIED` (Tooling, Schemas & Verifiers) / `GATED_STORAGE_TRANSFER` (Live Cloud Upload)  

---

## 1. DATASET INVENTORY SUMMARY

The ACREVIA agricultural computer vision model trains on a canonical 28-class pathology taxonomy covering Cotton, Rice, and Chilli. The raw photographic leaf image corpus is inventoried below:

| Field | Canonical Value | Verification Method |
|---|---|---|
| **Canonical Dataset Identifier** | `acrevia-pathology-28` | Manifest metadata |
| **Dataset Version** | `v1.0.0` (Immutable release) | Version tag & SHA-256 |
| **Taxonomy Version** | `28_class_manifest.yaml` (v1.0) | `ml/configs/taxonomy/` |
| **Crops Covered** | Cotton (10 classes), Rice (10 classes), Chilli (8 classes) | Taxonomy schema |
| **Source & Origin** | PJTSAU Agromet Stations, Telangana KVK Field Collections, Curated Public Benchmarks | Provenance registry |
| **License Type** | `PROPRIETARY_AGRICULTURAL_RESEARCH` & `CC-BY-NC-4.0` | Ingestion metadata |
| **Farmer Consent Status** | `EXPLICIT_FARMER_CONSENT_RECORDED` (for Telangana smallholder field photographs) | UserConsent audit log |
| **Deduplication Baseline** | Perceptual hashing (`pHash`, threshold $\le 6$) | `ml/datasets/deduplication/` |
| **Quality Filter Baseline** | Laplacian blur variance $> 100.0$ | `ml/datasets/quality/` |
| **Group Split Isolation** | Field- and Farmer-isolated stratified split (Train 70%, Val 15%, Test 15%) | `ml/datasets/splitting/` |
| **Archival Storage Prefix** | `datasets/acrevia/acrevia-pathology-28/v1.0.0/` | S3 / R2 / Local adapter |

---

## 2. 28-CLASS TAXONOMY PARTITIONING & CLASS LIST

### Cotton (10 Pathology & Health Classes)
1. `COTTON_BACTERIAL_BLIGHT` (Xanthomonas citri pv. malvacearum)
2. `COTTON_GREY_MILDEW` (Ramularia areola)
3. `COTTON_LEAF_CURL_VIRUS` (Begomovirus)
4. `COTTON_PINK_BOLLWORM` (Pectinophora gossypiella)
5. `COTTON_SPOTTED_BOLLWORM` (Earias vittella)
6. `COTTON_APHIDS` (Aphis gossypii)
7. `COTTON_WHITEFLY` (Bemisia tabaci)
8. `COTTON_MAGNESIUM_DEFICIENCY` (Abiotic physiological reddening)
9. `COTTON_HEALTHY` (Asymptomatic foliar surface)
10. `COTTON_UNKNOWN_CONDITION` (Epistemic fallback class)

### Rice (10 Pathology & Health Classes)
11. `RICE_BLAST_LEAF` (Magnaporthe oryzae)
12. `RICE_BLAST_NECK` (Magnaporthe oryzae - neck phase)
13. `RICE_BACTERIAL_BLIGHT` (Xanthomonas oryzae pv. oryzae)
14. `RICE_BROWN_SPOT` (Bipolaris oryzae)
15. `RICE_SHEATH_BLIGHT` (Rhizoctonia solani)
16. `RICE_FALSE_SMUT` (Ustilaginoidea virens)
17. `RICE_STEM_BORER` (Scirpophaga incertulas)
18. `RICE_ZINC_DEFICIENCY` (Khaira disease / abiotic)
19. `RICE_HEALTHY` (Asymptomatic canopy)
20. `RICE_UNKNOWN_CONDITION` (Epistemic fallback class)

### Chilli (8 Pathology & Health Classes)
21. `CHILLI_ANTHRACNOSE_FRUIT_ROT` (Colletotrichum capsici)
22. `CHILLI_CERCOSPORA_SPOT` (Cercospora capsici)
23. `CHILLI_POWDERY_MILDEW` (Leveillula taurica)
24. `CHILLI_LEAF_CURL_VIRUS` (Begomovirus)
25. `CHILLI_BLACK_THRIPS` (Thrips parvispinus)
26. `CHILLI_YELLOW_MITE` (Polyphagotarsonemus latus)
27. `CHILLI_HEALTHY` (Asymptomatic foliar surface)
28. `CHILLI_UNKNOWN_CONDITION` (Epistemic fallback class)

---

## 3. ARCHIVAL DIRECTORY STRUCTURE & FILE SPECIFICATION

The private object-storage layout enforces strict versioning:

```
datasets/acrevia/acrevia-pathology-28/v1.0.0/
├── manifests/
│   ├── archival_manifest.json          # Master cryptographic manifest
│   ├── train_split.json                # Training set partition with pHash
│   ├── val_split.json                  # Validation set partition
│   └── test_split.json                 # Test holdout partition
├── metadata/
│   ├── collection_provenance.json      # Geospatial & collection timestamps
│   └── consent_governance.json         # Anonymized farmer consent registry
├── taxonomy/
│   ├── 28_class_manifest.yaml          # Canonical taxonomy definition
│   └── class_hierarchy.json            # Taxonomic hierarchy (Family, Genus, Pathogen)
└── raw/
    ├── cotton/                         # Cotton foliar photographs
    ├── rice/                           # Rice canopy & foliar photographs
    └── chilli/                         # Chilli leaf and fruit photographs
```
