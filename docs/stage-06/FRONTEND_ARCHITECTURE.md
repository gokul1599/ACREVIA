# ACREVIA Frontend Architecture Specification
**Stage 06: Farmer Experience & Mobile-First Progressive Web App**  
*Document Version:* 1.0.0  
*Framework:* Next.js 16 (App Router) + React 19 + TypeScript  
*Styling:* Tailwind CSS v4 + PostCSS  
*Target Deployment:* Vercel Serverless Platform (`sin1` Singapore aligned)

---

## 1. Architectural Philosophy & Overview

The ACREVIA frontend is engineered as a resilient, accessible, mobile-first Progressive Web App (PWA). It provides a responsive interface for smallholder farmers, connecting directly to the FastAPI enterprise backend (`http://localhost:8000/api/v1`) without introducing redundant state layers or client-side database connections.

```
       ┌────────────────────────────────────────────────────────┐
       │                   ACREVIA Farmer PWA                   │
       │           (Next.js App Router + TypeScript)            │
       └───────────────────────────┬────────────────────────────┘
                                   │
                    ┌──────────────┴──────────────┐
                    ▼                             ▼
       ┌────────────────────────┐    ┌────────────────────────┐
       │ LocalizationProvider   │    │ AuthProvider           │
       │ (Telugu, English, Hindi│    │ (JWT Bearer Management │
       │ Instant Switching)     │    │ Auto 401 Interception) │
       └────────────────────────┘    └────────────────────────┘
                    │                             │
                    └──────────────┬──────────────┘
                                   ▼
       ┌────────────────────────────────────────────────────────┐
       │                      ApiClient                         │
       │    (Typed Fetch Wrapper + Automatic Token Injection)   │
       └──────────────┬───────────────────────────┬─────────────┘
                      │                           │
          (Online)    ▼               (Offline)   ▼
       ┌────────────────────────┐    ┌────────────────────────┐
       │ Next.js API Rewrite    │    │ OfflineQueue           │
       │ (/api/v1/* -> FastAPI) │    │ (IndexedDB / Storage   │
       │ Port 8000              │    │ UUID Idempotency Key)  │
       └────────────────────────┘    └────────────────────────┘
```

---

## 2. Directory Structure

```text
frontend/
├── app/
│   ├── (auth)/
│   │   ├── login/page.tsx            # Farmer sign-in with phone / email
│   │   ├── register/page.tsx         # Farmer registration with language choice
│   │   └── onboarding/page.tsx       # 4-step farm and crop cycle initialization
│   ├── (farmer)/
│   │   ├── dashboard/page.tsx        # Central agronomic command center
│   │   ├── crops/page.tsx            # Farm holdings, plots & phenological seasons
│   │   ├── diagnosis/page.tsx        # CropVision mobile camera capture & pathology
│   │   ├── knowledge/page.tsx        # KrishiBrain RAG multilingual chat & citations
│   │   ├── croppulse/page.tsx        # Plant health timeline & visual observations
│   │   └── profile/page.tsx          # Account settings, language & offline sync
│   ├── globals.css                   # Tailwind v4 import & design system tokens
│   ├── layout.tsx                    # Root layout with providers, header & bottom nav
│   └── page.tsx                      # Public landing hero & auto-redirect
├── components/
│   ├── navigation/
│   │   ├── Header.tsx                # Sticky top header with brand and profile
│   │   └── BottomNav.tsx             # 5-tab mobile bottom navigation
│   └── ui/
│       ├── Button.tsx                # Reusable accessible button with loading states
│       ├── LanguageSelector.tsx      # Instant Telugu/English/Hindi switcher
│       └── OfflineBanner.tsx         # Connection state & pending sync alert
├── features/
│   └── voice/
│       └── voiceAdapter.ts           # Web Speech API STT and TTS abstraction
├── hooks/
│   └── useOnlineStatus.ts            # Network connectivity listener
├── lib/
│   ├── api/
│   │   ├── client.ts                 # Typed API client for all backend endpoints
│   │   └── types.ts                  # Pydantic-mirrored TypeScript schemas
│   ├── auth/
│   │   └── context.tsx               # AuthContext managing user session & tokens
│   ├── localization/
│   │   └── context.tsx               # LocalizationContext managing active language
│   └── offline/
│       └── queue.ts                  # Offline draft storage & sync state machine
├── messages/
│   ├── en.ts                         # English translation dictionary
│   ├── te.ts                         # Telugu translation dictionary (Telangana idioms)
│   ├── hi.ts                         # Hindi translation dictionary
│   └── index.ts                      # Dictionary exports and Locale types
├── public/
│   ├── icons/                        # PWA 192px and 512px application icons
│   ├── manifest.json                 # Web App Manifest
│   └── sw.js                         # Service worker for shell caching
├── tests/
│   ├── localization.test.js          # Dictionary key parity validation
│   ├── offline_queue.test.js         # Draft persistence & queue operations
│   ├── voice_adapter.test.js         # Speech locale code resolution
│   └── pwa_manifest.test.js          # Manifest & service worker integrity
├── next.config.mjs                   # Next.js config with reverse proxy rewrites
├── package.json                      # Pinned dependencies & test scripts
└── tsconfig.json                     # Strict TypeScript configuration
```

---

## 3. State Management Strategy

1. **Session & Identity State (`AuthProvider`):**
   - Stores current `UserSummary` object and JWT bearer token.
   - Automatically injects `Authorization: Bearer <token>` on all outbound API requests.
   - Detects HTTP 401 Unauthorized responses and redirects gracefully to `/login?expired=1`.
2. **Localization State (`LocalizationProvider`):**
   - Defaults to Telugu (`te`) for smallholders in Telangana.
   - Synchronizes locale changes instantly to `document.documentElement.lang` and `localStorage`.
3. **Offline Queue State (`OfflineQueue`):**
   - Generates client-side UUIDs for offline drafts.
   - Captures foliar photos as base64 data URLs for local persistence.
   - Emits sync events when online connectivity is restored.

---

## 4. Build & Production Optimization

- **Static Pre-Rendering (SSG):** All routes (`/`, `/dashboard`, `/diagnosis`, `/knowledge`, `/crops`, `/croppulse`, `/profile`) compile into static HTML shells during build.
- **Suspense Boundaries:** Search parameter hooks (`useSearchParams`) in `/diagnosis` and `/knowledge` are wrapped inside `<Suspense>` containers, eliminating dynamic CSR bailouts.
- **Reverse Proxy Rewriting:** In development and preview, `next.config.mjs` proxies `/api/v1/*` to the FastAPI backend at `http://127.0.0.1:8000`, resolving cross-origin resource sharing (CORS) complexities seamlessly.
