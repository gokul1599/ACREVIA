# KISANVISION — API AND INTEGRATION REGISTER

**Document Version:** 1.0.0  
**Status:** Approved for Stage 1 Baseline  
**Scope:** External Cloud Services, Pricing, Rate Limits, Provider Adapters & Privacy Assessment  
**Author:** Principal Software Architect, Senior Backend Engineer  

---

## 1. Provider Adapter Architecture Design

To ensure KisanVision remains resilient against external API price fluctuations, deprecations, or sudden outages, direct vendor SDK calls are strictly prohibited within core domain logic. Every integration connects through an abstract **Provider Adapter Interface**:

```mermaid
graph TD
    subgraph Domain["KisanVision Core Domain Services"]
        LLM_Service["Agronomic Dialogue & RAG Service"]
        Vision_Service["Visual Diagnosis Orchestrator"]
        Voice_Service["Speech Translation Engine"]
        Weather_Service["Micro-Climate Risk Engine"]
    end

    subgraph Adapters["Abstract Provider Adapters"]
        LLM_Adapter["ILLMProviderAdapter"]
        Vision_Adapter["IVisualReasoningAdapter"]
        Voice_Adapter["IVoiceTranslationAdapter"]
        Weather_Adapter["IWeatherProviderAdapter"]
    end

    subgraph Vendors["External Vendors & Fallbacks"]
        Groq["Groq API (Llama 3.3)"]
        Gemini["Google Gemini 1.5"]
        Sarvam["Sarvam AI (Saaras/Bulbul)"]
        Bhashini["Bhashini / Local Whisper"]
        OpenMeteo["Open-Meteo API"]
        IMD["IMD Mausam Open Feed"]
    end

    LLM_Service --> LLM_Adapter
    Vision_Service --> Vision_Adapter
    Voice_Service --> Voice_Adapter
    Weather_Service --> Weather_Adapter

    LLM_Adapter -->|Primary| Groq
    LLM_Adapter -->|Fallback| Gemini
    Vision_Adapter -->|Primary| Gemini
    Voice_Adapter -->|Primary| Sarvam
    Voice_Adapter -->|Fallback| Bhashini
    Weather_Adapter -->|Primary| OpenMeteo
    Weather_Adapter -->|Secondary| IMD
```

---

## 2. Exhaustive Provider Evaluation Matrix

### 2.1 Groq — High-Speed LLM Inference
- **Exact Intended Use:** Ultra-fast conversational query response generation and Telugu/Hindi agricultural dialogue completion using Llama 3.3 70B and Llama 3.1 8B.
- **Official Documentation URL:** `https://console.groq.com/docs`
- **Free-Tier Availability:** Yes (Free Developer Tier available upon phone/email verification).
- **Usage Restrictions:** Subject to dynamic request throttling; not intended for bulk batch retraining.
- **Rate Limits (Verified):** Free tier provides ~30 Requests Per Minute (RPM), up to 14,400 Tokens Per Minute (TPM), and 500,000 Tokens Per Day (TPD) for Llama-3 models.
- **Authentication Requirements:** Bearer API Key via HTTP header (`Authorization: Bearer $GROQ_API_KEY`).
- **Commercial-Use Restrictions:** Commercial use allowed under standard terms; models governed by Meta Llama 3 Community License.
- **Data Privacy Implications:** Queries processed through Groq cloud; zero data retention policy available on paid enterprise plans; ephemeral memory on developer tier.
- **Alternative Provider:** Google Gemini API, Together AI, local vLLM / Ollama (requires dedicated GPU).
- **MVP Requirement:** **REQUIRED FOR MVP (P0)**

---

### 2.2 Google Gemini — Multimodal Visual AI
- **Exact Intended Use:** High-precision visual reasoning for complex plant symptoms, ambiguous leaf lesions, multi-disease co-infections, and visual quality confirmation.
- **Official Documentation URL:** `https://ai.google.dev/docs`
- **Free-Tier Availability:** Yes (Google AI Studio Free Tier).
- **Usage Restrictions:** In free tier, input and output data may be reviewed by human reviewers to improve Google products. *Critical:* Paid Pay-As-You-Go tier disables human review and protects data privacy.
- **Rate Limits (Verified):** Gemini 1.5 Flash Free Tier: 15 RPM, 1,000,000 TPM, 1,500 Requests Per Day (RPD). Gemini 1.5 Pro: 2 RPM, 32,000 TPM, 50 RPD.
- **Authentication Requirements:** API key via query parameter or header (`x-goog-api-key: $GEMINI_API_KEY`).
- **Commercial-Use Restrictions:** Allowed under Google Cloud API Terms.
- **Data Privacy Implications:** Free tier logs data for training. Must explicitly transition to Google Cloud Vertex AI or Pay-As-You-Go tier with data-sharing disabled before ingesting real farmer photos.
- **Alternative Provider:** OpenAI GPT-4o mini, Anthropic Claude 3.5 Sonnet, local open-source vision backbones.
- **MVP Requirement:** **REQUIRED FOR MVP (P0)**

---

