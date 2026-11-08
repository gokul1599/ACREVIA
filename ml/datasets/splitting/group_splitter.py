"""
KisanVision - Group-Aware Leakage-Resistant Dataset Splitter.
Guarantees that all images from the same farm or plant stay strictly within one split partition.
"""

import random
from collections import defaultdict
from typing import List, Dict, Any, Tuple
import json
from pathlib import Path

from ml.datasets.deduplication.leakage_detector import DataLeakageDetector


class GroupSplitter:
    """
    Partitions dataset manifests into Train, Validation, and Locked Test sets
    stratified by groups (e.g. farm_group_id or plant_id) to eliminate group leakage.
    """
    def __init__(
        self,
        train_ratio: float = 0.70,
        val_ratio: float = 0.15,
        test_ratio: float = 0.15,
        random_seed: int = 42,
        group_key: str = "farm_group_id"
    ):
        total = train_ratio + val_ratio + test_ratio
        if abs(total - 1.0) > 1e-4:
            raise ValueError(f"Split ratios must sum to 1.0, got: {total}")
            
        self.train_ratio = train_ratio
        self.val_ratio = val_ratio
        self.test_ratio = test_ratio
        self.random_seed = random_seed
        self.group_key = group_key

    def split(self, manifests: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Splits manifests while keeping all members of any group together.
        """
        if not manifests:
            return {"train": [], "val": [], "test": [], "metrics": {}}

        # Group samples by group_key
        groups: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        for m in manifests:
            grp = m.get(self.group_key) or m.get("sample_id")  # fallback to sample_id if no group
            groups[grp].append(m)

        group_keys = list(groups.keys())
        rng = random.Random(self.random_seed)
        rng.shuffle(group_keys)

        total_samples = len(manifests)
        target_train = int(total_samples * self.train_ratio)
        target_val = int(total_samples * self.val_ratio)

        train_manifests: List[Dict[str, Any]] = []
        val_manifests: List[Dict[str, Any]] = []
        test_manifests: List[Dict[str, Any]] = []

        curr_train_count = 0
        curr_val_count = 0

        for grp_key in group_keys:
            grp_samples = groups[grp_key]
            count = len(grp_samples)
            
            if curr_train_count + count <= target_train or (curr_train_count == 0):
                train_manifests.extend(grp_samples)
                curr_train_count += count
            elif curr_val_count + count <= target_val or (curr_val_count == 0):
                val_manifests.extend(grp_samples)
                curr_val_count += count
            else:
                test_manifests.extend(grp_samples)

        # Audit with DataLeakageDetector
        audit_report = DataLeakageDetector.audit_splits(
            train_manifests=train_manifests,
            val_manifests=val_manifests,
            test_manifests=test_manifests
        )

        if not audit_report.is_leak_free:
            raise RuntimeError(f"Data leakage detected during splitting: {audit_report.to_dict()}")

        # Compute class distribution across splits
        def get_dist(items):
            d = defaultdict(int)
            for item in items:
                d[item.get("normalized_label", "UNKNOWN")] += 1
            return dict(d)

        return {
            "train": train_manifests,
            "val": val_manifests,
            "test": test_manifests,
            "metadata": {
                "split_seed": self.random_seed,
                "group_key": self.group_key,
                "total_samples": total_samples,
                "train_count": len(train_manifests),
                "val_count": len(val_manifests),
                "test_count": len(test_manifests),
                "train_groups": len({m.get(self.group_key) for m in train_manifests}),
                "val_groups": len({m.get(self.group_key) for m in val_manifests}),
                "test_groups": len({m.get(self.group_key) for m in test_manifests}),
                "class_distributions": {
                    "train": get_dist(train_manifests),
                    "val": get_dist(val_manifests),
                    "test": get_dist(test_manifests)
                },
                "leakage_audit": audit_report.to_dict()
            }
        }
