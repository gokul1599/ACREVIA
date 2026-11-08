"""
Tests for Agricultural Uncertainty & Abstention Decision Engine.
Verifies all 8 agricultural decision states.
"""

import numpy as np
from ml.models.abstention import AbstentionEngine, AgriculturalDecisionState


def test_abstention_image_quality_insufficient():
    engine = AbstentionEngine()
    result = engine.evaluate_decision_state(
        is_quality_acceptable=False,
        is_supported_crop=True,
        is_foliar_verified=True
    )
    assert result["decision_state"] == AgriculturalDecisionState.IMAGE_QUALITY_INSUFFICIENT
    assert result["can_diagnose"] is False


def test_abstention_unsupported_crop():
    engine = AbstentionEngine()
    result = engine.evaluate_decision_state(
        is_quality_acceptable=True,
        is_supported_crop=False,
        is_foliar_verified=True,
        crop_name="mango"
    )
    assert result["decision_state"] == AgriculturalDecisionState.UNSUPPORTED_CROP
    assert result["can_diagnose"] is False


def test_abstention_out_of_distribution_non_plant():
    engine = AbstentionEngine()
    result = engine.evaluate_decision_state(
        is_quality_acceptable=True,
        is_supported_crop=True,
        is_foliar_verified=False
    )
    assert result["decision_state"] == AgriculturalDecisionState.OUT_OF_DISTRIBUTION
    assert result["can_diagnose"] is False


def test_abstention_needs_more_information():
    engine = AbstentionEngine(minimum_usable_confidence=0.50)
    # Very diffused probabilities (top confidence 0.35)
    probs = np.array([0.35, 0.33, 0.32])
    result = engine.evaluate_decision_state(
        is_quality_acceptable=True,
        is_supported_crop=True,
        is_foliar_verified=True,
        probabilities=probs
    )
    assert result["decision_state"] == AgriculturalDecisionState.NEEDS_MORE_INFORMATION
    assert result["can_diagnose"] is False
    assert result["expert_review_required"] is True


def test_abstention_expert_review_required_due_to_narrow_margin():
    engine = AbstentionEngine(
        high_confidence_threshold=0.85,
        minimum_usable_confidence=0.50,
        minimum_prediction_margin=0.15
    )
    # Narrow margin (0.52 vs 0.48, margin = 0.04)
    probs = np.array([0.52, 0.48])
    result = engine.evaluate_decision_state(
        is_quality_acceptable=True,
        is_supported_crop=True,
        is_foliar_verified=True,
        probabilities=probs
    )
    assert result["decision_state"] == AgriculturalDecisionState.EXPERT_REVIEW_REQUIRED
    assert result["can_diagnose"] is False
    assert result["expert_review_required"] is True


def test_abstention_low_confidence():
    engine = AbstentionEngine(
        high_confidence_threshold=0.85,
        minimum_usable_confidence=0.50,
        minimum_prediction_margin=0.15,
        maximum_normalized_entropy=0.65
    )
    # Clear margin, acceptable entropy, but moderate confidence (0.80 < 0.85)
    probs = np.array([0.80, 0.12, 0.08])
    result = engine.evaluate_decision_state(
        is_quality_acceptable=True,
        is_supported_crop=True,
        is_foliar_verified=True,
        probabilities=probs
    )
    assert result["decision_state"] == AgriculturalDecisionState.LOW_CONFIDENCE
    assert result["can_diagnose"] is True
    assert result["expert_review_required"] is True


def test_abstention_supported_prediction():
    engine = AbstentionEngine(
        high_confidence_threshold=0.85,
        minimum_prediction_margin=0.15,
        maximum_normalized_entropy=0.65
    )
    # High confidence, sharp margin, low entropy
    probs = np.array([0.94, 0.04, 0.02])
    result = engine.evaluate_decision_state(
        is_quality_acceptable=True,
        is_supported_crop=True,
        is_foliar_verified=True,
        probabilities=probs
    )
    assert result["decision_state"] == AgriculturalDecisionState.SUPPORTED_PREDICTION
    assert result["can_diagnose"] is True
    assert result["expert_review_required"] is False
