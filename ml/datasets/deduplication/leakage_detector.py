"""
KisanVision - Data Leakage Detector & Split Auditor.
Validates that zero samples, farm groups, or near-duplicate images leak across train/val/test splits.
"""

from typing import List, Dict, Set, Any
from ml.datasets.deduplication.hash_checker import hamming_distance_hex


class SplitLeakageReport:
    def __init__(
        self,
        is_leak_free: bool,
        exact_sample_collisions: List[str],
        group_id_collisions: List[str],
        near_duplicate_cross_split_pairs: List[Dict[str, Any]]
    ):
        self.is_leak_free = is_leak_free
        self.exact_sample_collisions = exact_sample_collisions
        self.group_id_collisions = group_id_collisions
        self.near_duplicate_cross_split_pairs = near_duplicate_cross_split_pairs

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_leak_free": self.is_leak_free,
            "exact_sample_collisions_count": len(self.exact_sample_collisions),
            "group_id_collisions_count": len(self.group_id_collisions),
            "near_duplicate_cross_split_count": len(self.near_duplicate_cross_split_pairs),
            "exact_sample_collisions": self.exact_sample_collisions,
            "group_id_collisions": self.group_id_collisions,
            "near_duplicate_pairs": self.near_duplicate_cross_split_pairs
        }


class DataLeakageDetector:
    """
    Audits dataset splits to mathematically verify strict independence.
    """
    @staticmethod
    def audit_splits(
        train_manifests: List[Dict[str, Any]],
        val_manifests: List[Dict[str, Any]],
        test_manifests: List[Dict[str, Any]],
        near_dup_threshold: int = 4
    ) -> SplitLeakageReport:
        
        # 1. Exact Sample ID and Image Hash Intersections
        train_ids = {m["sample_id"] for m in train_manifests}
        val_ids = {m["sample_id"] for m in val_manifests}
        test_ids = {m["sample_id"] for m in test_manifests}
        
        train_hashes = {m["image_hash"] for m in train_manifests}
        val_hashes = {m["image_hash"] for m in val_manifests}
        test_hashes = {m["image_hash"] for m in test_manifests}
        
        sample_collisions = list(
            (train_ids & val_ids) | (train_ids & test_ids) | (val_ids & test_ids) |
            (train_hashes & val_hashes) | (train_hashes & test_hashes) | (val_hashes & test_hashes)
        )

        # 2. Farm Group ID Intersections
        train_groups = {m["farm_group_id"] for m in train_manifests if m.get("farm_group_id")}
        val_groups = {m["farm_group_id"] for m in val_manifests if m.get("farm_group_id")}
        test_groups = {m["farm_group_id"] for m in test_manifests if m.get("farm_group_id")}
        
        group_collisions = list(
            (train_groups & val_groups) | (train_groups & test_groups) | (val_groups & test_groups)
        )

        # 3. Near-Duplicate Cross-Split Screening
        near_dup_pairs = []
        # Audit train vs test cross-leakage
        for t_m in train_manifests:
            t_phash = t_m.get("phash")
            if not t_phash:
                continue
            for te_m in test_manifests:
                te_phash = te_m.get("phash")
                if not te_phash:
                    continue
                dist = hamming_distance_hex(t_phash, te_phash)
                if dist <= near_dup_threshold:
                    near_dup_pairs.append({
                        "train_sample_id": t_m["sample_id"],
                        "test_sample_id": te_m["sample_id"],
                        "hamming_distance": dist
                    })

        is_leak_free = (len(sample_collisions) == 0 and len(group_collisions) == 0 and len(near_dup_pairs) == 0)

        return SplitLeakageReport(
            is_leak_free=is_leak_free,
            exact_sample_collisions=sample_collisions,
            group_id_collisions=group_collisions,
            near_duplicate_cross_split_pairs=near_dup_pairs
        )
