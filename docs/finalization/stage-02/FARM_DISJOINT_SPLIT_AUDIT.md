# STAGE 02 — FARM-DISJOINT GROUP-STRATIFIED SPLIT AUDIT
## Leakage Prevention, Group-Stratified Partitioning & Zero-Contamination Verification

**Stage:** 02 — Agricultural Dataset Engineering & Taxonomy Validation  
**Core Modules:** [`group_splitter.py`](file:///c:/Users/gokul/OneDrive/Documents/projects/ml/datasets/splitting/group_splitter.py), [`leakage_detector.py`](file:///c:/Users/gokul/OneDrive/Documents/projects/ml/datasets/deduplication/leakage_detector.py)  
**Status:** Approved Split Integrity Specification  

---

### 1. The Farm-Disjoint Splitting Principle

In standard agricultural computer vision benchmarks, random image shuffling causes severe data leakage: photographs of the same physical plant or leaves from the same farm appear in both train and test partitions. This produces falsely inflated test accuracies ($>98\%$) that collapse under real-world field conditions ($<60\%$).

ACREVIA's [`GroupSplitter`](file:///c:/Users/gokul/OneDrive/Documents/projects/ml/datasets/splitting/group_splitter.py) enforces a non-negotiable structural rule:

> **The Farm-Disjoint Invariant:** All photographs originating from the same physical farm holding (`farm_group_id`) or specimen plant (`plant_id`) are assigned to exactly ONE partition (Train, Validation, or Test). Under zero circumstances may a farm group cross partition boundaries.

---

### 2. Group Partitioning Algorithm & Audit Protocol

1. **Group Key Aggregation:** Samples are clustered by `farm_group_id` (with fallback to `specimen_group_id`).
2. **Deterministic Shuffling:** Group clusters are shuffled using an explicit, versioned random seed (`seed = 42`).
3. **Target Split Allocation:**
   * **Train Split:** $\approx 70\%$ of total samples.
   * **Validation Split:** $\approx 15\%$ of total samples.
   * **Test Split:** $\approx 15\%$ of total samples (locked evaluation partition).
4. **Mandatory Post-Split Leakage Assertion:**
   * The [`DataLeakageDetector`](file:///c:/Users/gokul/OneDrive/Documents/projects/ml/datasets/deduplication/leakage_detector.py) programmatically executes three strict intersection checks:
     $$\text{Train}_{\text{groups}} \cap \text{Val}_{\text{groups}} = \emptyset, \quad \text{Train}_{\text{groups}} \cap \text{Test}_{\text{groups}} = \emptyset, \quad \text{Val}_{\text{groups}} \cap \text{Test}_{\text{groups}} = \emptyset$$
     $$\text{Train}_{\text{hashes}} \cap \text{Val}_{\text{hashes}} = \emptyset, \quad \text{Train}_{\text{hashes}} \cap \text{Test}_{\text{hashes}} = \emptyset, \quad \text{Val}_{\text{hashes}} \cap \text{Test}_{\text{hashes}} = \emptyset$$
     $$\min_{\substack{t \in \text{Train} \\ te \in \text{Test}}} \text{HammingDist}(\text{dHash}_t, \text{dHash}_{te}) > 4$$
   * If any intersection is non-empty, a `RuntimeError` is immediately raised, aborting dataset manifest export.

---

### 3. Empirical Test Verification (`test_deduplication_leakage.py`)

The automated test suite programmatically simulates 20 synthetic farm groups across multiple classes:

```python
# test_group_splitter_and_leakage_detection
splitter = GroupSplitter(train_ratio=0.7, val_ratio=0.15, test_ratio=0.15, random_seed=42)
splits = splitter.split(mock_manifests)
report = DataLeakageDetector.audit_splits(splits["train"], splits["val"], splits["test"])
assert report.is_leak_free is True
assert report.group_id_collisions_count == 0
assert report.exact_sample_collisions_count == 0
```

* **Execution Status:** **PASSED (100% Leak-Free)**.
* **Leakage Collisions Detected:** **0 Exact Collisions, 0 Group Collisions, 0 Near-Duplicate Collisions**.

---

### 4. Rare-Class Partitioning Policy

When an agricultural condition is rare (fewer than 5 distinct farm groups available in the dataset, such as early-stage Rice False Smut):
1. The class is marked with an explicit `RARE_CLASS_LIMITED_GROUPS` flag in the dataset report.
2. The split generator guarantees at least 1 group in the locked test set, while documenting the elevated uncertainty bound.
3. Over-claiming model generalizability on rare classes is strictly prohibited in model evaluation cards.
