"""
ACREVIA - Hugging Face Hub Client Adapter.
Provides optional authentication, model metadata lookup, and dataset inspection via Hugging Face Hub API.
Treats HF_TOKEN as strictly optional, operates with read-only permissions, and incurs zero costs.
"""

from typing import Dict, Any, Optional
import time
import httpx

from backend.app.core.config import settings
from backend.app.core.logging import logger


class HuggingFaceClient:
    """
    Adapter for Hugging Face Hub API.
    Supports both authenticated (HF_TOKEN) and anonymous public access for open-weight models and datasets.
    """
    BASE_URL = "https://huggingface.co/api"

    def __init__(self, token: Optional[str] = None):
        if token is not None:
            self.token = token
        else:
            self.token = settings.HF_TOKEN

    @property
    def is_authenticated(self) -> bool:
        """Returns True if a token is configured."""
        return bool(self.token and self.token.strip())

    def _get_headers(self) -> Dict[str, str]:
        headers = {"User-Agent": "ACREVIA-AgriPlatform/1.0"}
        if self.is_authenticated:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    async def check_health(self) -> Dict[str, Any]:
        """
        Verifies Hugging Face API connectivity and authentication status without exposing secrets.
        """
        headers = self._get_headers()

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                t0 = time.time()
                if self.is_authenticated:
                    # Authenticated token verification
                    resp = await client.get(f"{self.BASE_URL}/whoami-v2", headers=headers)
                    latency_ms = round((time.time() - t0) * 1000, 1)

                    if resp.status_code == 200:
                        data = resp.json()
                        return {
                            "status": "CONFIGURED",
                            "provider": "Hugging Face",
                            "auth_mode": "AUTHENTICATED",
                            "user_type": data.get("type", "user"),
                            "username": data.get("name", "unknown"),
                            "latency_ms": latency_ms,
                            "free_tier": True
                        }
                    elif resp.status_code == 401:
                        return {
                            "status": "AUTHENTICATION_FAILED",
                            "provider": "Hugging Face",
                            "auth_mode": "INVALID_TOKEN",
                            "error": "Configured HF_TOKEN is invalid or expired."
                        }
                    else:
                        return {
                            "status": "DEGRADED",
                            "provider": "Hugging Face",
                            "http_status": resp.status_code
                        }
                else:
                    # Anonymous public verification
                    resp = await client.get(
                        f"{self.BASE_URL}/models/sentence-transformers/all-MiniLM-L6-v2",
                        headers=headers
                    )
                    latency_ms = round((time.time() - t0) * 1000, 1)
                    return {
                        "status": "CONFIGURED",
                        "provider": "Hugging Face",
                        "auth_mode": "ANONYMOUS_PUBLIC",
                        "public_access": resp.status_code == 200,
                        "latency_ms": latency_ms,
                        "free_tier": True
                    }
        except httpx.TimeoutException:
            logger.warning("Hugging Face API request timed out.")
            return {"status": "TIMEOUT", "provider": "Hugging Face"}
        except Exception as e:
            logger.warning(f"Hugging Face connection error: {e}")
            return {"status": "UNAVAILABLE", "provider": "Hugging Face", "error": str(e)}

    async def get_model_info(self, model_id: str) -> Dict[str, Any]:
        """
        Retrieves public or gated model card metadata from Hugging Face Hub.
        """
        headers = self._get_headers()
        url = f"{self.BASE_URL}/models/{model_id}"

        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                resp = await client.get(url, headers=headers)
                if resp.status_code == 200:
                    data = resp.json()
                    return {
                        "success": True,
                        "model_id": data.get("id"),
                        "downloads": data.get("downloads", 0),
                        "pipeline_tag": data.get("pipeline_tag"),
                        "tags": data.get("tags", [])[:10],
                        "private": data.get("private", False),
                        "gated": data.get("gated", False)
                    }
                elif resp.status_code == 404:
                    return {"success": False, "error_code": "MODEL_NOT_FOUND", "model_id": model_id}
                elif resp.status_code == 403:
                    return {"success": False, "error_code": "GATED_ACCESS_REQUIRED", "model_id": model_id}
                else:
                    return {"success": False, "error_code": f"HTTP_{resp.status_code}", "model_id": model_id}
        except Exception as e:
            logger.warning(f"Failed to query Hugging Face model {model_id}: {e}")
            return {"success": False, "error_code": "CONNECTION_ERROR", "error": str(e)}


hf_client = HuggingFaceClient()
