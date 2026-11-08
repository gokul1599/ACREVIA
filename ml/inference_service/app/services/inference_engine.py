"""
KisanVision Inference Service - Central Diagnostic Engine.
Orchestrates validation, quality gating, OOD detection, ONNX execution,
calibrated probability estimation, and structured differential diagnosis creation.
"""

import time
import uuid
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional
import numpy as np
from PIL import Image

from ml.inference_service.app.core.config import config
from ml.inference_service.app.core.logging import logger
from ml.inference_service.app.schemas.response import (
    InferencePredictionResponse,
    CandidatePrediction
)
from ml.inference_service.app.validators.image_validator import ImageIngestionValidator
from ml.inference_service.app.preprocessing.transforms import InferencePreprocessor
from ml.inference_service.app.model_loader.loader import ModelArtifactLoader
from ml.models.abstention import AbstentionEngine, AgriculturalDecisionState
from ml.models.ood_detector import FoliarImageDetector
from ml.datasets.quality.quality_validator import ImageQualityValidator


class DedicatedInferenceEngine:
    """
    Production agricultural ML inference coordinator.
    """
    def __init__(self):
        self.loader = ModelArtifactLoader()
        self.preprocessor = InferencePreprocessor()
        self.quality_validator = ImageQualityValidator()
        self.foliar_detector = FoliarImageDetector()
        self.abstention_engine = AbstentionEngine(
            high_confidence_threshold=config.HIGH_CONFIDENCE_THRESHOLD,
            minimum_usable_confidence=config.MINIMUM_USABLE_CONFIDENCE,
            maximum_normalized_entropy=config.MAXIMUM_NORMALIZED_ENTROPY,
            minimum_prediction_margin=config.MINIMUM_PREDICTION_MARGIN
        )
        self.taxonomies: Dict[str, Dict[str, Any]] = {}
        self._load_taxonomies()

    def _load_taxonomies(self):
        """Loads bilingual agricultural taxonomy definitions."""
        tax_dir = Path(config.TAXONOMY_DIR)
        for crop in config.SUPPORTED_CROPS:
            tax_path = tax_dir / f"{crop}_taxonomy.yaml"
            if tax_path.exists():
                try:
                    with open(tax_path, "r", encoding="utf-8") as f:
                        self.taxonomies[crop] = yaml.safe_load(f)
                        logger.info(f"Loaded taxonomy for {crop}")
                except Exception as e:
                    logger.error(f"Error loading taxonomy for {crop}: {e}")

    def predict(
        self,
        image_bytes: bytes,
        crop_type: str,
        filename: str = "leaf.jpg",
        preferred_language: str = "en"
    ) -> InferencePredictionResponse:
        """
        Executes complete defensive diagnostic inference pipeline.
        """
        request_id = str(uuid.uuid4())
        timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ")
        crop_key = crop_type.lower().strip()
        is_supported_crop = crop_key in config.SUPPORTED_CROPS

        # 1. Validation & Safe Image Decompression
        try:
            pil_image, detected_mime = ImageIngestionValidator.validate_and_decode(image_bytes, filename)
        except ValueError as e:
            # Fatal input rejection
            return InferencePredictionResponse(
                request_id=request_id,
                timestamp=timestamp,
                status=AgriculturalDecisionState.PROCESSING_FAILED.value,
                crop=crop_key,
                predictions=[],
                uncertainty_status="INPUT_VALIDATION_ERROR",
                image_quality={"error": str(e)},
                ood_status={},
                model_version="none",
                taxonomy_version=config.TAXONOMY_VERSION,
                preprocessing_version=config.PREPROCESSING_VERSION,
                limitations=["Invalid or corrupted image payload."],
                next_steps=["Re-upload a valid JPEG or PNG file."],
                safety_guideline="No chemical advice issued for invalid inputs."
            )

        # 2. Image Quality Gate
        quality_eval = self.quality_validator.validate(pil_image)
        is_quality_acceptable = quality_eval.is_admissible_for_inference
        blur_metric = quality_eval.metrics.get("blur", {})
        exposure_metric = quality_eval.metrics.get("exposure", {})

        quality_data = {
            "overall_status": quality_eval.overall_status.value,
            "is_acceptable": is_quality_acceptable,
            "sharpness_score": round(float(blur_metric.get("sharpness_score", 0.0)), 2),
            "exposure_status": exposure_metric.get("status", "UNKNOWN"),
            "camera_guidance": quality_eval.reason_codes
        }

        # 3. Foliar Botanical Gate (Tier 1 OOD)
        foliar_eval = self.foliar_detector.analyze_foliar_content(pil_image)
        ood_data = {
            "is_foliar_verified": foliar_eval["is_foliar"],
            "foliar_pixel_ratio": foliar_eval["foliar_pixel_ratio"],
            "contrast_std": foliar_eval["contrast_std"],
            "validation_reason": foliar_eval["reason"]
        }

        # Early check for quality / crop / non-plant failure
        if not is_quality_acceptable or not is_supported_crop or not foliar_eval["is_foliar"]:
            decision = self.abstention_engine.evaluate_decision_state(
                is_quality_acceptable=is_quality_acceptable,
                is_supported_crop=is_supported_crop,
                is_foliar_verified=foliar_eval["is_foliar"],
                crop_name=crop_key
            )
            return InferencePredictionResponse(
                request_id=request_id,
                timestamp=timestamp,
                status=decision["decision_state"].value,
                crop=crop_key,
                predictions=[],
                uncertainty_status="ABSTAINED_PRE_INFERENCE",
                image_quality=quality_data,
                ood_status=ood_data,
                model_version=f"kisanvision_{crop_key}_mobilenet_v3_small_int8",
                taxonomy_version=config.TAXONOMY_VERSION,
                preprocessing_version=config.PREPROCESSING_VERSION,
                limitations=[decision["reason"]],
                next_steps=[decision["action_guidance"]],
                safety_guideline="Intervention withheld: input failed verification criteria."
            )

        # 4. Model Retrieval & Preprocessing
        session, manifest = self.loader.get_session(crop_key)
        input_tensor = self.preprocessor.preprocess(pil_image)

        # 5. ONNX Inference
        input_name = session.get_inputs()[0].name
        output_name = session.get_outputs()[0].name
        raw_logits = session.run([output_name], {input_name: input_tensor})[0][0]

        # 6. Temperature Calibration & Softmax
        temperature = float(manifest.get("temperature", 1.0))
        scaled_logits = raw_logits / max(temperature, 0.1)
        exp_logits = np.exp(scaled_logits - np.max(scaled_logits))
        probabilities = exp_logits / np.sum(exp_logits)

        # 7. Class Mapping
        tax_classes = {c.get("class_id", c.get("id")): c for c in self.taxonomies.get(crop_key, {}).get("classes", [])}
        class_names = manifest.get("class_names", list(tax_classes.keys()))
        if not class_names:
            class_names = [f"{crop_key}_class_{i}" for i in range(len(probabilities))]

        # 8. Decision State Evaluation (Tier 2 OOD / Uncertainty)
        decision = self.abstention_engine.evaluate_decision_state(
            is_quality_acceptable=True,
            is_supported_crop=True,
            is_foliar_verified=True,
            probabilities=probabilities,
            class_names=class_names,
            crop_name=crop_key
        )

        # 9. Format Differential Candidates
        sorted_indices = np.argsort(probabilities)[::-1]
        candidates: List[CandidatePrediction] = []
        for rank, idx in enumerate(sorted_indices[:min(3, len(probabilities))]):
            cid = class_names[idx]
            cinfo = tax_classes.get(cid, {})
            disp = cinfo.get("display_names", {})

            candidates.append(CandidatePrediction(
                rank=rank + 1,
                class_id=cid,
                display_name_en=disp.get("en", cinfo.get("name_en", cid.replace("_", " ").title())),
                display_name_te=disp.get("te", cinfo.get("name_te", cid.replace("_", " ").title())),
                display_name_hi=disp.get("hi", cinfo.get("name_hi", cid.replace("_", " ").title())),
                pathogen_or_cause=cinfo.get("scientific_name", cinfo.get("pathogen", None)),
                calibrated_probability=round(float(probabilities[idx]), 4),
                raw_score=round(float(raw_logits[idx]), 4)
            ))

        top1_conf = float(decision.get("confidence", candidates[0].calibrated_probability if candidates else 0.0))
        top1_score = float(raw_logits[sorted_indices[0]]) if len(raw_logits) > 0 else None

        safety = (
            "Mandatory CIBRC Compliance: All chemical interventions must adhere to registered Central "
            "Insecticides Board & Registration Committee guidelines and label instructions. "
            "Verify with your local Mandal Agricultural Officer (MAO) or KVK agronomist before application."
        )

        return InferencePredictionResponse(
            request_id=request_id,
            timestamp=timestamp,
            status=decision["decision_state"].value,
            crop=crop_key,
            predictions=candidates,
            model_score=round(top1_score, 4) if top1_score is not None else None,
            calibrated_probability=round(top1_conf, 4),
            uncertainty_status=decision["decision_state"].value,
            normalized_entropy=decision.get("normalized_entropy"),
            prediction_margin=decision.get("margin"),
            image_quality=quality_data,
            ood_status=ood_data,
            model_version=f"kisanvision_{crop_key}_mobilenet_v3_small_int8",
            taxonomy_version=config.TAXONOMY_VERSION,
            preprocessing_version=config.PREPROCESSING_VERSION,
            limitations=[decision["reason"]],
            next_steps=[decision["action_guidance"]],
            safety_guideline=safety
        )
