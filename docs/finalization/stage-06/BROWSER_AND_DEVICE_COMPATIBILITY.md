# ACREVIA — BROWSER & DEVICE COMPATIBILITY MATRIX
**Programme:** ACREVIA 14-Stage Finalization Programme  
**Target Stage:** Stage 06 — Vernacular Progressive Web App & Voice Interaction  
**Date:** 2026-11-08  
**Status:** COMPATIBILITY TESTED & CERTIFIED (`PASS`)

---

## 1. Device Diversity in Telangana Smallholder Farming

Smallholder devices in Telangana span a wide variety of hardware: low-cost Xiaomi, Realme, Vivo, and Samsung handsets running Android 10 through 14, alongside desktop browsers used by Krishi Vigyan Kendra (KVK) extension officers.

ACREVIA was evaluated across 6 primary environments to establish empirical compatibility.

---

## 2. Empirical Compatibility Matrix

| Operating Environment | Primary Engine | PWA Installable | Offline Shell | IndexedDB Storage | Camera Capture | Speech Recognition | Speech Synthesis |
|---|---|---|---|---|---|---|---|
| **Android Chrome (v120+)** | Blink / Chromium | **YES** (Native Prompt) | **PASS** | **PASS** | **PASS** (Direct Env) | **PASS** (`te-IN`, `hi-IN`) | **PASS** |
| **Android Samsung Internet** | Blink / Tizen | **YES** (Install Icon) | **PASS** | **PASS** | **PASS** | **PASS** | **PASS** |
| **Android Firefox (v121+)** | Gecko | **YES** | **PASS** | **PASS** | **PASS** | **Text Fallback** | **PASS** |
| **iOS Safari (iOS 16.4+)** | WebKit | **YES** (Add to Home) | **PASS** | **PASS** | **PASS** | **Limited / Fallback** | **PASS** |
| **Windows Desktop Edge / Chrome** | Chromium | **YES** (Desktop PWA) | **PASS** | **PASS** | **PASS** (Webcam/File) | **PASS** | **PASS** |
| **Windows Desktop Firefox** | Gecko | **No (Tab Only)** | **PASS** | **PASS** | **PASS** (File Upload) | **Text Fallback** | **PASS** |

---

## 3. Graceful Feature Degradation Strategy

When an advanced capability is unsupported on a specific platform:

```
[Feature: PWA Installation]
   ├── Supported (Chrome/Edge): Render "Install App" button.
   └── Unsupported (Desktop Firefox): Suppress button; operate seamlessly as web app.

[Feature: Voice Input (Web Speech Recognition)]
   ├── Supported (Android Chrome): Display interactive microphone button.
   └── Unsupported (Firefox/Safari): Hide mic button; focus standard vernacular text input.

[Feature: Voice Output (Speech Synthesis)]
   ├── Supported (All modern browsers): Render "Play Audio" button.
   └── Unsupported / Voice Missing: Hide audio control; full text remains visible.
```

No platform experiences a broken interface, unhandled exception, or blocked agricultural workflow.
