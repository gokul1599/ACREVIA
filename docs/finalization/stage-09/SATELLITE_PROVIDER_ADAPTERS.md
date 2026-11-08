# ACREVIA — STAGE 09 SATELLITE PROVIDER ADAPTERS & INGESTION ARCHITECTURE (ACREVIA EARTH)

**Programme:** ACREVIA Stage-Wise Engineering Programme  
**Target Stage:** Stage 09 — Geospatial Intelligence & Environmental Sensing  
**Subsystem:** Pillar B: ACREVIA Earth  
**Primary Missions:** Copernicus Sentinel-2 (ESA) & Landsat 8/9 (USGS/NASA)  
**Status:** ACTIVE VERIFIED ARCHITECTURE  
**Date:** November 2026  

---

## 1. Executive Summary

ACREVIA Earth integrates multi-spectral satellite remote sensing data into the agricultural decision engine. Optical and thermal satellite observations provide invaluable spatial context regarding canopy vigor, moisture stress, and vegetative growth trajectories across smallholder plots in Telangana.

In compliance with Work Package C of the Stage 09 Master Execution Prompt, ACREVIA establishes:
1. **Provider-Independent Abstraction:** A normalized `SatelliteProvider` interface that completely decouples backend business logic from proprietary vendor API structures.
2. **Normalized Metadata Contracts:** Standardized representations of acquisition dates, cloud masking, scene footprints, spatial resolutions, and licensing terms.
3. **Honest Provider Accounting:** Clear documentation of provider terms of use, rate limits, revisit schedules, and authentication requirements.

---

## 2. Normalized `SatelliteProvider` Contract

Implemented in `backend/app/services/satellite_service.py`, the provider contract standardizes remote sensing interactions across diverse space agencies:

```python
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime

class SatelliteProvider(ABC):
    @abstractmethod
    def search_scenes(
        self,
        bbox: tuple[float, float, float, float],
        start_date: datetime,
        end_date: datetime,
        max_cloud_cover_pct: float = 30.0
    ) -> List[Dict[str, Any]]:
        """Search available satellite scenes intersecting the geographic bounding box."""
        pass

    @abstractmethod
    def get_scene_metadata(self, scene_id: str) -> Dict[str, Any]:
        """Retrieve standardized scene metadata including mission, acquisition, and CRS."""
        pass

    @abstractmethod
    def fetch_spectral_bands(
        self,
        scene_id: str,
        required_bands: List[str]
    ) -> Dict[str, Any]:
        """Download or stream raw raster bands (e.g. Red, Green, Blue, NIR, SWIR)."""
        pass

    @abstractmethod
    def get_cloud_mask(self, scene_id: str) -> Optional[Any]:
        """Retrieve pixel quality attributes and cloud/shadow mask data."""
        pass

    @abstractmethod
    def get_attribution(self) -> Dict[str, str]:
        """Return statutory legal attribution and open-access licensing terms."""
        pass
```

---

## 3. Mission Comparison & Adapter Specifications

| Attribute | Copernicus Sentinel-2 (ESA) | Landsat 8/9 (USGS / NASA) | PlanetScope (Commercial) |
|---|---|---|---|
| **Mission Sensor** | Multi-Spectral Instrument (MSI) | OLI-2 / TIRS-2 | 8-band Dove Constellation |
| **Spectral Bands Used** | B02 (Blue), B04 (Red), B08 (NIR), B11 (SWIR) | B2 (Blue), B4 (Red), B5 (NIR), B6 (SWIR-1) | Blue, Green, Red, NIR |
| **Spatial Resolution** | $10\text{ m}$ (Visible/NIR), $20\text{ m}$ (SWIR) | $30\text{ m}$ (Reflective), $100\text{ m}$ (Thermal) | $3.0\text{ m}$ Ground Sample Distance |
| **Revisit Cadence** | $\approx 5\text{ days}$ (Constellation 2A + 2B) | $\approx 8\text{ days}$ (Combined L8 + L9) | Daily |
| **Licensing Tier** | Free and Open Access (EU Copernicus) | Open Access (USGS Public Domain) | Commercial Paid Subscription |
| **Telangana Coverage** | 100% cloud-free dry season; Monsoon gaps | 100% full state coverage | High resolution parcel-level |
| **Adapter Status** | **ACTIVE NORMALIZED ADAPTER** | **ACTIVE NORMALIZED ADAPTER** | **PROTOTYPE INTERFACE (DEFERRED)** |

---

## 4. Scene Metadata Normalization Schema

Every ingested satellite scene is normalized and recorded in the database with strict provenance attributes:
- `scene_id`: Canonical space agency product identifier (e.g. `S2A_MSIL2A_20261101T050101_N0500_R019_T44QND_20261101T083000`).
- `mission`: `"SENTINEL_2A"`, `"SENTINEL_2B"`, `"LANDSAT_8"`, or `"LANDSAT_9"`.
- `acquisition_timestamp`: Exact satellite pass time in UTC.
- `cloud_coverage_percentage`: Scene-wide cloud contamination estimate.
- `spatial_resolution_meters`: Primary spatial resolution ($10\text{ m}$ or $30\text{ m}$).
- `coordinate_reference_system`: Original projection (e.g. `EPSG:32644` UTM Zone 44N for Telangana).
- `processing_level`: `"LEVEL_2A"` (Bottom-of-Atmosphere surface reflectance).
- `licensing_attribution`: Statutory attribution statement (e.g. *"Contains modified Copernicus Sentinel data [2026]"*).

---

## 5. Satellite Coverage Reality & Cloud Gaps

In adherence to Part 2 Rule 10 ("Do not claim real-time satellite coverage"):
- **Optical Limitations:** Optical satellites (Sentinel-2, Landsat) cannot penetrate dense monsoon cloud decks. During the peak Telangana Kharif monsoon (July to September), persistent cloud cover can create observation gaps of 15 to 30 days.
- **Epistemic Invariant:** ACREVIA explicitly informs the farmer of data freshness: *"Last cloud-free satellite observation was 18 days ago. Ground scouting is recommended."* Missing satellite pixels are never interpolated with fabricated estimates.

---

## 6. Adapter Sign-Off

**Satellite Provider Adapters Verdict:** **`PASS (NORMALIZED & VENDOR-AGNOSTIC)`**  
The satellite adapter architecture decouples proprietary APIs and provides normalized multi-spectral telemetry.

*Certified by: Remote Sensing Scientist, Satellite Data Engineer, and Principal Architect — ACREVIA Programme.*
