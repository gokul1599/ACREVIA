# ACREVIA — Stage 11 Testing Strategy & Test Matrix
**Stage:** 11  
**Frameworks:** Pytest (Backend & ML), Node Test Runner (Frontend), TypeScript Compiler, Next.js Production Build

---

## 1. Test Scenarios Matrix

| Scenario | Objective | Validation Invariants |
| :--- | :--- | :--- |
| **Scenario A: Farm Financial Ledger** | Expense recording, payment status, receipt attachment, corrections | Decimal arithmetic exactness, audit trail generated on correction, no silent overwrite. |
| **Scenario B: Market Intelligence & Comparison** | Mandi price queries, commodity normalization, net realization calculation | Validates distance-based transport deductions, cess calculation, handling fees. |
| **Scenario C: Harvest Operations** | Multi-session harvesting, picking indexing, unit conversion, loss logging | Harvest session creation automatically generates a linked ProduceLot; loss tracking recorded. |
| **Scenario D: Post-Harvest Quality & Storage** | Quality measurement provenance, crop grading, storage lot allocation | Parameter validation (moisture, staple length, ASTA); storage capacity constraints. |
| **Scenario E: Produce Traceability & QR** | Lot generation, public vs. private data redaction, movement balance check | Public QR endpoint redacts farmer PII & exact GPS; lot transfers cannot exceed remaining quantity. |
| **Scenario F: Season Economics & Insurance** | Aggregated cultivation costs, gross revenue, net margin, loss evidence bundle | Incomplete data flag triggered when core categories are missing; SHA-256 package hash verified. |
| **Security & Authorization** | Multi-tenant isolation and input boundary validation | Cross-tenant access rejected; negative quantities rejected; malformed UUID rejected. |

---

## 2. Automated Test Execution Commands
- Backend Stage 11 suite: `.venv/Scripts/python -m pytest backend/tests/test_stage11.py -v`
- Full backend suite: `.venv/Scripts/python -m pytest backend/tests/`
- Frontend test suite: `npm --prefix frontend test`
- Next.js build verification: `npm --prefix frontend run build`
