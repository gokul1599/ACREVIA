# ACREVIA — Security, Privacy and Financial Governance Review
**Focus:** Data Isolation, QR Public Privacy Separation, Decimal Math Security, and Tamper-Evidence

---

## 1. Multi-Tenant Farm Financial Isolation

- **Tenant Scoping:** All financial endpoints (`/expenses`, `/sales`, `/seasons/{id}/economics`) require JWT authentication and verify that `farm_id` matches the authenticated user or an authorized field extension worker.
- **Cross-Farm Access Prevention:** Strict tenancy checks prevent Farmer A from querying Farmer B's production costs, selling transactions, or private receipts. Attempted cross-tenant access returns HTTP 403 Forbidden.

---

## 2. Public QR Token & PII Redaction Boundary

The public traceability QR code is scanned by unknown external consumers, traders, and inspectors.
- **No Private Data in Token:** The QR code contains an opaque, unguessable cryptographic token (`qr_token`), not raw database keys or farmer IDs.
- **Strict Redaction Filter:**
  - Redacted: Farmer name, phone, Aadhaar/PAN, bank account, exact latitude/longitude coordinates, property boundary shapefiles, individual invoice images, and transaction prices.
  - Allowed: Crop name, variety name, harvest month/year, harvest session picking number, district/state, verified quality grading parameters, and certified storage facility.

---

## 3. Financial Integrity & Immutability Rules

1. **No Silent In-Place Mutation of Amounts:**
   - Updating an existing expense amount requires a formal correction call (`POST /ledger/expenses/{id}/correct`) with an explicit reason string.
   - The historical amount and timestamp are permanently preserved in `financial_corrections`.
2. **Preventing Lot Overdrafts:**
   - A `ProduceLot` tracks `remaining_quantity`.
   - When recording lot movements or sale transactions, the service uses atomic transactional checks (`SELECT ... FOR UPDATE`) ensuring:
     $$\Delta Q \le \text{remaining\_quantity}$$
   - Any attempt to dispatch or sell more produce than available raises HTTP 400 Bad Request (`INSUFFICIENT_LOT_QUANTITY`).

---

## 4. Cryptographic Hashing for Insurance Evidence Packages

- PMFBY insurance and disaster relief claims require verifiable integrity.
- Each evidence package creates a canonical JSON payload and computes a SHA-256 signature (`package_hash`).
- Any post-issuance tampering with weather logs, yield losses, or timestamps invalidates the package signature.
