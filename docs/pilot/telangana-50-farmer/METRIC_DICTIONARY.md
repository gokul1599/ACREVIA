# ACREVIA 30-Day Pilot Metric Dictionary
## Formal Mathematical Specifications, Numerators, Denominators & Acceptance Thresholds
**Target Stage:** Stage 08 Remediation (`TASK-S08-01` / Evaluation Framework)  
**Scope:** Telangana 50-Farmer Field Pilot  

---

## 1. Technical & Systems Metrics (Pillar 1)

### `M-TECH-01`: Offline Data Retention Rate ($\text{ODR}$)
- **Definition:** Proportion of observation records saved in offline conditions that remain uncorrupted in IndexedDB upon network restoration.
- **Formula:**
  $$\text{ODR} = \frac{\sum_{i=1}^{N_{\text{offline}}} \mathbb{I}(\text{record } i \text{ retrieved uncorrupted})}{\sum_{i=1}^{N_{\text{offline}}} 1} \times 100\%$$
- **Numerator:** Count of successfully deserialized records in `acrevia_offline_db_v2`.
- **Denominator:** Total records initiated by client while in offline mode.
- **Target:** **100.0%** (Zero data loss allowed).

---

### `M-TECH-02`: Synchronization Success Rate ($\text{SSR}$)
- **Definition:** Ratio of queued sync records successfully committed to PostgreSQL on the backend.
- **Formula:**
  $$\text{SSR} = \frac{N_{\text{synced\_success}}}{N_{\text{sync\_attempts}}} \times 100\%$$
- **Numerator:** Count of records transitioning to state `SYNCED` with HTTP 200/201.
- **Denominator:** Total sync attempts initiated by PWA queue processor.
- **Target:** $\ge \mathbf{99.0\%}$.

---

### `M-TECH-03`: PWA Crash-Free Session Rate ($\text{CFSR}$)
- **Definition:** Percentage of app launches that do not encounter an unhandled runtime JS exception.
- **Formula:**
  $$\text{CFSR} = \left( 1 - \frac{N_{\text{crash\_sessions}}}{N_{\text{total\_sessions}}} \right) \times 100\%$$
- **Target:** $\ge \mathbf{99.5\%}$.

---

### `M-TECH-04`: Rate Limit False Positive Rate ($\text{RL-FPR}$)
- **Definition:** Percentage of legitimate farmer requests incorrectly throttled with HTTP 429.
- **Formula:**
  $$\text{RL-FPR} = \frac{N_{429\text{ on farmer tokens}}}{N_{\text{total farmer requests}}} \times 100\%$$
- **Target:** $< \mathbf{0.1\%}$.

---

## 2. Machine Learning & Vision Metrics (Pillar 2)

### `M-ML-01`: Top-1 Agronomist Concordance ($\text{CONC}_1$)
- **Definition:** Agreement between model top-1 predicted pathology and KVK pathologist blinded diagnosis.
- **Formula:**
  $$\text{CONC}_1 = \frac{1}{N_{\text{ground\_truth}}} \sum_{i=1}^{N_{\text{ground\_truth}}} \mathbb{I}(\hat{y}_{i}^{(1)} = y_{i}^{*}) \times 100\%$$
- **Target:** $\ge \mathbf{75.0\%}$.

---

### `M-ML-02`: Top-3 Agronomist Concordance ($\text{CONC}_3$)
- **Definition:** Presence of KVK pathologist ground truth within model's top-3 predictions.
- **Formula:**
  $$\text{CONC}_3 = \frac{1}{N_{\text{ground\_truth}}} \sum_{i=1}^{N_{\text{ground\_truth}}} \mathbb{I}(y_{i}^{*} \in \{\hat{y}_{i}^{(1)}, \hat{y}_{i}^{(2)}, \hat{y}_{i}^{(3)}\}) \times 100\%$$
- **Target:** $\ge \mathbf{85.0\%}$.

---

