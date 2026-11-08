"""
End-to-End Training & Checkpoint Smoke Test with Synthetic Tensor Tensors.
Validates that the entire PyTorch training loop, validation step, and checkpointing run cleanly on CPU.
"""

import tempfile
from pathlib import Path
import torch
from torch.utils.data import TensorDataset, DataLoader
from ml.models.classifier import KisanVisionClassifier
from ml.training.trainer import KisanVisionTrainer


def test_training_smoke_and_checkpoint():
    with tempfile.TemporaryDirectory() as tmp_dir:
        # Synthetic dataset: 16 training samples, 8 validation samples, 4 classes
        num_classes = 4
        x_train = torch.randn(16, 3, 224, 224)
        y_train = torch.randint(0, num_classes, (16,))
        train_loader = DataLoader(TensorDataset(x_train, y_train), batch_size=8)
        
        x_val = torch.randn(8, 3, 224, 224)
        y_val = torch.randint(0, num_classes, (8,))
        val_loader = DataLoader(TensorDataset(x_val, y_val), batch_size=8)
        
        class_names = [f"CLASS_{i}" for i in range(num_classes)]
        model = KisanVisionClassifier(
            architecture="mobilenet_v3_small",
            num_classes=num_classes,
            pretrained=False
        )
        
        trainer = KisanVisionTrainer(
            model=model,
            train_loader=train_loader,
            val_loader=val_loader,
            class_names=class_names,
            device="cpu",
            checkpoint_dir=tmp_dir,
            early_stopping_patience=2
        )
        
        # Run 1 epoch smoke test
        results = trainer.fit(epochs=1)
        
        assert results["epochs_completed"] == 1
        assert len(trainer.history) == 1
        assert "val_macro_f1" in trainer.history[0]
        
        # Verify checkpoint file was created
        checkpoint_file = Path(tmp_dir) / "best_model.pt"
        assert checkpoint_file.exists(), "Checkpoint best_model.pt must exist"
        
        # Verify checkpoint loads cleanly
        checkpoint = torch.load(checkpoint_file, map_location="cpu")
        assert "model_state_dict" in checkpoint
        assert checkpoint["class_names"] == class_names
