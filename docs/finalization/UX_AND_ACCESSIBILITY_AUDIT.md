# ACREVIA — USER EXPERIENCE, MULTI-PERSONA & ACCESSIBILITY AUDIT
## Multi-Persona Evaluation, Vernacular Interaction, Anti-Glare Usability & WCAG Compliance

**Document Version:** 1.0.0  
**Status:** Approved UX & Usability Audit  
**Target User Population:** Rural Telangana Smallholder Farmers, University Agronomists, FPO Coordinators, Agricultural Researchers & Developers  
**Standards:** WCAG 2.1 Level AA, Mobile-First PWA Guidelines  

---

### 1. Multi-Persona Usability Audit

| User Persona | Core Target Workflow | UX Audit Finding | Verification & Safety Status |
|---|---|---|---|
| **First-Time Farmer** | Vernacular onboarding, phone OTP login, setting up first farm and plot. | Simple 3-step wizard with visual crop selector (Cotton, Rice, Chilli) in Telugu; zero jargon. | Verified. Default language is Telugu (`te`); clear input assistance. |
| **Returning Farmer** | Daily dashboard check, taking foliar photo, receiving diagnosis and spray weather warnings. | High-contrast status cards; big touch targets ($\ge 48 \times 48\text{ px}$); weather conflict alert clearly highlighted with amber warning banner. | Verified. Mobile responsive; offline queue indicators show sync state. |
| **Agricultural Expert** | Reviewing escalated diagnosis cases, inspecting multimodal dossiers (photos, Grad-CAM, weather). | Clean triage queue; side-by-side comparison of AI prediction vs farmer notes; revision history logging. | Verified. Restricted to `AGRICULTURAL_EXPERT` role via RBAC. |
| **Administrator** | Verifying expert credentials, monitoring platform metrics, managing partner institutions. | Dedicated administration panel; audit logs visible; role promotion controls. | Verified. Restricted strictly to `ADMIN` role. |
| **Agricultural Researcher** | Accessing anonymized research datasets, reviewing inter-annotator agreement metrics. | Dedicated research export builder with explicit purpose-specific consent filtering. | Verified. Enforces farm-disjoint splits and strips farmer PII. |
| **FPO / Collective Manager** | Viewing aggregate crop health across member farms; scheduling shared machinery/inputs. | Member management; aggregate metrics automatically suppressed if fewer than 5 farms contribute. | Verified. $N \ge 5$ privacy guardrail enforced in UI and backend. |
| **Developer / Agritech Partner** | Creating API keys, testing webhook endpoints, inspecting OpenAPI contracts. | Self-service developer console (`ak_live_...` / `ak_sand_...`); HMAC webhook secret generator; interactive Swagger documentation. | Verified. Clear scope selectors (`read:farm`, `write:soil`). |
| **External Integration Partner** | Ingesting soil lab test results or syncing mandi prices into ACREVIA. | Standardized data exchange forms with preview, validation errors, and conflict detection notices. | Verified. Non-overwriting import conflict warnings surfaced clearly. |

---

### 2. Physical & Environmental Usability in Rural Conditions

1. **Anti-Glare Sunlight Readability:**
   * High-contrast color palette (Tailwind CSS neutral-900 on pure white background, avoiding subtle low-contrast pastels).
   * Minimum contrast ratio $\ge 7.1:1$ for primary text (exceeding WCAG AAA).
2. **One-Thumb Operation:**
   * Primary action buttons (Scout Leaf, Ask KrishiBrain, View Alerts) anchored to bottom mobile action bar.
   * Large capacitive touch targets ($\ge 48 \times 48\text{ px}$) to accommodate outdoor usage with soil-stained hands or field gloves.
3. **Vernacular Voice & Audio Interaction:**
   * Integrated Web Speech API adapter (`frontend/src/lib/speech.ts`) enabling speech-to-text input and text-to-speech audio readback in Telugu (`te-IN`), Hindi (`hi-IN`), and Indian English (`en-IN`).
   * Graceful fallback to text input when the mobile browser lacks Web Speech API support.
4. **Offline Resilience & Sync Feedback:**
   * Persistent status banner when operating offline.
   * Visual badge counter on `OfflineQueue` showing unsynchronized field scouting notes.
   * Toast notification upon network reconnection confirming successful synchronization.

---

### 3. Action Integrity Audit (Zero Dead Buttons Policy)

* **Audit Finding:** Every clickable button, link, or tab across all 13 Next.js static pages maps to a live API endpoint, modal dialogue, or router transition.
* **Placeholder Elimination:** No decorative or unfunctional controls exist. Actions requiring external configuration (e.g., live mandi API key) display explicit state banners (`CONFIGURED_SANDBOX`) explaining the operational status.
