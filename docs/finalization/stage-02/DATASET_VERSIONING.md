# STAGE 02 — DATASET VERSIONING & REPRODUCIBILITY PROTOCOL
## Immutable Manifest Releases, SHA-256 Digest Tracking & Storage Isolation

**Stage:** 02 — Agricultural Dataset Engineering & Taxonomy Validation  
**Core Modules:** [`manifest_schema.py`](file:///c:/Users/gokul/OneDrive/Documents/projects/ml/datasets/manifests/manifest_schema.py), [`manifest_generator.py`](file:///c:/Users/gokul/OneDrive/Documents/projects/ml/datasets/ingestion/manifest_generator.py)  
**Status:** Approved Versioning Specification  

---

### 1. Four-Tier Versioning Identifier

Every dataset artifact generated in ACREVIA carries a quadruple-version tag:

$$\text{Version ID} = \langle D_{\text{ver}}, T_{\text{ver}}, P_{\text{ver}}, S_{\text{ver}} \rangle$$

1. **$D_{\text{ver}}$ (Dataset Version):** e.g., `v1.0.0-gold` (identifies raw source collection and curation release).
2. **$T_{\text{ver}}$ (Taxonomy Version):** e.g., `1.0.0` (identifies active 28-class taxonomy configuration).
3. **$P_{\text{ver}}$ (Processing Version):** e.g., `1.0.0` (identifies quality gate parameters: $Var(\Delta) \ge 100$, 1024px scale).
4. **$S_{\text{ver}}$ (Split Version):** e.g., `seed42_r70_15_15` (identifies group partition seed and ratios).

---

### 2. Dataset Release Manifest Package

A formal dataset release consists of a versioned directory archived in private object storage:

```
releases/dataset_v1.0.0/
├── manifest_full.jsonl           # Complete catalog of all inspected samples
├── train_manifest.jsonl          # Farm-disjoint training partition (~70%)
├── val_manifest.jsonl            # Farm-disjoint validation partition (~15%)
├── test_manifest.jsonl           # Locked farm-disjoint test partition (~15%)
├── duplicate_clusters.jsonl      # Quarantined near-duplicate audit records
├── quality_rejections.jsonl      # Blur, exposure, and corrupt file rejection audit
├── taxonomy_snapshot.yaml        # Pinned 28-class definitions used for release
└── RELEASE_CHECKSUMS.sha256      # SHA-256 digests of all manifest files
```

---

### 3. Git Repository vs Object Storage Boundary

In adherence to Section 10.4 of the Antigravity Specification:
* **Committed to Git:** Python pipeline code, Pydantic schemas, YAML taxonomy files, automated test suites, and documentation.
* **Excluded from Git (`.gitignore`):** Raw high-resolution image binaries (`data/raw/`, `data/storage/`), heavy `.tar.gz` image archives, and gigabyte-scale training cache directories.
* **Durable Storage:** Image binaries are persisted in private, access-controlled S3-compatible object storage with server-side AES-256 encryption.
