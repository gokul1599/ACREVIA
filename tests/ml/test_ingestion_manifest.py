"""
Tests for ImageReader and ManifestGenerator using synthetic in-memory fixtures.
"""

import io
from PIL import Image
from pathlib import Path
from ml.datasets.ingestion.image_reader import ImageReader, compute_sha256, compute_difference_hash
from ml.datasets.ingestion.manifest_generator import ManifestGenerator, TaxonomyNormalizer


def create_synthetic_image(width=128, height=128, color=(34, 139, 34)) -> bytes:
    """Creates an in-memory PNG image of given size and color."""
    img = Image.new("RGB", (width, height), color=color)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def test_image_reader_valid():
    raw_bytes = create_synthetic_image(100, 100)
    result = ImageReader.read_from_bytes(raw_bytes, file_name="synthetic_leaf.png")
    
    assert result.is_valid is True
    assert result.sha256_hash == compute_sha256(raw_bytes)
    assert len(result.phash) == 16  # 64-bit dHash represented as 16 hex chars
    assert result.metadata["width"] == 100
    assert result.metadata["height"] == 100
    assert result.metadata["format"] == "PNG"


def test_image_reader_corrupt():
    corrupt_bytes = b"NOT_A_VALID_IMAGE_HEADER_DATA_1234567890"
    result = ImageReader.read_from_bytes(corrupt_bytes, file_name="bad.jpg")
    
    assert result.is_valid is False
    assert "Corrupt" in result.error_message or "Unsupported" in result.error_message


def test_manifest_generator():
    normalizer = TaxonomyNormalizer(Path("ml/configs/taxonomy"))
    generator = ManifestGenerator(normalizer)
    raw_bytes = create_synthetic_image(128, 128)
    
    manifest = generator.create_manifest(
        image_bytes=raw_bytes,
        original_filename="cotton_sample_01.png",
        relative_storage_path="data/raw/cotton/cotton_sample_01.png",
        dataset_id="ds_test_v1",
        source_name="ICAR_CICR",
        source_url="https://cicr.icar.gov.in",
        license_identifier="CC-BY-4.0",
        crop="cotton",
        original_label="cotton_bacterial_blight",
        farm_group_id="mandal_warangal_farm_001"
    )
    
    assert manifest.normalized_label == "COTTON_BACTERIAL_BLIGHT"
    assert manifest.crop == "cotton"
    assert manifest.farm_group_id == "mandal_warangal_farm_001"
    assert manifest.image_hash == compute_sha256(raw_bytes)
