# ACREVIA Redis Configuration & Operations Manual
## Distributed Rate Limiting & Transient Cache Infrastructure
**Target Stage:** Stage 08 — Production Hardening & Operations  
**Task ID:** TASK-S08-02  
**Target Environment:** Vercel Serverless / Containerized FastAPI Replicas + Managed Redis (Upstash / AWS ElastiCache)  

---

## 1. Architectural Role

In the ACREVIA multi-tenant deployment, multiple FastAPI worker instances run across distributed containers or serverless runtimes. While domain entities and long-term state reside in Neon PostgreSQL (`pgvector`), transient high-frequency state—specifically sliding-window rate limits and short-lived throttling keys—is managed in Redis.

```
                    +--------------------------------+
                    |  Vercel Edge / API Gateway     |
                    +---------------+----------------+
                                    |
            +-----------------------+-----------------------+
            |                                               |
            v                                               v
+-----------------------+                       +-----------------------+
|  FastAPI Replica 1    |                       |  FastAPI Replica 2    |
| (Worker PID 101)      |                       | (Worker PID 204)      |
+-----------+-----------+                       +-----------+-----------+
            |                                               |
            +-----------------------+-----------------------+
                                    | (TLS 1.3 `rediss://`)
                                    v
                     +-----------------------------+
                     |  Managed Redis Instance     |
                     |  - Sliding-Window ZSETs     |
                     |  - Atomic Lua / Pipelines   |
                     |  - Auto-evicting TTLs       |
                     +-----------------------------+
```

---

## 2. Configuration Parameters

Environment variables configured in `backend/app/core/config.py`:

| Parameter | Type | Default Value | Production Recommended | Description |
| :--- | :---: | :---: | :---: | :--- |
| `REDIS_URL` | `str` | `""` | `rediss://default:<token>@<host>:6379` | Full connection URI. Must use `rediss://` (TLS) in staging and production. |
| `RATE_LIMIT_ENABLED` | `bool` | `True` | `True` | Global master toggle for rate limiting enforcement. |
| `RATE_LIMIT_FAIL_MODE` | `str` | `"open"` | `"open"` | `"open"` allows traffic if Redis times out; `"closed"` returns HTTP 503. |
| `RATE_LIMIT_NAMESPACE` | `str` | `"acrevia"` | `"acrevia:prod"` | Prefix for all Redis keys to avoid collision with shared caches. |

---

## 3. Connection Pooling & Latency Budgets

FastAPI workers initialize a thread-safe connection pool with strict socket timeouts:
- **Connection Timeout:** `0.5s` (prevents worker starvation during network jitter)
- **Read/Write Timeout:** `0.5s`
- **Max Connections per Worker:** `20`
- **Health Check Interval:** `30s` (recycles stale idle TCP sockets)

```python
redis_client = redis.Redis.from_url(
    settings.REDIS_URL,
    decode_responses=False,
    socket_connect_timeout=0.5,
    socket_timeout=0.5,
    health_check_interval=30
)
```

---

## 4. Memory Footprint & Sizing Model

Redis memory consumption is strictly bounded because:
1. Every rate limit key has a hard TTL of `window_seconds + 5s` (maximum 65 seconds).
2. Expired records inside active keys are removed on each request via `ZREMRANGEBYSCORE`.

### Memory Calculations:
- Single request entry in `ZSET`: ~128 bytes (score 8 bytes + UUID member 36 bytes + zset overhead).
- Base key overhead: ~80 bytes.
- 1 Active User emitting 15 requests in 60s: $80 + (15 \times 128) \approx 2.0\text{ KB}$.

| Workload Scenario | Active Concurrent Users | Memory Required | Recommended Redis Tier |
| :--- | :---: | :---: | :--- |
| **Stage 08 Pilot (Warangal/Nalgonda)** | 50 farmers + 5 agronomists | < 1 MB | Upstash Serverless Free / Micro |
| **District Expansion (10 Blocks)** | 5,000 farmers | ~12 MB | Upstash Standard / ElastiCache cache.t4g.micro |
| **State-Wide Scale (Telangana)** | 100,000 farmers | ~240 MB | ElastiCache cache.t4g.small (1.37 GB RAM) |

---

## 5. Operations & Eviction Policy

### Redis Server Settings:
```ini
# Memory eviction strategy
maxmemory 256mb
maxmemory-policy volatile-lru

# Persistence (Rate limiting is transient; disable RDB/AOF if dedicated)
save ""
appendonly no
```
*Note:* If Redis reaches `maxmemory`, `volatile-lru` evicts the keys with nearest expiration first. Because all rate limit keys have TTLs, this safely evicts the oldest sliding windows without throwing Out-Of-Memory errors.

---

## 6. Operational Health Checks & Verification Runbook

### Step 1: Connectivity & Latency Ping
```bash
redis-cli -u $REDIS_URL ping
# Output: PONG (Latency should be < 15ms)
```

### Step 2: Key Namespace Inspection
```bash
redis-cli -u $REDIS_URL keys "acrevia:*"
```

### Step 3: Key Inspection for a Rate Limited Route
```bash
# Inspect members and scores of active AI inference rate limit key
redis-cli -u $REDIS_URL zrangebyscore "acrevia:default:ai:usr_123" -inf +inf withscores
# Check remaining TTL
redis-cli -u $REDIS_URL ttl "acrevia:default:ai:usr_123"
```

### Step 4: Emergency Bypass (Circuit Breaker)
If Redis fails catastrophically or suffers an external provider outage:
1. Set `RATE_LIMIT_FAIL_MODE=open` (platform runs without blocking requests).
2. Or set `RATE_LIMIT_ENABLED=false` in Vercel environment variables to disable the rate limiter middleware completely until Redis service is restored.
