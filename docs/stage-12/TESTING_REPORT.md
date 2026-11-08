# ACREVIA — Stage 12 Testing Strategy & Test Matrix
**Stage:** 12  
**Frameworks:** Pytest (Backend & ML), Node Test Runner (Frontend), TypeScript Compiler, Next.js Production Build

---

## 1. Test Scenarios Matrix

| Scenario | Objective | Validation Invariants |
| :--- | :--- | :--- |
| **Scenario A: ACREVIA Connect** | Community spaces, post publishing, expert replies, helpful votes, abuse reporting | Verified expert replies carry badge; helpful votes do not alter scientific trust; report queues functional. |
| **Scenario B: ACREVIA Commons** | Knowledge contribution submission, agricultural review, translation versioning, KrishiBrain handoff | Unreviewed contributions never enter RAG; only approved articles pass through ingestion. |
| **Scenario C: ACREVIA Collectives** | FPO registration, verification, membership roles, collective activities, privacy analytics | Aggregate statistics enforce minimum cohort size $\ge 5$; individual farmer ledgers and plots remain hidden. |
| **Scenario D: ACREVIA Research Hub** | Research project creation, purpose-specific consent, dataset contributions, annotation disagreements | Separate consent scopes; dual-annotation disagreement tracking; farm-disjoint dataset splitting. |
| **Scenario E: Regional Pulse** | Signal ingestion, privacy threshold ($\ge 3$ distinct farms), suppression of unverified outbreak claims | Unverified rumors labelled `UNVALIDATED_OBSERVATION`; confidence tiers strictly distinguished. |
| **Security & Authorization** | Role boundary enforcement and tenant isolation | Cross-org queries rejected; unauthorized review attempts rejected. |

---

## 2. Automated Test Commands
- Stage 12 backend suite: `.venv/Scripts/python -m pytest backend/tests/test_stage12.py -v`
- Full backend suite: `.venv/Scripts/python -m pytest backend/tests/`
- Frontend test runner: `npm --prefix frontend test`
- Next.js build verification: `npm --prefix frontend run build`
