"""
KisanVision - Manifest Generator & Taxonomy Normalizer.
Generates standardized dataset manifests and maps source labels to canonical KisanVision taxonomy.
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional
import yaml

from ml.datasets.manifests.manifest_schema import (
    UnifiedSampleManifest,
    ImageQualityStatus,
    AnnotationStatus,
    CollectionContext,
    ConsentStatus
)
from ml.datasets.ingestion.image_reader import ImageReader, ImageReadResult


class TaxonomyNormalizer:
    """Loads version-controlled taxonomy definitions and validates class identifiers."""
    def __init__(self, taxonomy_dir: Path):
        self.taxonomy_dir = taxonomy_dir
        self.crop_taxonomies: Dict[str, Dict[str, Any]] = {}
        self.valid_class_ids: set = set()
        self._load_taxonomies()

    def _load_taxonomies(self):
        for crop in ["cotton", "rice", "chilli"]:
            file_path = self.taxonomy_dir / f"{crop}_taxonomy.yaml"
            if file_path.exists():
                with open(file_path, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                    self.crop_taxonomies[crop] = data
                    for item in data.get("classes", []):
                        self.valid_class_ids.add(item["class_id"])
                        
        # Include generic non-crop class
        self.valid_class_ids.add("GENERIC_NON_CROP_OR_BACKGROUND")

    def is_valid_class(self, class_id: str) -> bool:
        return class_id in self.valid_class_ids

    def normalize(self, crop: str, raw_label: str) -> str:
        """
        Maps known public dataset labels to canonical KisanVision classes.
        Fallback to generic unknown if not mapped.
        """
        # Exact match check
        if raw_label in self.valid_class_ids:
            return raw_label
            
        clean_label = raw_label.strip().lower().replace(" ", "_")
        
        # PlantVillage / Public dataset mappings
        mappings = {
            # Chilli / Pepper mappings
            "pepper__bell___bacterial_spot": "CHILLI_CERCOSPORA_SPOT",  # Closest foliar bacterial/fungal spot
            "pepper__bell___healthy": "CHILLI_HEALTHY",
            "chilli_healthy": "CHILLI_HEALTHY",
            "chilli_anthracnose": "CHILLI_ANTHRACNOSE_FRUIT_ROT",
            "chilli_leaf_curl": "CHILLI_LEAF_CURL_VIRUS",
            "chilli_thrips": "CHILLI_BLACK_THRIPS",
            "chilli_mites": "CHILLI_YELLOW_MITE",
            
            # Rice mappings
            "rice_blast": "RICE_BLAST_LEAF",
            "bacterial_leaf_blight": "RICE_BACTERIAL_BLIGHT",
            "brown_spot": "RICE_BROWN_SPOT",
            "sheath_blight": "RICE_SHEATH_BLIGHT",
            "rice_healthy": "RICE_HEALTHY",
            
            # Cotton mappings
            "cotton_bacterial_blight": "COTTON_BACTERIAL_BLIGHT",
            "cotton_grey_mildew": "COTTON_GREY_MILDEW",
            "cotton_healthy": "COTTON_HEALTHY",
            "pink_bollworm": "COTTON_PINK_BOLLWORM",
            "cotton_leaf_curl": "COTTON_LEAF_CURL_VIRUS"
        }
        
        if clean_label in mappings:
            return mappings[clean_label]
            
        # Fallback to crop-specific unknown class
        unknown_map = {
            "cotton": "COTTON_UNKNOWN_CONDITION",
            "rice": "RICE_UNKNOWN_CONDITION",
            "chilli": "CHILLI_UNKNOWN_CONDITION"
        }
        return unknown_map.get(crop.lower(), "GENERIC_NON_CROP_OR_BACKGROUND")


class ManifestGenerator:
    """Processes source images, applies quality screening, and emits standardized manifests."""
    def __init__(self, normalizer: TaxonomyNormalizer):
        self.normalizer = normalizer

    def create_manifest(
        self,
        image_bytes: bytes,
        original_filename: str,
        relative_storage_path: str,
        dataset_id: str,
        source_name: str,
        source_url: str,
        license_identifier: str,
        crop: str,
        original_label: str,
        farm_group_id: str,
        variety: Optional[str] = None,
        plant_id: Optional[str] = None,
        capture_date: Optional[str] = None,
        collection_context: CollectionContext = CollectionContext.OPEN_FIELD,
        consent_status: ConsentStatus = ConsentStatus.PUBLIC_OPEN_ACCESS,
        quality_status: ImageQualityStatus = ImageQualityStatus.ACCEPTED,
        quality_metrics: Optional[Dict[str, Any]] = None
    ) -> UnifiedSampleManifest:
        
        read_result = ImageReader.read_from_bytes(image_bytes, file_name=original_filename)
        if not read_result.is_valid:
            raise ValueError(f"Cannot generate manifest for invalid image: {read_result.error_message}")
            
        normalized_label = self.normalizer.normalize(crop=crop, raw_label=original_label)
        
        metrics = read_result.metadata.copy()
        if quality_metrics:
            metrics.update(quality_metrics)

        manifest = UnifiedSampleManifest(
            dataset_id=dataset_id,
            source_name=source_name,
            source_url=source_url,
            license_identifier=license_identifier,
            image_path=relative_storage_path,
            original_filename=original_filename,
            image_hash=read_result.sha256_hash,
            phash=read_result.phash,
            crop=crop.lower(),
            variety=variety,
            original_label=original_label,
            normalized_label=normalized_label,
            taxonomy_version="1.0.0",
            annotation_status=AnnotationStatus.SOURCE_PROVIDED,
            image_quality_status=quality_status,
            collection_context=collection_context,
            capture_date=capture_date,
            plant_id=plant_id,
            farm_group_id=farm_group_id,
            consent_status=consent_status,
            dataset_version="v0.1.0-alpha",
            quality_metrics=metrics
        )
        return manifest
