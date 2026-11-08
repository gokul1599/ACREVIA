# ACREVIA — Produce Traceability Architecture
**Subsystem:** Pillar E — ACREVIA Trace  
**Primary Objective:** Cryptographically secure, lot-based traceability linking produce from harvest through storage and sale, with strict privacy-preserving public verification.

---

## 1. Traceability Lifecycle & Lot Model

Each harvest generates one or more discrete, identifiable lots:

```
[CropSeason] 
   └── [HarvestSession]
          └── [ProduceLot] (lot_code: "LOT-TEL-2026-CTN-00129", qr_token: "d9f8e4c2-...")
                 ├── [QualityMeasurement] (Moisture 8.5%, Staple 29mm)
                 ├── [LotMovement 1] (HARVEST -> STORAGE_ENTRY: 25 Quintals)
                 ├── [LotMovement 2] (STORAGE -> SALE: 15 Quintals)
                 └── Remaining Balance: 10 Quintals
```

### Traceability Invariants:
1. **Quantity Conservation Law:**
   - A lot starts with `initial_quantity`.
   - Any transfer, split, or sale movement reduces `remaining_quantity`.
   - The system prevents lot overdrafts: $\sum \text{Movement Transfers} \le \text{Initial Quantity}$.
2. **Unique Identifiers:**
   - Human-readable `lot_code`: E.g., `ACR-LOT-2026-RICE-WGL-0891`.
   - Cryptographic `qr_token`: High-entropy UUID v4 or HMAC signature token used in public QR codes.

---

## 2. Public vs. Private Data Boundary (Privacy Enforcement)

When a trader, consumer, or inspector scans a QR code, the public verification endpoint strictly separates verifiable agricultural provenance from private farmer information:

| Data Field | Public Verification View | Authenticated Owner / Field Agent View |
| :--- | :---: | :---: |
| **Commodity / Crop** | Visible (e.g. Cotton) | Visible |
| **Variety** | Visible (e.g. Bollgard II RCH-659) | Visible |
| **Harvest Date & Session** | Visible (e.g. 2026-10-15) | Visible |
| **Quality Grade & Lab Values** | Visible (e.g. Moisture 8.4%, Grade A) | Visible |
| **Region / District** | Visible (e.g. Warangal, Telangana) | Visible |
| **Traceability Status** | Visible (`VERIFIED_ORIGIN`) | Visible |
| **Farmer Legal Name** | **REDACTED** ("Verified Producer") | Visible |
| **Phone Number / Contact** | **REDACTED** | Visible |
| **Precise GPS Plot Coordinates** | **REDACTED** (Only District shown) | Visible (Exact Lat/Lon) |
| **Financial / Sales Amount** | **REDACTED** | Visible |
| **Internal Receipts** | **REDACTED** | Visible |
