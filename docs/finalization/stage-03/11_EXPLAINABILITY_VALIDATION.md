# ACREVIA — STAGE 03 EXPLAINABILITY VALIDATION
## Grad-CAM Saliency, Feature Attribution & Agronomic Non-Causal Disclaimers

**Document Reference:** `docs/finalization/stage-03/11_EXPLAINABILITY_VALIDATION.md`  
**Stage:** 03 — Advanced Computer Vision & ML Inference Validation  
**Primary Class:** `GradCAMExplainer` in [`ml/evaluation/gradcam.py`](file:///c:/Users/gokul/OneDrive/Documents/projects/ml/evaluation/gradcam.py)  
**Test Suite:** [`tests/ml/test_gradcam.py`](file:///c:/Users/gokul/OneDrive/Documents/projects/tests/ml/test_gradcam.py)  

---

### 1. Explainability Objectives & Safety Invariants

In smallholder agriculture, black-box AI predictions undermine trust. If a farmer or extension officer receives a diagnosis of "Cotton Leaf Reddening" without visual confirmation, they cannot determine whether the neural network detected genuine anthocyanin accumulation or was tricked by a reddish-brown soil background.

ACREVIA implements **Gradient-weighted Class Activation Mapping (Grad-CAM)** to generate spatial saliency heatmaps highlighting the exact foliar regions that drove convolutional layer activations.

#### Safety Invariant & Non-Causal Disclaimer
> [!IMPORTANT]
> **Advisory Visual Explanation Only:** Grad-CAM heatmaps demonstrate statistical attribution in the final convolutional layer of the model. They highlight features correlated with the classification decision (e.g., lesion patterns, vein chlorosis). Saliency maps do **not** constitute biological proof of infection causation and must be evaluated alongside agronomic field observations.

---

### 2. Grad-CAM Mathematical Formulation

For target class $c$ and convolutional feature activation maps $A^k \in \mathbb{R}^{u \times v}$ in the final depthwise separable convolutional block:

1. **Neuron Importance Weights ($\alpha_k^c$):**
   Computed via global average pooling of gradients:
   $$\alpha_k^c = \frac{1}{Z} \sum_{i=1}^u \sum_{j=1}^v \frac{\partial y^c}{\partial A_{i, j}^k}$$
   where $y^c$ is the logit score for class $c$, and $Z = u \cdot v$ is the spatial dimensions of the feature map ($7 \times 7$ in MobileNetV3).

2. **Weighted Combination & Rectified Linear Unit:**
   $$L_{\text{Grad-CAM}}^c = \text{ReLU}\left( \sum_{k} \alpha_k^c A^k \right)$$
   The $\text{ReLU}$ operator guarantees that only features with positive contribution towards the target pathology class are retained, discarding pixels that contribute towards alternative classes.

3. **Min-Max Normalization & Upsampling:**
   $$H_{\text{norm}}(i, j) = \frac{L_{\text{Grad-CAM}}^c(i, j) - \min(L)}{\max(L) - \min(L) + \epsilon}$$
   The resulting $7 \times 7$ activation grid is upsampled via bilinear interpolation to match the native $224 \times 224$ image resolution.

4. **Alpha Blending Overlay:**
   $$I_{\text{overlay}} = (1 - \alpha) \cdot I_{\text{original}} + \alpha \cdot \text{Colormap}(H_{\text{norm}})$$
   where $\alpha = 0.40$ provides clear visibility of underlying leaf veins and lesion margins.

---

### 3. Verification & Saliency Inspection

In [`tests/ml/test_gradcam.py`](file:///c:/Users/gokul/OneDrive/Documents/projects/tests/ml/test_gradcam.py):
- `test_gradcam_computation`:
  - Instantiates `MultiCropKisanVisionClassifier`.
  - Attaches forward and backward hooks to the final convolutional layer of the backbone.
  - Passes a synthetic foliar batch and generates CAM for the predicted class.
  - Asserts heatmap output shape is strictly 2D `(224, 224)` and all values fall within $[0.0, 1.0]$.
- `test_gradcam_overlay`:
  - Confirms PIL image overlay blending maintains 3-channel RGB image format.
  - Verifies that overlay correctly highlights localized synthetic lesions.
