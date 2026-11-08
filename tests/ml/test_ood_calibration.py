"""
Tests for Calibration Metrics (ECE/MCE), Temperature Scaling, and OOD Detection.
"""

import numpy as np
import torch
from PIL import Image
from ml.evaluation.calibration import CalibrationEvaluator, TemperatureScaler
from ml.models.ood_detector import FoliarImageDetector, ModelUncertaintyAuditor


def test_ece_perfect_calibration():
    # Perfectly calibrated case: confidence = 1.0, accuracy = 1.0
    probabilities = np.array([
        [1.0, 0.0],
        [1.0, 0.0],
        [0.0, 1.0],
        [0.0, 1.0]
    ])
    labels = np.array([0, 0, 1, 1])

    result = CalibrationEvaluator.compute_ece(probabilities, labels, num_bins=10)
    assert result["expected_calibration_error"] == 0.0
    assert result["max_calibration_error"] == 0.0


def test_ece_uncalibrated_case():
    # Model is 100% confident on wrong predictions (severe miscalibration)
    probabilities = np.array([
        [0.99, 0.01],
        [0.99, 0.01],
        [0.01, 0.99],
        [0.01, 0.99]
    ])
    labels = np.array([1, 1, 0, 0])  # Actual is opposite

    result = CalibrationEvaluator.compute_ece(probabilities, labels, num_bins=10)
    assert result["expected_calibration_error"] > 0.90


def test_temperature_scaler():
    logits = torch.tensor([
        [5.0, 1.0],
        [4.0, 2.0],
        [1.0, 6.0],
        [2.0, 5.0]
    ], requires_grad=False)
    labels = torch.tensor([0, 0, 1, 1])

    scaler = TemperatureScaler(initial_temperature=1.0)
    opt_temp = scaler.fit(logits, labels, max_iter=20)
    assert opt_temp > 0.1

    calibrated_probs = scaler.calibrate(logits.numpy(), temperature=opt_temp)
    assert calibrated_probs.shape == (4, 2)
    assert np.allclose(np.sum(calibrated_probs, axis=1), 1.0)


def test_foliar_detector_natural_leaf():
    detector = FoliarImageDetector(min_foliar_ratio=0.10)
    
    # Create synthetic green leaf image (green > red and blue with natural gradient)
    np_img = np.zeros((224, 224, 3), dtype=np.uint8)
    np_img[:, :, 0] = 50   # Red
    np_img[:, :, 1] = 160  # Green
    np_img[:, :, 2] = 40   # Blue
    # Add texture noise
    noise = np.random.randint(-20, 20, (224, 224, 3))
    np_img = np.clip(np_img.astype(int) + noise, 0, 255).astype(np.uint8)
    
    leaf_img = Image.fromarray(np_img)
    result = detector.analyze_foliar_content(leaf_img)
    
    assert result["is_foliar"] is True
    assert result["foliar_pixel_ratio"] > 0.50
    assert result["reason"] == "VERIFIED_FOLIAR_CANOPY"


def test_foliar_detector_non_plant_rejection():
    detector = FoliarImageDetector(min_foliar_ratio=0.10)
    
    # Solid black/dark image (e.g. lens cap on or extreme dark object)
    dark_img = Image.new("RGB", (224, 224), (10, 10, 10))
    result = detector.analyze_foliar_content(dark_img)
    assert result["is_foliar"] is False

    # Blue metal surface (non-plant object)
    blue_img = Image.new("RGB", (224, 224), (20, 30, 200))
    result_blue = detector.analyze_foliar_content(blue_img)
    assert result_blue["is_foliar"] is False


def test_model_uncertainty_auditor():
    auditor = ModelUncertaintyAuditor(
        min_confidence_threshold=0.85,
        max_normalized_entropy=0.65,
        min_prediction_margin=0.15
    )
    classes = ["cotton_healthy", "cotton_bacterial_blight", "cotton_pink_bollworm"]

    # 1. High confidence sample
    confident_probs = np.array([0.92, 0.05, 0.03])
    rep_conf = auditor.evaluate_uncertainty(confident_probs, classes)
    assert rep_conf["status"] == "IN_DISTRIBUTION"
    assert rep_conf["top1_class"] == "cotton_healthy"
    assert rep_conf["prediction_margin"] > 0.80

    # 2. Ambiguous / high-entropy sample
    ambiguous_probs = np.array([0.35, 0.33, 0.32])
    rep_amb = auditor.evaluate_uncertainty(ambiguous_probs, classes)
    assert rep_amb["status"] in ["LOW_CONFIDENCE", "UNCERTAIN_AMBIGUOUS"]
    assert rep_amb["action"] in ["EXPERT_REVIEW_RECOMMENDED", "DIFFERENTIAL_DIAGNOSIS_REQUIRED"]
    assert len(rep_amb["differential_candidates"]) == 3
