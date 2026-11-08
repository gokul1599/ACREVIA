# ACREVIA — Crop Season Economics Architecture
**Subsystem:** Pillar F — ACREVIA Economics  
**Primary Objective:** Transparent, explainable calculation of cost of cultivation, gross revenue, net realization, and unit profit margins with explicit data completeness labeling.

---

## 1. Agricultural Cost of Cultivation Modeling

Drawing upon agricultural economic frameworks (CACP methodology):
1. **Operating Cost ($A_1$):**
   - Paid-out expenses in cash or kind:
     - Seeds, chemical & organic fertilizers, pesticides.
     - Hired human labour, hired bullock/machinery labour.
     - Irrigation fees, electricity charges, diesel fuel.
     - Transport, gunny bags, handling charges.
2. **Gross Revenue ($GR$):**
   - Total realized monetary income from all sales transactions of that season:
     $$GR = \sum (\text{Sale Quantity}_i \times \text{Price per Unit}_i - \text{Deductions}_i)$$
3. **Net Realization / Farm Margin:**
   $$\text{Net Farm Margin} = GR - \text{Total Operating Expenses}$$
4. **Unit Cost of Production:**
   $$\text{Cost per Quintal} = \frac{\text{Total Operating Expenses}}{\text{Total Harvested Quantity (Quintals)}}$$

---

## 2. Incomplete Data Labeling & Uncertainty Transparency

Farming operations frequently have gaps in manual record-keeping (e.g. unrecorded family labour or missing receipts for local seed purchases).

### Completeness Score Calculation:
$$\text{Data Completeness \%} = \frac{\text{Recorded Core Categories}}{\text{Mandatory Crop Cost Buckets (Seeds, Nutrients, Protection, Labour, Harvest)}} \times 100$$

### UI & Economic Reporting Rules:
- If Completeness $< 60\%$: The economic summary is clearly badged:
  `PARTIAL DATA — ESTIMATE ONLY`.
- Unrecorded expense warnings detail which major categories are missing.
- When family labour is not priced, the report explicitly notes: *"Excludes imputed family labour value (CACP A1 concept)"*.
- All financial balances are computed using decimal-safe logic.
