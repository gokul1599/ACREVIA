"""
ACREVIA - GroqCloud AI Inference Client Adapter.
Provides high-speed, free-tier LLM inference for KrishiBrain multilingual agronomic guidance.
Strictly respects free-tier quotas and implements controlled error and rate-limit handling.
"""

from typing import Dict, Any, List, Optional
import time
import httpx

from backend.app.core.config import settings
from backend.app.core.logging import logger


class GroqClient:
    """
    Client adapter for GroqCloud free-tier AI inference.
    Uses Groq's OpenAI-compatible completions API with non-negotiable rate-limit and error safety.
    """
    BASE_URL = "https://api.groq.com/openai/v1"

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        timeout: Optional[float] = None,
    ):
        self.api_key = api_key or settings.GROQ_API_KEY
        self.model = model or settings.GROQ_MODEL
        self.timeout = timeout or settings.GROQ_TIMEOUT_SECONDS

    @property
    def is_configured(self) -> bool:
        """Returns True if a non-empty API key is available."""
        return bool(self.api_key and self.api_key.strip())

    async def check_health(self) -> Dict[str, Any]:
        """
        Queries Groq models API to verify credential validity without leaking secret values.
        """
        if not self.is_configured:
            return {
                "status": "NOT_CONFIGURED",
                "provider": "GroqCloud",
                "details": "GROQ_API_KEY is not set. Deterministic fallback active."
            }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "User-Agent": "ACREVIA-AgriBrain/1.0"
        }

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                t0 = time.time()
                resp = await client.get(f"{self.BASE_URL}/models", headers=headers)
                latency_ms = round((time.time() - t0) * 1000, 1)

                if resp.status_code == 200:
                    data = resp.json().get("data", [])
                    available_models = [m.get("id") for m in data]
                    return {
                        "status": "CONFIGURED",
                        "provider": "GroqCloud",
                        "model": self.model,
                        "model_active": self.model in available_models,
                        "latency_ms": latency_ms,
                        "free_tier": True
                    }
                elif resp.status_code == 401:
                    logger.warning("Groq authentication failed (HTTP 401).")
                    return {
                        "status": "AUTHENTICATION_FAILED",
                        "provider": "GroqCloud",
                        "error": "Invalid API key"
                    }
                elif resp.status_code == 429:
                    retry_after = resp.headers.get("retry-after", "60")
                    return {
                        "status": "RATE_LIMITED",
                        "provider": "GroqCloud",
                        "retry_after_seconds": int(retry_after) if retry_after.isdigit() else 60
                    }
                else:
                    return {
                        "status": "DEGRADED",
                        "provider": "GroqCloud",
                        "http_status": resp.status_code
                    }
        except httpx.TimeoutException:
            logger.warning("Groq API health check timed out.")
            return {"status": "TIMEOUT", "provider": "GroqCloud"}
        except Exception as e:
            logger.warning(f"Groq API connection error: {e}")
            return {"status": "UNAVAILABLE", "provider": "GroqCloud", "error": str(e)}

    async def generate_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.2,
        max_tokens: int = 512,
    ) -> Dict[str, Any]:
        """
        Executes an inference request against GroqCloud.
        Enforces free-tier limits, timeout budgets, and structured failure handling.
        """
        if not self.is_configured:
            return {
                "success": False,
                "error_code": "NOT_CONFIGURED",
                "message": "Groq API key not configured. Using deterministic grounded answer."
            }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "ACREVIA-AgriBrain/1.0"
        }

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": max(0.0, min(1.0, temperature)),
            "max_tokens": min(1024, max_tokens),  # Bound tokens to avoid free quota exhaustion
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                t0 = time.time()
                resp = await client.post(
                    f"{self.BASE_URL}/chat/completions",
                    headers=headers,
                    json=payload
                )

                # Fallback to active free model if primary model is unavailable or decommissioned on Groq
                if resp.status_code == 404 and payload["model"] != "qwen/qwen3.8-27b":
                    logger.info("Configured Groq model returned 404; retrying with active free model qwen/qwen3.8-27b.")
                    payload["model"] = "qwen/qwen3.8-27b"
                    resp = await client.post(
                        f"{self.BASE_URL}/chat/completions",
                        headers=headers,
                        json=payload
                    )

                latency_ms = round((time.time() - t0) * 1000, 1)

                if resp.status_code == 200:
                    body = resp.json()
                    choices = body.get("choices", [])
                    content = choices[0].get("message", {}).get("content", "") if choices else ""
                    usage = body.get("usage", {})
                    return {
                        "success": True,
                        "content": content,
                        "model": body.get("model", self.model),
                        "provider": "GroqCloud",
                        "latency_ms": latency_ms,
                        "usage": {
                            "prompt_tokens": usage.get("prompt_tokens", 0),
                            "completion_tokens": usage.get("completion_tokens", 0),
                            "total_tokens": usage.get("total_tokens", 0)
                        }
                    }
                elif resp.status_code == 429:
                    retry_after = resp.headers.get("retry-after", "30")
                    logger.warning(f"Groq free-tier rate limit exceeded (Retry-After: {retry_after}s).")
                    return {
                        "success": False,
                        "error_code": "RATE_LIMIT_EXCEEDED",
                        "retry_after_seconds": int(retry_after) if retry_after.isdigit() else 30,
                        "message": "Groq free-tier rate limit exceeded. Falling back to local grounded guidance."
                    }
                elif resp.status_code in [500, 502, 503, 504]:
                    logger.warning(f"Groq provider server error: HTTP {resp.status_code}")
                    return {
                        "success": False,
                        "error_code": "PROVIDER_UNAVAILABLE",
                        "message": f"Groq inference service temporarily unavailable (HTTP {resp.status_code})."
                    }
                else:
                    logger.warning(f"Groq request rejected with HTTP {resp.status_code}")
                    return {
                        "success": False,
                        "error_code": "REQUEST_FAILED",
                        "status_code": resp.status_code,
                        "message": "Groq request failed. Falling back to grounded guidance."
                    }
        except httpx.TimeoutException:
            logger.warning(f"Groq inference request timed out after {self.timeout}s.")
            return {
                "success": False,
                "error_code": "TIMEOUT",
                "message": f"Groq response timed out after {self.timeout}s."
            }
        except Exception as e:
            logger.error(f"Unexpected error communicating with Groq: {e}")
            return {
                "success": False,
                "error_code": "CONNECTION_ERROR",
                "message": str(e)
            }


groq_client = GroqClient()
