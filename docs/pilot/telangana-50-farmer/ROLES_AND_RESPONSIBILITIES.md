# ACREVIA 50-Farmer Telangana Pilot: Roles, Responsibilities & Governance Matrix
## Operational Roles, RACI Matrix & Escalation Hierarchy
**Target Stage:** Stage 08 Remediation (`TASK-S08-01`)  
**Scope:** Multi-stakeholder governance across ACREVIA, KVK PJTSAU, and Farmer Cohorts  

---

## 1. Stakeholder Role Definitions

### 1.1 Participating Farmer ($N = 50$)
- **Primary Function:** In-field system user and primary crop observer.
- **Key Responsibilities:**
  - Attend Phase 1 onboarding and sign informed consent.
  - Perform twice-weekly crop scouting (minimum 8 observations over 30 days).
  - Capture clear leaf photographs adhering to the 5-point capture rule.
  - Record voice/text symptoms and review generated AI advisory.
  - Report unexpected crop conditions or app bugs to the Village Field Assistant.
  - Participate in the Day 30 exit survey and usability interview.

### 1.2 Village Field Assistant / Enumerator ($N = 2$, 1 per cluster)
- **Primary Function:** On-the-ground technical facilitator and vernacular liaison.
- **Key Responsibilities:**
  - Guide farmers through PWA installation, offline mode, and camera autofocus.
  - Assist semi-literate participants in submitting observations and voice notes.
  - Perform weekly check-ins with every farmer in their cluster (in-person or phone).
  - Verify that offline sync occurs when farmers visit cellular connectivity zones.
  - Maintain the physical logbook of device issues and feedback.

### 1.3 KVK Extension Scientist / Plant Pathologist ($N = 2$ Pathologists, $N = 2$ Agronomists)
- **Primary Function:** Scientific authority, ground-truth assessor, and safety gatekeeper.
- **Key Responsibilities:**
  - Perform weekly field visits to 20% random cohort plots for independent physical diagnosis.
  - Access the ACREVIA Expert Portal (`/expert/reviews`) daily to audit pending diagnoses.
  - Verify AI-generated pathology predictions against PJTSAU Package of Practices.
  - Approve or modify recommended management interventions.
  - Immediately intervene if a quarantine pest or dangerous off-label chemical use is flagged.

### 1.4 ACREVIA Field Operations Lead ($N = 1$)
- **Primary Function:** End-to-end pilot management and field coordination.
- **Key Responsibilities:**
  - Oversee onboarding, logistics, KVK coordination, and field assistant supervision.
  - Track cohort engagement, observation frequency, and drop-off risks.
  - Enforce ethics protocols and handle participant withdrawal requests.

### 1.5 ACREVIA Platform & ML Reliability Engineers ($N = 2$)
- **Primary Function:** Technical platform maintenance, data integrity, and API observability.
- **Key Responsibilities:**
  - Monitor backend uptime, Neon PostgreSQL connections, Redis rate limiter metrics, and Vercel edge latency.
  - Inspect PWA offline sync telemetry and investigate sync failure alerts.
  - Monitor ML inference latency, Int8 ONNX runtime performance, and OOD rejection distributions.
  - Maintain daily encrypted backups of trial data.

### 1.6 Data Protection Officer (DPO) & Compliance Lead ($N = 1$)
- **Primary Function:** DPDP Act 2023 compliance and privacy assurance.
- **Key Responsibilities:**
  - Oversee secure storage of signed consent forms and consent revocation workflows.
  - Audit database access logs to ensure multi-tenant boundary compliance.
  - Enforce coordinate dithering and phone number pseudonymization.

---

## 2. RACI Governance Matrix

**Legend:**
- **R (Responsible):** The role that performs the activity.
- **A (Accountable):** The individual with final approval and veto authority.
- **C (Consulted):** Role offering two-way input and specialist advice.
- **I (Informed):** Role kept updated on progress or outcomes.

| Pilot Lifecycle Activity | Farmer | Field Assistant | KVK Scientist | Field Ops Lead | Platform/ML Eng | Data Protection Officer |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Cohort Recruitment & Screening** | I | R | C | A | I | C |
| **Informed Consent Collection** | R | R | I | A | I | C |
| **PWA App Installation & Onboarding** | R | R | I | A | C | I |
| **Routine Field Scouting & Photo Upload**| R | C | I | I | I | I |
| **Offline Record Synchronization** | R | R | I | I | A | I |
| **Automated AI Diagnosis Generation** | I | I | I | I | R / A | I |
| **Weekly Ground-Truth Pathology Audit** | I | C | R / A | C | I | I |
| **High-Risk Case Escalation & Approval** | I | I | R / A | C | I | I |
| **Adverse Agricultural Event Intervention**| I | C | R / A | A | I | I |
| **PWA / Server Technical Troubleshooting**| I | C | I | I | R / A | I |
| **Data Privacy & Consent Revocation** | C | I | I | I | C | R / A |
| **Exit Survey & SUS Scoring** | R | R | C | A | I | I |
| **Final Evaluation Report & Publication** | I | I | R / A | A | R / A | C |

---

## 3. Communication Channels & SLAs

| Channel | Purpose | Participants | Operating Hours | Response SLA |
| :--- | :--- | :--- | :--- | :--- |
| **Rythu Help Line (Phone/WhatsApp)** | Farmer technical issues & bug reports | Farmers $\leftrightarrow$ Field Assistant | 07:00 – 19:00 IST | $< 30$ minutes |
| **KVK Expert Review Queue** | Asynchronous diagnosis validation | Scientists $\leftrightarrow$ System | 08:00 – 18:00 IST | $< 4$ hours for high-risk; $< 24$ hours routine |
| **Ops Emergency WhatsApp Group** | Platform outages, high-risk pest alarms | KVK Leads + Ops Lead + Engineers | 24 / 7 Monitoring | $< 15$ minutes |
| **Weekly Standup (Video / In-Person)** | Cohort progress, metrics, and case reviews | Ops Lead + KVK Scientists + Engineers | Every Friday 16:00 IST | Scheduled weekly |