### 2.3 Hugging Face — Model Hub & Serverless Inference
- **Exact Intended Use:** Hosting fine-tuned model checkpoints (MobileNetV3, EfficientNet-B0), downloading tokenizers, staging public datasets, and optional cloud GPU training via Hugging Face Jobs.
- **Official Documentation URL:** `https://huggingface.co/docs`
- **Free-Tier Availability:** Yes (Unlimited public repository hosting; free serverless inference API with cold-start limits).
- **Usage Restrictions:** Free inference API has shared concurrency and no SLA; rate-limited on heavy batch calls.
- **Rate Limits (Verified):** Dynamic rate limiting based on cluster load (typically ~30–60 calls/min on standard accounts).
- **Authentication Requirements:** User Access Token (`Authorization: Bearer $HF_TOKEN`).
- **Commercial-Use Restrictions:** Permitted depending on individual model licenses (MIT/Apache 2.0).
- **Data Privacy Implications:** Private repositories remain strictly confidential; public repos are open source.
- **Alternative Provider:** GitHub Releases, AWS S3 / Cloudflare R2 for direct model weight hosting.
- **MVP Requirement:** **REQUIRED FOR MVP (P0)**

---

### 2.4 Sentence Transformers — Local Embedding Engine
- **Exact Intended Use:** Generating high-dimensional vector embeddings for PJTSAU agricultural knowledge chunks and farmer queries locally without cloud latency or per-token costs.
- **Official Documentation URL:** `https://sbert.net/`
- **Free-Tier Availability:** 100% Free Open-Source (Apache 2.0 License).
- **Usage Restrictions:** Runs entirely locally; bounded only by CPU/RAM throughput.
- **Rate Limits:** No external rate limits; ~150 chunks/sec on AMD Ryzen 5500U using `all-MiniLM-L6-v2` or `paraphrase-multilingual-MiniLM-L12-v2`.
- **Authentication Requirements:** None (Offline local execution).
- **Commercial-Use Restrictions:** None (Apache 2.0).
- **Data Privacy Implications:** 100% Private (No data ever leaves the local server boundary).
- **Alternative Provider:** Google `text-embedding-004`, OpenAI `text-embedding-3-small`, Hugging Face `bge-m3`.
- **MVP Requirement:** **REQUIRED FOR MVP (P0)**

---

### 2.5 Open-Meteo — Hyperlocal Weather API
- **Exact Intended Use:** Hourly and daily forecast data (Temperature, Relative Humidity, Precipitation, Wind Speed, Soil Moisture at 0-7cm) mapped to Telangana mandals for disease outbreak modeling and spray safety alerts.
- **Official Documentation URL:** `https://open-meteo.com/en/docs`
- **Free-Tier Availability:** Yes (Free for non-commercial open use; attribution required).
- **Usage Restrictions:** Up to 10,000 daily API calls for free tier.
- **Rate Limits (Verified):** Up to 600 calls/minute; 10,000 calls/day.
- **Authentication Requirements:** None required for free tier; commercial key passed via `&apikey=` query parameter.
- **Commercial-Use Restrictions:** Commercial subscription required once traffic exceeds 10,000 daily calls or if platform generates direct commercial revenue (commercial tiers start at €29/month).
- **Data Privacy Implications:** Only geographic coordinates (latitude/longitude) are transmitted; zero user PII.
- **Alternative Provider:** Tomorrow.io, WeatherAPI, IMD Mausam API.
- **MVP Requirement:** **REQUIRED FOR MVP (P0)**

---

### 2.6 IMD (India Meteorological Department) — National Weather & Agromet Bulletins
- **Exact Intended Use:** Ground-truth district agrometeorological advisories issued by IMD and PJTSAU Agromet Field Units (AMFUs).
- **Official Documentation URL:** `https://mausam.imd.gov.in` / `https://agromet.imd.gov.in`
- **Free-Tier Availability:** Public domain government bulletins (PDF/HTML).
- **Usage Restrictions:** No standardized public REST API for raw telemetry; requires automated PDF scraping and parsing.
- **Rate Limits:** Web server rate limiting; periodic scraping once daily.
- **Authentication Requirements:** None.
- **Commercial-Use Restrictions:** Public domain government data (National Data Sharing and Accessibility Policy - NDSAP).
- **Data Privacy Implications:** Public advisories; no user data shared.
- **Alternative Provider:** Open-Meteo.
- **MVP Requirement:** **P1 (Supplementary Verification for Open-Meteo)**

---

### 2.7 Sarvam AI — Indic Language Voice & Speech Engine
- **Exact Intended Use:** High-accuracy Telugu and Hindi Speech-to-Text (`saaras:v1`) and Text-to-Speech (`bulbul:v1`) tuned specifically to Indian regional phonetics and agricultural vernacular.
- **Official Documentation URL:** `https://docs.sarvam.ai/`
- **Free-Tier Availability:** Trial credits provided upon developer registration; pay-as-you-go thereafter.
- **Usage Restrictions:** API consumption capped by account balance.
- **Rate Limits (Verified):** Default rate limits: 10 concurrent requests; 60 RPM on standard developer accounts.
- **Authentication Requirements:** API key in header (`API-Subscription-Key: $SARVAM_API_KEY`).
- **Commercial-Use Restrictions:** Commercial use permitted under paid terms.
- **Data Privacy Implications:** Audio processed in Indian data center; compliant with Indian data localization standards.
- **Alternative Provider:** Bhashini (Government of India open AI initiative), OpenAI Whisper (Self-hosted on CPU).
- **MVP Requirement:** **REQUIRED FOR MVP (P0)**

