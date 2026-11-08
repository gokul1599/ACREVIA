# STAGE 02 — IMAGE QUALITY VALIDATION & PREPROCESSING AUDIT
## Laplacian Blur Detection, Exposure Thresholds, Format Security & Quality Gates

**Stage:** 02 — Agricultural Dataset Engineering & Taxonomy Validation  
**Core Modules:** [`blur_detector.py`](file:///c:/Users/gokul/OneDrive/Documents/projects/ml/datasets/quality/blur_detector.py), [`exposure_analyzer.py`](file:///c:/Users/gokul/OneDrive/Documents/projects/ml/datasets/quality/exposure_analyzer.py), [`quality_validator.py`](file:///c:/Users/gokul/OneDrive/Documents/projects/ml/datasets/quality/quality_validator.py)  
**Status:** Approved Quality Gate Specification  

---

### 1. Quality Gate Architecture & Metric Calibration

The [`ImageQualityValidator`](file:///c:/Users/gokul/OneDrive/Documents/projects/ml/datasets/quality/quality_validator.py) screens all ingested foliar photographs before permitting them into model training or diagnostic inference:

```
[Raw Foliar Upload]
         │
         ▼
[Format & Corruption Check] ──► Fails ──► QUARANTINED (HTTP 422: CORRUPT_OR_UNSUPPORTED)
         │
         ▼
[Dimension & Aspect Ratio]  ──► Fails ──► QUARANTINED (HTTP 422: RESOLUTION_TOO_LOW)
         │
         ▼
[1024px Thumbnail Resample] (Normalizes Laplacian scale across diverse smartphone cameras)
         │
         ▼
[Laplacian Blur Detection]  ──► Var(Δ) < 100.0 ──► RETAKE_OR_REVIEW (IMAGE_TOO_BLURRY)
         │
         ▼
[Exposure & Pixel Clipping] ──► Clipping > 25% ──► RETAKE_OR_REVIEW (OVER_OR_UNDEREXPOSED)
         │
         ▼
[ACCEPTED FOR TRAINING & INFERENCE]
```

---

### 2. Quality Metrics & Threshold Calibration

| Quality Metric | Tested Operator | Reject Threshold | Warning / Retake Threshold | Accepted Range |
|---|---|---|---|---|
| **Sharpness / Focus** | Laplacian Variance ($Var(\Delta)$ on greyscale) | $< 100.0$ (`BLURRY`) | $100.0 \le Var(\Delta) < 250.0$ (`MILD_BLUR`) | $\ge 250.0$ (`SHARP`) |
| **Mean Illumination**| Average pixel brightness ($0–255$) | $< 35.0$ or $> 225.0$ | $35.0 \le \mu < 50.0$ or $210.0 < \mu \le 225.0$ | $50.0 \le \mu \le 210.0$ |
| **Pixel Clipping** | Proportion of pixels $< 15$ or $> 240$ | $> 0.25$ (25% clipped) | $0.10 < \text{Ratio} \le 0.25$ | $\le 0.10$ |
| **Contrast Spread** | Standard deviation of pixel intensities ($\sigma$) | $< 20.0$ (`LOW_CONTRAST`) | $20.0 \le \sigma < 30.0$ | $\ge 30.0$ |
| **Minimum Resolution**| Width $\times$ Height in pixels | $< 64 \times 64$ | $< 224 \times 224$ | $\ge 224 \times 224$ |
| **Aspect Ratio Range**| $\frac{\text{Width}}{\text{Height}}$ | $< 0.25$ or $> 4.0$ | $< 0.50$ or $> 2.0$ | $0.50 \le \text{AR} \le 2.0$ |

---

### 3. Structured Quality Rejection Schema

When an image fails the quality gate, it is rejected non-destructively with an actionable, localized payload:

```json
{
  "accepted": false,
  "overall_status": "RETAKE_OR_REVIEW",
  "reason_codes": [
    "IMAGE_TOO_BLURRY",
    "UNDEREXPOSED_TOO_DARK"
  ],
  "localized_guidance": {
    "te": "చిత్రం చాలా అస్పష్టంగా మరియు చీకటిగా ఉంది. స్మార్ట్‌ఫోన్‌ను స్థిరంగా పట్టుకుని, ఆకుపై ఫోకస్ చేయడానికి స్క్రీన్‌పై తాకండి.",
    "en": "Image is severely blurred and underexposed. Hold the smartphone steady and tap to focus on the leaf under good light.",
    "hi": "तस्वीर बहुत धुंधली और अंधेरी है। कृपया फोन को स्थिर रखें और रोशनी में पत्ते पर फोकस करें।"
  },
  "metrics": {
    "laplacian_variance": 42.15,
    "mean_brightness": 28.40,
    "clipping_ratio": 0.312
  }
}
```

---

### 4. Non-Destructive Storage Protocol

1. Original uploaded images are preserved in immutable storage without destructive cropping or compression artifacts.
2. Normalized crops ($224 \times 224$ for MobileNetV3) and thumbnail previews ($1024 \times 1024$) are derived as separate, versioned artifacts with independent SHA-256 digests.
