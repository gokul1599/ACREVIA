# ACREVIA STAGE 10: SECURITY AND PRIVACY REVIEW
## Multi-Tenant Farm Isolation, Provenance Integrity & Access Controls

---

## 1. Threat Modeling & Scope

The digital twin and decision intelligence platform stores sensitive agricultural data including farm cadastral boundaries, harvest yields, input purchases, sensor telemetry, and operational schedules. 

Key threats analyzed:
1. **Cross-Tenant Data Tampering & Leakage:** Unauthorized users accessing or injecting malicious state into another farmer's digital twin.
2. **Adversarial Simulation Manipulation:** Crafting malicious simulation parameters to overload serverless compute or induce denial of service.
3. **Pesticide / Chemical Poisoning Exploits:** Forcing the decision engine to emit dangerous, off-label, or banned pesticide recommendations.
4. **Historical Snapshot Repudiation:** Altering past snapshots to obscure faulty agronomic advice or fraudulent insurance claims.

---

## 2. Security Controls & Architecture

### 2.1 Strict Multi-Tenant Authorization Enforcement
Every endpoint in Stage 10 enforces strict database-level and service-layer tenancy checks:
- The authenticated `user_id` from the verified JWT is mapped to farm ownership records.
- Any request for a `farm_id` or `plot_id` not belonging to the authenticated user (or not explicitly assigned to an extension agent with active delegation tokens) returns `HTTP 403 Forbidden` or `HTTP 404 Not Found` without disclosing record existence.
- Cross-tenant object references in simulation requests (e.g., requesting simulation for Plot B while authenticated as Owner of Plot A) are blocked before compute execution.

### 2.2 Immutable Snapshot Integrity
- `TwinSnapshot` records are strictly append-only.
- Updates and deletions on snapshot tables are prevented at the service layer and through database triggers.
- Each snapshot stores an SHA-256 state payload hash to ensure verifiable tamper-detection.

### 2.3 Strict Parameter Bounds on Simulation & Optimization
To prevent compute exhaustion and denial of service:
- Maximum simulation horizon is capped at 30 days.
- Maximum number of plots in a multi-plot optimization problem is capped at 10.
- Optimization iteration limits are enforced at the solver level (< 500 iterations, 150ms timeout).
- Input parameters (e.g. irrigation depth, rainfall, fertilizer dosage) are validated against hard agronomic ranges via Pydantic validators.

### 2.4 Safety Guardrails for Chemical Recommendations
- Recommendations are constrained by a hardcoded negative blocklist of banned/restricted agrochemicals in India (e.g., Monocrotophos on vegetables, Endosulfan, Paraquat dichloride without PPE).
- When a crop diagnosis or pest alert indicates severe pressure, the engine is programmatically barred from emitting automated chemical prescriptions. It must set `recommendation_state = REQUIRES_EXPERT_REVIEW` and route to ExpertConnect.

---

## 3. Compliance & Audit Verification Matrix

| Security Dimension | Mechanism | Test Result |
|:---|:---|:---|
| **Tenant Isolation** | Scoped SQL queries by `user_id` & `farm_id` | Verified (Test Case passes) |
| **Tamper Proofing** | Immutable snapshots & hash verification | Verified (Test Case passes) |
| **Compute Sandboxing** | Bounded iterations & timeouts | Verified (Execution strictly < 150ms) |
| **Safety Blocklist** | Pre-synthesis chemical filter | Verified (100% blocked) |
| **PII & Data Minimization** | Zero external transfer of cadastral coordinates | Verified |
