# ACREVIA Stage 14 — Connector Bridge Framework

## 1. Abstract Adapter Interface
Every external adapter connects through `BaseConnectorAdapter` in `backend/app/services/connector_bridge.py`:

```python
class BaseConnectorAdapter(ABC):
    @abstractmethod
    def get_capabilities(self) -> List[str]: ...

    @abstractmethod
    def validate_credentials(self, credentials: Dict[str, Any]) -> bool: ...

    @abstractmethod
    def health_check(self) -> Dict[str, Any]: ...

    @abstractmethod
    def fetch_data(self, params: Dict[str, Any]) -> List[Dict[str, Any]]: ...

    @abstractmethod
    def normalize_data(self, raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]: ...
```

---

## 2. Integrated Adapters
1. **SoilLabConnector:**
   - Standard: ICAR Soil Health Card & accredited regional testing labs.
   - Capabilities: `SOIL_MACRONUTRIENTS`, `SOIL_MICRONUTRIENTS`, `SALINITY_EC`, `PH_LEVELS`, `CARBON_STOCK`.
   - Normalization: Maps lab sample codes and nutrient concentrations into standard ACREVIA soil entities.
2. **MarketPriceConnector:**
   - Standard: e-NAM & Telangana Agricultural Market Committee (AMC) mandis.
   - Capabilities: `MODAL_PRICES`, `DAILY_ARRIVALS`, `GRADE_PREMIUMS`, `HISTORICAL_PRICE_TRENDS`.
3. **WeatherConnector:**
   - Standard: Automated Weather Stations (AWS), TSDPS, and IMD meteorological feeds.
   - Capabilities: `REALTIME_TEMP`, `RAINFALL_ACCUMULATION`, `WIND_SPEED`, `HUMIDITY`, `SHORT_RANGE_FORECAST`.
4. **SatelliteConnector:**
   - Standard: Multi-spectral Earth observation (Sentinel-2, Landsat, ISRO Bhuvan).
   - Capabilities: `NDVI_INDEX`, `NDWI_WATER_INDEX`, `EVI_CANOPY`, `CLOUD_MASK`, `SCENE_METADATA`.
5. **IoTTelemetryConnector:**
   - Standard: In-situ field sensor nodes (LoRaWAN / NB-IoT / Modbus gateways).
   - Capabilities: `SOIL_MOISTURE_PROBE`, `SOIL_TEMP`, `CANOPY_HUMIDITY`, `BATTERY_LEVEL`, `SIGNAL_RSSI`.
