# ACREVIA — Stage 12 API Contracts Specification
**Base URL:** `/api/v1`  
**Authentication:** Bearer JWT required for all endpoints, with RBAC role authorization.

---

## 1. ACREVIA Connect Endpoints (`/api/v1/connect`)

### `GET /api/v1/connect/communities`
List available communities filtered by category or crop.
- **Query Params:** `category`, `crop_id`, `limit`, `offset`
- **Response `200 OK`:** `List[CommunityResponse]`

### `POST /api/v1/connect/communities/{community_id}/join`
Join an open agricultural community.
- **Response `200 OK`:** `CommunityMembershipResponse`

### `POST /api/v1/connect/communities/{community_id}/posts`
Create a question, field experience, or observation post.
- **Request Body:**
  ```json
  {
    "post_type": "QUESTION",
    "title": "Unusual leaf reddening in cotton after October rains",
    "content": "Noticed lower leaves turning purplish-red in Warangal plot. Is this magnesium deficiency or boll rot stress?",
    "language": "en",
    "crop_id": "cotton",
    "growth_stage": "BOLL_DEVELOPMENT"
  }
  ```
- **Response `201 Created`:** `CommunityPostResponse`

### `POST /api/v1/connect/posts/{post_id}/comments`
Add an answer or peer discussion comment.
- **Request Body:**
  ```json
  {
    "content": "Apply 1% Magnesium Sulphate + 1% Urea foliar spray as per PJTSAU advisory."
  }
  ```
- **Response `201 Created`:** `CommunityCommentResponse` (includes `is_expert_reply` flag if author is verified agronomist)

### `POST /api/v1/connect/posts/{post_id}/report`
Flag misleading, dangerous, or promotional content.
- **Request Body:**
  ```json
  {
    "reason_category": "DANGEROUS_ADVICE",
    "details": "Recommending unapproved pesticide cocktail violating CIBRC regulations."
  }
  ```
- **Response `201 Created`:** `CommunityReportResponse`

---

## 2. ACREVIA Commons Endpoints (`/api/v1/commons`)

### `POST /api/v1/commons/contributions`
Submit an agricultural explainer or advisory for formal review.
- **Request Body:**
  ```json
  {
    "contribution_type": "EXPLANATION",
    "title": "High Density Planting System (HDPS) in Telangana Cotton",
    "description": "Spacing guidelines (80x20 cm), canopy management with mepiquat chloride, and defoliation timing.",
    "original_language": "en",
    "crop_id": "cotton",
    "geographic_scope": "Telangana (Warangal, Adilabad)",
    "growth_stage": "VEGETATIVE",
    "evidence_references": ["PJTSAU HDPS Cotton Package of Practices 2025-26", "CICR Bulletin No. 42"]
  }
  ```
- **Response `201 Created`:** `KnowledgeContributionResponse` (status `SUBMITTED`)

### `POST /api/v1/commons/contributions/{contribution_id}/reviews`
Submit expert agronomic review (restricted to `AGRICULTURAL_EXPERT` role).
- **Request Body:**
  ```json
  {
    "decision": "APPROVE",
    "comments": "Agronomically verified against PJTSAU cotton research guidelines.",
    "scientific_rating": 5,
    "safety_assessment": "Safe for Telangana black cotton soils under rainfed/semi-irrigated regimes."
  }
  ```
- **Response `200 OK`:** `ContributionReviewResponse` (transitions status to `APPROVED`)

---

## 3. ACREVIA Collectives Endpoints (`/api/v1/collectives`)

### `POST /api/v1/collectives/organizations`
Register an FPO or cooperative workspace.
- **Request Body:**
  ```json
  {
    "name": "Kakatiya Cotton & Chilli Producer Company Ltd",
    "org_type": "FPO",
    "registration_number": "ROC-HYD-2024-FPO-8812",
    "district": "Warangal",
    "description": "FPO of 450 smallholder cotton and chilli farmers in Geesugonda and Wardhannapet."
  }
  ```
- **Response `201 Created`:** `AgriculturalOrganizationResponse`

### `GET /api/v1/collectives/organizations/{organization_id}/analytics`
Privacy-preserving aggregate metrics across members (enforces cohort size $\ge 5$, zero individual plot GPS or finances).
- **Response `200 OK`:**
  ```json
  {
    "organization_id": "uuid",
    "total_member_farms": 14,
    "aggregated_acreage": 42.5,
    "crop_distribution": { "cotton": 28.0, "chilli": 14.5 },
    "privacy_cohort_status": "VALID_COHORT_GE_5"
  }
  ```

---

## 4. ACREVIA Research Hub Endpoints (`/api/v1/research`)

### `POST /api/v1/research/projects`
Create an authorized research project.
- **Response `201 Created`:** `ResearchProjectResponse`

### `POST /api/v1/research/projects/{project_id}/consent`
Record explicit purpose-specific farmer consent.
- **Request Body:**
  ```json
  {
    "consent_scope": "ANNOTATED_IMAGES",
    "consent_version": "1.0"
  }
  ```
- **Response `201 Created`:** `ResearchConsentResponse`

### `POST /api/v1/research/annotations`
Submit expert diagnostic annotations with taxonomy versioning.
- **Response `201 Created`:** `AnnotationRecordResponse`

---

## 5. ACREVIA Extension Endpoints (`/api/v1/extension`)

### `GET /api/v1/extension/resources`
Query educational guides and government advisories.
- **Response `200 OK`:** `List[LearningResourceResponse]`

### `POST /api/v1/extension/events`
Create a training event or field demonstration.
- **Response `201 Created`:** `TrainingEventResponse`

---

## 6. ACREVIA Regional Pulse Endpoints (`/api/v1/regional-pulse`)

### `GET /api/v1/regional-pulse/signals`
Query qualified regional agricultural signals filtered by district or crop.
- **Query Params:** `district`, `crop_id`
- **Response `200 OK`:** `List[RegionalSignalResponse]`
