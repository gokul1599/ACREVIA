# ACREVIA — Stage 12 Deployment and Migration Guide
**Primary Target:** Vercel Global Edge & Functions (Singapore `sin1`) + Neon PostgreSQL 16 (Singapore `sin1`)

---

## 1. Database Migration Steps

1. **Verify Database Connectivity:**
   Confirm database target is configured on Neon PostgreSQL in Singapore (`sin1`).
2. **Execute Alembic Migration:**
   Apply revision `d2894a11c87d_stage12_collaborative_intelligence`:
   ```bash
   alembic upgrade head
   ```
3. **Verify Schema Generation:**
   Confirm creation of `communities`, `community_memberships`, `community_posts`, `community_comments`, `community_reports`, `knowledge_contributions`, `contribution_reviews`, `translation_versions`, `agricultural_organizations`, `organization_memberships`, `collective_activities`, `research_projects`, `research_consents`, `dataset_contributions`, `annotation_tasks`, `annotation_records`, `learning_resources`, `training_events`, `event_registrations`, `learning_feedback`, `regional_signals`, and `regional_signal_evidences`.

---

## 2. Reference Seed Data

Pre-seed canonical Telangana community spaces and extension guides:
- *Telangana Cotton Cultivators* (`cotton`)
- *Paddy / Rice Systems* (`rice`)
- *Red Chilli Growers* (`chilli`)
- *Soil Health & Irrigation Practice Circle*
- Standard PJTSAU package of practice extension guides for Cotton, Rice, and Chilli.

---

## 3. Pre-Deployment Verification

1. Backend pytest: `.venv/Scripts/python -m pytest backend/tests/` (100% green).
2. Frontend node test: `npm --prefix frontend test` (100% green).
3. Next.js production build: `npm --prefix frontend run build` (zero errors).
