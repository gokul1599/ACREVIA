# ACREVIA — Stage 11 API Contracts Specification
**Base URL:** `/api/v1`  
**Authentication:** Bearer JWT for authenticated endpoints; Open access for Public Traceability QR verification.

---

## 1. Farm Financial Ledger (`/api/v1/ledger`)

### `POST /api/v1/ledger/expenses`
Record a new farm expense.
- **Request Body:**
  ```json
  {
    "farm_id": "uuid",
    "plot_id": "uuid",
    "crop_season_id": "uuid",
    "category": "FERTILIZERS",
    "description": "5 bags Urea 45kg from Primary Agricultural Cooperative Society",
    "amount": "1332.50",
    "currency": "INR",
    "quantity": 5.0,
    "unit": "BAGS",
    "transaction_date": "2026-10-12",
    "payment_status": "PAID",
    "payment_method": "UPI",
    "vendor_name": "PACS Warangal",
    "receipt_url": "https://storage.acrevia.ag/receipts/rec_01.jpg"
  }
  ```
- **Response `201 Created`:** `FarmExpenseResponse`

### `GET /api/v1/ledger/expenses`
Query expenses filtered by `farm_id`, `crop_season_id`, `category`.
- **Response `200 OK`:** `List[FarmExpenseResponse]`

### `POST /api/v1/ledger/expenses/{expense_id}/correct`
Submit a financial correction with mandatory audit reason.
- **Request Body:**
  ```json
  {
    "new_amount": "1250.00",
    "reason": "Corrected for ₹82.50 subsidy discount applied on invoice"
  }
  ```
- **Response `200 OK`:** `FarmExpenseResponse` with updated amount and attached correction record.

### `POST /api/v1/ledger/sales`
Record a crop sale transaction.
- **Request Body:**
  ```json
  {
    "crop_season_id": "uuid",
    "lot_id": "uuid",
    "buyer_name": "Enumamula Cotton Traders",
    "buyer_type": "MANDI_TRADER",
    "quantity_sold": 22.50,
    "unit": "QUINTAL",
    "price_per_unit": "7450.00",
    "gross_amount": "167625.00",
    "deductions_amount": "2100.00",
    "sale_date": "2026-11-02",
    "payment_status": "PAID",
    "notes": "Moisture docked 1.5%"
  }
  ```
- **Response `201 Created`:** `SaleTransactionResponse`

---

## 2. Market Intelligence (`/api/v1/market`)

### `GET /api/v1/market/prices`
Query latest market observations by `canonical_crop_id`, `district`.
- **Response `200 OK`:** `List[MarketPriceObservationResponse]`

### `GET /api/v1/market/compare`
Compare market realization across mandis for a specific farm plot and crop quantity.
- **Query Parameters:** `plot_id`, `crop_id`, `quantity_quintals`
- **Response `200 OK`:**
  ```json
  {
    "crop_id": "cotton",
    "quantity_quintals": 20.0,
    "comparisons": [
      {
        "market_name": "Warangal (Enumamula)",
        "distance_km": 42.5,
        "modal_price": "7500.00",
        "estimated_gross": "150000.00",
        "estimated_transport_cost": "1800.00",
        "estimated_mandi_cess": "1500.00",
        "estimated_net_realization": "146700.00",
        "effective_rate_per_quintal": "7335.00"
      }
    ]
  }
  ```

---

## 3. Harvest Management (`/api/v1/harvest`)

### `POST /api/v1/harvest/plans`
Create a harvest plan for a crop season.
- **Response `201 Created`:** `HarvestPlanResponse`

### `POST /api/v1/harvest/sessions`
Record a picking/harvest session. Automatically mints a linked `ProduceLot`.
- **Request Body:**
  ```json
  {
    "plot_id": "uuid",
    "crop_season_id": "uuid",
    "harvest_plan_id": "uuid",
    "picking_number": 1,
    "harvest_date": "2026-10-20",
    "harvested_quantity": 18.5,
    "unit": "QUINTAL",
    "quantity_type": "MEASURED",
    "loss_quantity": 0.5,
    "notes": "First picking - excellent staple"
  }
  ```
- **Response `201 Created`:** `HarvestSessionResponse` (includes generated `produce_lot_id` and `lot_code`)

---

## 4. Post-Harvest Quality & Storage (`/api/v1/quality` & `/api/v1/storage`)

### `POST /api/v1/quality/measurements`
Log physical/chemical quality parameters.
- **Request Body:**
  ```json
  {
    "lot_id": "uuid",
    "parameter_name": "MOISTURE_PCT",
    "measured_value": 8.4,
    "unit": "%",
    "measurement_method": "MEASURED_DIGITAL_SENSOR",
    "instrument_details": "AgroSens Pin Moisture Meter Pro"
  }
  ```
- **Response `201 Created`:** `QualityMeasurementResponse`

### `POST /api/v1/storage/lots`
Deposit a produce lot into a designated storage location.
- **Response `201 Created`:** `StorageLotResponse`

---

## 5. Produce Traceability (`/api/v1/trace`)

### `GET /api/v1/trace/lots/{lot_id}`
Authenticated internal lot view with complete movement history.
- **Response `200 OK`:** `ProduceLotDetailResponse`

### `POST /api/v1/trace/lots/{lot_id}/movements`
Record a lot movement (transfer, storage, or partial sale) with remaining balance validation.
- **Response `201 Created`:** `LotMovementResponse`

### `GET /api/v1/trace/public/{qr_token}` (Open Public Verification)
Public verification endpoint scanned from bags or shipping containers.
- **Response `200 OK`:**
  ```json
  {
    "lot_code": "ACR-LOT-2026-CTN-0104",
    "crop_name": "Cotton (కపాస్)",
    "variety": "RCH-659 BG II",
    "harvest_date": "2026-10-20",
    "district": "Warangal",
    "state": "Telangana",
    "origin_verification": "VERIFIED_ACREVIA_FARM",
    "quality_summary": {
      "moisture_pct": 8.4,
      "grade": "Grade A Premium"
    },
    "harvest_session": "1st Picking",
    "public_notice": "Personal farmer information redacted for privacy protection."
  }
  ```

---

## 6. Crop Economics & Loss Evidence (`/api/v1/economics`)

### `GET /api/v1/economics/seasons/{season_id}`
Calculate comprehensive season financials: total expenses, revenue, net margin, and completeness percentage.
- **Response `200 OK`:** `CropSeasonEconomicsResponse`

### `POST /api/v1/economics/evidence-package`
Generate a cryptographically hashed crop loss documentation bundle for PMFBY insurance claims.
- **Response `201 Created`:** `CropLossEvidencePackageResponse`
