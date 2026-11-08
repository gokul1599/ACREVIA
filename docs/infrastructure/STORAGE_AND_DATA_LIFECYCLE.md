# ACREVIA — STORAGE ABSTRACTION AND DATA LIFECYCLE SPECIFICATION
## Foliar Media Storage Architecture, Deduplication, Quality Ingestion, and DPDP Compliance

---

## 1. Storage Abstraction Architecture

ACREVIA decouples the backend application code from physical storage infrastructure through the `StorageProvider` abstract base class:

```python
class StorageProvider(ABC):
    @abstractmethod
    def save_file(self, content: bytes, filename: str, mime_type: str) -> Dict[str, Any]:
        """Persists file content and returns storage metadata."""
        pass

    @abstractmethod
    def read_file(self, storage_path: str) -> bytes:
        """Reads file bytes from storage."""
        pass

    @abstractmethod
    def delete_file(self, storage_path: str) -> bool:
        """Deletes file from storage."""
        pass

    @abstractmethod
    def get_url(self, storage_path: str, expires_in_seconds: int = 3600) -> str:
        """Generates a secure access URL."""
        pass
```

### Implementations:
1. **`LocalStorageProvider`:** High-speed development and local testing adapter that persists files in an isolated filesystem directory with filename path-traversal sanitization.
2. **`S3StorageProvider` (Cloud Ready):** Production adapter targeting AWS S3 (Mumbai `ap-south-1` region) or private Supabase Storage with AES-256 server-side encryption (`SSE-S3` or `SSE-KMS`).

---

## 2. Foliar Photograph Ingestion Pipeline

Every plant leaf image uploaded to ACREVIA undergoes a multi-stage validation pipeline:

```
[Incoming Image (Multipart/Form-Data)]
               │
               ▼
[MIME Type Check: image/jpeg, image/png, image/webp]
               │ (Pass)
               ▼
[File Size Check: <= 15 MB]
               │ (Pass)
               ▼
[Compute SHA-256 Cryptographic Checksum]
               │
               ▼
[Persist via StorageProvider]
               │
               ▼
[Automated Image Quality Assessment (ImageQualityValidator)]
  ├── Sharpness Evaluation (Laplacian Variance >= 100.0)
  ├── Exposure Analysis (Over/Under-exposure, Histogram Spread)
  └── Botanical Feasibility (Aspect Ratio & Dimensions >= 64x64)
               │
               ▼
[Create ObservationMedia & ImageQualityAssessment Database Records]
```

---

## 3. Cryptographic Deduplication

To conserve storage costs and prevent redundant inference computations:
- Every uploaded foliar image is hashed using **SHA-256** across its raw byte stream.
- The 64-character hexadecimal hash is stored in `observation_media.sha256_hash` with an active B-Tree database index.
- If multiple farmers or scout workers upload identical images, the storage layer recognizes the hash match, permitting shared backing storage while maintaining isolated tenant ownership records.

---

## 4. Digital Personal Data Protection (DPDP) Compliance & Retention

In accordance with the **Digital Personal Data Protection Act (India)**:
1. **Purpose Limitation:** Farmer photographs and agronomic observations are captured exclusively for diagnostic assistance, crop health monitoring, and authorized agronomist review.
2. **Explicit Consent Tracking:** The `consent_records` table captures granular consent declarations:
   - `CORE_SERVICE`: Basic disease diagnosis and farm management.
   - `EXPERT_REVIEW`: Sharing anonymized foliar evidence with certified KVK agronomists.
   - `RESEARCH_PARTICIPATION`: Aggregated regional disease surveillance studies.
   - `MODEL_TRAINING`: Voluntary inclusion of verified samples in future model calibration retrainings.
3. **Right to Erasure:** Deleting a farm cascades deletions across all linked plots, observations, and foliar media files, guaranteeing complete physical erasure of farmer data upon request.
