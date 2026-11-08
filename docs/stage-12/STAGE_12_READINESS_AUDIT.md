# ACREVIA — Stage 12 Readiness Audit & Dependency Matrix
**Stage:** 12 — Agricultural Collaboration Network, Farmer Collectives, Expert Communities, Knowledge Contribution, Research Collaboration & Regional Agricultural Intelligence  
**Phase:** Phase III — Collaborative Agricultural Intelligence  
**Geographic Target:** Telangana-first (Warangal, Khammam, Suryapet, Karimnagar, Adilabad, Nalgonda)  
**Initial Supported Crops:** Cotton (*Gossypium hirsutum*), Rice (*Oryza sativa*), Chilli (*Capsicum annuum*)  
**Languages:** Telugu (`te`), English (`en`), Hindi (`hi`)  
**Audit Timestamp:** 2026-11-08

---

## 1. Executive Summary & Mandatory Entry-Gate Audit

This readiness audit verifies the platform prerequisites, security controls, and architectural dependencies for **ACREVIA Stage 12**. Stage 12 expands ACREVIA into a multi-stakeholder collaborative ecosystem connecting smallholder farmers, verified agronomists, farmer producer organizations (FPOs), cooperatives, and agricultural research institutions.

The audit was performed on a clean codebase with **109 passing automated tests** (75 backend + 27 frontend + 7 ML) and a verified Next.js 16 production build.

---

## 2. Dependency Matrix & Classification

| System Component | Prior Stage Dependency | Status | Architectural Invariant & Evidence |
| :--- | :--- | :--- | :--- |
| **Authentication & RBAC** | Stages 1, 4, 8 | `READY` | Bcrypt password hashing, JWT bearer tokens, role hierarchy (`FARMER`, `AGRICULTURAL_EXPERT`, `RESEARCHER`, `COMMUNITY_MODERATOR`, `ADMIN`). Reused directly without introducing a secondary auth system. |
| **Farm & Plot Ownership Boundaries** | Stages 1–4, 11 | `READY` | Multi-tenant isolation enforced via `verify_farm_access`. Strict boundary: collective/group membership **never** automatically exposes individual plot boundaries, diagnosis histories, or farm financial ledgers. |
| **Human Expert Verification (ExpertConnect)** | Stages 7–8 | `READY` | `ExpertProfile`, `ExpertReviewCase`, and agronomist credentialing are reused. Community expert badges must reflect validated `ExpertProfile` status; users cannot self-certify as experts. |
| **KrishiBrain RAG & Knowledge Source Governance** | Stage 5 | `READY` | `KnowledgeSource`, `KnowledgeDocument`, `KnowledgeChunk`, `KnowledgeEmbedding`. Community posts are strictly candidates for review; only approved contributions pass through formal ingestion. |
| **CropVision & Field Observations (CropPulse)** | Stages 3, 6, 8 | `READY` | Visual diagnostics and user observations. Reused for community image questions and regional pulse signal ingestion. |
| **RiskCast & Agro-Meteorology** | Stages 7, 9 | `READY` | Weather observations, PJTSAU rule alerts, and microclimate indicators serve as environmental context for regional pulse signals. |
| **ACREVIA Ledger & Market** | Stage 11 | `READY` | Decimal-safe financial ledgers and mandi prices. Collectives can view permitted aggregate cohort summaries (minimum cohort $\ge 5$), but private individual expenses remain strictly confidential. |
| **Primary Relational Database (Neon PostgreSQL)** | Stages 1–11 | `READY` | Single primary relational store in Singapore (`sin1`) with pgvector. Alembic migrations extend schema without table duplication. |
| **Application Hosting (Vercel Global Edge & Functions)** | Stages 6, 8 | `READY` | Next.js 16 App Router + FastAPI. Regional alignment Singapore (`sin1`). Bounded serverless execution. |
| **Trilingual Parity (Telugu, English, Hindi)** | Stages 6, 11 | `READY` | Complete dictionary parity across `messages/en.ts`, `te.ts`, and `hi.ts`. Original post languages preserved with explicit translation versioning. |
| **ACREVIA Connect Subsystem** | Stage 12 New | `READY FOR IMPLEMENTATION` | Structured communities, post lifecycle, helpful voting (which does not confer scientific truth), and moderation reporting. |
| **ACREVIA Commons Subsystem** | Stage 12 New | `READY FOR IMPLEMENTATION` | Multi-stage contribution review (`DRAFT` $\to$ `AGRICULTURAL_REVIEW` $\to$ `LANGUAGE_REVIEW` $\to$ `APPROVED`), controlled KrishiBrain handoff. |
| **ACREVIA Collectives Subsystem** | Stage 12 New | `READY FOR IMPLEMENTATION` | Organization profiles (FPOs/Cooperatives), verification lifecycle, member roles, shared activities, privacy-preserving aggregate metrics. |
| **ACREVIA Research Hub Subsystem** | Stage 12 New | `READY FOR IMPLEMENTATION` | Purpose-specific consent, dataset contributions, annotation workflows with disagreement tracking, dataset version manifests. |
| **ACREVIA Extension Subsystem** | Stage 12 New | `READY FOR IMPLEMENTATION` | Educational guides, training events, institutional resource publishing with verified attribution, learner feedback. |
| **ACREVIA Regional Pulse Subsystem** | Stage 12 New | `READY FOR IMPLEMENTATION` | Privacy-preserving aggregation ($\ge 3$ distinct farms), suppression of unverified outbreak claims, confidence tiering. |

---

## 3. Strict Entry-Gate & Governance Invariants

1. **Popularity $\ne$ Scientific Truth:**
   - A community post or answer receiving numerous upvotes or "helpful" marks is explicitly **not** promoted to a verified agricultural recommendation.
2. **Zero Automated Physical Actuation:**
   - The platform delivers human collaboration, knowledge sharing, and extension coordination; zero automated physical control of farm equipment.
3. **Strict Privacy Boundary for Farmer Collectives:**
   - FPO and cooperative workspaces never expose individual farmer expenses, receipts, or precise plot GPS coordinates by default.
   - Aggregate statistics require minimum cohort sizes ($\ge 5$ farms) to prevent reverse-identification.
4. **Governed KrishiBrain Knowledge Handoff:**
   - Community contributions must complete formal agricultural review (by an ExpertConnect certified agronomist) and language review before generating an ingestion job for production KrishiBrain RAG.
5. **No Unsupported Disease Outbreak Claims:**
   - Regional Pulse aggregates signals into confidence tiers (`FARMER_REPORT`, `MULTIPLE_INDEPENDENT`, `AI_ASSISTED`, `EXPERT_REVIEWED`, `OFFICIAL_ADVISORY`). Unverified signals are prominently labelled; sensational or unconfirmed "outbreak" declarations are suppressed.
6. **Purpose-Specific Research Consent:**
   - General platform Terms of Service do not authorize research dataset inclusion or AI model training. Separate, explicit, revocable consent records are mandatory.

---

## 4. Audit Verdict: `PROCEED WITH STAGE 12`
All dependencies and previous-stage prerequisites are satisfied. Proceed to Phase 12A comprehensive architectural monographs.
