# STAGE 02 — DEDUPLICATION & PERCEPTUAL COLLISION AUDIT
## SHA-256 Cryptographic Screening, 64-Bit dHash Calibration & Non-Destructive Quarantine

**Stage:** 02 — Agricultural Dataset Engineering & Taxonomy Validation  
**Core Modules:** [`hash_checker.py`](file:///c:/Users/gokul/OneDrive/Documents/projects/ml/datasets/deduplication/hash_checker.py), [`leakage_detector.py`](file:///c:/Users/gokul/OneDrive/Documents/projects/ml/datasets/deduplication/leakage_detector.py)  
**Status:** Approved Deduplication Architecture  

---

### 1. Two-Tier Deduplication Strategy

To prevent artificial dataset inflation and train/test leakage, ACREVIA combines cryptographic exact-match filtering with perceptual difference hashing:

```
[Candidate Foliar Image]
            │
            ▼
[Tier 1: Cryptographic SHA-256] ──► Match Found ──► Duplicate: Re-use Existing Sample UUID
            │
            ▼ (Unique Image Bytes)
[Tier 2: 64-Bit Perceptual dHash]
            │
            ▼
[Compute Hamming Distance] ───────► Dist <= 4 bits ──► Candidate Burst / Near-Duplicate
            │                                           (Quarantined or Clustered to Same Farm Group)
            ▼ (Dist > 4 bits)
[REGISTER AS NOVEL INDEPENDENT SPECIMEN]
```

---

### 2. Algorithmic Specifications

#### A. Cryptographic Hash (SHA-256)
* **Algorithm:** Standard FIPS 180-4 SHA-256 digest over raw decoded image bytes.
* **Invariant:** Any byte-for-byte identical image (regardless of filename, folder location, or upload timestamp) generates the exact same 64-character hexadecimal digest and maps to the existing canonical `sample_id`.

#### B. Perceptual Difference Hash (dHash)
* **Algorithm:** 64-bit gradient difference hash.
  1. Downsamples image to $9 \times 8$ grayscale using bilinear interpolation.
  2. Compares adjacent horizontal pixels ($P[x, y] > P[x+1, y]$), producing an $8 \times 8 = 64$-bit binary matrix.
  3. Encodes 64 bits into a 16-character hexadecimal string.
* **Hamming Distance Threshold:**
  * $\text{Hamming Dist} = 0$: Identical visual content (different encoding or minor compression).
  * $1 \le \text{Hamming Dist} \le 4$: Near-duplicate burst photograph (same leaf, slightly different angle/light).
  * $\text{Hamming Dist} > 4$: Structurally independent leaf photograph.

---

### 3. Empirical Test Results (`test_deduplication_leakage.py`)

| Test Scenario | Input Condition | Expected Action | Actual Test Result |
|---|---|---|---|
| **Exact Hash Collision** | Two files with identical byte content and different filenames | Flagged as duplicate; returns original sample ID | **PASSED** (`test_exact_duplicate_checker`) |
| **Near-Duplicate Burst** | Slight brightness and contrast perturbation ($\text{dist} \le 4$) | Detected as near-duplicate cluster | **PASSED** (`test_near_duplicate_checker`) |
| **Independent Pathology** | Distinct leaves with different disease symptoms ($\text{dist} \ge 12$) | Registered as independent non-colliding samples | **PASSED** (`test_near_duplicate_checker`) |
| **Non-Destructive Quarantine**| Near-duplicate detected during dataset build | Retained in duplicate cluster manifest without deleting original | **PASSED** |
