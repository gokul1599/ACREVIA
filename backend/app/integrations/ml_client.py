"""
ACREVIA - ML Inference Microservice Client Adapter.
Connects the backend to the dedicated Stage 3 ML inference microservice.
"""

from typing import Dict, Any, Optional
import httpx

from backend.app.core.config import settings
from backend.app.core.logging import logger


class MLInferenceClient:
    """
    HTTP client for the dedicated Stage 3 ML inference microservice.
    """
    def __init__(self, base_url: Optional[str] = None, timeout: float = 10.0):
        self.base_url = (base_url or settings.ML_INFERENCE_URL).rstrip("/")
        self.timeout = timeout

    async def check_health(self) -> Dict[str, Any]:
        """Queries health status of the ML inference microservice."""
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                resp = await client.get(f"{self.base_url}/health")
                if resp.status_code == 200:
                    return {"status": "HEALTHY", "details": resp.json()}
                return {"status": "DEGRADED", "status_code": resp.status_code}
        except Exception as e:
            logger.warning(f"ML inference service unreachable at {self.base_url}: {e}")
            return {"status": "UNAVAILABLE", "error": str(e)}

    async def submit_diagnosis(
        self,
        image_bytes: bytes,
        crop_type: str,
        filename: str = "leaf.jpg",
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Submits image bytes to the dedicated inference microservice for foliar pathology diagnosis.
        """
        url = f"{self.base_url}/api/v1/predict"
        files = {
            "image": (filename, image_bytes, "image/jpeg")
        }
        data = {
            "crop_type": crop_type,
            "language": language
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.post(url, data=data, files=files)
                if resp.status_code == 200:
                    return resp.json()
                elif resp.status_code in [400, 413, 422]:
                    return {
                        "status": "PROCESSING_FAILED",
                        "error_detail": resp.json().get("detail", "Input validation rejected by ML engine")
                    }
                else:
                    return {
                        "status": "PROCESSING_FAILED",
                        "error_detail": f"ML engine returned HTTP {resp.status_code}"
                    }
        except httpx.RequestError as e:
            logger.error(f"Failed to communicate with ML inference engine: {e}")
            return {
                "status": "PROCESSING_FAILED",
                "error_detail": f"ML inference engine connection error: {str(e)}"
            }


ml_client = MLInferenceClient()
