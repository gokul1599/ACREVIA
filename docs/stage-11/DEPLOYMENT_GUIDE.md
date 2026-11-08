# ACREVIA — Stage 11 Deployment and Migration Guide
**Primary Target:** Vercel Global Edge & Functions (Singapore `sin1`) + Neon PostgreSQL 16 (Singapore `sin1`)

---

## 1. Database Migration Steps

1. **Verify Database Connectivity:**
   Ensure connection strings point to Neon PostgreSQL instance with connection pooling enabled.
2. **Execute Alembic Migration:**
   Apply migration version `stage11_agricultural_economics`:
   ```bash
   alembic upgrade head
   ```
3. **Verify Table Schema & Constraints:**
   Ensure `farm_expenses`, `financial_corrections`, `sale_transactions`, `market_locations`, `market_commodities`, `market_price_observations`, `harvest_plans`, `harvest_sessions`, `produce_quality_profiles`, `quality_measurements`, `storage_locations`, `storage_lots`, `produce_lots`, `lot_movements`, `crop_season_economics`, and `crop_loss_evidence_packages` are created.

---

## 2. Seed Data Deployment

Execute Stage 11 reference seed data:
- Pre-seeded Mandi locations: Warangal (Enumamula), Khammam, Karimnagar, Suryapet, Adilabad.
- Canonical market commodities for Cotton (Kapas), Rice (Paddy Common & Superfine), Chilli (Dry Red Teja).
- Quality profile templates conforming to AGMARK and Telangana agricultural standards.

---

## 3. Vercel Application Deployment & Verification

1. **Environment Variables:**
   - No new secret keys required; uses existing Neon DB URL and JWT signing secret.
2. **Pre-Deployment Build Verification:**
   - `npm --prefix frontend run build` must complete with zero TypeScript or styling errors.
3. **Smoke Tests:**
   - Verify `/api/v1/market/prices` returns latest mandi benchmarks.
   - Verify public QR route `/api/v1/trace/public/{token}` serves privacy-redacted payload.
