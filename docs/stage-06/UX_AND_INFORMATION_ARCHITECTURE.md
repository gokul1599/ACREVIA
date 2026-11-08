# ACREVIA — UX & Information Architecture Specification
**Stage 06: Farmer Experience & Mobile-First Progressive Web App**  
*Document Version:* 1.0.0  
*Target Users:* Smallholder farmers, Agricultural field officers, KVK agronomists  
*Target Geography:* Telangana, India (Warangal, Karimnagar, Khammam, Nalgonda, Adilabad)  
*Languages:* Telugu (`te`), English (`en`), Hindi (`hi`)

---

## 1. User Personas & Real-World Constraints

### Persona 1: Mallesh (Cotton Farmer, Warangal District)
- **Profile:** Cultivates 3 acres of rainfed Bt cotton on black cotton soil (*nalla regadi nelalu*). Uses a mid-tier Android phone (Redmi Note series) with 4G cellular data that fluctuates between 1 and 3 bars.
- **Language:** Primary Telugu (*తెలుగు*). Limited English literacy. Prefers audio feedback and voice input.
- **Key Pain Point:** Pink bollworm attack causing rosette flowers; unsure whether to spray or install pheromone traps. Needs immediate, trusted advice without technical jargon.

### Persona 2: Lakshmi (Rice Farmer, Karimnagar District)
- **Profile:** Cultivates 2.5 acres of wetland paddy (*vari pantalu*). Uses smartphone primarily for WhatsApp and voice messages.
- **Language:** Telugu and basic Hindi.
- **Key Pain Point:** Brown spots appearing on paddy leaves during tillering stage; needs to know if it's Rice Blast or Brown Spot, and whether the image quality is clear enough for diagnosis.

### Persona 3: Anji Reddy (Chilli Farmer, Khammam District)
- **Profile:** Cultivates 4 acres of commercial chilli (*mirapa*). Highly conscious of pesticide costs and chemical residue issues for exports.
- **Language:** Telugu and English.
- **Key Pain Point:** Invasive Black Thrips (*Thrips parvispinus*) curling leaves upwards; wants verifiable advice with CIBRC dosage recommendations and human agronomist verification.

---

## 2. Core UX Principles for Rural Smallholders

1. **Restrained Visual Anchor:** Deep forest agricultural green (`#1E3A2B`) paired with fertile soil neutrals (`#F7F5F0`) and high-contrast charcoal text (`#1A241F`). No neon gradients or distracting decorative glassmorphism.
2. **Touch-First Ergonomics:** All primary interaction buttons, tabs, and cards have minimum touch targets of **48px $\times$ 48px** with generous thumb zones along the bottom of the viewport.
3. **Calm, Non-Alarmist Semantics:** Uncertainty is presented as an invitation for more information or expert review, not as a catastrophic error.
4. **Honest AI Labeling:** Predictions are explicitly labeled as *"AI Assessment (Not Verified by Agronomist)"*. Confirmed diagnoses are reserved exclusively for human expert overrides.
5. **Offline Transparency:** A persistent offline indicator displays connection state, queued drafts, and pending uploads without blocking local browsing.

---

## 3. Information Architecture & Route Tree

```
/(auth)
├── /login                    [Phone / Email + Password Login]
├── /register                 [Name, Phone, Language, Password]
└── /onboarding               [4-Step Guided Setup: Lang, Profile, Farm, First Crop]

/(farmer)
├── /dashboard                [Context Header, Quick Actions, Active Crops, Recent Alerts, Weather]
├── /farms                    [Farm Holdings List, Add Farm, Farm Details]
│   └── /[id]                 [Plots, Soil Types, Irrigation, Weather, Memberships]
├── /crops                    [Active Crop Seasons, Phenological Stage Tracker, Timeline]
│   └── /[seasonId]           [Detailed Crop Cycle, Observations History, Stage Events]
├── /diagnosis                [Mobile Camera Capture, Foliar Upload, CropVision Assessment]
│   └── /[id]                 [Prediction Result, Differential Candidates, Citations, Expert Escalation]
├── /knowledge                [KrishiBrain Chat Assistant, Citations Drawer, Audio Readout, Feedback]
├── /croppulse                [Plant Health Chronology, Visual Comparison, Longitudinal Notes]
├── /profile                  [Farmer Profile, Language Switcher, Offline Sync Queue, Settings]
```

---

## 4. Primary Farmer User Journeys

### Journey 1: Foliar Scan & Diagnosis Workflow
```
[Tap 'Scan Crop' Button]
         │
         ▼
[Select Crop: Cotton / Rice / Chilli]
         │
         ▼
[Camera Capture or Photo Picker]
         │
         ▼
[Instant Client-Side Preview & Framing Guidance]
         │
         ▼
[Upload to /api/v1/observations/ + Quality Gate]
         │
         ├── Quality Usable ──► [Submit to /api/v1/diagnoses/]
         │                              │
         │                              ▼
         │                      [CropVision Result Screen]
         │                      - Top Predicted Condition
         │                      - Confidence & Entropy Gauge
         │                      - Differential Candidates
         │                      - CIBRC Advisory
         │                      - "Ask KrishiBrain" or "Request Expert"
         │
         └── Quality Low ────► [Friendly Alert: "Photo too blurry/dark. Retake?"]
```

### Journey 2: Multilingual KrishiBrain Advisory Workflow
```
[Open KrishiBrain Tab]
         │
         ▼
[Choose Input: Type or Tap Microphone for Voice]
         │
         ▼
[Speak Query in Telugu / Hindi / English]
         │
         ▼
[Preview & Confirm Transcribed Query]
         │
         ▼
[Fetch /api/v1/knowledge/query with Crop Context]
         │
         ▼
[Display Verified Response]
         ├── Listen via Audio Player (TTS)
         ├── Expand Citations (Page No., Publisher, Excerpt)
         ├── Follow-up Questions Suggestions
         └── Submit Helpful / Unhelpful Feedback
```

---

## 5. Multilingual Localization Architecture

The application implements a zero-dependency, ultra-fast client localization store:
- Translations organized in dictionary modules: `messages/en.ts`, `messages/te.ts`, `messages/hi.ts`.
- Persistent language state stored in `localStorage` and synchronized with user profile in backend.
- Full RTL/LTR and vernacular word-wrapping safety with system fonts optimized for Telugu (`Gautami`, `Nirmala UI`, `sans-serif`) and Devanagari Hindi (`Mangal`, `Nirmala UI`, `sans-serif`).
