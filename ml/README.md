# KisanVision — Machine Learning & Computer Vision Core

This directory contains the custom computer vision research and engineering foundation for **KisanVision**, targeting Cotton, Rice, and Chilli pathology in Telangana, India.

---

## Directory Architecture

```
ml/
├── configs/
│   ├── taxonomy/           # Version-controlled crop pathology taxonomy (YAML)
│   ├── experiments/        # Experiment hyperparameters and model configs
│   └── preprocessing/      # Input resolution and normalization configs
├── datasets/
│   ├── manifests/          # Pydantic UnifiedSampleManifest schema
│   ├── ingestion/          # Safe byte decoding, SHA-256, format validation
│   ├── quality/            # Laplacian blur, exposure, and aspect ratio checks
│   ├── deduplication/      # Exact cryptographic and perceptual hash deduplication
│   ├── annotations/        # Multi-tier annotation schemas and expert review gates
│   ├── splitting/          # Group-stratified farm-leakage-free dataset splitter
│   └── transforms/         # PyTorch/torchvision training and inference pipelines
├── models/
│   ├── backbones.py        # MobileNetV3, ResNet, EfficientNet backbones
│   └── classifier.py       # Dual-head classifier with calibrated uncertainty
├── training/
│   └── trainer.py          # PyTorch training loop, early stopping, checkpointing
├── evaluation/
│   └── metrics.py          # Macro F1, Per-class breakdown, Confusion matrix
└── registry/
    └── model_registry.py   # Traceable model and experiment registry
```

---

## Quickstart & Verification

```powershell
# Run the complete ML test suite
& .venv\Scripts\python.exe -m pytest tests/ml/ -v
```
