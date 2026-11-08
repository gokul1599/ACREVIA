# ACREVIA — STAGE 04 CIBRC REGULATORY SOURCE AUDIT
## Statutory Authority, Registered Product Inventories, Pre-Harvest Intervals & Prohibitions

**Document Reference:** `docs/finalization/stage-04/CIBRC_SOURCE_AUDIT.md`  
**Stage:** 04 — KrishiBrain Multilingual Multimodal Agricultural RAG Intelligence Engine  
**Statutory Basis:** The Insecticides Act, 1968 & Insecticides Rules, 1971 (Government of India)  
**Database Record:** Source `401398e6-d3c0-4394-b2dd-a7d3f3c9fe01` in [`backend/app/models/knowledge_source.py`](file:///c:/Users/gokul/OneDrive/Documents/projects/backend/app/models/knowledge_source.py)  

---

### 1. Statutory Role of CIBRC in ACREVIA

The Central Insecticides Board & Registration Committee (CIBRC) under the Ministry of Agriculture & Farmers Welfare is the statutory body regulating the import, manufacture, sale, transport, distribution, and use of insecticides in India. 

Under ACREVIA knowledge governance, **CIBRC regulations represent statutory law**. No university package of practices, agronomist advice, or commercial manufacturer brochure can authorize an agrochemical use that conflicts with CIBRC registration.

---

### 2. Verified Active Ingredients & Approved Crop Registrations

The CIBRC statutory corpus ingested into Neon PostgreSQL validates approved active ingredients across ACREVIA's three target crops:

#### 2.1 Cotton (*Gossypium hirsutum*)
| Registered Active Ingredient | Formulation | Target Pests / Pathogens | Registered Dosage | Approved PHI (Days) |
|---|---|---|---|---|
| **Profenofos** | 50% EC | Pink Bollworm, Spodoptera | $1.5 - 2.0 \text{ ml/L}$ | 15 days |
| **Emamectin Benzoate** | 5% SG | Bollworms, Helicoverpa | $0.4 - 0.5 \text{ g/L}$ | 14 days |
| **Flonicamid** | 50% WG | Aphids, Jassids | $0.3 - 0.4 \text{ g/L}$ | 25 days |
| **Chlorantraniliprole** | 18.5% SC | Bollworm complex | $0.3 \text{ ml/L}$ | 21 days |

#### 2.2 Rice (*Oryza sativa*)
| Registered Active Ingredient | Formulation | Target Pests / Pathogens | Registered Dosage | Approved PHI (Days) |
|---|---|---|---|---|
| **Tricyclazole** | 75% WP | Rice Blast (*Magnaporthe oryzae*) | $0.6 \text{ g/L}$ | **30 days** |
| **Isoprothiolane** | 40% EC | Blast, Sheath Rot | $1.5 \text{ ml/L}$ | 28 days |
| **Pymetrozine** | 50% WG | Brown Plant Hopper (BPH) | $0.6 \text{ g/L}$ | 19 days |
| **Triflumezopyrim** | 10% SC | BPH, Whitebacked Planthopper | $0.5 \text{ ml/L}$ | 21 days |
| **Copper Oxychloride** | 50% WP | Bacterial Leaf Blight | $2.5 \text{ g/L}$ (+ Plantomycin 0.1g) | 15 days |

#### 2.3 Chilli (*Capsicum annuum*)
| Registered Active Ingredient | Formulation | Target Pests / Pathogens | Registered Dosage | Approved PHI (Days) |
|---|---|---|---|---|
| **Spinetoram** | 11.7% SC | Invasive Black Thrips (*T. parvispinus*) | $0.9 - 1.0 \text{ ml/L}$ | **7 days** |
| **Fipronil** | 5% SC | Thrips, Fruit Borer | $2.0 \text{ ml/L}$ | 15 days |
| **Spiromesifen** | 22.9% SC | Yellow Mite (*P. latus*) | $1.0 \text{ ml/L}$ | 10 days |
| **Diafenthiuron** | 50% WP | Mites, Whiteflies | $1.25 \text{ g/L}$ | 12 days |
| **Azoxystrobin** | 23% SC | Anthracnose / Fruit Rot | $1.0 \text{ ml/L}$ | 5 days |

---

### 3. Prohibited Formulations & Strict Bans

KrishiBrain enforces hard negative filters against agrochemicals banned or restricted under Government of India Gazette notifications:
1. **Monocrotophos:** Strictly prohibited for use on vegetables, chillies, and pulses under statutory order. Requests to spray Monocrotophos on chilli are immediately blocked.
2. **Endosulfan:** Completely banned nationwide by Supreme Court ruling.
3. **Phorate 10G & Carbofuran 3G:** High-toxicity organophosphates/carbamates strictly restricted in smallholder open cultivation.

---

### 4. Pre-Harvest Interval (PHI) Compliance

The Pre-Harvest Interval is the mandatory minimum waiting time between the final chemical spray and crop harvest to ensure toxic residues dissipate below Food Safety and Standards Authority of India (FSSAI) Maximum Residue Limits. 

Whenever KrishiBrain retrieves a chemical treatment, the generator automatically appends the statutory PHI notice to the response advisory card.
