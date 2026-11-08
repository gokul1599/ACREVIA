# KisanVision — Model Evaluation & Research Metrics

This package provides standardized metrics computation following strict agricultural AI reporting guidelines.

---

## Metric Outputs

1. **Overall Accuracy:** Standard classification accuracy.
2. **Macro F1 Score:** Unweighted mean of class F1 scores (prevents majority-class bias).
3. **Weighted F1 Score:** Support-weighted mean F1 score.
4. **Per-Class Breakdown:** Precision, Recall, F1-Score, and Support Count per class.
5. **Confusion Matrix:** Full $N \times N$ integer matrix.
6. **Inference Latency Profile:** Mean, median, P95, and P99 latency percentiles in milliseconds.
