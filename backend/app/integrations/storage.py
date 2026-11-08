"""
ACREVIA - Secure Object Storage Abstraction.
Supports private image storage, cryptographic checksumming, and provider switching.
"""

import os
import hashlib
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, Tuple, Optional
from fastapi import UploadFile

from backend.app.core.config import settings
from backend.app.core.logging import logger


class StorageProvider(ABC):
    @abstractmethod
    def save_file(self, content: bytes, filename: str, mime_type: str) -> Dict[str, Any]:
        """Saves file bytes and returns storage metadata."""
        pass

    @abstractmethod
    def get_url(self, storage_path: str, expires_in_seconds: int = 3600) -> str:
        """Generates a secure access URL."""
        pass

    @abstractmethod
    def delete_file(self, storage_path: str) -> bool:
        """Deletes file from storage."""
        pass

    @abstractmethod
    def read_file(self, storage_path: str) -> bytes:
        """Reads file bytes from storage."""
        pass

    @abstractmethod
    def get_absolute_path(self, storage_path: str) -> Path:
        """Returns the local filesystem path if available."""
        pass


class LocalStorageProvider(StorageProvider):
    """Local filesystem storage provider for development and testing."""
    def __init__(self, base_dir: Optional[str] = None):
        self.base_dir = Path(base_dir or settings.STORAGE_LOCAL_DIR).resolve()
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def save_file(self, content: bytes, filename: str, mime_type: str) -> Dict[str, Any]:
        # Compute SHA-256
        sha256 = hashlib.sha256(content).hexdigest()
        ext = Path(filename).suffix or ".jpg"
        unique_name = f"{sha256[:16]}_{Path(filename).stem}{ext}"
        target_path = self.base_dir / unique_name

        with open(target_path, "wb") as f:
            f.write(content)

        logger.info(f"Saved private media: {unique_name} ({len(content)} bytes)")
        return {
            "storage_path": str(unique_name),
            "file_size_bytes": len(content),
            "mime_type": mime_type,
            "sha256_hash": sha256,
            "provider": "LOCAL"
        }

    def get_url(self, storage_path: str, expires_in_seconds: int = 3600) -> str:
        # In local dev, return endpoint route or file URI
        return f"/api/v1/storage/{storage_path}"

    def delete_file(self, storage_path: str) -> bool:
        file_path = self.base_dir / storage_path
        if file_path.exists():
            file_path.unlink()
            return True
        return False

    def read_file(self, storage_path: str) -> bytes:
        file_path = self.get_absolute_path(storage_path)
        if not file_path.exists():
            raise FileNotFoundError(f"Storage object '{storage_path}' not found.")
        with open(file_path, "rb") as f:
            return f.read()

    def get_absolute_path(self, storage_path: str) -> Path:
        # Sanitize storage_path to prevent path traversal
        clean_name = Path(storage_path).name
        return self.base_dir / clean_name


def get_storage_provider() -> StorageProvider:
    """Factory returning configured storage provider."""
    # Production can switch to S3StorageProvider or SupabaseStorageProvider
    return LocalStorageProvider()
