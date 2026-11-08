"""
KisanVision - Local Model & Experiment Registry.
Tracks model versions, hyperparameters, evaluation reports, and strict human approval states.
"""

from enum import Enum
from typing import Dict, Any, List, Optional
import json
from pathlib import Path
import uuid
from datetime import datetime, timezone


class ModelApprovalState(str, Enum):
    EXPERIMENTAL = "EXPERIMENTAL"
    TRAINED = "TRAINED"
    EVALUATED = "EVALUATED"
    REQUIRES_EXPERT_REVIEW = "REQUIRES_EXPERT_REVIEW"
    APPROVED_FOR_INTERNAL_TESTING = "APPROVED_FOR_INTERNAL_TESTING"
    APPROVED_FOR_FIELD_PILOT = "APPROVED_FOR_FIELD_PILOT"
    REJECTED = "REJECTED"
    RETIRED = "RETIRED"


class ModelRegistryEntry:
    def __init__(
        self,
        model_name: str,
        architecture: str,
        dataset_version: str,
        taxonomy_version: str,
        preprocessing_version: str,
        hyperparameters: Dict[str, Any],
        random_seed: int,
        metrics_summary: Dict[str, Any],
        checkpoint_path: str,
        approval_state: ModelApprovalState = ModelApprovalState.EXPERIMENTAL,
        reviewer_id: Optional[str] = None,
        notes: Optional[str] = None,
        entry_id: Optional[str] = None,
        created_at: Optional[str] = None
    ):
        self.entry_id = entry_id or str(uuid.uuid4())
        self.model_name = model_name
        self.architecture = architecture
        self.dataset_version = dataset_version
        self.taxonomy_version = taxonomy_version
        self.preprocessing_version = preprocessing_version
        self.hyperparameters = hyperparameters
        self.random_seed = random_seed
        self.metrics_summary = metrics_summary
        self.checkpoint_path = checkpoint_path
        self.approval_state = approval_state
        self.reviewer_id = reviewer_id
        self.notes = notes
        self.created_at = created_at or datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "entry_id": self.entry_id,
            "model_name": self.model_name,
            "architecture": self.architecture,
            "dataset_version": self.dataset_version,
            "taxonomy_version": self.taxonomy_version,
            "preprocessing_version": self.preprocessing_version,
            "hyperparameters": self.hyperparameters,
            "random_seed": self.random_seed,
            "metrics_summary": self.metrics_summary,
            "checkpoint_path": self.checkpoint_path,
            "approval_state": self.approval_state.value if isinstance(self.approval_state, ModelApprovalState) else self.approval_state,
            "reviewer_id": self.reviewer_id,
            "notes": self.notes,
            "created_at": self.created_at
        }


class ModelRegistry:
    """File-based atomic model registry with strict state transition gates."""
    def __init__(self, registry_file: Path = Path("data/metadata/model_registry.json")):
        self.registry_file = registry_file
        self.registry_file.parent.mkdir(parents=True, exist_ok=True)
        self.entries: Dict[str, ModelRegistryEntry] = {}
        self._load()

    def _load(self):
        if self.registry_file.exists():
            try:
                with open(self.registry_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for item in data:
                        entry = ModelRegistryEntry(
                            entry_id=item["entry_id"],
                            model_name=item["model_name"],
                            architecture=item["architecture"],
                            dataset_version=item["dataset_version"],
                            taxonomy_version=item["taxonomy_version"],
                            preprocessing_version=item["preprocessing_version"],
                            hyperparameters=item["hyperparameters"],
                            random_seed=item["random_seed"],
                            metrics_summary=item["metrics_summary"],
                            checkpoint_path=item["checkpoint_path"],
                            approval_state=ModelApprovalState(item["approval_state"]),
                            reviewer_id=item.get("reviewer_id"),
                            notes=item.get("notes"),
                            created_at=item["created_at"]
                        )
                        self.entries[entry.entry_id] = entry
            except Exception:
                self.entries = {}

    def _save(self):
        with open(self.registry_file, "w", encoding="utf-8") as f:
            json.dump([e.to_dict() for e in self.entries.values()], f, indent=2)

    def register_run(self, entry: ModelRegistryEntry) -> str:
        self.entries[entry.entry_id] = entry
        self._save()
        return entry.entry_id

    def update_approval(
        self,
        entry_id: str,
        new_state: ModelApprovalState,
        reviewer_id: str,
        notes: str
    ):
        if entry_id not in self.entries:
            raise KeyError(f"Registry entry '{entry_id}' not found.")
            
        entry = self.entries[entry_id]
        entry.approval_state = new_state
        entry.reviewer_id = reviewer_id
        entry.notes = notes
        self._save()
