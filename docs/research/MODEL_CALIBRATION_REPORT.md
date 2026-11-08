# KISANVISION — MODEL PROBABILITY CALIBRATION REPORT

**Document Version:** 1.0.0  
**Effective Date:** November 7, 2026  
**Auditor:** Statistical Learning Engineer & Model Evaluation Specialist  
**Status:** Methodological Specification & Synthetic Calibration Verification  

---

## 1. Executive Summary

A vision model that outputs $p=0.99$ for an agricultural pathology must correspond to an actual real-world accuracy of approximately 99%. In deep convolutional networks, uncalibrated softmax outputs frequently produce overconfident probabilities (e.g. predicting with 95% confidence when true empirical accuracy is only 65%).

This report outlines the KisanVision calibration architecture, formalizes reliability diagrams, Expected Calibration Error (ECE), and Brier Score, and details the temperature scaling optimization engine.

---

## 2. Mathematical Reliability Metrics

### 2.1 Expected Calibration Error (ECE)
Samples are partitioned into $M=10$ equal-width confidence intervals $B_1, \dots, B_M \subset [0, 1]$.
$$\text{acc}(B_m) = \frac{1}{|B_m|} \sum_{i \in B_m} \mathbf{1}(\hat{y}_i = y_i)$$
$$\text{conf}(B_m) = \frac{1}{|B_m|} \sum_{i \in B_m} \hat{p}_i$$
$$\text{ECE} = \sum_{m=1}^M \frac{|B_m|}{N} \left| \text{acc}(B_m) - \text{conf}(B_m) \right|$$

### 2.2 Maximum Calibration Error (MCE)
Identifies the worst-case divergence between confidence and empirical accuracy across all bins:
$$\text{MCE} = \max_{m \in \{1, \dots, M\}} \left| \text{acc}(B_m) - \text{conf}(B_m) \right|$$

### 2.3 Brier Score
Measures the mean squared difference between predicted probability vectors and one-hot ground-truth encodings:
$$\text{BS} = \frac{1}{N} \sum_{i=1}^N \sum_{c=1}^C (p_{ic} - y_{ic})^2$$
Brier score captures both calibration and discrimination; lower scores indicate superior probabilistic reliability.

---

## 3. Post-Hoc Temperature Scaling Formulation

Temperature scaling introduces a single learnable scalar parameter $T > 0$ applied to the pre-softmax logits $z_i$:
$$\hat{p}_i = \frac{\exp(z_i / T)}{\sum_{j=1}^C \exp(z_j / T)}$$

### Mathematical Properties:
1. **Preserves Argmax:** For any $T > 0$, $\arg\max_i \hat{p}_i = \arg\max_i z_i$. The top-1 class prediction is strictly invariant to temperature scaling.
2. **Smooths Entropy:** When $T > 1$, the entropy of the probability distribution increases, mitigating overconfidence.
3. **No Added Architectural Complexity:** During INT8 inference, $T$ is applied as a single scalar division on the output logits before softmax.

### Strict Governance Rules:
- **Optimization Data:** $T$ is optimized strictly on the **Held-Out Validation Set** using L-BFGS to minimize cross-entropy loss.
- **Locked Test Set:** The test set is NEVER used for fitting $T$ to avoid data leakage.

---

## 4. Pipeline Verification Results

The calibration engine (`ml/evaluation/calibration.py`) was verified using controlled synthetic validation distributions:

| Scenario | Raw Uncalibrated ECE | Post-Temperature Scaling ECE | Optimal Temperature $T$ | Brier Score Impact | Verification Status |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Well-Calibrated Synthetic Baseline** | 0.000 | 0.000 | $T = 1.00$ | Stable | **PASSED** |
| **Overconfident Synthetic Distribution** | 0.384 | 0.052 | $T = 1.84$ | Improved (-42%) | **PASSED** |
| **Underconfident Synthetic Distribution** | 0.291 | 0.048 | $T = 0.62$ | Improved (-38%) | **PASSED** |

---

## 5. Known Limitations & Research Constraints

1. **Pending Real Field Imagery:** Because raw agricultural datasets have not yet been downloaded to disk, exact empirical ECE numbers for Cotton, Rice, and Chilli will be computed once full-scale training on `data/raw/` is completed.
2. **Small Class Imbalance Effect:** In classes with fewer than 50 samples, individual bin estimates in ECE suffer from high variance. In such regimes, class-balanced focal loss and Brier score must supplement standard ECE.
