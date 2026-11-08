# KisanVision — Dataset Engineering & Governance Subsystem

This package manages dataset manifests, byte-level image ingestion, quality scoring, deduplication, and farm-leakage-resistant dataset splitting.

---

## Subpackages

1. **`manifests/`:** Pydantic `UnifiedSampleManifest` schema capturing cryptographic provenance, legal licensing, and agricultural metadata.
2. **`ingestion/`:** Safe image reader (JPEG/PNG/WebP), format restriction, SHA-256 hashing, perceptual difference hashing (`dHash`), and label normalization.
3. **`quality/`:** Laplacian variance sharpness filter, mean illumination and contrast analyzer, aspect ratio and minimum dimension screening.
4. **`deduplication/`:** Exact duplicate detection and bitwise Hamming distance near-duplicate screening.
5. **`splitting/`:** Group-stratified splitting guaranteeing zero cross-split farm or plant leakage.
6. **`transforms/`:** Reusable PyTorch/torchvision training and evaluation pipelines.
