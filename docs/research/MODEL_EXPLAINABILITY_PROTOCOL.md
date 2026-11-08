# KISANVISION — MODEL EXPLAINABILITY & VISUAL INSPECTION PROTOCOL

**Document Version:** 1.0.0  
**Effective Date:** November 7, 2026  
**Auditor:** Principal Computer Vision Research Scientist & Agricultural AI Specialist  
**Status:** Approved Research Protocol  

---

## 1. Objective & Scope

Visual attribution methods like Grad-CAM (Gradient-Weighted Class Activation Mapping) generate heatmaps highlighting the spatial regions that exerted the greatest numerical influence on a convolutional network's final output score.

In agricultural AI, explainability serves two distinct stakeholders:
1. **Machine Learning Engineers & Agronomists:** Auditing whether the model is focusing on legitimate foliar lesions versus spurious background artifacts (e.g. soil, fingers, weeds).
2. **Smallholder Farmers & Extension Workers:** Providing visual transparency so users understand which leaf region provoked the diagnostic concern.

---

## 2. Mathematical Formulation of Grad-CAM

Given an input image $x$ and a target convolutional layer with activation maps $A^k \in \mathbb{R}^{u \times v}$:

1. **Neuron Importance Weights:**
   $$\alpha_k^c = \frac{1}{Z} \sum_{i=1}^u \sum_{j=1}^v \frac{\partial y^c}{\partial A_{i, j}^k}$$
   where $y^c$ is the pre-softmax logit for class $c$, and $Z = u \cdot v$ is the spatial area.
2. **Rectified Linear Activation Map:**
   $$L_{\text{Grad-CAM}}^c = \text{ReLU}\left( \sum_k \alpha_k^c A^k \right)$$
   The $\text{ReLU}$ non-linearity ensures that only features positively contributing to class $c$ are retained, discarding negatively correlated inhibitory features.

---

## 3. Scientific Limitations & Ethical Cautions

> [!WARNING]
> **A Saliency Map is NOT Biological Proof:**
> A Grad-CAM heatmap illustrates statistical correlation inside a neural network; it does NOT establish biological causation, pathogen viability, or microscopic presence.

### Known Failure Modes & Confounders:
1. **Background Weed Confounding:** If training images of Rice Brown Spot frequently contained background duckweed (*Lemna minor*), the heatmap may light up on the duckweed rather than the foliar rice lesion.
2. **Farmer Finger / Hand Artifact:** Saliency maps often highlight a farmer's thumb holding the leaf because the contrasting skin tone provides strong edge gradients.
3. **Specular Solar Glint:** Highlights on waxy cotton leaves frequently attract spurious gradient activations.
4. **Sanity Check Failures (Adebayo et al., NeurIPS 2018):** Visual saliency maps can produce superficially plausible heatmaps even when higher layer weights are completely randomized.

### Operational Policy:
- Heatmaps must **NEVER** be displayed to smallholder farmers with claims such as *"AI has proven bacteria is here"*.
- Heatmaps are labeled strictly as:  
  `"Model Focus Region (Algorithmic Attention Map — Not Microscopic Proof)"`.
- When the attention map falls primarily outside the leaf boundary ($>40\%$ activation on background), the inference is immediately flagged as `SUSPECT_BACKGROUND_CONFUSION`.
