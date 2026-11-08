# ACREVIA Multilingual Localization & Agricultural Terminology Guide
**Stage 06: Farmer Experience & Mobile-First Progressive Web App**  
*Document Version:* 1.0.0  
*Supported Languages:* Telugu (`te`), English (`en`), Hindi (`hi`)  
*Target Geography:* Telangana, India

---

## 1. Localization Architecture

ACREVIA implements a zero-overhead, ultra-fast client localization store:
- Translations are modularized into typed dictionaries: `messages/en.ts`, `messages/te.ts`, `messages/hi.ts`.
- The `LocalizationProvider` (`frontend/lib/localization/context.tsx`) manages active locale, exposes the typed translation tree `t`, and synchronizes preferences with `localStorage` and `document.documentElement.lang`.
- Switching languages executes instantaneously without triggering page reloads or network requests.

---

## 2. Telangana Agricultural Terminology Glossary

Literal translation tools frequently corrupt agricultural advice (e.g., translating "plant tillering" to unrelated words). ACREVIA establishes an authoritative agronomic translation glossary:

| English Term | Telugu Field Term (*తెలంగాణ వాడుక భాష*) | Hindi Field Term (*हिंदी*) | Agronomic Context |
| :--- | :--- | :--- | :--- |
| **Pink Bollworm** | గులాబీ రంగు పురుగు (*Gulabi rangu purugu*) | गुलाबी सुंडी (*Gulabi sundi*) | Major destructive pest of cotton (*Pectinophora gossypiella*) |
| **Rosette Flower** | ముడుచుకున్న పూత / రోసెట్ పువ్వు | मुड़ा हुआ फूल | Early diagnostic indicator of pink bollworm infestation |
| **Brown Planthopper** | సుడి దోమ (*Sudi doma*) | भूरा फुदका (*Bhoora phudka*) | Severe sap-sucking pest of paddy causing hopper burn |
| **Rice Blast** | అగ్గి తెగులు (*Aggi tegulu*) | झुलसा रोग (*Jhulsā rog*) | Fungal foliar and neck blast pathogen (*Magnaporthe oryzae*) |
| **Black Thrips** | నల్ల తామర పురుగులు (*Nalla thamara purugulu*) | काले थ्रिप्स (*Kaale thrips*) | Invasive sucking pest curling chilli leaves upwards (*Thrips parvispinus*) |
| **Anthracnose / Dieback** | కొమ్మ ఎండు / కాయ కుళ్లు తెగులు | उकठा / फल सड़न रोग | Major fungal disease causing twig dieback in chilli |
| **Black Cotton Soil** | నల్లరేగడి నేలలు (*Nalla regadi nelalu*) | काली कपास मिट्टी | Heavy vertisol soils prevalent in Warangal and Adilabad |
| **Red Chalka Soil** | ఎర్ర నేలలు / చల్క నేలలు | लाल मिट्टी | Sandy loam alfisols common in Karimnagar and Nalgonda |
| **Pheromone Trap** | లింగాకర్షక బుట్టలు (*Lingakarshaka buttalu*) | फेरोमोन ट्रैप | Non-chemical pest monitoring and mass trapping tool |
| **Pre-Harvest Interval (PHI)** | కోతకు ముందు వేచి ఉండే కాలం | कटाई पूर्व प्रतीक्षा अवधि | Mandatory safety waiting period between pesticide spray and harvest |

---

## 3. Typographical Rendering & Wrapping Safety

Telugu and Hindi scripts use complex conjuncts and vowel marks (matras):
- Words are wrapped using `overflow-wrap: break-word` and `hyphens: auto`.
- Line heights on vernacular advisories are expanded to `1.6` to prevent vertical collision of upper and lower diacritical accents.
- Responsive button labels support multi-line truncation without breaking layout grids.

---

## 4. Verification & Testing Evidence

Automated parity tests in `frontend/tests/localization.test.js` verify that 100% of namespace keys across `app`, `nav`, `auth`, `onboarding`, `dashboard`, `diagnosis`, `knowledge`, `croppulse`, and `common` match across English, Telugu, and Hindi.
