# ACREVIA — FARM ACTION JOURNAL USER EXPERIENCE & INTERACTION DESIGN
**Programme:** ACREVIA 14-Stage Finalization Programme  
**Target Stage:** Stage 05 — Farm Action Journal, Observations, Geolocation & Weather  
**Date:** 2026-11-08  
**Status:** VERIFIED & VALIDATED (`PASS`)

---

## 1. Interaction Design Objective

Smallholder farmers in Telangana need an intuitive, longitudinal record of what occurred in their fields across the season: when lesions first appeared, what weather preceded them, what intervention was applied (e.g. neem oil spray, drainage clearing, bio-control), and whether the crop recovered.

The **Farm Action Journal** (`frontend/app/(farmer)/croppulse/page.tsx` and `dashboard/page.tsx`) provides this chronological intelligence stream.

---

## 2. Information Architecture & Timeline Layout

```
+-----------------------------------------------------------------------+
|  ACREVIA CROP PULSE — FARM ACTION JOURNAL                             |
|  [Select Farm: Warangal Cotton Farm v]         [+ New Field Record]    |
+-----------------------------------------------------------------------+
|  [!] Capture Consistency Reminder:                                    |
|      To enable trustworthy visual progression tracking, photograph    |
|      the exact same tagged plant from ~30 cm distance.               |
+-----------------------------------------------------------------------+
|  TIMELINE FEED                                                        |
|                                                                       |
|  * 2026-11-08 09:30 AM  [Plot: North Parcel | Crop: Cotton (Kharif)]  |
|    "Routine scouting - mild reddish spots observed on lower canopy"   |
|    [Image: leaf_001.jpg (Quality: ACCEPTED | Sharpness: 142.5)]       |
|    Weather Context: 28.5°C | RH: 78% | Precip: 0.0mm (Open-Meteo)     |
|    Action Status: AI Diagnosis Completed -> Cercospora Leaf Spot      |
|                                                                       |
|  * 2026-11-04 04:15 PM  [Plot: North Parcel | Crop: Cotton (Kharif)]  |
|    "Pre-emptive application of 5% Neem Seed Kernel Extract (NSKE)"     |
|    Action Status: Farmer Intervention Recorded                        |
|                                                                       |
|  * 2026-10-28 11:00 AM  [Plot: South Parcel | Crop: Chilli]           |
|    "Healthy vegetative flush, flower buds emerging"                  |
|    [Image: chilli_004.jpg (Quality: ACCEPTED)]                        |
+-----------------------------------------------------------------------+
```

---

## 3. Multilingual Accessibility & Smallholder Usability

Implemented in [`frontend/lib/localization/translations.ts`](file:///c:/Users/gokul/OneDrive/Documents/projects/frontend/lib/localization/translations.ts):

### 3.1 Localization Keys

| Key | English (`en`) | Telugu (`te`) | Hindi (`hi`) |
|---|---|---|---|
| `croppulse.title` | Crop Pulse | పంట నాడి (క్రాప్ పల్స్) | क्रॉप पल्स |
| `croppulse.subtitle` | Field observations & timeline | క్షేత్ర పరిశీలనలు & కాలక్రమం | खेत के अवलोकन और समयरेखा |
| `croppulse.newRecord` | New Field Record | కొత్త నమోదు | नया रिकॉर्ड |
| `croppulse.notesPlaceholder` | Describe observations, leaf symptoms, or applied sprays... | ఆకులపై లక్షణాలు లేదా వేసిన మందుల వివరాలు నమోదు చేయండి... | पत्तियों के लक्षण या किए गए छिड़काव का विवरण लिखें... |

### 3.2 High-Contrast Outdoor Usability
1. **Touch Targets:** All buttons, file inputs, and modal dismissals enforce a minimum touch target size of $48\text{px} \times 48\text{px}$ (`touch-target` utility class) for one-handed operation in muddy field conditions.
2. **Contrast Ratio:** Typography utilizes high-contrast emerald green (`#1E3A2B`) on light sand canvas (`#FAFAF7`), achieving WCAG 2.1 AAA contrast ratios exceeding $8.5:1$.
3. **Camera Integration:** Direct HTML5 `capture="environment"` attribute prompts the native rear camera sensor, bypassing confusing gallery selection dialogs.
