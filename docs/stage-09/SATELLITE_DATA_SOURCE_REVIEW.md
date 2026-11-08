# ACREVIA — SATELLITE DATA SOURCE REVIEW
## Comparative Evaluation of Earth Observation Constellations for Telangana Smallholder Agriculture

---

## 1. Constellation Comparison

| Parameter | Sentinel-2 MSI (Copernicus) | Landsat-8/9 OLI-2 (USGS/NASA) | PlanetScope (Commercial) | ISRO RISAT-1A / EOS-04 (SAR) |
|---|---|---|---|---|
| **Constellation Type** | Dual satellite (2A & 2B) | Tandem (Landsat 8 & 9) | Constellation of ~200 CubeSats | C-band Synthetic Aperture Radar |
| **Spatial Resolution** | 10m (VNIR), 20m (Red Edge/SWIR) | 30m (VNIR/SWIR), 15m (Pan) | 3.0m - 3.7m | 1m - 50m (mode dependent) |
| **Temporal Revisit** | 5 days at equator (Telangana: ~3-5 days) | 8 days (combined 8+9) | Daily | 12-24 days |
| **Spectral Bands** | 13 bands (Red Edge, SWIR, Water Vapour) | 11 bands (Thermal TIRS, Coastal Aerosol) | 8 bands (Coastal, Blue, Green, Red, NIR) | Radar backscatter (HH, HV, VH, VV) |
| **Cloud Penetration** | Optical (Blocked by clouds) | Optical (Blocked by clouds) | Optical (Blocked by clouds) | Microwave (Cloud-penetrating) |
| **Data Licensing** | **Open Access / Free (CC BY-SA)** | **Open Access / Free (Public Domain)** | Commercial ($$$ per km²) | Specialized Government / Free academic |
| **Primary Suitability** | **Primary baseline for Acrevia Earth** | Secondary calibration / backup | High-value niche / Large corporate | Monsoon cloud backup (Phase III) |

---

## 2. Telangana Agricultural Fit Analysis
1. **Average Smallholder Field Size:** In Telangana (Warangal, Khammam, Nalgonda), average holding size is 1.1 to 2.5 acres (approx. 0.45 to 1.0 hectare).
2. **Resolution Adequacy:** 
   - A 1-hectare plot contains approximately **100 pixels** of Sentinel-2 10m bands (Red, NIR), enabling reliable internal zonal statistics after 1-pixel perimeter buffer erosion.
   - Landsat 30m provides only ~11 pixels per hectare, making it suitable for regional agro-climatic validation but less precise for individual plot boundaries.
3. **Monsoon (Kharif) Cloud Challenge:**
   - From June to September, cloud cover over Telangana often exceeds 70%.
   - Acrevia Earth applies strict quality filtering and integrates ground IoT leaf wetness and soil probes when optical satellite acquisitions are obscured.

---

## 3. Data Ingestion Architecture & Adapter Design
- **Primary Provider APIs:** Copernicus Data Space Ecosystem (CDSE) STAC API & AWS Open Data Sentinel-2 S3 registry (`s3://sentinel-cogs`).
- **Processing Architecture:** Vercel edge endpoints invoke async Cloudflare R2 / S3 caching workers to retrieve pre-computed COG (Cloud-Optimized GeoTIFF) band subsets for registered plot bounding boxes.
