# ACREVIA — ALEMBIC MIGRATION BASELINE REPORT
## LINEAR REVISION GRAPH, MIGRATION HEAD & SCHEMA PARITY
**Document:** `MIGRATION_BASELINE_REPORT.md`  
**Classification:** Database Integrity Audit  
**Date:** 2026-11-08  
**Component:** `backend/app/database/migrations/versions/`  
**Status:** `COMPLETE_VERIFIED`  

---

## 1. MIGRATION REVISION CHAIN VERIFICATION

The Alembic revision graph forms a single, linear, unbroken chain spanning 7 version files from base revision `f043516098f8` to target head `f4894a11c87d`:

```
f043516098f8 (initial_acrevia_schema)
    │
    ▼
e738192a54b1 (stage9_precision_agriculture)
    │
    ▼
b894a11c87d2 (stage10_digital_twin)
    │
    ▼
c1894a11c87d (stage11_agricultural_economics)
    │
    ▼
d2894a11c87d (stage12_collaborative_intelligence)
    │
    ▼
e3894a11c87d (stage13_climate_resilient_sustainability)
    │
    ▼
f4894a11c87d (stage14_interoperability_ecosystem) [HEAD]
```

---

## 2. METRIC COMPARISON & PARITY

| Property | Value | Verification Source |
|---|---|---|
| **Alembic Revisions in Repo** | 7 Revisions | File system inspection & AST parsing |
| **Alembic Heads** | **1 Head** (`f4894a11c87d`) | Verified linear chain (0 branches) |
| **Base Migration** | `f043516098f8` | `down_revision = None` |
| **Declarative ORM Models** | 132 Domain Entities | `Base.metadata.tables.keys()` |
| **Live Neon Tables** | 133 Tables | 132 ORM tables + 1 `alembic_version` |
| **Live Database Engine** | PostgreSQL 18.6 (ac70818) | AWS Singapore (`sin1`) |
| **pgvector Version** | v0.8.6 | Active in `public` schema |
| **Migration Consistency** | **100% Match** | All ORM entities represented in live schema |
