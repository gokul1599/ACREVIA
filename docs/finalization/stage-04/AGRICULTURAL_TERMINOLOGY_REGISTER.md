# ACREVIA — STAGE 04 AGRICULTURAL TERMINOLOGY REGISTER
## Canonical Trilingual Glossary: English, Telugu, Hindi & Scientific Binomials

**Document Reference:** `docs/finalization/stage-04/AGRICULTURAL_TERMINOLOGY_REGISTER.md`  
**Stage:** 04 — KrishiBrain Multilingual Multimodal Agricultural RAG Intelligence Engine  
**Standard Authority:** PJTSAU Telangana & ICAR Specialized Institutes  

---

### 1. Governed Terminology Standard

To prevent dangerous ambiguities when smallholder farmers describe foliar afflictions, KrishiBrain maintains a canonical trilingual terminology registry mapping vernacular Telugu and Hindi vocabulary directly to scientific binomials and standardized English nomenclature:

| Concept Identifier | English Term | Telugu Term (తెలుగు) | Hindi Term (हिंदी) | Scientific / Taxonomic Name | Category |
|---|---|---|---|---|---|
| `CROP_COTTON` | Cotton | పత్తి | कपास | *Gossypium hirsutum* | Crop |
| `CROP_RICE` | Rice / Paddy | వరి | धान / चावल | *Oryza sativa* | Crop |
| `CROP_CHILLI` | Chilli | మిరప | मिर्च | *Capsicum annuum* | Crop |
| `PEST_PBW` | Pink Bollworm | గులాబీ రంగు కాయతొలుచు పురుగు | गुलाबी सुंडी | *Pectinophora gossypiella* | Insect Pest |
| `PEST_BPH` | Brown Plant Hopper | సుడిదోమ | भूरा फुदका | *Nilaparvata lugens* | Insect Pest |
| `PEST_THRIPS` | Black Thrips | నల్ల తామర పురుగు | काली थ्रिप्स | *Thrips parvispinus* | Insect Pest |
| `PEST_MITE` | Yellow Mite | పచ్చ నల్లి | पीली मकड़ी | *Polyphagotarsonemus latus* | Acarine Pest |
| `DIS_BLAST` | Rice Blast | అగ్గితెగులు | ब्लास्ट / झुलसा | *Magnaporthe oryzae* | Fungal Disease |
| `DIS_BLB` | Bacterial Leaf Blight | బాక్టీరియా ఆకు ఎండు తెగులు | जीवाणु पत्ती झुलसा | *Xanthomonas oryzae* | Bacterial Disease |
| `DIS_SHBL` | Sheath Blight | పొడ తెగులు | शीथ ब्लाइट | *Rhizoctonia solani* | Fungal Disease |
| `DIS_ANTH` | Anthracnose / Fruit Rot| కాయకుళ్లు తెగులు | फल सड़न / एन्थ्रेक्नोज | *Colletotrichum capsici* | Fungal Disease |
| `DEF_ZINC` | Zinc Deficiency (Khaira)| జింక్ లోపం / ఖైరా | खैरा रोग | Abiotic (Nutrient) | Deficiency |
| `ABIO_RED` | Cotton Leaf Reddening | పత్తి ఆకు ఎరుపు | पत्ती लाल होना | Abiotic (Low Temp/Mg) | Physiological |
| `PRAC_ETL` | Economic Threshold Level| ఆర్థిక నష్ట పరిమితి | आर्थिक क्षति स्तर | Dynamic Agronomic Metric | Practice |
| `PRAC_TRAP`| Pheromone Trap | లింగాకర్షక బుట్ట | फेरोमोन ट्रैप | IPM Monitoring Tool | Tool |
| `PRAC_PHI` | Pre-Harvest Interval | కోతకు ముందు వేచి ఉండే సమయం | तुड़ाई पूर्व प्रतीक्षा अवधि | CIBRC Safety Period | Regulation |

---

### 2. Lexical Disambiguation Invariants

1. **Local Telugu Dialect Handling:** In Warangal, farmers refer to Brown Plant Hopper as *"సుడిదోమ"* (whirlpool bug); in Khammam, it is occasionally called *"మట్టదోమ"*. Both dialectal strings are indexed to canonical concept ID `PEST_BPH`.
2. **Invasive Pest Distinction:** In chilli, farmers often confuse native yellow thrips with invasive Indonesian black thrips (*Thrips parvispinus*). The terminology register maps *"నల్ల తామర"* specifically to `PEST_THRIPS` (*T. parvispinus*) to ensure that recommended chemical regimes reflect current resistance patterns.
3. **Non-Invention Rule:** If an uncatalogued regional term is encountered, the system never fabricates a translation; it requests clarification while presenting the recognized scientific term.
