# KisanVision — Model Training Engine

This package manages the PyTorch training execution, loss optimization, validation loops, early stopping, and model checkpointing.

---

## Capabilities

- **`trainer.py` (`KisanVisionTrainer`):**
  - Configurable loss function with class weighting support.
  - Evaluation tracking: computes validation loss, accuracy, and Macro F1 on every epoch.
  - Best model checkpointing based on peak validation Macro F1 score.
  - Early stopping with configurable patience counter.
  - Device agnostic: runs seamlessly on CPU or CUDA GPU.
