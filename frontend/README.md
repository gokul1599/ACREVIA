# ACREVIA — Farmer Progressive Web Application (Frontend)

## Overview

The ACREVIA Farmer frontend is an offline-first Progressive Web Application (PWA) built with Next.js 16 (App Router), React 19, TypeScript, and Tailwind CSS v4. It delivers localized agronomic advisory, pest/disease diagnosis, and digital twin insights directly to smallholder farmers across Telangana.

---

## Core Capabilities

1. **Offline Persistence & Synchronization:**
   - Powered by transactional `IndexedDB` (`acrevia_offline_db_v2`).
   - Supports structured draft storage, photo binary attachments, and non-destructive 409 conflict handling.
   - Exponential backoff synchronization queue with randomized jitter.

2. **Multilingual Agronomic Localization:**
   - 100% dictionary key parity across Telugu (`te`), English (`en`), and Hindi (`hi`).
   - PJTSAU-certified terminology for cotton, rice, and chilli cultivation.

3. **Client-Side Security:**
   - Secure serverless authentication via JWT and bcrypt.
   - Strictly validates API endpoints and prevents open redirection / duplicate routing.

---

## Testing & Quality Assurance

To execute the offline test suite:
```bash
npm test
```

To build production bundle:
```bash
npm run build
```
