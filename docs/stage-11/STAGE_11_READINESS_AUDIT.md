# ACREVIA — Stage 11 Readiness Audit & Dependency Matrix
**Stage:** 11 — Agricultural Economics, Farm Profitability Intelligence, Market Analytics, Harvest Management, Post-Harvest Intelligence & Produce Traceability  
**Geographic Target:** Telangana-first (Warangal, Khammam, Karimnagar, Nalgonda, Adilabad, Mahabubnagar)  
**Initial Supported Crops:** Cotton (*Gossypium hirsutum*), Rice (*Oryza sativa*), Chilli (*Capsicum annuum*)  
**Languages:** Telugu (`te`), English (`en`), Hindi (`hi`)  
**Audit Timestamp:** 2026-11-08

---

## 1. Executive Summary

This readiness audit assesses the system prerequisites, architectural compatibility, and runtime dependencies for **ACREVIA Stage 11**. Stage 11 establishes the agricultural business intelligence layer, connecting farm-level operational realities (expenses, harvests, quality grading) with external commercial realities (market arrivals, modal prices, mandi distances, and produce traceability) to evaluate season economics and support informed harvest/selling decisions.

Every component has been verified against the current codebase status (Stage 10 completed, 98 passing tests, clean tree on `main`).

---

## 2. Dependency Audit Matrix

| System Component | Prior Stage Dependency | Status | Notes & Invariants |
| :--- | :--- | :--- | :--- |
| **Neon PostgreSQL + pgvector** | Stages 1–10 | `READY` | Single primary relational store in Singapore (`sin1`). Connection pooling via PgBouncer. `Numeric(12, 2)` required for all financial amounts to prevent binary floating-point drift. |
| **FastAPI Backend Architecture** | Stages 1–10 | `READY` | Async ASGI runtime with Pydantic v2 schemas (`ConfigDict(from_attributes=True, populate_by_name=True)`). Router structure modularized under `/api/v1/`. |
| **Farm & Plot Hierarchy** | Stages 1–2 | `READY` | `Farm` (`id`, `total_acreage`), `Plot` (`id`, `farm_id`, `acreage`). Financial expenses and harvests link directly to plots and seasons. |
| **Crop & CropSeason System** | Stage 2 | `READY` | `Crop` (`id`, `name_en`, `name_te`, `name_hi`), `CropSeason` (`id`, `plot_id`, `crop_id`, `sowing_date`, `current_stage`, `status`). Season lifecycle provides the economic bounding box. |
| **Operations Ledger** | Stages 2, 10 | `READY` | `FarmOperation` tracks agronomic actions. Financial ledger complements operational actions with monetary cost and receipt verification. |
| **KrishiBrain RAG & Context** | Stage 5 | `READY` | Provides ag-economic knowledge grounding (APMC rules, standard moisture thresholds, MSP definitions). |
| **CropVision & ML Models** | Stages 3–4 | `READY` | Quality grading draws upon visual quality traits and post-harvest diagnostic checks. |
| **RiskCast & ExpertConnect** | Stages 7–8 | `READY` | Crop loss evidence packaging draws upon RiskCast weather incidents and ExpertConnect diagnostic reviews for insurance documentation. |
| **ACREVIA Digital Twin & Predict** | Stages 9–10 | `READY` | Harvest planning leverages yield forecasts from `predictive_service` and plot status from `twin_service`. |
| **Next.js 16 Frontend App** | Stage 6 | `READY` | Responsive mobile-first PWA, multilingual i18n (`te`, `en`, `hi`), Tailwind CSS, Accessible components. |
| **Agmarknet & e-NAM Adapters** | Stage 11 New | `READY FOR IMPLEMENTATION` | Mocked & normalized adapters with fallback offline datasets for Telangana mandis (Warangal, Khammam, Suryapet, etc.). |
| **Produce Traceability & QR Tokens** | Stage 11 New | `READY FOR IMPLEMENTATION` | Cryptographic tamper-evident UUID/HMAC tokens with zero PII exposure on public endpoints. |

---

## 3. Strict Agricultural & Technical Invariants

1. **Decimal-Safe Financial Arithmetic:**
   - Under no circumstances will binary `float` types be used for financial transactions, commodity prices, or ledger totals.
   - Database columns use `Numeric(12, 2)` (or `Numeric(10, 2)` for per-quintal rates).
   - Python code uses `decimal.Decimal` and `quantize(Decimal("0.01"))`.
2. **Honest Selling Support — Zero Profit Guarantees:**
   - The platform provides comparative market insights, net realization models (deducting transport, cess, and handling), and historical trends.
   - It strictly **does not promise higher profits, guaranteed sales, or speculative futures**.
3. **Traceability Public vs. Private Data Boundary:**
   - Public scanning of lot QR codes reveals: Crop, Variety, Harvest Date, Quality Grade, Certified Testing Station, Traceability Verification Status, and District/State.
   - Public scanning **redacts**: Farmer name, phone number, exact GPS plot coordinates, financial figures, and raw receipts.
4. **Physical Actuation Boundary:**
   - Recommendations remain purely decision support for the farmer; zero automated control over physical gates, warehouse locks, or machinery.

---

## 4. Audit Verdict: `PROCEED WITH STAGE 11`
All architectural prerequisites are satisfied. Proceed to Phase 11A comprehensive architectural documentation.
