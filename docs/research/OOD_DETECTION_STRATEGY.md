# KISANVISION — OUT-OF-DISTRIBUTION (OOD) DETECTION STRATEGY

**Document Version:** 1.0.0  
**Effective Date:** November 7, 2026  
**Auditor:** Principal Computer Vision Research Scientist & ML Security Engineer  
**Status:** Approved Research Protocol  

---

## 1. The OOD Problem in Smallholder Agricultural AI

In field deployment across rural Telangana, farmers will inevitably photograph objects outside the model's training distribution:
- **Non-Plant Objects:** Tractors, cattle, shoes, hands, faces, tools, indoor rooms, pesticides containers.
- **Unsupported Crops:** Tomato, Mango, Maize, Sugarcane, Brinjal, Banana.
- **Unrecognized Pathologies:** Rare viral strains, novel invasive pests, or complex herbicide toxicities not covered in the 28-class taxonomy.
- **Severe Degradation:** Extreme solar flare lens glare, muddy leaves, night-time flash photographs.

A naive deep learning classifier will force any input into one of its pre-defined classes with deceptively high softmax probabilities. KisanVision implements a multi-tier defense system to actively detect and abstain on OOD samples.

---

## 2. Multi-Tier OOD Detection Hierarchy

```mermaid
flowchart TD
    A["Raw Camera Upload"] --> B["Tier 0: Quality Gate"]
    B -->|Blur / Glare / Dark| C["Reject: IMAGE_QUALITY_INSUFFICIENT"]
    
    B -->|Quality OK| D["Tier 1: Botanical Foliar Detector"]
    D -->|ExG Ratio < 8% OR Texture Std < 5| E["Reject: OUT_OF_DISTRIBUTION (Non-Plant)"]
    
    D -->|Foliar Confirmed| F["Tier 2: Auxiliary Crop Gate"]
    F -->|Crop Conf < 0.85| G["Reject: UNSUPPORTED_CROP"]
    
    F -->|Crop Validated| H["Tier 3: Latent Feature & Energy Score"]
    H -->|Energy E(x) < Threshold| I["Flag: UNKNOWN_SYMPTOM_OR_PATHOLOGY"]
    
    H -->|Energy Normal| J["Tier 4: Predictive Entropy & Margin"]
    J -->|Entropy > 0.65 OR Margin < 0.15| K["Route: EXPERT_REVIEW_REQUIRED"]
    J -->|Passes All Tiers| L["Status: SUPPORTED_PREDICTION"]
```

---

## 3. Mathematical OOD Formulations

### 3.1 Botanical Foliar Spectrum (Tier 1)
Using the Excess Green Index ($ExG$):
$$ExG = 2G - R - B$$
- Healthy foliage: $ExG > 10.0$ and $G > 30.0$.
- Chlorotic / Yellowing foliage: $R > 70, G > 70, B < 100$.
- Necrotic / Blight lesions: $R > 60, G > 35, B > 15$ with earthy brown chromatic balance.
- Total Foliar Ratio $R_{\text{foliar}} = \frac{N_{\text{foliar}}}{N_{\text{total}}}$.
- Threshold: If $R_{\text{foliar}} < 0.08$, the image is classified as non-plant.

### 3.2 Free Energy-Based OOD Scoring (Tier 3)
Following Liu et al. (NeurIPS 2020), energy scores align directly with the data probability distribution without suffering from softmax score normalization artifacts:
$$E(x; f) = -T \cdot \log \sum_{i=1}^C \exp\left(\frac{f_i(x)}{T}\right)$$
- Samples with high free energy (lower negative logsumexp) represent out-of-distribution inputs.
- Energy threshold $\tau_E$ is calibrated on the in-distribution validation set to maintain a $95\%$ true positive rate (TPR95).

### 3.3 Latent Mahalanobis Distance (Feature Space)
For deep feature representations $z = \phi(x)$ extracted from the MobileNetV3 backbone:
$$D_M(z) = \min_c \sqrt{(z - \mu_c)^T \Sigma^{-1} (z - \mu_c)}$$
where $\mu_c$ is the class centroid and $\Sigma$ is the pooled covariance matrix computed over in-distribution validation embeddings.

---

## 4. OOD Evaluation Protocol

When real field data and negative distractor datasets are evaluated, the following metrics will be reported:
1. **FPR at 95% TPR (FPR95):** The false positive rate of OOD samples when the true positive rate of in-distribution samples is held at $95\%$.
2. **AUROC (Area Under the Receiver Operating Characteristic):** Measures threshold-independent discrimination between in-distribution and OOD inputs.
3. **AUPR (Area Under the Precision-Recall Curve):** Evaluates precision under severe class imbalance between common in-distribution samples and rare OOD anomalies.
