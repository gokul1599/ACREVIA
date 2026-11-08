# ACREVIA Agricultural Safety Governance Framework
## Human-in-the-Loop Safeguards, CIBRC Regulations & Zero-Harm Protocol
**Target Stage:** Stage 08 Remediation (`TASK-S08-01` / Evaluation Framework)  
**Regulatory Standards:** Central Insecticides Board & Registration Committee (CIBRC), Insecticides Act 1968, PJTSAU Package of Practices  

---

## 1. Principles of Agricultural AI Safety

In agricultural intelligence, an incorrect algorithm recommendation can destroy a farmer's seasonal livelihood, cause acute chemical poisoning, or introduce illegal pesticide residues that lead to crop seizure.

ACREVIA enforces four non-negotiable safety principles:
1. **The Precautionary Principle:** In the presence of diagnostic ambiguity or uncalibrated confidence, the platform must withhold automated chemical recommendations and escalate to human experts.
2. **Zero Off-Label / Banned Prescriptions:** No chemical input may be recommended unless explicitly registered with the CIBRC for that specific crop and target pest.
3. **Mandatory Personal Protective Equipment (PPE) Advisories:** Any chemical intervention must accompany unambiguous safety precautions and Pre-Harvest Interval (PHI) warnings in the farmer's native language.
4. **Human Authority & Agronomist Primacy:** Algorithms advise; human extension scientists supervise, validate, and possess final veto authority.

---

## 2. Chemical Input Governance & CIBRC Compliance

### 2.1 Banned & Restricted Agrochemicals (Strict System Filter)
The platform maintains a hardcoded exclusion blacklist in `backend/app/domain/safety_rules.py`. Any query or inference matching these substances triggers an immediate block:
- **Banned in India:** Monocrotophos (banned on vegetables/chilli), Endosulfan, Diazinon, Methyl Parathion.
- **Restricted / Red-Label Toxicity:** Requires mandatory prescription gating and cannot be shown directly in automated farmer UI.

### 2.2 Integrated Pest Management (IPM) Hierarchy
All management guidance delivered via KrishiBrain must follow the IPM hierarchy:
```
           [1. Cultural Controls] (Spacing, trap crops, sanitation)
                     │
                     ▼
           [2. Biological Controls] (Trichoderma, neem oil, pheromone traps)
                     │
                     ▼
           [3. Economic Threshold Level (ETL) Assessment]
                     │
                     ▼
           [4. Chemical Controls] (Only as last resort when ETL exceeded)
```

---

## 3. Human-in-the-Loop (HITL) Expert Review Triggers

An observation or advisory is automatically locked in state `PENDING_EXPERT_REVIEW` if any of the following conditions are met:

```
                                INCOMING OBSERVATION
                                         │
        ┌────────────────────────────────┼────────────────────────────────┐
        ▼                                ▼                                ▼
[Confidence < 0.60]           [Quarantine / Epidemic Pest]     [Severe Infestation]
 - High ambiguity              - Pink Bollworm in Cotton        - > 50% plot canopy
 - OOD score elevated          - Rice Blast epidemic            - Defoliation risk
        │                                │                                │
        └────────────────────────────────┼────────────────────────────────┘
                                         ▼
                 [AUTOMATIC SAFETY CIRCUIT BREAKER TRIPS]
                                         │
                                         ▼
                 [Chemical Advice Withheld in Farmer UI]
                 [Urgent Notification Dispatched to KVK Scientist]
```

### Response Time SLAs for KVK Reviewers:
- **Critical / Epidemic Pest:** Review and validation within **4 daylight hours**.
- **Routine Moderate Ambiguity:** Review and validation within **24 hours**.

---

## 4. Algorithmic Abstention & "I Don't Know" Policy

Unlike consumer chatbots that fabricate answers when uncertain, ACREVIA enforces an explicit abstention policy:
- If a user asks KrishiBrain about an unsupported crop (e.g. apple, sugarcane) or an unverified tank mix:
  - The model returns an abstention message in Telugu:
    *"క్షమించండి, ఈ అంశంపై PJTSAU అధికారిక మార్గదర్శకాలు అందుబాటులో లేవు. సరికాని సలహా ఇవ్వడం కంటే మీ సమీప వ్యవసాయ అధికారిని సంప్రదించాల్సిందిగా కోరుతున్నాము."*  
    *(Sorry, official PJTSAU guidelines on this topic are unavailable. Rather than providing incorrect advice, we recommend consulting your local agricultural officer.)*
- This abstention behavior is verified in automated unit tests (`backend/tests/test_knowledge.py::test_knowledge_query_abstention_on_unsupported_topic`).

---

## 5. Pre-Harvest Interval (PHI) & Maximum Residue Limit (MRL) Guardrails

Whenever a chemical fungicide or insecticide is approved for display:
1. **Pre-Harvest Interval (PHI):** The minimum waiting period between spray and harvest must be rendered in bold red text (e.g., *"వేచి ఉండవలసిన సమయం: 15 రోజులు - Waiting Period: 15 Days"*).
2. **Dosage Guardrail:** Dosages are explicitly stated per acre and per 10-litre knapsack sprayer (e.g., *"10 లీటర్ల నీటికి 20 మి.లీ"*), avoiding vague percentages.
3. **PPE Warning:** Mandatory pictorial warning showing face mask, rubber gloves, and eye protection during spray preparation.
