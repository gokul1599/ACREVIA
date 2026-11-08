"""
KisanVision - Hash & Duplicate Screening Engine.
Identifies exact cryptographic collisions and near-duplicate photographic bursts.
"""

from typing import Dict, List, Tuple, Set, Optional


def hamming_distance_hex(hash1: str, hash2: str) -> int:
    """
    Computes bitwise Hamming distance between two hex-encoded perceptual hashes.
    """
    if len(hash1) != len(hash2):
        raise ValueError(f"Hash length mismatch: {len(hash1)} vs {len(hash2)}")
        
    val1 = int(hash1, 16)
    val2 = int(hash2, 16)
    xor_val = val1 ^ val2
    # Count the number of set bits (bin(xor_val).count('1'))
    return bin(xor_val).count("1")


class ExactDuplicateChecker:
    """Detects 100% byte-for-byte identical images using SHA-256."""
    def __init__(self):
        self.seen_hashes: Dict[str, str] = {}  # sha256 -> sample_id

    def check_or_register(self, sha256_hash: str, sample_id: str) -> Tuple[bool, Optional[str]]:
        """
        Returns (is_duplicate, original_sample_id).
        If not duplicate, registers the hash.
        """
        if sha256_hash in self.seen_hashes:
            return True, self.seen_hashes[sha256_hash]
        self.seen_hashes[sha256_hash] = sample_id
        return False, None


class NearDuplicateChecker:
    """
    Screens for near-duplicate photographic bursts using perceptual difference hashing.
    Default threshold: Hamming distance <= 4 bits out of 64 bits.
    """
    def __init__(self, hamming_threshold: int = 4):
        self.hamming_threshold = hamming_threshold
        self.hash_registry: List[Tuple[str, str]] = []  # (sample_id, phash_hex)

    def find_near_duplicates(self, phash_hex: str, current_sample_id: str) -> List[Tuple[str, int]]:
        """
        Compares candidate hash against registered samples.
        Returns list of (matched_sample_id, distance).
        """
        matches = []
        for reg_sample_id, reg_hash in self.hash_registry:
            if reg_sample_id == current_sample_id:
                continue
            dist = hamming_distance_hex(phash_hex, reg_hash)
            if dist <= self.hamming_threshold:
                matches.append((reg_sample_id, dist))
        return matches

    def register(self, sample_id: str, phash_hex: str):
        self.hash_registry.append((sample_id, phash_hex))
