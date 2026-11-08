# KISANVISION — DATASET PROVENANCE AND LICENSING CATALOG

**Document Version:** 1.0.0  
**Effective Date:** November 7, 2026  
**Curator:** Dataset Quality and Governance Specialist, ML Research Engineer  
**Governance Standard:** Open Data Licensing & DPDPA 2023 Compliance  

---

## 1. Candidate Dataset Registry

| Field | Dataset 1: PlantVillage | Dataset 2: PlantDoc | Dataset 3: Mendeley Cotton/Rice | Dataset 4: Telangana Field Photos |
| :--- | :--- | :--- | :--- | :--- |
| **Dataset Name** | PlantVillage | PlantDoc | Indian Agricultural Image Repositories | KisanVision Telangana Field Curation |
| **Official Source** | Penn State University & EPFL | Indian Institute of Technology (IIT) Delhi | Mendeley Data / ICAR Research Archive | KisanVision Partnered Extension Units |
| **Original Publisher** | Hughes & Salathé (2015) | Singh, Sharma & Vinayak (2020) | Various University Authors | PJTSAU & Rythu Vedika Field Officers |
| **Download Location** | `https://plantvillage.psu.edu` | `https://github.com/pratikkayal/PlantDoc-Dataset` | `https://data.mendeley.com` | Internal Encrypted S3 Bucket |
| **License Type** | Creative Commons Attribution 4.0 (CC-BY 4.0) | MIT License | CC-BY 4.0 | Proprietary Agricultural Research License |
| **Attribution Requirement** | Mandatory citation of Hughes et al. (2015) | Mandatory attribution to Singh et al. (CoDS-COMAD 2020) | Mandatory citation of respective authors | Strict farmer privacy & institutional attribution |
| **Commercial Permissions** | Permitted with attribution | Permitted under MIT terms | Permitted under CC-BY terms | Non-commercial smallholder advisory use |
| **Crops Covered** | Chilli (Pepper), Cotton (Subset), Rice (None) | Rice, Pepper (Bell/Chilli), Cotton (Limited) | Cotton, Rice (Bacterial blight, blast) | Cotton, Rice, Chilli (All 28 local classes) |
| **Label Coverage** | 38 crop-pathology pairs | 27 classes across 13 species | 8 specific Indian crop disease classes | Full Telangana taxonomy |
| **Verified Image Count** | 54,303 total (across all plant species) | 2,598 total in-field images | ~3,500 curated images | Target: 6,000 images (Zero currently downloaded) |
| **Image Conditions** | Controlled lab: single leaf on grey background | Real field: natural sunlight, background weeds | Mixed field and shade-house photography | True field: variable phone sensors, direct sun |
| **Geographic Relevance** | Global / North American lab specimens | India & Web scrape | India (Maharashtra, Punjab, Telangana) | Telangana (Warangal, Nalgonda, Khammam) |
| **Known Limitations** | Severe domain shift; 0% background clutter | Modest class sizes; duplicate web images | Class imbalance; missing invasive thrips | Time required for multi-season field collection |
| **Download Status** | **NOT DOWNLOADED (Clean Slate)** | **NOT DOWNLOADED (Clean Slate)** | **NOT DOWNLOADED (Clean Slate)** | **COLLECTION IN PROGRESS** |
| **Approval Status** | Approved for initial feature extraction only | Approved for in-field fine-tuning benchmark | Approved for comparative baselines | Approved for production deployment |

---

## 2. Dataset Storage Architecture & Retention Rules

```
data/
├── incoming/        # Temporary landing zone for raw uninspected field uploads
├── quarantined/     # Corrupted, unreadable, or severe blur failures (isolated)
├── raw/             # Immutable master source images (read-only, SHA-256 indexed)
├── processed/       # Resized, normalized, and preprocessed image tensors
├── annotations/     # JSON/YAML annotation manifests linking images to taxonomy
├── splits/          # Immutable train/val/test split manifests (farm-grouped)
├── metadata/        # Image quality metrics, perceptual hash indexes, audit logs
└── exports/         # Versioned dataset packages for cloud training runs
```

### 2.1 Immutability & Provenance Invariant
- Files deposited into `data/raw/` are immediately hashed (SHA-256) and marked read-only.
- Preprocessing pipelines never overwrite or modify `data/raw/` files; all transformed images are written exclusively to `data/processed/`.
- Every processed file retains a foreign key reference (`image_hash` and `sample_id`) to its raw source ancestor.
