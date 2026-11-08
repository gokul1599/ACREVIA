# ACREVIA — STAGE 09 IoT DEVICE & SENSOR NETWORK ARCHITECTURE (ACREVIA SENSE)
## DEVICE REGISTRY, AUTHENTICATED TELEMETRY INGESTION & LIFECYCLE MANAGEMENT

**Programme:** ACREVIA Stage-Wise Engineering Programme  
**Target Stage:** Stage 09 — Geospatial Intelligence & Environmental Sensing  
**Subsystem:** Pillar C: ACREVIA Sense  
**Target Hardware:** In-Situ Soil Moisture Probes, Canopy Thermometers & Micro-AWS Nodes  
**Status:** ACTIVE VERIFIED ARCHITECTURE  
**Date:** November 2026  

---

## 1. Executive Summary

ACREVIA Sense provides the in-situ ground-truth telemetry layer for precision micro-climate and soil intelligence. Physical sensor nodes installed in agricultural plots measure root-zone soil moisture, soil temperature, canopy humidity, and rainfall, providing continuous validation for satellite indicators and gridded weather models.

In compliance with Work Package E of the Stage 09 Master Execution Prompt, ACREVIA Sense establishes:
1. **Managed Device Registry:** Comprehensive registration of sensor hardware, manufacturer specs, and plot bindings.
2. **Cryptographic Ingestion Authentication:** Individualized device authentication tokens (`dev_sec_...`) with replay protection and plot authorization checks.
3. **Formal Device Lifecycle States:** Explicit state machine governing hardware activation, calibration verification, and decommissioning.

---

## 2. IoT Data Model & Schema Relationships

Implemented in `backend/app/models/sensor.py` and persisted in Neon PostgreSQL:

```mermaid
erDiagram
    PLOTS ||--o{ SENSOR_DEVICES : hosts
    SENSOR_DEVICES ||--o{ SENSOR_MEASUREMENTS : records
    SENSOR_DEVICES ||--o{ SENSOR_CALIBRATIONS : calibrated_by

    SENSOR_DEVICES {
        string id PK
        string farm_id FK
        string plot_id FK
        string device_serial_number
        string device_category
        string auth_token_hash
        string lifecycle_status
        datetime last_seen_at
        float battery_voltage
    }

    SENSOR_MEASUREMENTS {
        string id PK
        string device_id FK
        string plot_id FK
        datetime recorded_at
        json measurements_json
        string data_quality_flag
        boolean calibration_valid
    }

    SENSOR_CALIBRATIONS {
        string id PK
        string device_id FK
        string calibrated_by
        datetime calibration_date
        datetime expires_at
        json coefficients_json
        boolean is_active
    }
```

---

## 3. Supported Sensor Hardware Categories

| Device Category | Physical Parameters Measured | Standard Agricultural Units | Target Agronomic Workflow |
|---|---|---|---|
| **`SOIL_PROBE`** | Volumetric Water Content (VWC) at 15cm & 30cm; Soil Temp | $\% \text{ VWC}, ^\circ\text{C}$ | Irrigation scheduling, soil moisture stress tracking. |
| **`WEATHER_STATION`** | Ambient Temp, Relative Humidity, Rain Gauge, Solar Rad | $^\circ\text{C}, \%, \text{mm}, \text{W/m}^2$ | RiskCast leaf wetness hours, micro-climate disease triggers. |
| **`CANOPY_SENSOR`** | Infrared Canopy Temperature, Leaf Wetness Duration | $^\circ\text{C}, \text{Hours}$ | Crop water stress index (CWSI), fungal infection favorability. |
| **`WATER_LEVEL`** | Standing water head in lowland paddy fields | $\text{cm}$ | Rice alternate wetting and drying (AWD) water management. |
| **`SOIL_EC_SENSOR`** | Bulk Electrical Conductivity, Salinity index | $\text{dS/m}$ | Soil salinity accumulation, fertilizer salt index. |

---

## 4. Secure Telemetry Ingestion Contract

Telemetry ingestion operates via an isolated, lightweight REST endpoint (`POST /api/v1/sense/telemetry`):

### 4.1 Ingestion Security & Validation Controls
1. **Bearer Token Authentication:** The sensor node passes its unique secret token in the `Authorization` header (`Bearer dev_sec_...`). Unauthenticated requests are rejected with `401 Unauthorized`.
2. **Plot Authorization Check:** The backend verifies that the requesting `device_id` is physically registered and bound to the submitted `plot_id`. A sensor node cannot push readings to a plot it does not belong to (`403 Forbidden`).
3. **Timestamp Validity & Replay Protection:** Ingested timestamps must fall within $\pm 24\text{ hours}$ of server UTC. Stale packets or duplicate timestamps from the same device are rejected to prevent replay attacks.
4. **Token Security:** Raw device secret tokens are hashed (SHA-256) prior to database storage; tokens are never exposed in UI responses.

---

## 5. Device Lifecycle State Machine

A sensor device transitions through six formalized operational states:

```mermaid
stateDiagram-v2
    [*] --> REGISTERED : Factory Registration
    REGISTERED --> PENDING_INSTALLATION : Assigned to Plot
    PENDING_INSTALLATION --> UNCALIBRATED : First Ping Received
    UNCALIBRATED --> ACTIVE : Lab Calibration Verified
    ACTIVE --> STALE : No Ping for > 48 Hours
    STALE --> ACTIVE : Telemetry Resumed
    ACTIVE --> SUSPENDED : Hardware Malfunction Flagged
    SUSPENDED --> ACTIVE : Recalibrated & Serviced
    ACTIVE --> RETIRED : Decommissioned
    RETIRED --> [*]
```

- **`REGISTERED`:** Device serial number provisioned; authentication token generated.
- **`UNCALIBRATED`:** Device is active and transmitting, but lacks a valid lab calibration record. Telemetry is flagged with `data_quality_flag: "UNCALIBRATED"`.
- **`ACTIVE`:** Device possesses valid, unexpired calibration coefficients. Telemetry is flagged as `data_quality_flag: "VALID"`.
- **`STALE`:** No telemetry received for $> 48\text{ hours}$. Triggers an operational advisory in the agronomist dashboard.

---

## 6. Architecture Verdict

**IoT Sensor Architecture Verdict:** **`PASS (SECURE & LIFECYCLE-CONTROLLED)`**  
The sensor registry, token authentication, plot binding, and state machine provide a secure foundation for in-situ telemetry.

*Certified by: IoT Systems Architect, Sensor Calibration Engineer, and Principal Architect — ACREVIA Programme.*
