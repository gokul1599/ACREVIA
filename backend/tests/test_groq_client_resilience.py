"""
ACREVIA - GroqCloud Multi-Model Fallback & AI Resilience Test Suite.
Verifies multi-model failover, bounded retries, and structured deterministic RAG degradation.
"""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock
import httpx

from backend.app.integrations.groq_client import GroqClient


@pytest.mark.anyio
async def test_unconfigured_client_returns_deterministic_fallback():
    client = GroqClient(api_key="")
    result = await client.generate_completion(
        messages=[{"role": "user", "content": "Crop disease advice"}]
    )
    assert result["success"] is False
    assert result["error_code"] == "NOT_CONFIGURED"
    assert result["deterministic_fallback_active"] is True


@pytest.mark.anyio
async def test_primary_model_success():
    client = GroqClient(api_key="gsk_test_mock_key", model="qwen/qwen3.8-27b")

    mock_resp = MagicMock(spec=httpx.Response)
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "choices": [{"message": {"content": "Apply Neem oil 5ml/L."}}],
        "usage": {"prompt_tokens": 10, "completion_tokens": 8, "total_tokens": 18}
    }

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_resp
        res = await client.generate_completion([{"role": "user", "content": "Treatment"}])

        assert res["success"] is True
        assert res["content"] == "Apply Neem oil 5ml/L."
        assert res["model"] == "qwen/qwen3.8-27b"
        assert res["fallback_triggered"] is False
        assert mock_post.call_count == 1


@pytest.mark.anyio
async def test_primary_model_404_falls_back_to_secondary():
    client = GroqClient(api_key="gsk_test_mock_key", model="qwen/qwen3.8-27b")

    mock_404 = MagicMock(spec=httpx.Response)
    mock_404.status_code = 404

    mock_200 = MagicMock(spec=httpx.Response)
    mock_200.status_code = 200
    mock_200.json.return_value = {
        "choices": [{"message": {"content": "Fallback guidance from Llama 3.3."}}],
        "usage": {"prompt_tokens": 12, "completion_tokens": 10, "total_tokens": 22}
    }

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.side_effect = [mock_404, mock_200]
        res = await client.generate_completion([{"role": "user", "content": "Treatment"}])

        assert res["success"] is True
        assert res["content"] == "Fallback guidance from Llama 3.3."
        assert res["model"] == "llama-3.3-70b-versatile"
        assert res["fallback_triggered"] is True
        assert mock_post.call_count == 2


@pytest.mark.anyio
async def test_all_models_fail_returns_structured_rag_degradation():
    client = GroqClient(api_key="gsk_test_mock_key", model="qwen/qwen3.8-27b")

    mock_503 = MagicMock(spec=httpx.Response)
    mock_503.status_code = 503

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_503
        res = await client.generate_completion([{"role": "user", "content": "Treatment"}])

        assert res["success"] is False
        assert res["error_code"] == "ALL_MODELS_UNAVAILABLE"
        assert res["deterministic_fallback_active"] is True
        assert len(res["models_attempted"]) == 3  # Tried primary + 2 fallbacks


@pytest.mark.anyio
async def test_health_check_detects_fallbacks_and_active_status():
    client = GroqClient(api_key="gsk_test_mock_key", model="qwen/qwen3.8-27b")

    mock_resp = MagicMock(spec=httpx.Response)
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "data": [
            {"id": "llama-3.3-70b-versatile"},
            {"id": "llama-3.1-8b-instant"}
        ]
    }

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_resp
        health = await client.check_health()

        assert health["status"] == "CONFIGURED"
        assert health["primary_model_active"] is False  # qwen preview not in list
        assert "llama-3.3-70b-versatile" in health["active_fallbacks"]
