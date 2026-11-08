# STAGE 02 — DATA PRIVACY & EXIF METADATA AUDIT
## Farmer Privacy Protection, Location Coarsening & Metadata Sanitization

**Stage:** 02 — Agricultural Dataset Engineering & Taxonomy Validation  
**Legal Framework:** Digital Personal Data Protection Act (DPDP Act 2023, India)  
**Status:** Approved Privacy Audit  

---

### 1. EXIF Metadata Extraction & Stripping Pipeline

When smallholder farmers capture foliar photographs in the field, mobile camera sensors embed EXIF metadata (GPS coordinates, device serial numbers, owner names). ACREVIA's [`AgriculturalImageReader`](file:///c:/Users/gokul/OneDrive/Documents/projects/ml/datasets/ingestion/image_reader.py) enforces strict metadata separation:

1. **Extraction for Agronomic Context:**
   * GPS latitude and longitude are extracted temporarily to confirm plot boundary alignment and fetch micro-meteorological history via Open-Meteo.
2. **Immediate Ingestion Sanitization:**
   * The raw EXIF block is completely stripped from the image binary prior to storage in the image manifest or training archive.
   * EXIF fields stripped include: `GPSInfo`, `Make`, `Model`, `Software`, `Artist`, `CameraSerialNumber`, `LensSerialNumber`.
3. **Location Coarsening for Research & Public APIs:**
   * Exact sub-meter GPS coordinates are coarsened to the district or mandal centroid level in all exportable manifests and public QR endpoints (`ProduceLot`).
   * High-precision coordinates remain accessible only to the authenticated farm owner via encrypted database relations.

---

### 2. Privacy Assertion Verification

| # | Privacy Invariant | Enforcement Mechanism | Audit Finding |
|---|---|---|---|
| **01** | Raw foliar images in training manifests contain zero GPS tags | `ImageReader.strip_exif_metadata()` rebuilds image bytes using pure PIL pixel buffer | **VERIFIED** |
| **02** | Farmer personal identity (name, phone) is decoupled from sample manifests | Manifests use random UUID `sample_id` and hashed `farm_group_id` | **VERIFIED** |
| **03** | Public QR traceability does not leak farm boundaries | `ProduceLot` endpoint redacts precise plot geometry | **VERIFIED** |
| **04** | Consent revocation purges sample from active training pipelines | `consent_status == "REVOKED"` automatically excludes sample from future split generations | **VERIFIED** |
