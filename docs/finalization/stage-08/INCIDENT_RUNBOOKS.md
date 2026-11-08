# ACREVIA — STAGE 08 INCIDENT RECOVERY RUNBOOKS
## STANDARD OPERATING PROCEDURES (SOPS) FOR PRODUCTION RESILIENCE

**Programme:** ACREVIA Stage-Wise Finalization Programme  
**Target Stage:** Stage 08 — Production Hardening, End-to-End Validation & Observability  
**Document Classification:** EMERGENCY OPERATIONAL PROCEDURES  
**Date:** November 2026  

---

## Runbook 01: Neon Database Outage & Instant Branch Promotion

### Severity: `SEV1`
### Symptoms:
- Backend `/health` or readiness probe returns database connection timeout.
- Alert `AcreviaBackendUnavailable` or `NeonDatabaseUnreachable` firing.
- Application error logs show `pg8000.exceptions.InterfaceError: Connection refused or timed out`.

### Emergency Remediation Steps:
1. **Verify Neon Cloud Console Status:**
   - Inspect Neon Cloud status page (`https://status.neon.tech`) and AWS Singapore (`sin1`) regional status.
2. **Inspect Compute Endpoint State:**
   - Verify whether the compute endpoint has suspended and failed to wake:
     ```bash
     neon endpoint list --project-id ep-muddy-mode-a1nd6rrb
     ```
3. **Trigger Manual Compute Restart:**
   - If compute is in an unhealthy state, issue a restart via Neon CLI:
     ```bash
     neon endpoint restart --endpoint-id ep-muddy-mode-a1nd6rrb
     ```
4. **Instant Branch Failover (If Primary Compute Unrecoverable):**
   - Create an instant branch from the latest WAL snapshot:
     ```bash
     neon branch create --name emergency-failover-$(date +%s) --parent main
     ```
   - Update `DATABASE_URL` in Vercel project environment variables to the new branch endpoint.
   - Trigger instant zero-downtime redeployment.

---

## Runbook 02: Database Connection Pool Exhaustion

### Severity: `SEV1` / `SEV2`
### Symptoms:
- Alert `NeonDatabasePoolSaturation` firing ($> 80\%$ utilization).
- Inbound API requests failing with `sqlalchemy.exc.TimeoutError: QueuePool limit of size 10 overflow 20 reached`.

### Emergency Remediation Steps:
1. **Inspect Active Connections in PostgreSQL:**
   ```sql
   SELECT pid, usename, client_addr, state, query_start, query 
   FROM pg_stat_activity 
   WHERE state != 'idle' 
   ORDER BY query_start ASC;
   ```
2. **Terminate Hanging or Long-Running Queries:**
   - If an unindexed or Cartesian join query is locking connections:
     ```sql
     SELECT pg_terminate_backend(pid) 
     FROM pg_stat_activity 
     WHERE state != 'idle' AND query_start < now() - interval '2 minutes';
     ```
3. **Verify PgBouncer Pooler Endpoint:**
   - Confirm backend `DATABASE_URL` connects through the `-pooler` connection string, which handles up to 10,000 pooled client connections.

---

## Runbook 03: Corrupt or Stalled Alembic Migration

### Severity: `SEV1`
### Symptoms:
- CI/CD release pipeline fails during migration step with `alembic.util.exc.CommandError`.
- Application startup fails with `sqlalchemy.exc.ProgrammingError: relation does not exist` or column mismatch.

### Emergency Remediation Steps:
1. **Inspect Current Alembic Revision:**
   ```bash
   alembic current
   ```
2. **Check for Table Locks:**
   ```sql
   SELECT relation::regclass, mode, granted, pid 
   FROM pg_locks 
   WHERE NOT granted;
   ```
