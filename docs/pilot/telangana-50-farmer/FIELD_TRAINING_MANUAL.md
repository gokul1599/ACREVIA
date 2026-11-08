# ACREVIA Field Training Manual
## Visual & Step-by-Step Practical Field Training Guide
**Target Stage:** Stage 08 Remediation (`TASK-S08-01`)  
**Audience:** Village Field Assistants, KVK Extension Workers, Farmer Cohorts  
**Language Focus:** English / Telugu bilingual operational instructions  

---

## Module 1: PWA Installation & Home Screen Setup

```
[Open Chrome] ──> [Type: https://acrevia.app] ──> [Tap 3 Dots Menu] ──> [Add to Home screen]
```

### Steps:
1. Open Google Chrome on your Android smartphone.
2. Enter the URL: `https://acrevia.app` (or scan the village orientation QR code).
3. When prompted by the bottom banner: *"Add ACREVIA to Home Screen"* tap **Install**.
   *(If banner does not appear: tap the 3 vertical dots at top right $\to$ select "Add to Home screen" / "Install app")*.
4. Return to your phone's home screen. Confirm the green **ACREVIA leaf icon** is present.
5. Tap the icon to launch the app. It opens in standalone fullscreen mode without browser URL bars.

---

## Module 2: The 5-Point Leaf Photography Rule

Bad photographs cause AI misclassification. Train farmers on these 5 golden rules:

```
  CORRECT (Passes AI Quality Gate)                INCORRECT (Rejected by Model)
+------------------------------------+        +------------------------------------+
|  [Leaf fills 70% of frame]         |        |  [Tiny leaf far away in distance]  |
|  [Clear lesion boundary visible]   |        |  [Blurry, out of focus camera]     |
|  [Diffused morning sunlight]       |        |  [Harsh flash / pitch dark shadows]|
|  [Steady hand / supported leaf]    |        |  [Fingers or feet covering center] |
+------------------------------------+        +------------------------------------+
```

1. **Distance (15–25 cm):** Hold the camera 1 hand-span away from the leaf. The leaf must fill at least two-thirds of the screen.
2. **Focus & Sharpness:** Tap the smartphone screen directly on the diseased spot to force lens autofocus. Wait for the green square before snapping.
3. **Lighting (No Harsh Glare):** Avoid noon-day blazing sun. Shade the leaf with your body if necessary to create even, diffused lighting.
4. **Single Symptom Focus:** Photograph the worst affected leaf first. If both upper and lower leaf surfaces show symptoms (e.g. Powdery Mildew or Aphids), take 2 separate photos.
5. **Clean Contrast:** Avoid framing complex soil clods, weed patches, or tractor tires in the background.

---

## Module 3: Offline Mode & Background Synchronization

ACREVIA is built to work in remote fields with zero cell coverage.

### How Offline Mode Operates:
1. When you enter a zero-signal plot, the top status badge turns from green (`ఆన్‌లైన్ - Online`) to orange (`ఆఫ్‌లైన్ - Offline`).
2. You can still record observations, capture photos, and save journal entries normally.
3. Every offline observation is saved safely inside your phone's storage (`IndexedDB`). It will **never** be lost even if your battery dies.
4. The **Sync Queue** tab displays pending items:
   - `QUEUED (వేచి ఉంది)`: Record stored locally, waiting for network connection.
   - `SYNCING (సింక్ అవుతోంది)`: Currently uploading data and photo blobs.
   - `SYNCED (సింక్ పూర్తయింది)`: Successfully uploaded to server; agronomist can now view it.
   - `RETRY_PENDING`: Upload interrupted by poor network; system will automatically retry with exponential backoff.
5. **Manual Sync:** When you return home or reach a high-signal area, open ACREVIA and tap the blue **"Sync Now (ఇప్పుడే సింక్ చేయండి)"** button.

---

## Module 4: Understanding the AI Diagnosis & Uncertainty

```
+-------------------------------------------------------------+
| AI Diagnosis: Cotton Bacterial Blight                       |
| తెలుగు: పత్తి బ్యాక్టీరియల్ ఆకుమచ్చ తెగులు                 |
| Confidence: 87% [HIGH CONFIDENCE - అధిక ఖచ్చితత్వం]       |
+-------------------------------------------------------------+
| Management Guidance (PJTSAU PoP):                           |
| 1. Spray Copper Oxychloride (30g) + Streptocycline (1g)     |
|    in 10 litres of water.                                   |
| 2. Avoid excess nitrogenous fertilizer application.         |
+-------------------------------------------------------------+
```

### Explaining Confidence Bands to Farmers:
- **Green (> 80% Confidence):** High confidence. Common textbook symptoms detected. Standard PJTSAU management can be reviewed.
- **Yellow (50% – 80% Confidence):** Moderate confidence. Symptoms share visual similarities with other deficiencies or pests. Consult Village Field Assistant.
- **Red / Grey (< 50% or Out-of-Distribution):** Low confidence or unidentifiable image. The app will state:
  *"లక్షణాన్ని స్పష్టంగా గుర్తించలేకపోయాము. KVK శాస్త్రవేత్త సమీక్ష కోసం పంపబడింది."*  
  *(Cannot identify clearly. Escalated to KVK scientist for physical review.)*

---

## Module 5: KrishiBrain Voice & Vernacular Q&A

1. Tap the green **KrishiBrain (కృషి బ్రెయిన్)** tab on the bottom navigation bar.
2. Tap the **Microphone (మైక్రోఫోన్)** icon.
3. Speak clearly in Telugu:
   - *"నా పత్తి చేనులో ఆకులు ఎర్రబడుతున్నాయి, నివారణ ఏమిటి?"*  
     *(My cotton leaves are turning red, what is the remedy?)*
   - *"వరిలో అగ్గి తెగులు లక్షణాలు ఏమిటి?"*  
     *(What are the symptoms of blast disease in rice?)*
4. Listen to the spoken audio response or read the step-by-step guidance.
5. Every advice card shows the official PJTSAU citation and a green tick indicating scientific validation.

---

## Module 6: Technical Support & Helpdesk

If the app freezes, shows an error, or a farmer has any agronomic questions:
- **Contact Village Field Assistant:** Available in village from 08:00 to 18:00.
- **WhatsApp Support:** Send screenshot to `+91 94400 12345`.
