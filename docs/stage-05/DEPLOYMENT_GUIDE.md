# KrishiBrain Production Deployment & Infrastructure Guide
**ACREVIA — Agricultural Intelligence Platform (Stage 5)**  
*Document Version:* 1.0.0  
*Primary Infrastructure:* Neon PostgreSQL + pgvector  
*Serverless Compute:* Vercel (`sin1` - Singapore)  
*Orchestration:* FastAPI / Python 3.11+ / Alembic

---

## 1. Architecture & Geographic Region Alignment

To deliver sub-100ms response times for rural farmers in Telangana across constrained 3G/4G cellular networks, compute and database latency must be minimized:

- **Database Primary Region:** Neon Serverless PostgreSQL hosted in **Singapore (`ap-southeast-1`)**, the lowest latency tier to India.
- **Vercel Compute Region:** All FastAPI serverless functions and Next.js edge handlers are pinned to **`sin1` (Singapore)**.
- **Compute-to-Database Latency:** Intra-region datacenter network round-trip is $< 6\text{ ms}$, preventing high-latency database handshakes.

```
       [Farmer Device in Telangana]
                     │
                     │ Cellular (~45ms)
                     ▼
       ┌───────────────────────────┐
       │      Vercel Edge CDN      │
       │   Region: sin1 (Singapore)│
       └─────────────┬─────────────┘
                     │ Serverless Invoke (<10ms)
                     ▼
       ┌───────────────────────────┐
       │   FastAPI Serverless App  │
       │   KrishiBrain Retriever   │
       └─────────────┬─────────────┘
                     │ Direct TLS (<6ms)
                     ▼
       ┌───────────────────────────┐
       │  Neon PostgreSQL+pgvector │
       │   Region: ap-southeast-1  │
       └───────────────────────────┘
```

---

## 2. Neon Database & pgvector Provisioning

### 2.1 Enable pgvector Extension
Connect to the Neon PostgreSQL instance as superuser/admin and verify the vector extension:

```sql
-- Enable vector extension for 1536-dimensional semantic search
CREATE EXTENSION IF NOT EXISTS vector;

-- Verify extension is installed
SELECT * FROM pg_extension WHERE extname = 'vector';
```

### 2.2 Connection Pooling Configuration
Neon provides both direct and pooled connection strings. For serverless deployment on Vercel:
- **Use Pooled Endpoint:** Set `DATABASE_URL` to Neon's PgBouncer pooled endpoint (`-pooler` subdomain) on port `5432` or `6543`.
- **SSL Enforcement:** Append `?sslmode=require` to all connection strings.

---

## 3. Environment Configuration (`.env.production`)

Configure the following environment variables in the Vercel Project Dashboard:

```ini
# Environment
APP_ENV=production
PROJECT_NAME="ACREVIA - Agricultural Intelligence Platform"
PORT=8000

# Database (Neon PostgreSQL + pgvector in Singapore)
DATABASE_URL=postgresql://acrevia_user:SecretPassword@ep-cool-butterfly-123456-pooler.ap-southeast-1.aws.neon.tech/acrevia_db?sslmode=require

# Compute Region
VERCEL_REGION=sin1

# Authentication & Security
JWT_SECRET_KEY=94d8f1e2c8a7b6...production_secret_32bytes_minimum
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# KrishiBrain RAG & Embeddings
EMBEDDING_PROVIDER=local
# If transitioning to cloud provider:
# EMBEDDING_PROVIDER=cloud
# EMBEDDING_API_KEY=sk-proj-...
# EMBEDDING_MODEL=text-embedding-3-small

# Observability
LOG_LEVEL=INFO
```

---

## 4. Database Migrations Execution

Execute database migrations using Alembic prior to deploying updated serverless code:

```bash
# 1. Activate virtual environment
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# 2. Verify current migration state
alembic current

# 3. Upgrade to latest Stage 5 schema (including knowledge tables)
alembic upgrade head
```

### Tables Created:
- `knowledge_sources`
- `knowledge_documents`
- `knowledge_document_versions`
- `knowledge_chunks`
- `knowledge_embeddings`
- `ingestion_jobs`
- `knowledge_feedback`

---

## 5. Health Checks & Verification

After deployment, verify system health via automated health endpoints:

```bash
# Verify base platform health
curl -s -X GET https://api.acrevia.in/api/v1/health | jq .

# Verify knowledge service status
curl -s -X GET https://api.acrevia.in/api/v1/knowledge/sources \
  -H "Authorization: Bearer <token>" | jq .
```

---

## 6. Rollback & Disaster Recovery Protocol

If an ingestion job causes database lockup or an incompatible migration is deployed:

1. **Vercel Rollback:**
   - In the Vercel Dashboard, select the previous stable deployment and click **"Promote to Production"**. Rollback takes $< 15$ seconds.

2. **Database Rollback:**
   - To revert the knowledge table schema:
     ```bash
     alembic downgrade -1
     ```
   - Neon provides instant point-in-time branch recovery. Create a branch of the database prior to the incident if data corruption is suspected.
