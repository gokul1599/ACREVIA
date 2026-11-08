# ACREVIA 30-Day Pilot Data Collection Plan
## Multi-Modal Data Ingestion, Storage Schema & Protection Protocols
**Target Stage:** Stage 08 Remediation (`TASK-S08-01` / Evaluation Framework)  
**Scope:** Field Telemetry, Crop Images, Blinded Diagnoses, Usability Surveys  
**Compliance:** DPDP Act 2023 & Institutional Review Ethics  

---

## 1. Data Collection Architecture

```
+-----------------------------------------------------------------------------------+
| 1. CLIENT EDGE DATA (PWA / IndexedDB)                                             |
|    - Offline observation drafts & binary image blobs                              |
|    - Sync queue state transitions (QUEUED -> SYNCING -> SYNCED)                   |
|    - Device metadata (OS version, screen dimensions, network status)              |
+-----------------------------------------------------------------------------------+
                                          │
                                          ▼ (TLS 1.3 Sync)
+-----------------------------------------------------------------------------------+
| 2. BACKEND OPERATIONAL DATA (Neon PostgreSQL)                                     |
|    - Dithered farm coordinates (2 decimal places)                                 |
|    - Crop stage, pathology predictions & temperature-scaled confidences           |
|    - KrishiBrain query strings, voice transcripts & citation linkages             |
+-----------------------------------------------------------------------------------+
                                          │
                                          ▼
+-----------------------------------------------------------------------------------+
| 3. EXPERT & EVALUATION GROUND TRUTH                                               |
|    - Blinded KVK plant pathology physical inspection scoring sheets               |
|    - Expert Connect review actions (APPROVED, MODIFIED, REJECTED)                 |
|    - Day 30 System Usability Scale (SUS) survey responses (Telugu)                |
+-----------------------------------------------------------------------------------+
```

---

## 2. Data Categories & Collection Protocols

### 2.1 Edge & Client Telemetry Data
- **Storage Tier:** Client `acrevia_offline_db_v2` $\to$ Backend `sync_metadata` table.
- **Attributes Collected:**
  - `record_id`: UUIDv4
  - `timestamp_created`: Client ISO 8601 timestamp
  - `timestamp_synced`: Server ISO 8601 commit timestamp
  - `sync_latency_ms`: Elapsed time between network availability and successful server 200 response
  - `retry_count`: Number of backoff attempts before success
  - `network_type`: Cellular generation (`2g`, `3g`, `4g`, `wifi`) recorded at time of sync

### 2.2 Computer Vision Diagnostic Data
- **Storage Tier:** Object storage (`s3://acrevia-pilot/observations/`) + `observations` table in PostgreSQL.
- **Attributes Collected:**
  - `image_hash`: SHA-256 checksum of original JPEG image
  - `exif_metadata`: Camera focal length, exposure time, ISO (GPS stripped/dithered)
  - `predicted_crop`: Cotton, Rice, or Chilli
  - `top_1_class` & `top_1_prob`: Primary predicted pathology and raw softmax probability
  - `calibrated_confidence`: Post-temperature scaling probability
  - `top_3_classes`: Array of top-3 pathology candidates with probabilities
  - `ood_score`: Out-of-Distribution score; image quality gate flag (`PASS` / `REJECT`)
  - `gradcam_heatmap_uri`: Storage path for explainability activation map

### 2.3 KrishiBrain RAG Q&A Data
- **Storage Tier:** `rag_query_logs` table.
- **Attributes Collected:**
  - `query_modality`: `voice` or `text`
  - `query_text_raw`: User query string in Telugu, English, or Hindi
  - `query_language`: Detected language code (`te`, `en`, `hi`)
  - `retrieved_chunk_ids`: UUIDs of pgvector knowledge chunks retrieved
  - `citation_urls`: References to PJTSAU bulletins cited in response
  - `response_text`: Generated advisory text in vernacular language
  - `response_latency_ms`: Time to first token and total response completion time

### 2.4 KVK Expert Ground Truth & Concordance Data
- **Storage Tier:** `expert_evaluations` table + scanned physical field datasheets.
- **Attributes Collected:**
  - `evaluation_id`: UUIDv4
  - `plot_id` & `participant_id`: Anonymized cohort identifiers
  - `audit_date`: Date of physical field visit
  - `kvk_scientist_id`: Identifier of inspecting pathologist
  - `kvk_ground_truth_diagnosis`: Pathology class determined by physical inspection
  - `ai_prediction_viewed`: Boolean (enforcing blinded assessment)
  - `concordance_rating`: `CONCORDANT_EXACT`, `CONCORDANT_GENUS`, or `DISCORDANT`
  - `pop_alignment_score`: 1–5 Likert score on management guidance accuracy

### 2.5 Usability & Survey Data
- **Storage Tier:** `survey_responses` table.
- **Attributes Collected:**
  - `participant_id`: Anonymized farmer ID
  - `survey_type`: `BASELINE_DEMOGRAPHIC` or `EXIT_SUS_SURVEY`
  - `sus_responses`: Array of 10 integer ratings (1–5 scale)
  - `perceived_loss_prevention`: Binary / text qualitative response
  - `vernacular_clarity_rating`: 1–5 scale on Telugu translation naturalness
