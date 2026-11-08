# ACREVIA Design System & Token Specifications
**Stage 06: Farmer Experience & Mobile-First Progressive Web App**  
*Document Version:* 1.0.0  
*Brand Identity:* ACREVIA Agricultural Intelligence Platform  
*Target Devices:* Android mobile smartphones (primary), tablets, desktop workstations  
*Target Users:* Telangana smallholder farmers, KVK agronomists, extension officers

---

## 1. Visual Identity & Brand Foundations

ACREVIA rejects the generic, hyper-animated consumer AI aesthetic in favor of a calm, grounded, and functional agricultural technology identity. For a farmer standing in direct sunlight in a Warangal cotton field, low-contrast text or decorative glassmorphism degrades usability.

### 1.1 Color Tokens

| Token Name | Hex Code | Semantic Role & Agricultural Purpose |
| :--- | :---: | :--- |
| `--color-forest-900` | `#14291E` | Deepest brand anchor; pressed button states and active navigation icons |
| `--color-forest-800` | `#1E3A2B` | Primary brand green; headers, primary CTA buttons, and brand badges |
| `--color-forest-700` | `#284D3A` | Hover states on primary elements |
| `--color-forest-100` | `#E8F0EC` | Soft leaf background for tags, badges, and secondary buttons |
| `--color-soil-800` | `#4A3525` | Deep earth brown for soil context cards and crop timelines |
| `--color-surface-warm` | `#F7F5F0` | Warm, non-glare canvas background that minimizes eye strain in sunlight |
| `--color-surface-card` | `#FFFFFF` | Elevated cards for distinct observational data blocks |
| `--color-text-primary` | `#1A241F` | High-contrast charcoal text meeting WCAG AAA contrast ratio ($\ge 7:1$) |
| `--color-text-secondary`| `#556059` | Subtitles, helper text, and secondary metadata |
| `--color-border-subtle` | `#E5E0D8` | Structural card and input borders |
| `--color-alert-red` | `#C92A2A` | Chemical hazard alerts, safety warnings, and high-risk flags |
| `--color-warn-amber` | `#D97706` | Model uncertainty warnings, offline notices, and OOD states |
| `--color-success-green` | `#15803D` | Confirmed university evidence, healthy crop states, and sync completion |

---

## 2. Typography & Script Fallbacks

To ensure high legibility across multilingual scripts on low-cost Android hardware, font stacks incorporate dedicated Telugu and Devanagari typography:

```css
--font-sans: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Nirmala UI", Gautami, Mangal, sans-serif;
```

- **Telugu Fallback:** `Gautami`, `Nirmala UI` render complex Telugu conjuncts (*వత్తులు* / *దీర్ఘాలు*) without clipping or misaligned diacritics.
- **Hindi Fallback:** `Mangal`, `Nirmala UI` provide clean Devanagari glyph spacing.
- **Font Scale:**
  - Microcopy / Metadata: $11\text{px} - 12\text{px}$ (uppercase, bold).
  - Body Text / Advisories: $14\text{px} - 16\text{px}$ ($1.6$ line-height for effortless reading).
  - Subheadings / Card Titles: $18\text{px}$ (bold).
  - Page Titles: $24\text{px} - 32\text{px}$ (extrabold).

---

## 3. Touch Ergonomics & Spatial Rules

Smallholder farmers frequently use smartphones with one hand while walking through fields, or with soiled fingers. 

1. **Strict 48px Minimum Touch Target:**
   - Every button, navigation icon, select dropdown, and expandable card implements `.touch-target` with minimum dimensions of $48\text{px} \times 48\text{px}$.
2. **Bottom-Weighted Navigation:**
   - Primary interactive workflows (`Scan Crop`, `KrishiBrain`, `Crops`) are anchored along the bottom thumb zone via `BottomNav`.
3. **Generous Card Padding:**
   - Cards use `p-5` ($20\text{px}$) to `p-6` ($24\text{px}$) padding with clean border separators to prevent accidental mis-taps.

---

## 4. Reusable Component Catalog

The component library resides in `frontend/components/`:

- **`Button`:** Supports `primary` (Forest Green), `secondary` (Soft Green), `outline`, `danger`, and `ghost` variants with built-in loading spinners and disabled states.
- **`Header`:** Sticky mobile header featuring brand mark, dynamic page context, language selector, and user profile avatar.
- **`BottomNav`:** 5-tab mobile navigation bar with a highlighted, elevated center button for foliar scanning.
- **`OfflineBanner`:** Accessible alert banner that animates when device transitions offline or has unsynchronized drafts.
- **`LanguageSelector`:** Compact, instant language toggle allowing switching between Telugu, English, and Hindi without page reloading.
- **`DiagnosisResultCard`:** Structured card presenting AI predicted condition, calibrated confidence gauge, uncertainty state badge, CIBRC advisory, and differential alternative causes.
- **`CitationCard`:** Expandable publication evidence component displaying university publisher, volume version, physical page number, and original excerpt.
