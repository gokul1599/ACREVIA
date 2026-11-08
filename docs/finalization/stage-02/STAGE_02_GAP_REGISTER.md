# STAGE 02 — GAP & DEFECT REGISTER
## Outstanding Defect Analysis, Risk Classification & Corrective Protocols

**Stage:** 02 — Agricultural Dataset Engineering & Taxonomy Validation  
**Document Version:** 1.0.0  
**Status:** Active Gap Register  

---

### Gap & Limitation Inventory

#### GAP-S02-01: Legacy Internal Product Naming (`KisanVision` vs `ACREVIA`)
* **Classification:** `P3_LOW` (Documentation / Cosmetic)
* **Requirement:** Consistent product identity across all internal docstrings and module metadata.
* **Evidence:** Several internal dataset module docstrings (e.g. `blur_detector.py`, `hash_checker.py`, `manifest_schema.py`) retain legacy header comments `KisanVision - ...`.
* **User Impact:** Zero impact on end-user experience (all user-facing UI and APIs use `ACREVIA`).
* **Technical Impact:** Zero impact on runtime execution; tests and imports unaffected.
* **Proposed Solution:** Retain stable internal module paths (`kisanvision.inference` logger name) to preserve backward compatibility with existing model checkpoint metadata, while updating user-facing schemas to `ACREVIA`.
* **Status:** `ACCEPTED_RESIDUAL_DESIGN`

---

#### GAP-S02-02: Public Dataset Benchmark Bias (Controlled Lab vs Open Field)
* **Classification:** `P2_MEDIUM` (Agronomic Reality)
* **Requirement:** Genuine agricultural field representations for Telangana smallholders.
* **Evidence:** Benchmark datasets like PlantVillage contain photographs taken against uniform gray/black laboratory backdrops rather than messy, complex open-field canopies.
* **User Impact:** Models evaluated purely on laboratory benchmarks can overestimate real-world field accuracy.
* **Technical Impact:** Localized open-field evaluation required in Stage 08 and Stage 09.
* **Proposed Solution:** Require that production validation manifests explicitly track `collection_context` (`CONTROLLED_LAB`, `SHADE_HOUSE`, `OPEN_FIELD`), and mandate that locked test sets contain only `OPEN_FIELD` samples for real-world certification.
* **Status:** `ADDRESSED_IN_SCHEMA` (Tracked via `CollectionContext` enum in `manifest_schema.py`)

---

#### GAP-S02-03: Rare Agricultural Condition Sample Scarcity
* **Classification:** `P2_MEDIUM` (Data Availability)
* **Requirement:** Farm-disjoint evaluation across all 28 classes.
* **Evidence:** Specific regional conditions (e.g. Rice False Smut spore balls or early Cotton Potassium deficiency) have fewer than 10 independent farm groups available in open datasets.
* **User Impact:** Model confidence may be lower on rare conditions.
* **Technical Impact:** Splitting rare classes across 3 partitions risks leaving $< 2$ groups in the test set.
* **Proposed Solution:** Enforce the Rare-Class Policy codified in `FARM_DISJOINT_SPLIT_AUDIT.md`: flag classes with $< 5$ groups with `RARE_CLASS_LIMITED_GROUPS` and mandate agronomist human review (`requires_expert_review: true`).
* **Status:** `MITIGATED_VIA_TAXONOMY_FLAGS`
