"""
Tests for Exact Deduplication, Near-Duplicate Screening, and Data Leakage Detection.
"""

import pytest
import hashlib
from ml.datasets.deduplication.hash_checker import (
    ExactDuplicateChecker,
    NearDuplicateChecker,
    hamming_distance_hex
)
from ml.datasets.deduplication.leakage_detector import DataLeakageDetector
from ml.datasets.splitting.group_splitter import GroupSplitter


def test_exact_duplicate_checker():
    checker = ExactDuplicateChecker()
    is_dup1, orig1 = checker.check_or_register("hash_abc123", "sample_01")
    assert is_dup1 is False
    assert orig1 is None
    
    # Second check with identical hash -> Duplicate detected
    is_dup2, orig2 = checker.check_or_register("hash_abc123", "sample_02")
    assert is_dup2 is True
    assert orig2 == "sample_01"


def test_near_duplicate_checker():
    checker = NearDuplicateChecker(hamming_threshold=4)
    # Register base hash (16 chars)
    checker.register("sample_base", "ffff0000ffff0000")
    
    # 1 bit difference: "ffff0000ffff0001" (Hamming distance = 1)
    matches = checker.find_near_duplicates("ffff0000ffff0001", "sample_test_close")
    assert len(matches) == 1
    assert matches[0][0] == "sample_base"
    assert matches[0][1] == 1
    
    # Completely different hash
    matches_far = checker.find_near_duplicates("0000ffff0000ffff", "sample_test_far")
    assert len(matches_far) == 0


def test_group_splitter_and_leakage_detection():
    # Construct 10 synthetic manifests originating from 3 distinct farms
    manifests = []
    for i in range(12):
        farm_id = f"farm_{(i % 3) + 1}"
        manifests.append({
            "sample_id": f"sample_{i}",
            "image_hash": f"hash_{i}",
            "phash": hashlib.sha256(f"unique_phash_{i}".encode()).hexdigest()[:16],
            "farm_group_id": farm_id,
            "normalized_label": "COTTON_HEALTHY" if i % 2 == 0 else "COTTON_BACTERIAL_BLIGHT"
        })
        
    splitter = GroupSplitter(train_ratio=0.6, val_ratio=0.2, test_ratio=0.2, random_seed=42)
    result = splitter.split(manifests)
    
    train_farms = {m["farm_group_id"] for m in result["train"]}
    val_farms = {m["farm_group_id"] for m in result["val"]}
    test_farms = {m["farm_group_id"] for m in result["test"]}
    
    # Verify strict zero intersection between farm sets
    assert len(train_farms & val_farms) == 0
    assert len(train_farms & test_farms) == 0
    assert len(val_farms & test_farms) == 0
    assert result["metadata"]["leakage_audit"]["is_leak_free"] is True
