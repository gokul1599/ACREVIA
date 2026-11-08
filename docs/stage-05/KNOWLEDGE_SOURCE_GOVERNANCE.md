# ACREVIA — KNOWLEDGE SOURCE GOVERNANCE PROTOCOL
## Approved Publisher Taxonomy, Verification Workflows, Document Lifecycle & Agronomic Scope

---

## 1. Governance Principles

KrishiBrain is the evidence and research foundation of ACREVIA. It operates under a strict **Zero-Hallucination, Proof-Backed Policy**:
1. **No Anonymous or Unverified Ingestion:** Only documents published by recognized, authoritative agricultural institutions are admissible into the production knowledge base.
2. **Provenance & Version Immutability:** Every chunk of text retrieved by the system retains a permanent, immutable link to its source document, publisher, document version, publication date, and physical page number.
3. **Controlled Approval State Machine:** Uploaded or ingested publications cannot be queried by farmers until an authorized agricultural expert or system administrator explicitly moves the source status to `APPROVED`.
4. **Decoupled from Private Records:** Public agronomic monographs, university advisories, and package-of-practices guides are stored in public knowledge schemas, completely separated from private farmer farm/plot observations.

---

## 2. Approved Publisher Tiers

| Tier | Institutional Category | Eligible Publishers | Authority Weight |
| :--- | :--- | :--- | :--- |
| **Tier 1 (Apex National & State)** | National & State Agricultural Universities & Councils | Indian Council of Agricultural Research (ICAR)<br>Professor Jayashankar Telangana State Agricultural University (PJTSAU)<br>Telangana State Department of Agriculture | 1.00 (Canonical) |
| **Tier 2 (Regional Extension)** | District Agricultural Research & Extension Centers | Krishi Vigyan Kendras (KVKs — Warangal, Khammam, Nalgonda, Adilabad)<br>Central Research Institute for Dryland Agriculture (CRIDA) | 0.95 (Regional) |
| **Tier 3 (Commodity Boards & Research)** | National Commodity Research Institutes | Central Institute for Cotton Research (CICR, Nagpur)<br>Indian Institute of Rice Research (IIRR, Hyderabad)<br>Indian Institute of Spices Research (IISR) | 0.95 (Crop-Specific) |
| **Tier 4 (Certified Agronomist Contributions)** | Expert Agronomist Case Submissions | Verified agronomists reviewing difficult field cases via ExpertConnect | 0.85 (Clinical Review) |

---

## 3. Source Approval Lifecycle

```
[DOCUMENT DISCOVERED / UPLOADED]
               │
               ▼
       [PENDING_REVIEW] ─── (Rejection Reason) ───> [REJECTED]
               │
      (Expert Verification)
               │
               ▼
          [APPROVED] ─── (Outdated / Superseded) ───> [EXPIRED]
               │
      (Flagged for Accuracy Issue)
               │
               ▼
         [SUSPENDED]
```

### Approval Invariants:
- A document in `PENDING_REVIEW`, `REJECTED`, `SUSPENDED`, or `EXPIRED` status is **automatically filtered out** of farmer-facing retrieval pipelines.
- Modifying or superseding a document produces a new `KnowledgeDocumentVersion` record. The previous version remains archived in the database so that historical citations from past queries remain fully verifiable and resolvable.

---

## 4. Initial Crop Taxonomies (Telangana Priority)

### 4.1 Cotton (*Gossypium hirsutum*)
1. **Soil & Land Preparation:** Deep black cotton soils (Vertisols), optimal pH 6.5–8.0, deep summer ploughing for pest pupae destruction.
2. **Sowing & Varieties:** Timely sowing with the onset of the Southwest monsoon (June 15 – July 15). Recommended BG-II hybrids and non-Bt refugia.
3. **Irrigation & Water Management:** Critical stages: square formation, flowering, and boll development. Prevention of waterlogging via ridge-and-furrow planting.
4. **Nutrient Management:** Balanced NPK based on soil testing. Split application of nitrogen and potassium to avoid vegetative flushing.
5. **Major Insect Pests:** Pink Bollworm (*Pectinophora gossypiella*), American Bollworm (*Helicoverpa armigera*), Sucking pests (Aphids, Jassids, Thrips, Whiteflies).
6. **Major Pathologies:** Bacterial Blight (*Xanthomonas citri pv. malvacearum*), Cercospora Leaf Spot (*Cercospora gossypina*), Alternaria Leaf Spot, Fusarium & Verticillium Wilt.
7. **Integrated Pest Management (IPM):** Pheromone traps (8/ha for monitoring, 20/ha for mass trapping), yellow sticky traps, neem oil formulations, CIBRC approved bio-rational interventions.

### 4.2 Rice (*Oryza sativa*)
1. **Establishment Methods:** Wet nursery transplanting and Direct Seeded Rice (DSR) under dry/semi-dry conditions.
2. **Seasons in Telangana:** Vanakalam (Kharif, June–November) and Yasangi (Rabi, November–April).
3. **Water Management:** Alternate Wetting and Drying (AWD) to reduce water consumption and methane emissions while suppressing sheath rot.
4. **Major Pests:** Brown Planthopper (*Nilaparvata lugens*), Yellow Stem Borer (*Scirpophaga incertulas*), Gall Midge.
5. **Major Diseases:** Rice Blast (*Magnaporthe oryzae*), Bacterial Leaf Blight (*Xanthomonas oryzae pv. oryzae*), Sheath Blight (*Rhizoctonia solani*).
6. **Deficiencies:** Zinc deficiency ("Khaira" disease symptoms in alkaline/calcified soils).

### 4.3 Chilli (*Capsicum annuum*)
1. **Nursery Management:** Pro-tray seedling raising under 50% shade nets to protect against early vector transmission.
2. **Transplanting & Spacing:** 35–40 day-old healthy seedlings transplanted during July–August.
3. **Major Insect Vectors & Pests:** Chilli Thrips (*Scirtothrips dorsalis*), Invasive Black Thrips (*Thrips parvispinus*), Mites (*Polyphagotarsonemus latus*).
4. **Major Diseases:** Anthracnose / Fruit Rot / Dieback (*Colletotrichum capsici*), Cercospora Leaf Spot, Powdery Mildew (*Leveillula taurica*), Chilli Leaf Curl Virus (transmitted by Whiteflies).
5. **IPM & Chemical Safety:** Monitoring vector thresholds, border crops (Maize/Sorghum), blue sticky traps for thrips, strictly adhering to pre-harvest intervals (PHI).
