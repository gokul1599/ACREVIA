# ACREVIA — MEDIA STORAGE SECURITY & OBJECT ABSTRACTION
**Programme:** ACREVIA 14-Stage Finalization Programme  
**Target Stage:** Stage 05 — Farm Action Journal, Observations, Geolocation & Weather  
**Date:** 2026-11-08  
**Status:** VERIFIED & HARDENED (`PASS`)

---

## 1. Storage Architecture & Multi-Cloud Portability

Foliar photographs captured in ACREVIA constitute proprietary, sensitive agricultural research data containing spatial provenance, crop phenology, and farm operational practices.

To prevent vendor lock-in and maintain complete sovereignty, ACREVIA defines a pluggable object storage provider pattern in [`backend/app/integrations/storage.py`](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/integrations/storage.py):

```python
class StorageProvider(ABC):
    @abstractmethod
    def save_file(self, content: bytes, filename: str, mime_type: str) -> Dict[str, Any]: ...
    @abstractmethod
    def get_url(self, storage_path: str, expires_in_seconds: int = 3600) -> str: ...
    @abstractmethod
    def delete_file(self, storage_path: str) -> bool: ...
    @abstractmethod
    def read_file(self, storage_path: str) -> bytes: ...
    @abstractmethod
    def get_absolute_path(self, storage_path: str) -> Path: ...
```

Supported Providers:
1. `LocalStorageProvider`: Active for local development, test automation, and on-premises edge deployments (`backend/storage/uploads/`).
2. Cloud Adapters (S3 / Cloudflare R2 / Supabase Storage): Supported via interface drop-in without modifying domain application code.

---

## 2. Cryptographic Content-Addressing & Deduplication

Files are stored using a content-addressed naming strategy:
$$\text{unique\_filename} = \text{SHA256}(C)[0:16] + \text{"\_"} + \text{stem} + \text{ext}$$

### 2.1 Benefits:
1. **Collision Resistance:** Identical images cannot accidentally overwrite distinct records.
2. **Tamper Evidence:** Any byte alteration on disk immediately invalidates the cryptographic checksum recorded in `observation_media.sha256_hash`.
3. **Storage Efficiency:** Enables hash-based deduplication across repetitive batch uploads.

---

## 3. Path Traversal & Injection Defenses

A critical vulnerability in object storage services is path traversal via malicious filenames (e.g. `../../etc/passwd` or `..\\..\\windows\\system32`).

### 3.1 Defense Implementation
In [`backend/app/integrations/storage.py`](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/integrations/storage.py):
```python
def get_absolute_path(self, storage_path: str) -> Path:
    # Sanitize storage_path to isolate basename, eliminating relative directory traversal
    clean_name = Path(storage_path).name
    return self.base_dir / clean_name
```
Even if an attacker crafts an exploit string containing traversal sequences, `Path.name` strips all path prefixes and strictly confines operations to `base_dir`.

---

## 4. EXIF Stripping & Location Sanitization

Mobile phone cameras automatically embed EXIF metadata containing GPS latitude, longitude, altitude, device IMEI, and timestamps.

### 4.1 Security Invariant
- **Internal Storage:** Original EXIF metadata is parsed upon upload to determine spatial provenance (with farmer consent) and stored in encrypted database columns.
- **External / Shared Derivatives:** Any thumbnail, public research export, or expert review preview generated for external viewers passes through an EXIF-stripping pipeline:
  ```python
  from PIL import Image
  
  def strip_exif(image_bytes: bytes) -> bytes:
      image = Image.open(io.BytesIO(image_bytes))
      clean_image = Image.new(image.mode, image.size)
      clean_image.putdata(list(image.getdata()))
      buf = io.BytesIO()
      clean_image.save(buf, format="JPEG", quality=90)
      return buf.getvalue()
  ```
This guarantees that no external party can reverse-engineer farmer home or field coordinates from shared imagery.

---

## 5. Tokenized Authenticated Streaming

Media files are never exposed via unauthenticated public URLs.
- Endpoints stream media via `GET /api/v1/observations/{obs_id}/media/{media_id}/file`.
- Every streaming request enforces `verify_farm_access(farm_id, current_user, db)`.
- If an unauthorized user or tenant attempts to access the URL, the server responds with HTTP 403 Forbidden.

### 5.1 Verification
Verified by automated test in [`backend/tests/test_observations.py::test_get_media_stream_authorized_and_cross_tenant`](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/tests/test_observations.py).
