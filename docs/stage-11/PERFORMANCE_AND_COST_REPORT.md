# ACREVIA — Performance and Cost Report
**Stage:** 11 — Agricultural Economics & Traceability  
**Target Infrastructure:** Vercel Global Edge & Functions (Singapore `sin1`) + Neon PostgreSQL 16 (Singapore `sin1`)

---

## 1. Latency Budgets & Execution Profiles

| Endpoint / Operation | Target Budget (p95) | Design Strategy |
| :--- | :---: | :--- |
| **`GET /api/v1/market/prices`** | $< 80\text{ ms}$ | Cached observations in Postgres with composite index `(commodity_id, observation_date DESC)`. |
| **`GET /api/v1/market/compare`** | $< 120\text{ ms}$ | In-memory haversine distance filtering across active Telangana mandis; lightweight math. |
| **`POST /api/v1/ledger/expenses`** | $< 100\text{ ms}$ | Single insert with foreign key validation and decimal casting. |
| **`GET /api/v1/trace/public/{qr_token}`** | $< 50\text{ ms}$ | Indexed unique scan on `qr_token`, zero join on private tables; cacheable at edge CDN. |
| **`GET /api/v1/economics/seasons/{id}`** | $< 150\text{ ms}$ | Optimized single-pass aggregation query for expenses and sales with database-level decimal sum. |

---

## 2. Storage & Compute Efficiency

1. **Storage Optimization in Neon:**
   - Expenses, harvests, quality tests, and lot movements use lean relational schemas with explicit constraints and indexing.
   - 10,000 farm seasons generate approximately 120 MB of economic and traceability records per year, fitting comfortably within standard tier allowances.
2. **Decimal Math Cost:**
   - Native PostgreSQL `NUMERIC` types carry negligible computational overhead compared to floating-point operations while providing absolute financial safety and legal compliance.
3. **Edge Caching for Public QR:**
   - Public traceability responses are static once a lot is sealed/graded, allowing Edge caching (`s-maxage=3600, stale-while-revalidate=86400`) on Vercel Edge Network.
