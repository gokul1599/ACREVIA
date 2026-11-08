"""
Unit & Integration Tests for ACREVIA Dataset Archival & Verification.
Stage 02 Remediation (TASK-S02-01).
"""

import tempfile
import pytest
from pathlib import Path

from ml.data.archival_manager import (
    DatasetArchivalManager,
    LocalStorageAdapter,
    DatasetInventoryItem,
)


@pytest.fixture
def sample_dataset_dir():
    """Creates a temporary synthetic image dataset structure."""
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        # Cotton folder
        cotton_dir = root / "cotton" / "COTTON_BOLLWORM"
        cotton_dir.mkdir(parents=True)
        img1 = cotton_dir / "leaf_01.jpg"
        img1.write_bytes(b"JPEG_HEADER_SAMPLE_COTTON_DATA_12345")
        img2 = cotton_dir / "leaf_02.png"
        img2.write_bytes(b"PNG_HEADER_SAMPLE_COTTON_DATA_67890")

        # Rice folder
        rice_dir = root / "rice" / "RICE_BLAST_LEAF"
        rice_dir.mkdir(parents=True)
        img3 = rice_dir / "paddy_01.jpg"
        img3.write_bytes(b"JPEG_HEADER_SAMPLE_RICE_BLAST_54321")

        # Non-image file to be ignored
        (root / "readme.txt").write_text("dataset info")

        yield root


def test_inventory_dataset_discovery(sample_dataset_dir):
    items = DatasetArchivalManager.inventory_dataset(sample_dataset_dir)
    assert len(items) == 3

    # Check cotton items
    cotton_items = [i for i in items if i.crop == "cotton"]
    assert len(cotton_items) == 2
    assert cotton_items[0].class_id == "COTTON_BOLLWORM"
    assert cotton_items[0].sha256_hash != ""

    # Check rice items
    rice_items = [i for i in items if i.crop == "rice"]
    assert len(rice_items) == 1
    assert rice_items[0].class_id == "RICE_BLAST_LEAF"


def test_create_manifest_deterministic(sample_dataset_dir):
    items1 = DatasetArchivalManager.inventory_dataset(sample_dataset_dir)
    items2 = DatasetArchivalManager.inventory_dataset(sample_dataset_dir)

    manifest1 = DatasetArchivalManager.create_manifest(items1, "test-ds", "v1.0")
    manifest2 = DatasetArchivalManager.create_manifest(items2, "test-ds", "v1.0")

    assert manifest1.manifest_sha256 == manifest2.manifest_sha256
    assert manifest1.total_files == 3
    assert "COTTON_BOLLWORM" in manifest1.classes_included
    assert "RICE_BLAST_LEAF" in manifest1.classes_included


def test_archive_dataset_dry_run(sample_dataset_dir):
    with tempfile.TemporaryDirectory() as storage_dir:
        adapter = LocalStorageAdapter(Path(storage_dir))
        items = DatasetArchivalManager.inventory_dataset(sample_dataset_dir)
        manifest = DatasetArchivalManager.create_manifest(items, "test-ds", "v1.0")

        result = DatasetArchivalManager.archive_dataset(
            sample_dataset_dir, items, manifest, adapter, dry_run=True
        )

        assert result["dry_run"] is True
        assert result["total_files_planned"] == 3
        # Storage directory should remain empty
        assert len(adapter.list_objects("")) == 0


def test_archive_dataset_execution_and_verification(sample_dataset_dir):
    with tempfile.TemporaryDirectory() as storage_dir:
        adapter = LocalStorageAdapter(Path(storage_dir))
        items = DatasetArchivalManager.inventory_dataset(sample_dataset_dir)
        manifest = DatasetArchivalManager.create_manifest(items, "test-ds", "v1.0")

        # Execute archival
        result = DatasetArchivalManager.archive_dataset(
            sample_dataset_dir, items, manifest, adapter, dry_run=False
        )

        assert result["dry_run"] is False
        assert result["files_archived"] == 3

        # Verify archive integrity
        verification = DatasetArchivalManager.verify_archive(manifest, adapter)
        assert verification.is_valid is True
        assert verification.verified_files == 3
        assert len(verification.missing_files) == 0
        assert len(verification.checksum_mismatches) == 0


def test_archive_tamper_and_missing_detection(sample_dataset_dir):
    with tempfile.TemporaryDirectory() as storage_dir:
        storage_path = Path(storage_dir)
        adapter = LocalStorageAdapter(storage_path)
        items = DatasetArchivalManager.inventory_dataset(sample_dataset_dir)
        manifest = DatasetArchivalManager.create_manifest(items, "test-ds", "v1.0")

        DatasetArchivalManager.archive_dataset(
            sample_dataset_dir, items, manifest, adapter, dry_run=False
        )

        # 1. Test tampering (corrupt one file)
        first_rel = items[0].relative_path
        stored_file = storage_path / manifest.storage_prefix / "raw" / first_rel
        assert stored_file.exists()
        stored_file.write_bytes(b"TAMPERED_CONTENT_MALICIOUS_BYTE")

        verification = DatasetArchivalManager.verify_archive(manifest, adapter)
        assert verification.is_valid is False
        assert len(verification.checksum_mismatches) == 1

        # 2. Test missing file
        stored_file.unlink()
        verification2 = DatasetArchivalManager.verify_archive(manifest, adapter)
        assert verification2.is_valid is False
        assert len(verification2.missing_files) == 1


def test_path_traversal_protection():
    with tempfile.TemporaryDirectory() as storage_dir:
        adapter = LocalStorageAdapter(Path(storage_dir))

        with pytest.raises(ValueError, match="path traversal detected"):
            adapter.put_object("../malicious.txt", b"evil")

        with pytest.raises(ValueError, match="path traversal detected"):
            adapter.get_object("sub/../../escape.txt")
