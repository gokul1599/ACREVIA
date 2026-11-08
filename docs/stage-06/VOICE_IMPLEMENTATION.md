# ACREVIA Voice Input & Audio Response Architecture
**Stage 06: Farmer Experience & Mobile-First Progressive Web App**  
*Document Version:* 1.0.0  
*Component Scope:* Speech-to-Text (STT) & Text-to-Speech (TTS)  
*Languages Supported:* Telugu (`te-IN`), Hindi (`hi-IN`), English (`en-IN`)

---

## 1. Architectural Strategy

In rural smallholder communities, many farmers have limited comfort with touchscreen typing or English-centric virtual keyboards. Voice interaction enables farmers to speak their crop questions naturally in Telugu or Hindi and listen to spoken agricultural advisories.

The voice layer is built as a **provider-independent adapter** (`frontend/features/voice/voiceAdapter.ts`):
- Leverages the native **Web Speech API** for zero-latency, device-optimized speech recognition and synthesis.
- Requires zero paid external speech API tokens or cloud round-trips for standard mobile browsers.
- Enforces explicit microphone consent and never records continuously in the background.
- Gracefully degrades to standard text chat when voice services are unavailable or permissions are denied.

---

## 2. Speech-to-Text (Voice Input) Workflow

```
[Farmer Taps Microphone Button]
               │
               ▼
   [Microphone Permission Check]
   ├── Granted ──► [Initialize Web Speech Recognizer with Locale (te-IN / hi-IN)]
   │                     │
   │                     ▼
   │               [Live Listening Animation (Red Pulse)]
   │                     │
   │                     ▼
   │               [Transcribed Text Returned to Input Box]
   │                     │
   │                     ▼
   │               [Farmer Reviews & Confirms Query]
   │
   └── Denied / Unsupported ──► [Friendly Toast Alert: "Voice unsupported; please type query"]
```

### 2.1 Language Locale Mapping
- **Telugu:** Configured as `te-IN`. Recognizes vernacular Telugu crop and pest names on Android devices equipped with Google Speech Services.
- **Hindi:** Configured as `hi-IN`.
- **English:** Configured as `en-IN` (Indian English phonetics).

---

## 3. Text-to-Speech (Audio Output) Workflow

When an advisory is returned by KrishiBrain, farmers can tap **"Listen to Advisory"**:
1. Advisory text is cleaned of Markdown tokens (`*`, `#`, `_`, `` ` ``).
2. `SpeechSynthesisUtterance` is initialized with active locale (`te-IN`, `hi-IN`, or `en-IN`).
3. Speech rate is set to **`0.95`** to ensure a deliberate, clear cadence suited for complex technical and chemical instructions.
4. Active utterance can be paused or stopped at any time via the "Stop Speaking" button.

---

## 4. Privacy & Consent Rules

1. **User-Initiated Only:** Microphone hardware is engaged exclusively upon a direct, voluntary tap on the microphone icon.
2. **Zero Ambient Listening:** Recording stops immediately once a single sentence or query pause is detected (`continuous: false`).
3. **No Raw Audio Retention:** No audio waveform bytes are recorded, stored, or transmitted to third-party marketing trackers.
