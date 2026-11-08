# KisanVision — Dedicated ML Inference Service

A high-performance, standalone FastAPI microservice serving quantized INT8 ONNX computer vision models for agricultural foliar disease diagnosis on local AMD Ryzen CPU hardware.

---

## 1. Features
- **Defensive Ingestion:** Magic byte MIME validation, maximum 10 MB payload limits, and decompression bomb protection.
- **Image Quality Filtering:** Rejects blurred, underexposed, and overexposed images before inference execution.
- **Two-Tier OOD Detection:** Excess Green Index ($ExG$) foliar validation and normalized entropy ambiguity detection.
- **Calibrated Uncertainty:** Post-hoc temperature scaling and 8 explicit agricultural decision states.
- **Zero-Torch Runtime:** Pure NumPy & Pillow image normalization with ONNX Runtime CPU Execution Provider.

---

## 2. API Endpoints

### `GET /health`
Liveness probe returning service operational telemetry.

### `GET /model-info`
Returns active models, taxonomy version, and INT8 quantization status.

### `POST /api/v1/predict`
Accepts `multipart/form-data`:
- `image`: Binary leaf image file (JPEG, PNG, WebP).
- `crop_type`: `cotton`, `rice`, or `chilli`.
- `language`: `te` (Telugu), `en` (English), or `hi` (Hindi).

Returns structured RFC 7807 differential diagnosis payload.

---

## 3. Running the Service Locally

```powershell
& .venv\Scripts\uvicorn.exe ml.inference_service.app.main:app --host 0.0.0.0 --port 8001 --reload
```

Interactive Swagger documentation available at: `http://localhost:8001/docs`
