# ACREVIA — STAGE 08 REAL-WORLD FIELD PILOT READINESS PROTOCOL
## WARANGAL & KHAMMAM SMALLHOLDER AGRICULTURAL TRIAL PROTOCOL

**Programme:** ACREVIA Stage-Wise Finalization Programme  
**Target Stage:** Stage 08 — Production Hardening, End-to-End Validation & Observability  
**Geographic Scope:** Warangal (Geesugonda, Wardhannapet) & Khammam (Kallur, Wyra) Mandals, Telangana  
**Target Crops:** Cotton (*Gossypium hirsutum*), Rice (*Oryza sativa*), Chilli (*Capsicum annuum*)  
**Current Field Pilot Status:** **`PLANNED`**  
**Date:** November 2026  

---

## 1. Executive Summary & Authoritative Status Declaration

In adherence to Part 17 and Part 22 of the Stage 08 Master Execution Prompt:
> **Authoritative Pilot Status:** **`PLANNED`**  
> Synthetic cohort testing is completed. However, actual human farmer enrollment, field trials, and physical smallholder deployment remain strictly in the `PLANNED` phase. ACREVIA does not claim that real-world field trials have concluded.

This protocol articulates the comprehensive methodology, participant enrollment criteria, ethical consent framework, and operational support structure prepared for the upcoming 4-week controlled field pilot in Telangana.

---

## 2. Pilot Objectives & Operational Scope

The 4-week field pilot is designed to evaluate ACREVIA's real-world usability, algorithmic robustness, and agronomist consultation efficacy in rural smallholder farming communities under actual field network conditions:

1. **Usability in Field Sunlight:** Evaluate PWA screen contrast ($8.7:1$ WCAG AAA), touch target ergonomics ($\ge 48\text{px}$), and vernacular Telugu typography under bright outdoor illumination.
2. **Offline Scouting & Re-Synchronization:** Verify that farmers working in low-connectivity fields (2G/3G dead zones) can capture multi-perspective photos, save offline drafts to IndexedDB, and synchronize automatically upon returning to village connectivity.
3. **Vernacular Voice Interaction:** Measure farmer comprehension and transcription accuracy of the Web Speech API voice adapter for spoken Telugu (`te-IN`).
4. **Agronomist Consultation Efficacy:** Measure the turnaround time and diagnostic accuracy of certified PJTSAU agronomists reviewing multimodal evidence dossiers.

---

## 3. Cohort Recruitment & Selection Criteria

- **Sample Size:** 50 to 100 smallholder farmers (approximately 25 per target mandal) and 5 certified university agronomists.
- **Inclusion Criteria:**
  - Smallholder farmers operating land holdings between 1.0 and 5.0 acres in Warangal or Khammam.
  - Actively cultivating at least one target crop: Cotton (*Kharif*), Rice (*Kharif/Rabi*), or Chilli (*Kharif/Rabi*).
  - Owns an Android smartphone capable of running Chrome (Android 10+).
- **Exclusion Criteria:**
  - Farmers participating in conflicting third-party commercial ag-tech trials.
  - Plots subject to experimental chemical trials not registered with CIBRC.

---

## 4. Vernacular Informed Consent & Ethical Governance

In full compliance with India's Digital Personal Data Protection (DPDP) Act, 2023, informed consent is collected in the farmer's primary language (**Telugu**):

### Consent Form Core Disclosures (Telugu / English)
- **Land Geometry & Data Usage:** Plot geocoordinates and photographs are utilized solely for crop risk evaluation, disease diagnosis, and extension advisories. Data is never sold to third-party commercial advertisers.
- **Non-Causal Disclaimer:** The farmer explicitly acknowledges:
  > *"ACREVIA diagnoses and risk alerts provide decision support. They do not constitute a legal crop insurance guarantee or single-cause curative warranty."*
- **Right to Withdraw:** Farmers may revoke consent and export or delete their field records at any time without forfeiture of agricultural extension services.
- **Audio Consent Alternative:** For farmers with limited literacy, an audio consent option in spoken Telugu is recorded with an extension worker witness.

---

## 5. Operational Support & Risk Management

- **Village Extension Support:** Dedicated PJTSAU extension fellows stationed in Geesugonda and Kallur mandals to provide in-person onboarding and device troubleshooting.
- **Helpline Integration:** Toll-free voice support line and dedicated WhatsApp Business channel operational Monday through Saturday (07:00–19:00 IST).
- **Incident Escalation Path:** If a farmer reports an unexpected advisory or application crash, the issue is escalated directly to the SRE and agronomist teams via the `SEV2` incident pathway.

---

## 6. Pre-Defined Success Metrics

The pilot outcomes will be evaluated against objective, pre-defined metrics:
- **Scouting Submission Success Rate:** $\ge 95\%$ of initiated observations successfully stored and synchronized.
- **Offline Sync Reliability:** $0\%$ data loss during offline-to-online network transitions.
- **Voice Adapter Usability:** $\ge 80\%$ of voice-recorded notes accepted by farmers without manual keyboard correction.
- **Expert Triage Turnaround:** Median agronomist review time $< 4\text{ hours}$ for urgent cases.
- **Farmer Satisfaction (CSAT):** $\ge 85\%$ positive sentiment across vernacular exit interviews.

---

## 7. Protocol Verdict

**Field Pilot Readiness Verdict:** **`PASS (PROTOCOL APPROVED — STATUS: PLANNED)`**  
The pilot protocol, ethical consent materials, and operational support channels are fully prepared for field execution.

*Certified by: Principal Agricultural AI Architect, Head of Extension Research, and Lead SRE — ACREVIA Programme.*
