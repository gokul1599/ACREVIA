"""
Tests for Agricultural Research Evaluation Metrics Calculator.
"""

from ml.evaluation.metrics import ResearchMetricsCalculator


def test_metrics_calculation():
    class_names = ["HEALTHY", "BLIGHT", "PEST"]
    y_true = [0, 1, 2, 1, 0, 2, 1, 0]
    y_pred = [0, 1, 2, 1, 0, 1, 1, 0]  # One mistake: true class 2 predicted as 1
    latencies = [15.2, 18.4, 14.1, 16.0, 17.2, 15.8, 14.9, 16.5]
    
    report = ResearchMetricsCalculator.compute_metrics(
        y_true=y_true,
        y_pred=y_pred,
        class_names=class_names,
        inference_latencies_ms=latencies
    )
    
    # 7 out of 8 correct = 0.875
    assert report["summary"]["accuracy"] == 0.875
    assert report["summary"]["total_samples"] == 8
    assert "HEALTHY" in report["per_class"]
    assert report["per_class"]["HEALTHY"]["precision"] == 1.0
    assert report["per_class"]["HEALTHY"]["recall"] == 1.0
    
    # Confusion matrix should be 3x3
    cm = report["confusion_matrix"]
    assert len(cm) == 3
    assert len(cm[0]) == 3
    
    # Latencies
    assert report["latency"]["mean_latency_ms"] > 10.0
