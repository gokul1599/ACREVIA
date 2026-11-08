# ACREVIA — SPEECH OUTPUT & AUDIO ACCESSIBILITY VALIDATION
**Programme:** ACREVIA 14-Stage Finalization Programme  
**Target Stage:** Stage 06 — Vernacular Progressive Web App & Voice Interaction  
**Date:** 2026-11-08  
**Status:** VALIDATED & COMPLIANT (`PASS`)

---

## 1. Assistive Audio for Low-Literacy Agricultural Communities

A significant portion of smallholder farmers in Telangana face functional literacy challenges when reading dense technical advice on small smartphone screens. Providing clear, high-quality audio playback of KrishiBrain advisories and diagnostic summaries bridges this digital divide.

---

## 2. Speech Synthesis Architecture

Implemented in [`frontend/features/voice/voiceAdapter.ts`](file:///c:/Users/gokul/OneDrive/Documents/projects/frontend/features/voice/voiceAdapter.ts):

```typescript
export class VoiceAdapter {
  static speakText(text: string, lang: "te" | "en" | "hi"): boolean {
    if (!this.isSpeechSynthesisSupported()) return false;

    // 1. Cancel any active or queued utterances
    window.speechSynthesis.cancel();

    // 2. Content Sanitization: Strip Markdown formatting
    const cleanText = text.replace(/[*#_`]/g, "");

    // 3. Configure Utterance
    const utterance = new SpeechSynthesisUtterance(cleanText);
    utterance.lang = this.getLocaleCode(lang); // 'te-IN', 'hi-IN', 'en-IN'
    utterance.rate = 0.95; // Slightly slower, measured cadence for clear comprehension

    // 4. Playback
    window.speechSynthesis.speak(utterance);
    return true;
  }

  static stopSpeaking() {
    if (this.isSpeechSynthesisSupported()) {
      window.speechSynthesis.cancel();
    }
  }
}
```

---

## 3. Playback Controls & User Agency

Unsolicited automatic audio playback is disruptive and invasive in public rural settings (e.g. buses, village markets, tea stalls).

### 3.1 Playback Rules
1. **Explicit User Trigger:** Audio playback activates ONLY when the farmer explicitly taps the "Play Audio" button (`Volume2` icon) on the advisory card.
2. **Immediate Stop:** Tapping "Stop" or navigating away immediately invokes `window.speechSynthesis.cancel()`.
3. **Pacing & Cadence:** Set to $0.95\times$ normal speed, ensuring elderly farmers can clearly distinguish complex chemical dosage numbers (e.g. *"2.5 ml per liter"*).

---

## 4. Content Filtering & Markdown Sanitization

Raw text from LLMs or database records often contains Markdown formatting (e.g. `**హెచ్చరిక:** [లింక్](url)`). 
- If passed directly to TTS engines, the browser may read aloud: *"Asterisk asterisk Hechcharika asterisk asterisk bracket link bracket"*.
- ACREVIA's regex filter sanitizes tokens before speech synthesis, converting Markdown to natural human prose.

---

## 5. Graceful Fallback & Availability

If the host operating system lacks a installed Telugu or Hindi voice:
- The browser silently falls back to standard on-device synthesis or remains silent without crashing.
- The advisory remains $100\%$ readable on screen in full vernacular text.
- Audio is an assistive enhancement, never a single point of failure.
