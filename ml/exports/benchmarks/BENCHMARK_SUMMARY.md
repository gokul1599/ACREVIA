# KisanVision Edge Vision Architecture Benchmark Summary

| Architecture | Total Params | FP32 Size | INT8 Size | Compression | INT8 p50 (ms) | INT8 p95 (ms) | INT8 FPS | Edge Compliant (<200ms, <15MB) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `mobilenet_v3_small` | 1,077,803 | 4.1 MB | 3.69 MB | 1.11x | 3.02 ms | 4.8 ms | 307.0 | **PASSED** |
| `mobilenet_v3_large` | 3,221,051 | 12.23 MB | 11.54 MB | 1.06x | 5.95 ms | 6.29 ms | 169.2 | **PASSED** |
| `resnet18` | 11,310,923 | 43.13 MB | 42.75 MB | 1.01x | 22.28 ms | 23.97 ms | 44.7 | **EXCEEDS_BUDGET** |
| `efficientnet_b0` | 4,338,567 | 16.46 MB | 15.54 MB | 1.06x | 14.85 ms | 17.7 ms | 66.2 | **EXCEEDS_BUDGET** |
