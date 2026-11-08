# ACREVIA — DEPLOYMENT GUIDE (STAGE 09)
## Migration, Environment Configuration & Release Procedures

---

## 1. Environment Variables & Secret Configuration

Add the following environment variables to your deployment environment (Vercel Project Settings and Backend `.env`):

```bash
# Core Database (Neon Singapore sin1)
DATABASE_URL=postgresql://acrevia_user:secret@ep-acrevia-sin1.neon.tech/acrevia_db?sslmode=require

# Security & Tokens
JWT_SECRET_KEY=production_strong_secret_key_minimum_32_characters
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Geospatial & Satellite Intelligence
SENTINEL_HUB_CLIENT_ID=optional_copernicus_or_sentinel_client_id
SENTINEL_HUB_CLIENT_SECRET=optional_copernicus_or_sentinel_client_secret
SATELLITE_CACHE_STORAGE_BUCKET=acrevia-satellite-cache

# Sensor Ingestion
DEVICE_AUTH_SECRET_KEY=production_device_telemetry_shared_secret
SENSOR_TELEMETRY_RATE_LIMIT=60/minute

# Predictive Research Feasibility
MINIMUM_YIELD_SAMPLES_THRESHOLD=50
```

---

## 2. Database Migrations Execution

Execute Alembic migrations from root:
```bash
# Run migration upgrade to latest revision
.venv/bin/python -m alembic -c backend/alembic.ini upgrade head
```

---

## 3. Vercel Production Build Verification

```bash
# In frontend directory
cd frontend
npm run lint
npm run build
```

Ensure output confirms all pages compiled statically (`○ / (Static)`) without runtime bundling errors.
