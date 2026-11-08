# ACREVIA — LIVE INTEGRATION & THIRD-PARTY CONNECTOR REGISTER
## Third-Party Provider Status, Activation Lifecycle & Credential Inventory

**Document Version:** 1.0.0  
**Status:** Canonical Integration Status Matrix  
**Guiding Principle:** Zero fictitious responses. Connectors without production credentials operate in verified sandbox mode with explicit state labeling.

---

### 1. Integration Status Matrix

| Connector Domain | Provider / Service | Protocol & Contract | Current State | Fallback Mechanism | Action Required to Go Live |
|---|---|---|---|---|---|
| **Agro-Meteorology** | Open-Meteo Weather API | REST / JSON (Hourly & Forecast) | `LIVE_VALIDATED` | Rolling 72h historical snapshot cache | None. Operational and verified. |
| **Market Intelligence** | Agmarknet / e-NAM | REST API / Mandi Price Feed | `CONFIGURED_SANDBOX` | Validated regional baseline price fixtures (Telangana mandis) | Inject authorized `MARKET_DATA_API_KEY` from DMI. |
| **Satellite Remote Sensing** | ESA Sentinel-2 / Copernicus STAC | Open STAC API / WMS | `SANDBOX_VALIDATED` | Synthetic/Sandbox multi-spectral bands with explicit research disclaimers | Configure Copernicus Data Space OAuth2 credentials (`SATELLITE_CLIENT_ID`, `SATELLITE_CLIENT_SECRET`). |
| **Earth Observation** | USGS Landsat-9 | STAC Earth Search | `CONFIGURED_SANDBOX` | Cloud-masked optical band simulations | USGS M2M API token configuration. |
| **Farmer Notifications** | Twilio / Exotel SMS Gateway | REST API / DLT Approved Templates | `NOT_CONFIGURED` | In-app notification center & PWA service worker push | Register DLT SMS headers with TRAI; supply `SMS_PROVIDER_API_KEY`. |
| **Farmer Messaging** | Meta WhatsApp Business API | Cloud API / Webhook | `AWAITING_PROVIDER_APPROVAL` | In-app notification feed & SMS fallback | Complete Meta Business Verification; configure `WHATSAPP_TOKEN` and `WHATSAPP_PHONE_ID`. |
| **Soil Laboratory Assays** | Telangana Soil Testing Laboratories | CSV / JSON Data Exchange Adapter | `SANDBOX_VALIDATED` | Manual certified lab certificate upload (`SoilSample`) | Sign institutional MoU with Department of Agriculture; issue partner API key. |
| **University Knowledge** | PJTSAU Vyavasaya Panchangam | Ingestion Pipeline / RAG | `LIVE_VALIDATED` | Seeded 48 PJTSAU/ICAR agronomic guides | Continuous annual publication update. |

---

### 2. Environment Variable & Secret Inventory

The following environment variables govern external integrations. Secret values must be configured via Vercel Project Settings or secure environment files and never committed to version control:

```env
# -----------------------------------------------------------------------------
# Core Database & Security
# -----------------------------------------------------------------------------
DATABASE_URL=postgresql+pg8000://...
JWT_SECRET_KEY=...
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=30

# -----------------------------------------------------------------------------
# Microservice Interconnection
# -----------------------------------------------------------------------------
ML_INFERENCE_URL=http://localhost:8001
NEXT_PUBLIC_API_URL=https://api.acrevia.in

# -----------------------------------------------------------------------------
# Market Data Providers (Stage 11)
# -----------------------------------------------------------------------------
MARKET_DATA_PROVIDER=AGMARKNET
MARKET_DATA_API_KEY=
MARKET_DATA_BASE_URL=https://api.agmarknet.gov.in/v1

# -----------------------------------------------------------------------------
# Satellite Earth Observation Providers (Stage 09)
# -----------------------------------------------------------------------------
SATELLITE_PROVIDER=COPERNICUS_STAC
SATELLITE_CLIENT_ID=
SATELLITE_CLIENT_SECRET=
SATELLITE_STAC_URL=https://catalogue.dataspace.copernicus.eu/stac

# -----------------------------------------------------------------------------
# Farmer Notification & Messaging Gateways (Optional)
# -----------------------------------------------------------------------------
SMS_PROVIDER=EXOTEL
SMS_PROVIDER_ACCOUNT_SID=
SMS_PROVIDER_API_KEY=
SMS_PROVIDER_SENDER_ID=ACREVI

WHATSAPP_PROVIDER=META_CLOUD_API
WHATSAPP_PROVIDER_TOKEN=
WHATSAPP_PHONE_NUMBER_ID=
WHATSAPP_BUSINESS_ACCOUNT_ID=
```

---

### 3. Step-by-Step Production Activation Runbook

1. **Market Prices (e-NAM / Agmarknet):**
   * Register on the National Agriculture Market developer portal (`enam.gov.in`).
   * Whitelist server outbound IP address.
   * Add `MARKET_DATA_API_KEY` to Vercel and backend `.env`.
   * Switch status from `CONFIGURED_SANDBOX` to `LIVE_VALIDATED`.
2. **Sentinel-2 Satellite Intelligence:**
   * Create account at `dataspace.copernicus.eu`.
   * Generate OAuth2 Client ID and Secret in Copernicus User Portal.
   * Populate `SATELLITE_CLIENT_ID` and `SATELLITE_CLIENT_SECRET`.
   * Run verification script `python -m backend.app.services.earth_service` to confirm live tile fetch.
3. **Farmer SMS / WhatsApp Alerts:**
   * Register ACREVIA enterprise entity and DLT message templates on TRAI portal (Vilpower/Jio/Airtel DLT).
   * Submit WhatsApp message templates for disease alerts, weather advisories, and expert case updates to Meta for template approval.
   * Configure Meta Webhook endpoint `/api/v1/webhooks/whatsapp` with verify token.
