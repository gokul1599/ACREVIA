# ACREVIA — DATABASE BACKUP & RESTORE RUNBOOK
## NEON SERVERLESS POSTGRESQL & PGVECTOR DISASTER RECOVERY PROCEDURES

**Programme:** ACREVIA Stage-Wise Finalization Programme  
**Target Stage:** Stage 08 — Production Hardening, End-to-End Validation & Observability  
**Target Database:** Neon PostgreSQL 18.6 with pgvector 0.8.6  
**Document Classification:** OPERATIONAL RUNBOOK  
**Date:** November 2026  

---

## 1. Overview & Recovery Objectives

This runbook establishes standard operating procedures (SOPs) for backing up, branching, and restoring the ACREVIA relational and vector database hosted on Neon Serverless PostgreSQL (`ep-muddy-mode-a1nd6rrb-pooler.ap-southeast-1.aws.neon.tech/neondb`).

### Service Level Objectives
- **Recovery Point Objective (RPO):** $< 5\text{ minutes}$. Neon maintains continuous Write-Ahead Log (WAL) archiving to cloud storage, enabling point-in-time recovery to any second within the retention window.
- **Recovery Time Objective (RTO):** $< 15\text{ minutes}$. Using Neon's copy-on-write storage architecture, a new recovery branch can be spawned and promoted in under 60 seconds, followed by connection string updating.

---

## 2. Backup Architecture & Retention Tiers

ACREVIA implements a three-tier defense-in-depth backup strategy:

1. **Continuous WAL Archiving (Neon Continuous Backup):**
   - Retained for 7 days in standard production tier (extendable to 30 days).
   - Enables restoration to any exact microsecond ($t_0$).
2. **Scheduled Logical Database Dumps (`pg_dump`):**
   - Daily automated logical export of schema and data using `pg_dump --format=custom`.
   - Exported to encrypted, versioned cloud object storage (`acrevia-backups-sin1`).
   - Retained for 90 days for statutory agricultural compliance.
3. **Instant Branch Snapshots (Pre-Deployment Safeguards):**
   - Prior to executing any Alembic migration or major release, an immutable point-in-time branch is created:
     ```bash
     neon branch create --name pre-release-stage08 --parent main
     ```

---

## 3. Emergency Restoration Procedures (Step-by-Step)

### Scenario A: Accidental Data Corruption or Unintended Truncation (Point-in-Time Branching)

When data corruption is detected at timestamp $T_{\text{corrupt}}$, recover to timestamp $T_{\text{target}} = T_{\text{corrupt}} - 60\text{s}$:

1. **Identify Corruption Timestamp:**
   - Inspect backend structured logs or audit logs to determine exact corruption time in UTC:
     `2026-11-08T11:45:00Z`
2. **Create Point-in-Time Branch via Neon CLI or Console:**
   ```bash
   neon branch create \
     --name recovery-pitr-20261108 \
     --parent main \
     --timestamp "2026-11-08T11:44:00Z"
   ```
3. **Validate Branch Integrity:**
   - Connect to the newly created branch:
     ```bash
     psql "postgresql://.../neondb?options=endpoint%3Dep-recovery-pitr"
     ```
   - Execute verification queries:
     ```sql
     SELECT count(*) FROM users;
     SELECT count(*) FROM farms;
     SELECT count(*) FROM observations;
     SELECT extversion FROM pg_extension WHERE extname = 'vector';
     ```
4. **Promote Recovery Branch to Production:**
   - Update `DATABASE_URL` environment variable in Vercel and backend runtime with the recovery endpoint.
   - Trigger a zero-downtime redeployment.

---

### Scenario B: Full Disaster Recovery from Logical Dump (`pg_restore`)

If the entire cloud project or region experiences catastrophic unrecoverable disruption:

1. **Retrieve Latest Encrypted Custom Dump:**
   ```bash
   aws s3 cp s3://acrevia-backups-sin1/daily/acrevia_dump_20261108.dump /tmp/acrevia_dump.dump
   ```
2. **Provision Target PostgreSQL Instance:**
   - Ensure target PostgreSQL 16+ or 18+ instance is created with `pgvector` installed:
     ```sql
     CREATE EXTENSION IF NOT EXISTS plpgsql;
     CREATE EXTENSION IF NOT EXISTS vector;
     ```
3. **Execute Clean Parallel Restoration:**
   ```bash
   pg_restore \
     --clean \
     --if-exists \
     --no-owner \
     --no-privileges \
     --dbname="$TARGET_DATABASE_URL" \
     --jobs=4 \
     /tmp/acrevia_dump.dump
   ```
4. **Reconcile Alembic Head:**
   ```bash
   alembic current
   # Expected output: f4894a11c87d (head)
   ```
5. **Run Automated Smoke Tests:**
   ```bash
   python -m pytest backend/tests/test_stage8_e2e.py -v
   ```

---

## 4. Media Storage Synchronization

- **Farmer Photographs & Media Files:**
  - Raw images are stored in S3-compatible private object storage partitioned by farm: `uploads/{farm_id}/{year}/{month}/{observation_id}/`.
  - Every `observation_media` record in the database maintains an immutable SHA-256 hash (`sha256_hash`).
- **Post-Restore Media Integrity Audit:**
  - A scheduled audit script iterates through `observation_media`, querying the object storage bucket to verify file existence and hash integrity. Any missing object is flagged in the incident log.

---

## 5. Operational Sign-Off & Verification

This runbook has been validated through simulated point-in-time recovery exercises. Live production credentials must never be written into documentation.

*Certified by: Lead Site Reliability Engineer and Senior Database Engineer — ACREVIA Programme.*
