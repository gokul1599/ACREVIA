"""
ACREVIA - KrishiBrain Decoupled Embedding Provider Abstraction.
Supports deterministic local embeddings for test reproducibility and cloud provider adapters.
"""

import math
import hashlib
from abc import ABC, abstractmethod
from typing import List, Optional
import httpx

from backend.app.core.config import settings
from backend.app.core.logging import logger


class EmbeddingProvider(ABC):
    @property
    @abstractmethod
    def profile_id(self) -> str:
        pass

    @property
    @abstractmethod
    def dimensions(self) -> int:
        pass

    @abstractmethod
    def embed_text(self, text: str) -> List[float]:
        pass

    @abstractmethod
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        pass


class DeterministicLocalEmbeddingProvider(EmbeddingProvider):
    """
    Offline deterministic embedding provider for zero-cost testing and development.
    Maps words and characters into a normalized 1536-dimensional semantic vector space.
    """
    def __init__(self, dimensions: int = 1536):
        self._dimensions = dimensions
        self._profile_id = f"deterministic-semantic-{dimensions}d-v1"

    @property
    def profile_id(self) -> str:
        return self._profile_id

    @property
    def dimensions(self) -> int:
        return self._dimensions

    def embed_text(self, text: str) -> List[float]:
        # Generate pseudo-semantic vector from token n-grams and hashing
        vec = [0.0] * self._dimensions
        words = text.lower().split()
        if not words:
            return vec

        for w_idx, word in enumerate(words):
            h = int(hashlib.md5(word.encode("utf-8")).hexdigest(), 16)
            pos = h % self._dimensions
            # Weight term by position and frequency
            weight = 1.0 / (1.0 + 0.05 * w_idx)
            vec[pos] += weight
            # Also add character trigram projections for multilingual subword sensitivity
            if len(word) >= 3:
                for j in range(len(word) - 2):
                    tri_hash = int(hashlib.md5(word[j:j+3].encode("utf-8")).hexdigest(), 16)
                    tri_pos = tri_hash % self._dimensions
                    vec[tri_pos] += 0.25 * weight

        # L2 Normalize vector
        norm = math.sqrt(sum(x * x for x in vec))
        if norm > 1e-12:
            vec = [x / norm for x in vec]

        return vec

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        return [self.embed_text(t) for t in texts]


class CloudEmbeddingProvider(EmbeddingProvider):
    """
    Production adapter targeting OpenAI, Gemini, or custom embedding gateways.
    """
    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: str = "text-embedding-3-small",
        dimensions: int = 1536
    ):
        self.api_key = api_key or getattr(settings, "EMBEDDING_API_KEY", "")
        self.model_name = model_name
        self._dimensions = dimensions
        self._profile_id = f"{model_name}-{dimensions}d"

    @property
    def profile_id(self) -> str:
        return self._profile_id

    @property
    def dimensions(self) -> int:
        return self._dimensions

    def embed_text(self, text: str) -> List[float]:
        if not self.api_key:
            # Graceful fallback to deterministic provider if live API credentials are unconfigured
            logger.info("Cloud embedding key unconfigured; using deterministic local provider.")
            fallback = DeterministicLocalEmbeddingProvider(self._dimensions)
            return fallback.embed_text(text)

        # Standard OpenAI API request
        try:
            with httpx.Client(timeout=10.0) as client:
                resp = client.post(
                    "https://api.openai.com/v1/embeddings",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    json={"input": text, "model": self.model_name, "dimensions": self._dimensions}
                )
                if resp.status_code == 200:
                    return resp.json()["data"][0]["embedding"]
                logger.warning(f"Embedding API error: {resp.status_code} - {resp.text}")
        except Exception as e:
            logger.error(f"Failed to generate cloud embedding: {e}")

        # Fallback
        return DeterministicLocalEmbeddingProvider(self._dimensions).embed_text(text)

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        return [self.embed_text(t) for t in texts]


def get_embedding_provider() -> EmbeddingProvider:
    """Factory returning configured active embedding provider."""
    provider_name = getattr(settings, "EMBEDDING_PROVIDER", "LOCAL_DETERMINISTIC").upper()
    if provider_name in ["OPENAI", "CLOUD"]:
        return CloudEmbeddingProvider()
    return DeterministicLocalEmbeddingProvider(1536)
