# STAGE 02 — DATASET PIPELINE ARCHITECTURE & SPECIFICATION
## End-to-End Ingestion Flow, Modular Processing Stages & Memory Optimization

**Stage:** 02 — Agricultural Dataset Engineering & Taxonomy Validation  
**Core Pipeline:** Ingestion $\to$ Quality Filtering $\to$ Deduplication $\to$ Farm Partitioning  
**Status:** Approved Pipeline Architecture  

---

### 1. End-to-End Logical Pipeline Flow

The ACREVIA agricultural data engineering pipeline processes image archives sequentially through 12 deterministic, testable operations:

```
[1. DISCOVER]          Scan raw directory trees for candidate foliar image files (.jpg, .png, .webp).
      │
      ▼
[2. REGISTER]          Instantiate preliminary manifest with dataset ID and ingestion timestamp.
      │
      ▼
[3. VALIDATE_FORMAT]   Inspect magic bytes; reject executables, HTML, or corrupted file headers.
      │
      ▼
[4. DECODE]            Safely decode image via PIL with decompression bomb limits (MAX_IMAGE_PIXELS).
      │
      ▼
[5. NORMALIZE]         Correct EXIF orientation, convert to standard RGB color space, extract GPS.
      │
      ▼
[6. QUALITY_CHECK]     Evaluate dimension limits, Laplacian variance blur ($Var(\Delta) \ge 100$), exposure.
      │
      ▼
[7. HASH]              Compute cryptographic SHA-256 and 64-bit gradient difference hash (dHash).
      │
      ▼
[8. DEDUPLICATE]       Filter exact byte duplicates and quarantine near-duplicate bursts ($\text{dist} \le 4$).
      │
      ▼
[9. ANNOTATION_CHECK]  Normalize source label against 28-class taxonomy; map unknown to UNKNOWN_CONDITION.
      │
      ▼
[10. GROUP]            Bind sample to physical holding (`farm_group_id`) or specimen plant (`plant_id`).
      │
      ▼
[11. SPLIT]            Partition group clusters into Train (70%), Val (15%), Test (15%) with leakage audit.
      │
      ▼
[12. MANIFEST & REPORT]Export versioned JSONL manifests, checksums, and dataset statistical report.
```

---

### 2. Engineering Guarantees & Memory Management

1. **Memory Budgeting on Host Machine (5.86 GB RAM limit):**
   * The pipeline processes images in streaming batches of 50 samples.
   * High-resolution images are decoded, measured, and closed immediately (`image.close()`), preventing heap ballooning.
   * Peak pipeline RAM consumption during test execution is $< 210\text{ MB}$.
2. **Idempotence & Resume Capability:**
   * Manifest generation produces deterministic outputs for identical input files and random seeds (`seed = 42`).
   * Intermediate results are indexed by SHA-256 digest; re-running the pipeline on an existing directory skips previously processed samples.
3. **Structured Logging & Diagnostics:**
   * Pipeline logs events using structured key-value format (`sample_id`, `crop`, `status`, `duration_ms`).
   * Failures record specific reason codes (`CORRUPT_HEADER`, `IMAGE_TOO_BLURRY`, `EXPOSURE_CLIPPED`).
