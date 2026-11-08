"""
KisanVision - PyTorch Training Engine.
Handles training loops, validation evaluation, early stopping, and checkpoint persistence.
"""

import time
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
import torch
import torch.nn as nn
from torch.utils.data import DataLoader

from ml.evaluation.metrics import ResearchMetricsCalculator


class KisanVisionTrainer:
    """
    Standardized trainer supporting class-weighted loss, early stopping, and checkpointing.
    """
    def __init__(
        self,
        model: nn.Module,
        train_loader: DataLoader,
        val_loader: DataLoader,
        class_names: List[str],
        criterion: Optional[nn.Module] = None,
        optimizer: Optional[torch.optim.Optimizer] = None,
        device: str = "cpu",
        checkpoint_dir: str = "data/models/checkpoints",
        early_stopping_patience: int = 5
    ):
        self.device = torch.device(device)
        self.model = model.to(self.device)
        self.train_loader = train_loader
        self.val_loader = val_loader
        self.class_names = class_names
        self.criterion = criterion or nn.CrossEntropyLoss()
        self.optimizer = optimizer or torch.optim.AdamW(self.model.parameters(), lr=1e-3, weight_decay=1e-4)
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        self.early_stopping_patience = early_stopping_patience
        
        self.history: List[Dict[str, Any]] = []

    def train_epoch(self) -> Tuple[float, float]:
        self.model.train()
        total_loss = 0.0
        correct = 0
        total = 0
        
        for batch_x, batch_y in self.train_loader:
            batch_x, batch_y = batch_x.to(self.device), batch_y.to(self.device)
            
            self.optimizer.zero_grad()
            logits = self.model(batch_x)
            loss = self.criterion(logits, batch_y)
            loss.backward()
            self.optimizer.step()
            
            total_loss += loss.item() * batch_x.size(0)
            preds = torch.argmax(logits, dim=1)
            correct += (preds == batch_y).sum().item()
            total += batch_x.size(0)
            
        epoch_loss = total_loss / max(total, 1)
        epoch_acc = correct / max(total, 1)
        return epoch_loss, epoch_acc

    def evaluate(self) -> Dict[str, Any]:
        self.model.eval()
        total_loss = 0.0
        y_true = []
        y_pred = []
        latencies = []
        total = 0
        
        with torch.no_grad():
            for batch_x, batch_y in self.val_loader:
                batch_x, batch_y = batch_x.to(self.device), batch_y.to(self.device)
                
                t0 = time.perf_counter()
                logits = self.model(batch_x)
                latencies.append((time.perf_counter() - t0) * 1000.0 / batch_x.size(0))
                
                loss = self.criterion(logits, batch_y)
                total_loss += loss.item() * batch_x.size(0)
                
                preds = torch.argmax(logits, dim=1)
                y_true.extend(batch_y.cpu().numpy().tolist())
                y_pred.extend(preds.cpu().numpy().tolist())
                total += batch_x.size(0)

        eval_metrics = ResearchMetricsCalculator.compute_metrics(
            y_true=y_true,
            y_pred=y_pred,
            class_names=self.class_names,
            inference_latencies_ms=latencies
        )
        eval_metrics["loss"] = round(total_loss / max(total, 1), 4)
        return eval_metrics

    def fit(self, epochs: int = 5) -> Dict[str, Any]:
        best_macro_f1 = -1.0
        patience_counter = 0
        best_checkpoint_path = None
        
        for epoch in range(1, epochs + 1):
            t_start = time.time()
            train_loss, train_acc = self.train_epoch()
            val_results = self.evaluate()
            duration = round(time.time() - t_start, 2)
            
            val_loss = val_results["loss"]
            val_macro_f1 = val_results["summary"]["macro_f1"]
            val_acc = val_results["summary"]["accuracy"]
            
            epoch_log = {
                "epoch": epoch,
                "train_loss": round(train_loss, 4),
                "train_acc": round(train_acc, 4),
                "val_loss": val_loss,
                "val_acc": val_acc,
                "val_macro_f1": val_macro_f1,
                "duration_seconds": duration
            }
            self.history.append(epoch_log)

            # Checkpoint on best validation Macro F1
            if val_macro_f1 > best_macro_f1:
                best_macro_f1 = val_macro_f1
                patience_counter = 0
                best_checkpoint_path = self.checkpoint_dir / "best_model.pt"
                torch.save({
                    "epoch": epoch,
                    "model_state_dict": self.model.state_dict(),
                    "optimizer_state_dict": self.optimizer.state_dict(),
                    "val_macro_f1": val_macro_f1,
                    "class_names": self.class_names
                }, best_checkpoint_path)
            else:
                patience_counter += 1
                if patience_counter >= self.early_stopping_patience:
                    break

        return {
            "best_macro_f1": best_macro_f1,
            "best_checkpoint_path": str(best_checkpoint_path) if best_checkpoint_path else None,
            "epochs_completed": len(self.history),
            "history": self.history
        }