### `M-ML-03`: Expected Calibration Error ($\text{ECE}$)
- **Definition:** Weighted average absolute difference between prediction confidence and actual accuracy across $M=10$ bins.
- **Formula:**
  $$\text{ECE} = \sum_{m=1}^{M} \frac{|B_m|}{N} \left| \text{acc}(B_m) - \text{conf}(B_m) \right|$$
- **Target:** $\le \mathbf{0.12}$.

---

### `M-ML-04`: Out-of-Distribution (OOD) False Rejection Rate ($\text{FRR}$)
- **Definition:** Valid crop leaf images incorrectly rejected by the quality gate as "Non-Crop" or "OOD".
- **Formula:**
  $$\text{FRR} = \frac{N_{\text{valid leaves rejected}}}{N_{\text{total valid leaf images}}} \times 100\%$$
- **Target:** $< \mathbf{8.0\%}$.

---

## 3. KrishiBrain RAG & Agronomic Guidance Metrics (Pillar 3)

### `M-RAG-01`: PJTSAU PoP Alignment Score ($\text{ALN}$)
- **Definition:** Mean rating assigned by KVK agronomists evaluating advice against university bulletins (scale 1–5).
- **Formula:**
  $$\text{ALN} = \frac{1}{K} \sum_{k=1}^{K} S_k$$
- **Target:** $\ge \mathbf{4.5 / 5.0}$.

---

### `M-RAG-02`: Citation Grounding Rate ($\text{CGR}$)
- **Definition:** Percentage of KrishiBrain responses containing verified citations to agricultural knowledge base.
- **Formula:**
  $$\text{CGR} = \frac{N_{\text{responses with valid citations}}}{N_{\text{total responses}}} \times 100\%$$
- **Target:** $\mathbf{100.0\%}$.

---

### `M-RAG-03`: Chemical Safety Violation Rate ($\text{CSVR}$)
- **Definition:** Proportion of responses containing unapproved chemical inputs or off-label dosage.
- **Formula:**
  $$\text{CSVR} = \frac{N_{\text{unapproved chemical recommendations}}}{N_{\text{total chemical recommendations}}} \times 100\%$$
- **Target:** **Exactly 0.0%** (Zero Tolerance).

---

## 4. Usability & Socio-Economic Behavioral Metrics (Pillar 4)

### `M-UX-01`: System Usability Scale Score ($\text{SUS}$)
- **Definition:** Composite score computed from standard 10-item Likert scale survey administered in Telugu.
- **Formula:**
  $$\text{SUS} = 2.5 \times \left[ \sum_{i \in \text{odd}} (R_i - 1) + \sum_{j \in \text{even}} (5 - R_j) \right]$$
- **Target:** Mean Cohort $\text{SUS} \ge \mathbf{75.0}$ (Corresponds to Grade B+ / Excellent).

---

### `M-UX-02`: Voice Interaction Modality Ratio ($\text{VMR}$)
- **Definition:** Share of KrishiBrain interactions conducted using voice audio input.
- **Formula:**
  $$\text{VMR} = \frac{N_{\text{voice queries}}}{N_{\text{total queries}}} \times 100\%$$
- **Target:** $\ge \mathbf{40.0\%}$.

---

### `M-UX-03`: Independent Task Completion Rate ($\text{ITCR}$)
- **Definition:** Percentage of observations recorded and submitted without requiring field assistant intervention.
- **Formula:**
  $$\text{ITCR} = \frac{N_{\text{independent submissions}}}{N_{\text{total submissions}}} \times 100\%$$
- **Target:** $\ge \mathbf{85.0\%}$.

---

### `M-UX-04`: Self-Reported Loss Prevention Utility ($\text{LPU}$)
- **Definition:** Farmers reporting that platform advice helped avoid crop damage or save input costs.
- **Formula:**
  $$\text{LPU} = \frac{N_{\text{positive utility responses}}}{N_{\text{participating farmers}}} \times 100\%$$
- **Target:** $\ge \mathbf{75.0\%}$.
