"""
Tests for KisanVision Agricultural Taxonomy validation.
"""

from pathlib import Path
import pytest
from ml.datasets.ingestion.manifest_generator import TaxonomyNormalizer


def test_taxonomy_loading_and_classes():
    taxonomy_dir = Path("ml/configs/taxonomy")
    assert taxonomy_dir.exists(), "Taxonomy directory must exist"
    
    normalizer = TaxonomyNormalizer(taxonomy_dir)
    
    # Check that key classes for all 3 crops exist
    assert normalizer.is_valid_class("COTTON_HEALTHY")
    assert normalizer.is_valid_class("COTTON_BACTERIAL_BLIGHT")
    assert normalizer.is_valid_class("COTTON_PINK_BOLLWORM")
    
    assert normalizer.is_valid_class("RICE_HEALTHY")
    assert normalizer.is_valid_class("RICE_BLAST_LEAF")
    assert normalizer.is_valid_class("RICE_BPH_HOPPERBURN")
    
    assert normalizer.is_valid_class("CHILLI_HEALTHY")
    assert normalizer.is_valid_class("CHILLI_BLACK_THRIPS")
    assert normalizer.is_valid_class("CHILLI_ANTHRACNOSE_FRUIT_ROT")
    
    assert normalizer.is_valid_class("GENERIC_NON_CROP_OR_BACKGROUND")


def test_taxonomy_normalization_mapping():
    taxonomy_dir = Path("ml/configs/taxonomy")
    normalizer = TaxonomyNormalizer(taxonomy_dir)
    
    # Test public label mappings
    assert normalizer.normalize("chilli", "pepper__bell___healthy") == "CHILLI_HEALTHY"
    assert normalizer.normalize("rice", "rice_blast") == "RICE_BLAST_LEAF"
    assert normalizer.normalize("cotton", "pink_bollworm") == "COTTON_PINK_BOLLWORM"
    
    # Test unmapped fallback to unknown
    assert normalizer.normalize("cotton", "unmapped_weird_spot") == "COTTON_UNKNOWN_CONDITION"
    assert normalizer.normalize("rice", "random_symptom") == "RICE_UNKNOWN_CONDITION"
