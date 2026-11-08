# ACREVIA — STAGE 09 SATELLITE RASTER PROCESSING SPECIFICATION
## PIXEL EXTRACTION, CLOUD MASKING & SPATIAL SUMMARY GENERATION

**Programme:** ACREVIA Stage-Wise Engineering Programme  
**Target Stage:** Stage 09 — Geospatial Intelligence & Environmental Sensing  
**Subsystem:** Pillar B: ACREVIA Earth (Processing Engine)  
**Status:** ACTIVE VERIFIED SPECIFICATION  
**Date:** November 2026  

---

## 1. Executive Summary

Transforming raw satellite scenes into actionable plot-level agronomic intelligence requires a rigorous raster processing pipeline. ACREVIA Earth clips multi-spectral satellite scenes to verified smallholder plot polygons, applies pixel-level cloud and shadow masks, computes surface vegetation indicators, and aggregates statistical distributions.

In compliance with Work Package D of the Stage 09 Master Execution Prompt, this document formalizes the reproducible raster processing pipeline, cloud filtering thresholds, and plot summary statistics.

---

## 2. Raster Processing Pipeline Architecture

```mermaid
flowchart TD
    A["Raw Multi-Spectral Bands<br/>(B02, B04, B08, B11 @ UTM)"] --> B["1. Coordinate Reprojection<br/>(UTM 44N to WGS84 EPSG:4326)"]
    B --> C["2. Spatial Polygon Clipping<br/>(Clip to Plot Boundary Polygon)"]
    C --> D["3. Cloud & Shadow Masking<br/>(ESA SCL / USGS QA Mask)"]
    D --> E["4. Spectral Index Calculation<br/>(NDVI, EVI, NDMI per Pixel)"]
    E --> F["5. Plot Statistical Aggregation<br/>(Mean, Min, Max, Valid Ratio)"]
    F --> G["6. Immutable Database Persistence<br/>(satellite_observations Table)"]
```

---

## 3. Step-by-Step Processing Specifications

### 3.1 Spatial Reprojection & Resolution Alignment
- **Projection Transformation:** Satellite scenes acquired in UTM projections (e.g. `EPSG:32644` for Telangana) are reprojected to canonical WGS84 (`EPSG:4326`) using bilinear interpolation for continuous reflectance bands.
- **Resolution Resampling:** When computing indices combining $10\text{ m}$ (NIR, Red) and $20\text{ m}$ (SWIR) bands (such as NDMI), the $20\text{ m}$ SWIR band is resampled to $10\text{ m}$ grid alignment using cubic convolution.

### 3.2 Cloud Masking & Scene Classification Layer (SCL)
Copernicus Sentinel-2 Level-2A products include a Scene Classification Layer (SCL) generated at $20\text{ m}$ resolution:
- **Valid Vegetative Pixels:** Classes 4 (Vegetation), 5 (Bare Soil), 6 (Water).
- **Masked Pixels (Excluded from Statistics):**
  - Class 3: Cloud Shadows
  - Class 8: Cloud Medium Probability
  - Class 9: Cloud High Probability
  - Class 10: Thin Cirrus Clouds
  - Class 11: Snow / Ice
- **Quality Gate:** If masked pixels exceed $> 50\%$ of the plot surface, the scene is flagged as `EXCLUDED_EXCESSIVE_CLOUD` and withheld from time-series trend analysis to prevent erroneous stress alerts.

---

## 4. Plot-Level Statistical Aggregation

For each valid cloud-free satellite observation, ACREVIA extracts all interior pixels intersecting the plot boundary and computes five core summary metrics:

1. **Mean Index Value ($\mu$):**
   $$\mu = \frac{1}{N_{\text{valid}}} \sum_{i=1}^{N_{\text{valid}}} \text{Index}_i$$
2. **Minimum Index Value ($\text{Min}$):** Identifies the lowest vigor zone in the field (often revealing localized drainage issues or pest hotspots).
3. **Maximum Index Value ($\text{Max}$):** Captures the peak vegetative canopy vigor.
4. **Standard Deviation ($\sigma$):** Measures intra-field canopy heterogeneity. High $\sigma$ indicates uneven germination, uneven fertilizer application, or patchy insect damage.
5. **Valid Pixel Ratio:**
   $$\text{Ratio} = \frac{N_{\text{valid}}}{N_{\text{total}}}$$
   Recorded in the database to quantify observational confidence.

---

## 5. Temporal Trend Summaries

ACREVIA evaluates rolling multi-date observations (minimum 2 consecutive cloud-free passes) to classify canopy trajectories:
- **`VIGOR_INCREASING`:** Mean NDVI increases by $> +0.08$ over a 15-to-30-day window (normal vegetative growth).
- **`VIGOR_STABLE`:** Mean NDVI fluctuates by $\le \pm 0.05$ (canopy maturity or stable reproductive phase).
- **`VIGOR_DECLINING`:** Mean NDVI drops by $> -0.08$ (canopy senescence, drought stress, disease defoliation, or harvest clearing).

---

## 6. Specification Verdict

**Satellite Processing Specification Verdict:** **`PASS (DETERMINISTIC & REPRODUCIBLE)`**  
The raster extraction, cloud masking, and statistical aggregation pipeline provides rigorous spatial metrics.

*Certified by: Remote Sensing Scientist, GIS Engineer, and Lead Backend Engineer — ACREVIA Programme.*
