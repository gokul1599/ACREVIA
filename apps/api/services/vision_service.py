"""
KisanVision API - Agricultural Vision Diagnostic Service.
Orchestrates image quality checks, foliar validation, INT8 ONNX inference,
multilingual taxonomy mapping, and CIBRC chemical safety advisories.
"""

import io
import time
import uuid
import yaml
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from PIL import Image

from apps.api.config import settings
from apps.api.schemas.vision import (
    VisionDiagnosisResponse,
    DifferentialCandidate,
    ImageQualityAssessment,
    FoliarVegetationAssessment,
    ModelInfoResponse
)
from ml.models.onnx_inference import ONNXInferenceEngine
from ml.models.classifier import KisanVisionClassifier
from ml.models.export_onnx import ONNXModelExporter
from ml.models.ood_detector import FoliarImageDetector
from ml.datasets.quality.quality_validator import ImageQualityValidator

logger = logging.getLogger("kisanvision.api.vision_service")


class VisionDiagnosticService:
    """
    High-level orchestrator for CropVision inference requests.
    """
    def __init__(self):
        self.taxonomies: Dict[str, Dict[str, Any]] = {}
        self.inference_engines: Dict[str, ONNXInferenceEngine] = {}
        self.quality_validator = ImageQualityValidator()
        self.foliar_detector = FoliarImageDetector()
        self._load_taxonomies()
        self._initialize_engines()

    def _load_taxonomies(self):
        """Loads crop taxonomies from YAML configuration files."""
        tax_dir = Path(settings.TAXONOMY_DIR)
        for crop in settings.SUPPORTED_CROPS:
            yaml_path = tax_dir / f"{crop}_taxonomy.yaml"
            if yaml_path.exists():
                try:
                    with open(yaml_path, "r", encoding="utf-8") as f:
                        data = yaml.safe_load(f)
                        self.taxonomies[crop] = data
                        logger.info(f"Loaded taxonomy for {crop}: {len(data.get('classes', []))} classes")
                except Exception as e:
                    logger.error(f"Failed to load taxonomy for {crop}: {e}")

    def _initialize_engines(self):
        """Initializes or exports ONNX inference engines for supported crops."""
        models_dir = Path(settings.MODELS_DIR)
        models_dir.mkdir(parents=True, exist_ok=True)
        exporter = ONNXModelExporter(export_dir=str(models_dir))

        for crop in settings.SUPPORTED_CROPS:
            tax = self.taxonomies.get(crop, {})
            classes = tax.get("classes", [])
            class_ids = [c.get("class_id", c.get("id")) for c in classes] if classes else [f"{crop}_healthy", f"{crop}_disease_1"]

            model_name = f"kisanvision_{crop}_mobilenet_v3_small"
            int8_path = models_dir / f"{model_name}_int8.onnx"
            manifest_path = models_dir / f"{model_name}_manifest.json"

            # If pre-quantized model does not exist on disk, export clean baseline model
            if not int8_path.exists():
                logger.info(f"Generating optimized INT8 baseline ONNX model for {crop}...")
                pt_model = KisanVisionClassifier(
                    architecture="mobilenet_v3_small",
                    num_classes=len(class_ids),
                    pretrained=False
                )
                exporter.export_and_quantize(
                    model=pt_model,
                    model_name=model_name,
                    class_names=class_ids,
                    crop_type=crop
                )

            # Load into runtime engine
            try:
                self.inference_engines[crop] = ONNXInferenceEngine(
                    model_path=int8_path,
                    manifest_path=manifest_path,
                    crop_type=crop
                )
                logger.info(f"Initialized ONNX engine for crop '{crop}' from {int8_path}")
            except Exception as e:
                logger.error(f"Failed to initialize engine for {crop}: {e}")

    def get_models_metadata(self) -> List[ModelInfoResponse]:
        """Returns metadata for all available vision models."""
        metadata = []
        for crop, engine in self.inference_engines.items():
            size_mb = engine.model_path.stat().st_size / (1024 * 1024) if engine.model_path.exists() else 0.0
            metadata.append(ModelInfoResponse(
                crop_type=crop,
                architecture=engine.manifest.get("architecture", "mobilenet_v3_small"),
                num_classes=len(engine.class_names),
                quantization="INT8_DYNAMIC",
                engine_provider="ONNXRuntime_CPU",
                model_size_mb=round(size_mb, 2),
                inference_device="AMD_Ryzen_CPU",
                status="ACTIVE"
            ))
        return metadata

    def diagnose_image(
        self,
        image_bytes: bytes,
        crop_type: str,
        preferred_language: str = "en"
    ) -> VisionDiagnosisResponse:
        """
        Executes end-to-end diagnostic workflow:
        Image Decoding -> Quality Filter -> Foliar Check -> ONNX Inference -> Safety Advice.
        """
        request_id = str(uuid.uuid4())
        timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ")
        crop_key = crop_type.lower().strip()

        if crop_key not in self.inference_engines:
            raise ValueError(f"Crop '{crop_type}' is not supported. Choose from: {settings.SUPPORTED_CROPS}")

        # 1. Decode Image Bytes
        try:
            pil_image = Image.open(io.BytesIO(image_bytes))
            pil_image.load()
        except Exception as e:
            raise ValueError(f"Corrupt or unreadable image bytes: {str(e)}")

        # 2. Image Quality Gate
        quality_eval = self.quality_validator.validate(pil_image)
        is_acceptable = quality_eval.is_admissible_for_inference

        blur_metric = quality_eval.metrics.get("blur", {})
        exposure_metric = quality_eval.metrics.get("exposure", {})

        sharpness_val = float(blur_metric.get("sharpness_score", 0.0))
        exposure_status = exposure_metric.get("status", "UNKNOWN")

        # Map reason codes to actionable agronomic capture recommendations
        guidance = []
        if "SEVERE_BLUR_OUT_OF_FOCUS" in quality_eval.reason_codes:
            guidance.append("Image is out of focus. Hold phone steady 15-20cm from the leaf surface.")
        if "UNDEREXPOSED_TOO_DARK" in quality_eval.reason_codes:
            guidance.append("Leaf is in deep shadow. Move to indirect natural daylight.")
        if "OVEREXPOSED_TOO_BRIGHT" in quality_eval.reason_codes:
            guidance.append("Intense direct solar glare. Shade leaf with hand or body.")
        if not guidance and not is_acceptable:
            guidance.extend(quality_eval.reason_codes)

        quality_report = ImageQualityAssessment(
            status=quality_eval.overall_status.value,
            is_acceptable=is_acceptable,
            sharpness_score=round(sharpness_val, 2),
            exposure_status=exposure_status,
            corrective_guidance=guidance
        )

        # Reject if image is blurry or severely underexposed/overexposed
        if not is_acceptable:
            return VisionDiagnosisResponse(
                request_id=request_id,
                timestamp=timestamp,
                crop_type=crop_key,
                status="QUALITY_REJECTED",
                triage_level="RETAKE_IMAGE",
                primary_diagnosis=None,
                differential_candidates=[],
                normalized_entropy=None,
                prediction_margin=None,
                image_quality=quality_report,
                foliar_assessment=None,
                safety_guideline="Image quality insufficient for agricultural chemical diagnosis.",
                expert_review_recommended=False,
                message="Image is blurred or poorly illuminated. Please capture a clear leaf photo following recommendations."
            )

        # 3. Foliar Vegetation Gate (Tier 1 OOD)
        foliar_eval = self.foliar_detector.analyze_foliar_content(pil_image)
        foliar_assessment = FoliarVegetationAssessment(
            is_foliar=foliar_eval["is_foliar"],
            foliar_pixel_ratio=foliar_eval["foliar_pixel_ratio"],
            contrast_std=foliar_eval["contrast_std"],
            validation_reason=foliar_eval["reason"]
        )

        if not foliar_eval["is_foliar"]:
            return VisionDiagnosisResponse(
                request_id=request_id,
                timestamp=timestamp,
                crop_type=crop_key,
                status="OOD_NON_PLANT",
                triage_level="RETAKE_IMAGE",
                primary_diagnosis=None,
                differential_candidates=[],
                normalized_entropy=None,
                prediction_margin=None,
                image_quality=quality_report,
                foliar_assessment=foliar_assessment,
                safety_guideline="Non-foliar image detected. Chemical recommendations withheld.",
                expert_review_recommended=False,
                message="Image lacks characteristic foliar vegetation. Please upload a clear photo of the crop leaf."
            )

        # 4. INT8 ONNX Model Inference
        engine = self.inference_engines[crop_key]
        prediction_result = engine.predict(pil_image)

        # 5. Multilingual Taxonomy Resolution
        tax_classes = {c.get("class_id", c.get("id")): c for c in self.taxonomies.get(crop_key, {}).get("classes", [])}
        
        candidates: List[DifferentialCandidate] = []
        for cand in prediction_result.get("differential_candidates", []):
            cid = cand["class_name"]
            cinfo = tax_classes.get(cid, {})
            disp = cinfo.get("display_names", {})
            
            candidates.append(DifferentialCandidate(
                rank=cand["rank"],
                class_id=cid,
                display_name_en=disp.get("en", cinfo.get("name_en", cid.replace("_", " ").title())),
                display_name_te=disp.get("te", cinfo.get("name_te", cid.replace("_", " ").title())),
                display_name_hi=disp.get("hi", cinfo.get("name_hi", cid.replace("_", " ").title())),
                pathogen_or_cause=cinfo.get("scientific_name", cinfo.get("pathogen", None)),
                confidence=cand["confidence"]
            ))

        primary = candidates[0] if candidates else None

        # 6. Triage & Decision Gate
        status = prediction_result.get("status", "IN_DISTRIBUTION")
        action = prediction_result.get("action", "DIRECT_DIAGNOSIS")
        
        if status == "IN_DISTRIBUTION" and primary and primary.confidence >= settings.HIGH_CONFIDENCE_THRESHOLD:
            # Check if healthy or active pathology
            if "healthy" in primary.class_id.lower():
                triage = "MONITOR"
                diagnosis_status = "CONFIRMED_DIAGNOSIS"
            else:
                triage = "IMMEDIATE_ACTION"
                diagnosis_status = "CONFIRMED_DIAGNOSIS"
            expert_recommended = False
        elif status == "LOW_CONFIDENCE":
            triage = "EXPERT_REVIEW_RECOMMENDED"
            diagnosis_status = "LOW_CONFIDENCE"
            expert_recommended = True
        else:
            triage = "EXPERT_REVIEW_RECOMMENDED"
            diagnosis_status = "UNCERTAIN_AMBIGUOUS"
            expert_recommended = True

        safety_guideline = (
            "Mandatory CIBRC Compliance: All chemical interventions must adhere to registered Central "
            "Insecticides Board & Registration Committee guidelines and label instructions. "
            "Verify with your local Mandal Agricultural Officer (MAO) or KVK agronomist before application."
        )

        return VisionDiagnosisResponse(
            request_id=request_id,
            timestamp=timestamp,
            crop_type=crop_key,
            status=diagnosis_status,
            triage_level=triage,
            primary_diagnosis=primary,
            differential_candidates=candidates,
            normalized_entropy=prediction_result.get("diagnosis", {}).get("normalized_entropy"),
            prediction_margin=prediction_result.get("diagnosis", {}).get("prediction_margin"),
            image_quality=quality_report,
            foliar_assessment=foliar_assessment,
            safety_guideline=safety_guideline,
            expert_review_recommended=expert_recommended,
            message="Diagnostic assessment completed successfully."
        )


# Global singleton instance for the API process
vision_service = VisionDiagnosticService()
