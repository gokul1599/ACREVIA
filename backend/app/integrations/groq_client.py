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
    Uses Groq's OpenAI-compatible completions API with non-negotiable rate-limit,
    multi-model fallback chain, and structured error safety.
    """
    BASE_URL = "https://api.groq.com/openai/v1"
    DEFAULT_FALLBACK_MODELS = [
        "llama-3.3-70b-versatile",
        "llama-3.1-8b-instant"
    ]

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        timeout: Optional[float] = None,
        fallback_models: Optional[List[str]] = None,
    ):
        self.api_key = api_key if api_key is not None else settings.GROQ_API_KEY
        self.model = model or settings.GROQ_MODEL
        self.timeout = timeout or settings.GROQ_TIMEOUT_SECONDS
        self.fallback_models = fallback_models or list(self.DEFAULT_FALLBACK_MODELS)

    @property
    def is_configured(self) -> bool:
        """Returns True if a non-empty API key is available."""
        return bool(self.api_key and self.api_key.strip())

    async def check_health(self) -> Dict[str, Any]:
        """
        Queries Groq models API to verify credential validity and active fallback models
        without leaking secret values.
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
                    available_model_ids = {m.get("id") for m in data if m.get("id")}
                    primary_active = self.model in available_model_ids
                    active_fallbacks = [fb for fb in self.fallback_models if fb in available_model_ids]
                    
                    status_val = "CONFIGURED" if (primary_active or active_fallbacks) else "DEGRADED"

                    return {
                        "status": status_val,
                        "provider": "GroqCloud",
                        "model": self.model,
                        "primary_model_active": primary_active,
                        "fallback_models": self.fallback_models,
                        "active_fallbacks": active_fallbacks,
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
        Executes an inference request against GroqCloud with automatic multi-model fallback.
        Attempts primary model first, followed by resilient fallbacks on 404/429/5xx.
        Guarantees structured degradation if all remote LLMs fail.
        """
        if not self.is_configured:
            return {
                "success": False,
                "error_code": "NOT_CONFIGURED",
                "message": "Groq API key not configured. Using deterministic grounded answer.",
                "deterministic_fallback_active": True
            }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "ACREVIA-AgriBrain/1.0"
        }

        # Build prioritized chain: Primary -> Fallback 1 -> Fallback 2
        models_to_try = [self.model]
        for fb in self.fallback_models:
            if fb not in models_to_try:
                models_to_try.append(fb)

        attempted_models = []
        bounded_models = models_to_try[:3]  # Maximum 3 attempts (primary + 2 fallbacks)

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                for candidate_model in bounded_models:
                    payload = {
                        "model": candidate_model,
                        "messages": messages,
                        "temperature": max(0.0, min(1.0, temperature)),
                        "max_tokens": min(1024, max_tokens),
                    }
                    t0 = time.time()
                    try:
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
                            fallback_used = (candidate_model != self.model)
                            if fallback_used:
                                logger.info(f"Groq primary model failed; successfully used fallback model '{candidate_model}'.")

                            return {
                                "success": True,
                                "content": content,
                                "model": candidate_model,
                                "primary_model": self.model,
                                "fallback_triggered": fallback_used,
                                "provider": "GroqCloud",
                                "latency_ms": latency_ms,
                                "usage": {
                                    "prompt_tokens": usage.get("prompt_tokens", 0),
                                    "completion_tokens": usage.get("completion_tokens", 0),
                                    "total_tokens": usage.get("total_tokens", 0)
                                }
                            }
                        elif resp.status_code in (404, 429, 500, 502, 503, 504):
                            headers_obj = getattr(resp, "headers", None)
                            retry_after_hdr = "30"
                            if headers_obj is not None and hasattr(headers_obj, "get"):
                                retry_after_hdr = str(headers_obj.get("retry-after", "30") or "30")
                            retry_after_int = int(retry_after_hdr) if retry_after_hdr.isdigit() else 30
                            logger.warning(
                                f"Groq candidate model '{candidate_model}' returned HTTP {resp.status_code}. "
                                f"Attempting next fallback model in chain."
                            )
                            attempted_models.append({
                                "model": candidate_model,
                                "status_code": resp.status_code,
                                "retry_after": retry_after_int,
                                "latency_ms": latency_ms
                            })
                            continue
                        else:
                            logger.warning(f"Groq request rejected with HTTP {resp.status_code} for '{candidate_model}'")
                            attempted_models.append({
                                "model": candidate_model,
                                "status_code": resp.status_code,
                                "latency_ms": latency_ms
                            })
                            continue
                    except httpx.TimeoutException:
                        logger.warning(f"Groq candidate model '{candidate_model}' timed out after {self.timeout}s.")
                        attempted_models.append({
                            "model": candidate_model,
                            "error": "TIMEOUT"
                        })
                        continue

            # If all attempted models returned 429:
            all_429 = attempted_models and all(m.get("status_code") == 429 for m in attempted_models)
            if all_429:
                retry_after_val = max([m.get("retry_after", 30) for m in attempted_models]) if attempted_models else 30
                return {
                    "success": False,
                    "error_code": "RATE_LIMIT_EXCEEDED",
                    "retry_after_seconds": retry_after_val,
                    "message": "Groq free-tier rate limit exceeded. Falling back to local grounded guidance.",
                    "deterministic_fallback_active": True,
                    "models_attempted": attempted_models
                }

            # If loop finished without success:
            logger.error(f"All candidate Groq models exhausted: {attempted_models}. Falling back to deterministic RAG.")
            return {
                "success": False,
                "error_code": "ALL_MODELS_UNAVAILABLE",
                "message": "AI inference providers temporarily unavailable or rate-limited. Grounded PJTSAU RAG fallback active.",
                "deterministic_fallback_active": True,
                "models_attempted": attempted_models
            }

        except Exception as e:
            logger.error(f"Unexpected error communicating with Groq: {e}")
            return {
                "success": False,
                "error_code": "CONNECTION_ERROR",
                "message": str(e),
                "deterministic_fallback_active": True
            }


groq_client = GroqClient()
