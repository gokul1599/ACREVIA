# STAGE 02 — DATASET SOURCE, PROVENANCE & LICENSING REGISTER
## Training and Evaluation Data Sources, Licences, Provenance Schemas & Dataset Separation

**Stage:** 02 — Agricultural Dataset Engineering & Taxonomy Validation  
**Status:** Approved Dataset Provenance Register  
**Guiding Principle:** Explicit separation of research benchmarks, field photographs, synthetic test fixtures, and verified training manifests. Zero synthetic data in production evaluations.

---

### 1. Dataset Source Registry

| Dataset Identifier | Source / Publisher | Permissible Licence | Target Crops Included | Annotation Integrity | Geographic Alignment | Storage Location |
|---|---|---|---|---|---|---|
| `DS_PLANTVILLAGE_BENCHMARK` | Penn State / EPFL (Hughes & Salathé) | CC-BY-SA 4.0 | Chilli (Bell Pepper), Rice baseline | Source labels verified; laboratory background | General subtropical | S3 Object Store / External Cache |
| `DS_ICAR_IIRR_RICE_SURVEY` | ICAR Indian Institute of Rice Research | Academic / Research Use | Rice (Blast, Sheath Blight, BLB, BPH) | Agronomist microscope & field verified | Telangana & Andhra Pradesh | Private Storage / Encrypted Archive |
| `DS_CICR_COTTON_PATHOLOGY` | ICAR Central Institute for Cotton Research | Institutional / Research Use | Cotton (Bollworm, Bacterial Blight, Jassids) | Entomologist & Pathologist verified | Central & Southern Telangana | Private Storage / Encrypted Archive |
| `DS_TELANGANA_FIELD_PILOT_2026` | ACREVIA Farm Scouting Pipeline | Proprietary Smallholder Consent | Cotton, Rice, Chilli | Farmer reported + ExpertConnect reviewed | Warangal, Khammam, Karimnagar | `data/storage/` (Encrypted / Local) |
| `DS_SYNTHETIC_TEST_FIXTURES` | Internal Antigravity Test Suite | Internal Developer Use | Synthetic test images (Blur, Corrupt, OOD) | Automated unit test fixtures only | N/A (Unit tests only) | In-memory / Test fixtures |

---

### 2. Unified Provenance Manifest Schema

Every image sample ingested into ACREVIA's ML pipeline is accompanied by a metadata record conforming to [`UnifiedSampleManifest`](file:///c:/Users/gokul/OneDrive/Documents/projects/ml/datasets/manifests/manifest_schema.py):

```json
{
  "sample_id": "018e47f2-9d3b-7a24-8b65-e9f029b3a45c",
  "dataset_id": "DS_CICR_COTTON_PATHOLOGY",
  "source_name": "ICAR-CICR Cotton Advisory Division",
  "source_url": "https://cicr.icar.gov.in/pathology_atlas",
  "license_identifier": "RESEARCH_USE_ONLY",
  "image_path": "cotton/2026/foliar_sample_0492.jpg",
  "original_filename": "IMG_20261014_093211.jpg",
  "image_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "phash": "a7b3c2e1f0d489b2",
  "crop": "cotton",
  "variety": "RCH-659 BG-II",
  "original_label": "Bacterial Angular Spot",
  "normalized_label": "COTTON_BACTERIAL_BLIGHT",
  "taxonomy_version": "1.0.0",
  "annotation_status": "EXPERT_CONFIRMED",
  "image_quality_status": "ACCEPTED",
  "collection_context": "OPEN_FIELD",
  "capture_date": "2026-10-14T09:32:11Z",
  "plant_id": "PLANT_WARANGAL_0492",
  "farm_group_id": "FARM_WARANGAL_0012",
  "consent_status": "RESEARCH_CONSENT_GRANTED",
  "dataset_version": "v1.0.0-gold",
  "quality_metrics": {
    "width": 1920,
    "height": 1080,
    "laplacian_variance": 342.18,
    "mean_brightness": 128.4,
    "contrast_std": 48.2
  }
}
```

---

### 3. Blocked & Quarantine Registry

1. **Unverified Web Scrapes:** Images downloaded without verified academic provenance or lacking explicit CC/research licences are strictly quarantined and prohibited from training manifests.
2. **Synthetic Data Separation:** Generative or synthetic images are restricted strictly to unit-level pipeline stress tests (e.g. testing blur detector thresholds) and are never mixed with real-world empirical validation sets.
