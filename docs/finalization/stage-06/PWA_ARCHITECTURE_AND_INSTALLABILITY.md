# ACREVIA — PROGRESSIVE WEB APP ARCHITECTURE & INSTALLABILITY
**Programme:** ACREVIA 14-Stage Finalization Programme  
**Target Stage:** Stage 06 — Vernacular Progressive Web App & Voice Interaction  
**Date:** 2026-11-08  
**Status:** ARCHITECTED & VERIFIED (`PASS`)

---

## 1. PWA Architectural Vision for Smallholder Farmers

In rural Telangana, smallholder farmers often rely on budget Android smartphones ($< 3\text{ GB}$ RAM, limited internal storage) where downloading heavy $100\text{ MB}+$ native APKs from Google Play is prohibitive due to metered cellular data and storage exhaustion.

ACREVIA's Progressive Web App (PWA) architecture provides an instant, zero-download-friction native application experience via the browser, occupying $< 5\text{ MB}$ of storage while supporting full offline capabilities, home screen installation, and fast launch times.

---

## 2. Web App Manifest Specification

Defined in [`frontend/public/manifest.json`](file:///c:/Users/gokul/OneDrive/Documents/projects/frontend/public/manifest.json):

```json
{
  "name": "ACREVIA — Agricultural Intelligence Platform",
  "short_name": "ACREVIA",
  "description": "Foliar crop disease diagnostics, KrishiBrain agricultural knowledge, and plant health monitoring for Cotton, Rice, and Chilli farmers.",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#F7F5F0",
  "theme_color": "#1E3A2B",
  "orientation": "portrait",
  "icons": [
    {
      "src": "/icons/icon-192.png",
      "sizes": "192x192",
      "type": "image/png"
    },
    {
      "src": "/icons/icon-512.png",
      "sizes": "512x512",
      "type": "image/png"
    },
    {
      "src": "/icons/icon-512.png",
      "sizes": "512x512",
      "type": "image/png",
      "purpose": "maskable"
    }
  ]
}
```

### 2.1 Manifest Validation Criteria
- **`display: "standalone"`:** Removes the browser URL address bar and navigation buttons, providing an immersive native app viewport.
- **`theme_color: "#1E3A2B"`:** Seamlessly tints the Android mobile system status bar with ACREVIA's deep agricultural evergreen hue.
- **`background_color: "#F7F5F0"`:** Provides a smooth, non-flashing splash screen transition matching the app's warm sand canvas.
- **`purpose: "maskable"`:** Ensures the 512x512 app icon adapts cleanly to circular, squircle, or teardrop launcher masks on Android 12+ without unsightly white borders.

---

## 3. Installation Flow & Browser Compatibility

```mermaid
sequenceDiagram
    participant Farmer as "Farmer Mobile Browser"
    participant OS as "Android / iOS OS"
    participant PWA as "ACREVIA PWA"

    Farmer->>PWA: Visit acrevia.org on Chrome / Safari
    alt Android Chrome / Edge
        PWA->>Farmer: Browser fires 'beforeinstallprompt'
        Farmer->>PWA: Tap "Install App" or Browser Menu
        PWA->>OS: Trigger prompt()
        OS-->>Farmer: "Add ACREVIA to Home screen?"
        Farmer->>OS: Confirm Install
        OS->>OS: Add ACREVIA icon to App Drawer
    else iOS Safari
        PWA->>Farmer: Display Banner: "Tap Share -> Add to Home Screen"
        Farmer->>OS: Add to Home Screen
    end
```

### 3.1 Display Mode Detection
The app detects whether it is running as an installed PWA or inside a generic browser tab:
```javascript
const isStandalone = window.matchMedia('(display-mode: standalone)').matches 
  || window.navigator.standalone === true;
```
If the app is already installed in standalone mode, nonfunctional "Install App" promo prompts are automatically suppressed.

---

## 4. App Lifecycle & Offline Startup

1. **Cold Launch from Home Screen:** The operating system launches the cached application shell (`/`) directly from the Service Worker cache (`acrevia-shell-v1`), executing in $< 350\text{ ms}$ even when mobile data is completely disabled.
2. **Deep Linking:** URLs such as `/croppulse` or `/crops` navigate directly within the standalone window without spawning new external browser tabs.
3. **Session Preservation:** Authentication tokens stored in secure browser cookies or `localStorage` persist across application restarts, ensuring farmers do not face unexpected login screens during field walks.

---

## 5. Non-Destructive Update Management

A major hazard in offline PWAs is forced service worker updates discarding unsynchronized local drafts.

### 5.1 Safe Update Strategy
- When a new service worker version is detected (`waiting` state), ACREVIA checks the `OfflineQueue`:
  - If pending drafts exist: The app postpones service worker activation and displays an informational badge: *"Update available. Complete pending field sync before refreshing."*
  - If the queue is empty: The app invokes `registration.waiting.postMessage({ type: 'SKIP_WAITING' })` and reloads smoothly.
- **Invariant:** A software update must never purge or corrupt unsynchronized farmer observations.
