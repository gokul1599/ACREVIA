"""
KisanVision - Evaluation & Research Metrics Calculator.
Computes comprehensive Macro/Weighted F1, Confusion Matrix, and Inference Latency.
"""

from typing import List, Dict, Any, Optional
import numpy as np
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix
)


class ResearchMetricsCalculator:
    """
    Standardized metrics evaluator adhering to agricultural AI research reporting rules.
    """
    @staticmethod
    def compute_metrics(
        y_true: List[int],
        y_pred: List[int],
        class_names: List[str],
        inference_latencies_ms: Optional[List[float]] = None
    ) -> Dict[str, Any]:
        
        y_true_arr = np.array(y_true)
        y_pred_arr = np.array(y_pred)
        num_classes = len(class_names)
        
        # Overall Accuracy
        acc = float(accuracy_score(y_true_arr, y_pred_arr))
        
        # Macro and Weighted Scores
        macro_f1 = float(f1_score(y_true_arr, y_pred_arr, average="macro", zero_division=0))
        weighted_f1 = float(f1_score(y_true_arr, y_pred_arr, average="weighted", zero_division=0))
        macro_precision = float(precision_score(y_true_arr, y_pred_arr, average="macro", zero_division=0))
        macro_recall = float(recall_score(y_true_arr, y_pred_arr, average="macro", zero_division=0))
        
        # Per-Class Metrics
        per_class_precision = precision_score(y_true_arr, y_pred_arr, average=None, labels=range(num_classes), zero_division=0)
        per_class_recall = recall_score(y_true_arr, y_pred_arr, average=None, labels=range(num_classes), zero_division=0)
        per_class_f1 = f1_score(y_true_arr, y_pred_arr, average=None, labels=range(num_classes), zero_division=0)
        
        # Class Counts
        unique, counts = np.unique(y_true_arr, return_counts=True)
        counts_dict = {class_names[i]: 0 for i in range(num_classes)}
        for u, c in zip(unique, counts):
            if u < num_classes:
                counts_dict[class_names[u]] = int(c)

        per_class_report = {}
        for i, name in enumerate(class_names):
            per_class_report[name] = {
                "precision": round(float(per_class_precision[i]), 4),
                "recall": round(float(per_class_recall[i]), 4),
                "f1_score": round(float(per_class_f1[i]), 4),
                "support_count": counts_dict.get(name, 0)
            }

        # Confusion Matrix
        cm = confusion_matrix(y_true_arr, y_pred_arr, labels=range(num_classes)).tolist()

        # Latency statistics
        latency_stats = {}
        if inference_latencies_ms:
            lat_arr = np.array(inference_latencies_ms)
            latency_stats = {
                "mean_latency_ms": round(float(np.mean(lat_arr)), 2),
                "median_latency_ms": round(float(np.median(lat_arr)), 2),
                "p95_latency_ms": round(float(np.percentile(lat_arr, 95)), 2),
                "p99_latency_ms": round(float(np.percentile(lat_arr, 99)), 2),
                "sample_count": len(inference_latencies_ms)
            }

        return {
            "summary": {
                "accuracy": round(acc, 4),
                "macro_f1": round(macro_f1, 4),
                "weighted_f1": round(weighted_f1, 4),
                "macro_precision": round(macro_precision, 4),
                "macro_recall": round(macro_recall, 4),
                "total_samples": len(y_true)
            },
            "per_class": per_class_report,
            "confusion_matrix": cm,
            "latency": latency_stats
        }