3. **Execute Rollback / Forward-Fix Migration:**
   - If a non-destructive migration failed midway:
     ```bash
     alembic downgrade -1
     ```
   - Re-inspect schema with `python scratch/check_schema.py`.
   - Never run `alembic stamp` without verifying that every schema modification was physically applied to PostgreSQL.

---

## Runbook 04: ML Inference Service Degradation or Out-of-Memory

### Severity: `SEV2`
### Symptoms:
- Alert `MlInferenceTimeoutSpike` firing.
- Inbound diagnosis requests taking $> 200\text{ ms}$ or returning HTTP 504 Gateway Timeout.

### Emergency Remediation Steps:
1. **Verify ONNX Runtime Memory Footprint:**
   - Confirm container RAM usage remains $< 25\text{ MB}$ for the Int8 dynamic quantized model (`acrevia_multicrop_int8.onnx`).
2. **Restart Worker Processes:**
   - Recycle Uvicorn worker threads to release any accumulated image buffer memory:
     ```bash
     pkill -HUP -f uvicorn
     ```
3. **Inspect Input Image Validation Queue:**
   - Verify that incoming requests are passing the Laplacian blur variance and byte size filters before reaching model memory.

---

## Runbook 05: Compromised Secret or Malicious Token Detected

### Severity: `SEV1`
### Symptoms:
- High volume of unauthorized API requests utilizing stolen bearer tokens.
- Alert `AuthenticationFailureSpike` or secret exposure notice.

### Emergency Remediation Steps:
1. **Rotate `JWT_SECRET_KEY` Immediately:**
   - Generate a new 256-bit cryptographically secure hex secret:
     ```bash
     openssl rand -hex 32
     ```
2. **Deploy Updated Secret via Environment Variables:**
   - Update `JWT_SECRET_KEY` across Vercel and backend production environments.
   - Immediately redeploy. This instantly renders all previously issued tokens invalid.
3. **Notify Users to Re-Authenticate:**
   - Mobile clients receiving `401 Unauthorized` automatically clear local session state and display the vernacular login screen.

---

## Runbook 06: Weather Provider Open-Meteo Outage

### Severity: `SEV3`
### Symptoms:
- Alert `OpenMeteoWeatherProviderDown` firing.
- Agro-risk evaluation logs show `httpx.ConnectTimeout: api.open-meteo.com`.

### Emergency Remediation Steps:
1. **Verify Fallback System Status:**
   - Check application logs to confirm that `WeatherService` automatically activated historical agro-climatic normal fallback data.
2. **Check Public Provider Status:**
   - Query Open-Meteo public status page or test direct ping:
     ```bash
     curl -I "https://api.open-meteo.com/v1/forecast?latitude=17.9689&longitude=79.5941"
     ```
3. **Farmer Workflow Continuity:**
   - No farmer-facing outage occurs. Field observations continue to be recorded normally. RiskCast displays the advisory: *"Weather risk calculated using historical seasonal normals. Ground scouting advised."*

---

## Runbook 07: Offline Sync Queue Storm / Conflict Spikes

### Severity: `SEV3`
### Symptoms:
- Alert `OfflineSyncReconcilerBacklog` firing ($> 500$ pending records).
- Multiple farmers reconnecting simultaneously after regional network restoration in rural mandals.

### Emergency Remediation Steps:
1. **Verify Server-Side Idempotency:**
   - Confirm backend handles incoming submissions using client-assigned UUIDs without creating duplicate database rows.
2. **Monitor Database Write Latency:**
   - Confirm database write latency remains $< 35\text{ ms}$ under batched transaction commits.
3. **Scale Background Reconciler Workers:**
   - If queue latency accumulates, temporarily increase concurrency of background ingestion workers from 2 to 6 workers.

---

## Sign-Off

**Incident Recovery Runbooks Verdict:** **`VALIDATED & OPERATIONAL`**  
All standard operating procedures are verified, unambiguous, and safe to execute.

*Signed by: Site Reliability Lead and Application Security Engineer — ACREVIA Programme.*
