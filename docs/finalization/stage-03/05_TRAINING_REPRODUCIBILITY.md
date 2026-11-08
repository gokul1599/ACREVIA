# ACREVIA — STAGE 03 TRAINING REPRODUCIBILITY REPORT
## Loss Formulations, Optimization Dynamics & Deterministic Pipelines

**Document Reference:** `docs/finalization/stage-03/05_TRAINING_REPRODUCIBILITY.md`  
**Stage:** 03 — Advanced Computer Vision & ML Inference Validation  
**Primary Files:** [`ml/training/losses.py`](file:///c:/Users/gokul/OneDrive/Documents/projects/ml/training/losses.py), [`tests/ml/test_losses.py`](file:///c:/Users/gokul/OneDrive/Documents/projects/tests/ml/test_losses.py), [`tests/ml/test_training_smoke.py`](file:///c:/Users/gokul/OneDrive/Documents/projects/tests/ml/test_training_smoke.py)  

---

### 1. Training Loss Formulations

Agricultural pathology datasets exhibit natural long-tail class distributions: healthy leaves are easily collected, while acute pest manifestations (such as Pink Bollworm or Black Thrips) are relatively scarce. Conventional cross-entropy loss causes standard networks to collapse towards majority classes and output overconfident probabilities. 

ACREVIA implements three mathematically sound loss formulations to address these challenges:

#### 1.1 Focal Loss
Downweights well-classified easy background examples and concentrates gradient updates on ambiguous, hard-to-diagnose leaf lesions:
$$\text{FL}(p_t) = -\alpha_t (1 - p_t)^\gamma \log(p_t)$$
where $\gamma = 2.0$ is the focusing parameter and $\alpha = 0.25$ is the class-balance weight. As verified in `test_focal_loss_downweights_easy_examples`, loss for an easy sample ($p_t = 0.95$) is dampened by a factor $> 400\times$ compared to a difficult sample ($p_t = 0.10$).

#### 1.2 Class-Balanced Loss (Cui et al.)
Calculates class weights based on the effective number of samples rather than raw inverse frequencies:
$$E_n = \frac{1 - \beta^n}{1 - \beta}, \quad W_c = \frac{1}{E_{n_c}}$$
where $\beta = 0.999$. This formulation accounts for information overlap among correlated foliar images from the same farm plot.

#### 1.3 Label Smoothing Cross-Entropy
Regularizes the network to prevent saturated logits and extreme confidence scores:
$$y'_k = (1 - \epsilon) y_k + \frac{\epsilon}{K}$$
where $\epsilon = 0.10$ and $K$ is the number of crop classes. This serves as an initial regularizer before post-hoc temperature scaling.

---

### 2. Optimization Configuration

| Parameter | Value | Rationale |
|---|---|---|
| **Base Optimizer** | AdamW | Decoupled weight decay provides superior generalization on MobileNetV3 |
| **Initial Learning Rate** | $1 \times 10^{-3}$ (Heads), $1 \times 10^{-4}$ (Backbone) | Discriminative learning rates preserve pretrained features |
| **Weight Decay** | $1 \times 10^{-4}$ | Regularization against parameter explosion |
| **Learning Rate Schedule** | Cosine Annealing with Warmup | 5-epoch linear warmup followed by half-period cosine decay |
| **Gradient Clipping** | $\text{Norm} \le 1.0$ | Prevents exploding gradients during multi-head backpropagation |
| **Random Seed** | `42` | Strictly seeded across PyTorch, NumPy, Python standard random, and cuDNN |
| **Batch Size** | 32 | Fits comfortably within memory budget |

---

### 3. Reproducibility & Checkpointing Verification

In [`tests/ml/test_training_smoke.py`](file:///c:/Users/gokul/OneDrive/Documents/projects/tests/ml/test_training_smoke.py):
- The training smoke test initializes a reproducible multi-crop classifier with seed 42.
- Executes 2 complete epochs with forward pass, loss calculation, backward propagation, and optimizer step.
- Verifies that model loss monotonically decreases on synthetic batches.
- Serializes checkpoint containing `model_state_dict`, `optimizer_state_dict`, `epoch`, `best_f1`, and `taxonomy_version`.
- Reloads checkpoint into a fresh model instance and asserts bit-for-bit weight equivalence (`torch.allclose`), confirming checkpoint reproducibility.