---

### 2.8 Supabase / Neon — Managed PostgreSQL + pgvector
- **Exact Intended Use:** Primary multi-tenant relational database (Users, Farms, Plots, Diagnoses) and semantic vector store (`pgvector`) for KrishiBrain RAG embeddings.
- **Official Documentation URL:** `https://supabase.com/docs` / `https://neon.tech/docs`
- **Free-Tier Availability:**
  - Supabase: 2 free projects, 500 MB database storage, 1 GB file storage, 50,000 monthly active users.
  - Neon: 0.5 GB storage, serverless autoscaling with auto-suspend.
- **Usage Restrictions:** Free tier projects pause after 7 days of inactivity (Supabase). Neon auto-suspends compute when idle (<500ms cold start).
- **Rate Limits:** Connection pooling via PgBouncer supports up to 200 concurrent client connections on free tier.
- **Authentication Requirements:** PostgreSQL Connection URI with SSL (`postgresql://postgres:[PASSWORD]@...`).
- **Commercial-Use Restrictions:** Full commercial rights.
- **Data Privacy Implications:** Hosted on AWS `ap-south-1` (Mumbai, India) ensuring strict Indian data sovereignty.
- **Alternative Provider:** Self-hosted PostgreSQL on managed VPS or AWS RDS.
- **MVP Requirement:** **REQUIRED FOR MVP (P0)**

---

### 2.9 OpenStreetMap (Nominatim & Overpass) — Mapping & Reverse Geocoding
- **Exact Intended Use:** Reverse geocoding of farmer GPS coordinates to identify Mandal, District, and Gram Panchayat names in Telugu and English.
- **Official Documentation URL:** `https://nominatim.org/release-docs/latest/`
- **Free-Tier Availability:** 100% Free Open Data (ODbL License).
- **Usage Restrictions:** Nominatim usage policy strictly limits automated calls to a maximum of 1 request per second (1 RPS). Heavy batch queries prohibited.
- **Rate Limits:** 1 request per second; requires identifying `User-Agent`.
- **Authentication Requirements:** None (Custom HTTP User-Agent required).
- **Commercial-Use Restrictions:** Permitted with attribution ("© OpenStreetMap contributors").
- **Data Privacy Implications:** Coordinates transmitted; no PII attached.
- **Alternative Provider:** Google Maps Geocoding API, MapmyIndia (Mappls).
- **MVP Requirement:** **REQUIRED FOR MVP (P0)**

---

### 2.10 Copernicus Data Space Ecosystem (CDSE) — Sentinel-2 Satellite Multispectral Data
- **Exact Intended Use:** Retrieving 10-meter resolution multispectral imagery (B04-Red, B08-NIR) to compute Normalized Difference Vegetation Index (NDVI) and Normalized Difference Water Index (NDWI) for regional crop vigor monitoring.
- **Official Documentation URL:** `https://dataspace.copernicus.eu/`
- **Free-Tier Availability:** Yes (Free registration for European Space Agency open access).
- **Usage Restrictions:** Subject to concurrent download limits and fair use policies.
- **Rate Limits:** 4 concurrent requests on free academic/research profile.
- **Authentication Requirements:** OAuth 2.0 Client Credentials (`COPERNICUS_CLIENT_ID`, `COPERNICUS_CLIENT_SECRET`).
- **Commercial-Use Restrictions:** Open and free under European Union Copernicus Regulation.
- **Data Privacy Implications:** Purely earth observation imagery; zero personal data.
- **Alternative Provider:** Google Earth Engine, Planet Labs (Commercial).
- **MVP Requirement:** **P2 (Post-MVP / Phase 3 Capability)**

---

### 2.11 e-NAM (National Agriculture Market) / Agmarknet — Agricultural Commodity Mandi Prices
- **Exact Intended Use:** Daily market arrival prices (minimum, maximum, modal price per quintal) for cotton, paddy, and chilli across major Telangana APMC mandis (Warangal, Khammam, Suryapet).
- **Official Documentation URL:** `https://enam.gov.in` / `https://agmarknet.gov.in`
- **Free-Tier Availability:** Public open government portal.
- **Usage Restrictions:** Public web interface; raw API requires formal registration via `data.gov.in` (Open Government Data Portal).
- **Rate Limits:** Moderate; cached once every 24 hours.
- **Authentication Requirements:** API key via data.gov.in or automated scheduled ingest.
- **Commercial-Use Restrictions:** Open public data.
- **Data Privacy Implications:** Public commodity trading records.
- **Alternative Provider:** Agmarknet scraping, regional market committee bulletins.
- **MVP Requirement:** **P2 (Phase 2 Enhancement)**
