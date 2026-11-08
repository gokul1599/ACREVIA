# ACREVIA — SATELLITE INTELLIGENCE ARCHITECTURE (PILLAR B: ACREVIA EARTH)
## Remote-Sensing Analysis, Cloud Masking & Non-Diagnostic Vegetation Dynamics

---

## 1. Overview & Ethical Mandate
Acrevia Earth translates multi-spectral satellite imagery into actionable agricultural vegetation and moisture time-series for farm plots. 

> [!IMPORTANT]
> **EVIDENCE DISTINCTNESS MANDATE (NON-NEGOTIABLE):**
> Satellite optical indices measure canopy greenness, leaf area density, and surface moisture absorption. 
> **They do NOT diagnose plant diseases, identify fungal or bacterial pathogens, or confirm pest infestations.**
> Every satellite API response and user interface element must present clear, qualified language distinguishing canopy vigor from biological diagnosis.

---

## 2. Ingestion Pipeline & Cloud Masking

```mermaid
flowchart LR
    Source["Sentinel-2 L2A / Landsat-9 OLI-2"] --> SceneFilter["Scene Quality Gate (< 30% Cloud Cover)"]
    SceneFilter --> CloudMask["Pixel-Level SCL / QA Cloud & Shadow Mask"]
    CloudMask --> BandExtract["Band Extraction (Blue, Red, NIR, SWIR)"]
    BandExtract --> IndexCalc["Index Computation (NDVI, EVI, NDMI)"]
    IndexCalc --> ZonalStats["Plot Zonal Stats (Mean, Min, Max, Std)"]
    ZonalStats --> TimeSeries["Time-Series & Trend Analysis Engine"]
    TimeSeries --> Disclaimer["Mandatory Evidence Disclaimer Tagging"]
```

### 2.1 Cloud & Shadow Masking Protocol
Optical imagery in tropical and monsoon regions (such as Telangana's Kharif season) is vulnerable to cloud contamination and cloud shadow.
1. **Scene Pre-Filter:** Discard raw acquisitions with total cloud cover $> 30\%$.
2. **Scene Classification Layer (SCL) Filtering for Sentinel-2:**
   - Retain only valid land cover pixels: `Vegetation (4)`, `Bare Soils (5)`, `Water (6)`.
   - Strictly mask out: `Defective Pixels (0)`, `Cast Shadows (2)`, `Cloud Shadows (3)`, `Cloud Low Probability (7)`, `Cloud Medium Probability (8)`, `Cloud High Probability (9)`, `Thin Cirrus (10)`, `Snow/Ice (11)`.
3. **Valid Pixel Ratio Threshold:** If less than $60\%$ of pixels within a plot polygon are unmasked, the observation is marked `INSUFFICIENT_CLEAR_PIXELS` and excluded from rolling trend calculations.

---

## 3. Spectral Index Formulations

### 3.1 Normalized Difference Vegetation Index (NDVI)
$$NDVI = \frac{NIR - RED}{NIR + RED} = \frac{B8 - B4}{B8 + B4}$$
- Range: $[-1.0, 1.0]$. Healthy dense crops typically register between $0.55$ and $0.85$.
- Indicates: Relative photosynthetic activity, chlorophyll absorption, and canopy biomass.

### 3.2 Enhanced Vegetation Index (EVI)
$$EVI = 2.5 \times \frac{NIR - RED}{NIR + 6 \times RED - 7.5 \times BLUE + 1.0} = 2.5 \times \frac{B8 - B4}{B8 + 6(B4) - 7.5(B2) + 1.0}$$
- Optimizes: Canopy signal in high-biomass stages (such as flowering cotton and panicle rice) where standard NDVI saturates, while correcting for atmospheric aerosols and soil background reflectance.

### 3.3 Normalized Difference Moisture Index (NDMI)
$$NDMI = \frac{NIR - SWIR}{NIR + SWIR} = \frac{B8 - B11}{B8 + B11}$$
- Range: $[-1.0, 1.0]$.
- Indicates: Crop canopy water content and moisture stress before visible wilting occurs.

---

## 4. Zonal Statistics & Trend Classification

For each plot polygon, Acrevia Earth extracts pixel distributions:
- $\mu_{\text{NDVI}}$ (Mean), $\sigma_{\text{NDVI}}$ (Std Dev), $\min$, $\max$.
- **Trend Classification (30-day window):**
  - $\Delta \mu > +0.08$: `VIGOR_INCREASING` (Normal vegetative progression)
  - $-0.05 \le \Delta \mu \le +0.08$: `STABLE_VIGOR` (Plateau / Maturation)
  - $-0.15 \le \Delta \mu < -0.05$: `MODERATE_CANOPY_DECLINE` (Potential water deficit or pest defoliation)
  - $\Delta \mu < -0.15$: `SHARP_CANOPY_DROP` (Harvesting, complete clearing, or catastrophic lodging/storm damage)

---

## 5. Causal Qualification in User Explanations
When presenting satellite observations to the farmer:
- Never report: *"Satellite shows your cotton has Bacterial Blight."*
- Strictly report: *"Satellite imagery from Nov 03 shows a 12% decline in canopy vigor across Plot 2. This indicates potential localized crop stress (such as moisture deficit or leaf shedding). Please inspect the ground with CropVision to diagnose causes."*
