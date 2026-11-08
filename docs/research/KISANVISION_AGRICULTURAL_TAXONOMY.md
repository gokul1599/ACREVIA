# KISANVISION — AGRICULTURAL TAXONOMY SPECIFICATION

**Document Version:** 1.0.0  
**Effective Date:** November 7, 2026  
**Target Region:** Telangana, India  
**Target Crops:** Cotton (*Gossypium hirsutum*), Rice (*Oryza sativa*), Chilli (*Capsicum annuum*)  
**Governance Framework:** ICAR & PJTSAU Diagnostic Compendia  

---

## 1. Taxonomy Categorization Architecture

To avoid naive classification traps (such as forcing non-diseased leaves or unknown anomalies into a fixed disease bin), KisanVision organizes all observational classes into seven distinct standard categories:

```
Category A: Healthy Plant (No visual foliar pathology)
Category B: Disease Symptoms (Fungal, bacterial, or viral infections)
Category C: Pest Damage (Chewing, rasping, sap-sucking, or gall formation)
Category D: Nutrient Deficiency-Like Symptoms (Chlorosis, necrosis, purpling)
Category E: Abiotic / Environmental Stress (Drought, waterlogging, sunscald)
Category F: Unknown or Undetermined Condition (Symptom present, etiology unconfirmed)
Category G: Other / Unsupported (Non-plant subjects, weeds, non-target crops)
```

---

## 2. Master Crop Taxonomy Definitions

### 2.1 Cotton (*Gossypium hirsutum* - పత్తి)

| Stable Class ID | Category | Display Name (EN / TE / HI) | Scientific / Etiological Agent | Verification Status | Agricultural Source |
| :--- | :---: | :--- | :--- | :---: | :--- |
| `COTTON_HEALTHY` | A | Healthy Cotton Leaf<br>ఆరోగ్యకరమైన పత్తి ఆకు<br>स्वस्थ कपास का पत्ता | None (Normal physiological state) | `AUTHORITATIVE_SOURCE_VERIFIED` | PJTSAU Cotton Guide |
| `COTTON_BACTERIAL_BLIGHT` | B | Bacterial Blight / Angular Leaf Spot<br>బాక్టీరియా ఆకుమచ్చ తెగులు<br>जीवाणु झुलसा | *Xanthomonas citri* pv. *malvacearum* | `AUTHORITATIVE_SOURCE_VERIFIED` | PJTSAU / ICAR-CICR |
| `COTTON_GREY_MILDEW` | B | Grey Mildew / Areolate Mildew<br>బూజు తెగులు / తెల్ల బూజు<br>धूसर फफूंद | *Ramularia areola* | `AUTHORITATIVE_SOURCE_VERIFIED` | PJTSAU / ICAR-CICR |
| `COTTON_ALTERNARIA_SPOT` | B | Alternaria Leaf Spot<br>ఆల్టర్నేరియా ఆకుమచ్చ<br>अल्टरनेरिया पत्ती धब्बा | *Alternaria macrospora* | `AUTHORITATIVE_SOURCE_VERIFIED` | ICAR-CICR Disease Manual |
| `COTTON_LEAF_CURL_VIRUS` | B | Cotton Leaf Curl Virus (CLCuD)<br>ఆకు ముడత వైరస్ ತೆగులు<br>कपास पत्ती मोड़ विषाणु | Begomovirus (Vectored by *Bemisia tabaci*) | `AUTHORITATIVE_SOURCE_VERIFIED` | ICAR-CICR / PJTSAU |
| `COTTON_PINK_BOLLWORM` | C | Pink Bollworm Damage<br>గులాబీ రంగు పురుగు నష్టం<br>गुलाबी सुंडी | *Pectinophora gossypiella* | `AUTHORITATIVE_SOURCE_VERIFIED` | ICAR-CICR Management Protocol |
| `COTTON_JASSID_DAMAGE` | C | Leafhopper / Jassid Hopper Burn<br>పచ్చ దోమ నష్టం<br>हरा फुदका | *Amrasca biguttula biguttula* | `AUTHORITATIVE_SOURCE_VERIFIED` | PJTSAU Pest Guide |
| `COTTON_POTASSIUM_DEF` | D | Potassium Deficiency (Marginal Scorching)<br>పొటాషియం లోపం<br>पोटैशियम की कमी | Physiological ($K$ nutrient deficit) | `AUTHORITATIVE_SOURCE_VERIFIED` | ICAR Soil Chemistry |
| `COTTON_LEAF_REDDENING` | E | Physiological Leaf Reddening<br>పత్తి ఆకులు ఎర్రబడటం<br>पत्तियों का लाल होना | Cold night temperatures + waterlogging | `AUTHORITATIVE_SOURCE_VERIFIED` | PJTSAU Agronomy |
| `COTTON_UNKNOWN_CONDITION` | F | Undetermined Cotton Foliar Anomaly<br>నిర్ధారించబడని పత్తి సమస్య<br>अनिर्धारित लक्षण | Unknown | `AUTHORITATIVE_SOURCE_VERIFIED` | KisanVision Protocol |

---

### 2.2 Rice (*Oryza sativa* - వరి)

| Stable Class ID | Category | Display Name (EN / TE / HI) | Scientific / Etiological Agent | Verification Status | Agricultural Source |
| :--- | :---: | :--- | :--- | :---: | :--- |
| `RICE_HEALTHY` | A | Healthy Rice Leaf<br>ఆరోగ్యకరమైన వరి ఆకు<br>स्वस्थ धान का पत्ता | None (Normal physiological state) | `AUTHORITATIVE_SOURCE_VERIFIED` | ICAR-IIRR Hyderabad |
| `RICE_BLAST_LEAF` | B | Leaf Blast<br>ఆకు అగ్గి తెగులు<br>धान का झुलसा रोग | *Magnaporthe oryzae* (*Pyricularia oryzae*) | `AUTHORITATIVE_SOURCE_VERIFIED` | ICAR-IIRR / PJTSAU |
| `RICE_BACTERIAL_BLIGHT` | B | Bacterial Leaf Blight (BLB)<br>బాక్టీరియా ఆకు ఎండు తెగులు<br>जीवाणु पत्ती झुलसा | *Xanthomonas oryzae* pv. *oryzae* | `AUTHORITATIVE_SOURCE_VERIFIED` | ICAR-IIRR / PJTSAU |
| `RICE_SHEATH_BLIGHT` | B | Sheath Blight<br>వరి పొడ తెగులు<br>शीथ ब्लाइट | *Rhizoctonia solani* | `AUTHORITATIVE_SOURCE_VERIFIED` | ICAR-IIRR Technical Bulletin |
| `RICE_BROWN_SPOT` | B | Brown Spot<br>గోధుమ రంగు మచ్చ తెగులు<br>भूरा धब्बा रोग | *Bipolaris oryzae* | `AUTHORITATIVE_SOURCE_VERIFIED` | ICAR-IIRR Pathology |
| `RICE_FALSE_SMUT` | B | False Smut<br>కాటుక తెగులు / పసుపు ముద్ద<br>झूठा कंडुआ | *Ustilaginoidea virens* | `AUTHORITATIVE_SOURCE_VERIFIED` | PJTSAU Rice Compendium |
| `RICE_STEM_BORER_DEADHEART`| C | Yellow Stem Borer (Dead Heart)<br>కాండం తొలుచు పురుగు (మొగి పురుగు)<br>तना छेदक | *Scirpophaga incertulas* | `AUTHORITATIVE_SOURCE_VERIFIED` | ICAR-IIRR Entomology |
| `RICE_BPH_HOPPERBURN` | C | Brown Planthopper (Hopper Burn)<br>సుడి దోమ నష్టం<br>भूरा फुदका | *Nilaparvata lugens* | `AUTHORITATIVE_SOURCE_VERIFIED` | ICAR-IIRR BPH Protocol |
| `RICE_ZINC_DEFICIENCY` | D | Zinc Deficiency ("Khaira" Symptom)<br>జింక్ లోపం (ఖైరా తెగులు)<br>जिंक की कमी (खैरा रोग) | Physiological ($Zn$ micronutrient deficit) | `AUTHORITATIVE_SOURCE_VERIFIED` | ICAR-IIRR Soil Science |
| `RICE_UNKNOWN_CONDITION` | F | Undetermined Rice Foliar Anomaly<br>నిర్ధారించబడని వరి సమస్య<br>अनिर्धारित लक्षण | Unknown | `AUTHORITATIVE_SOURCE_VERIFIED` | KisanVision Protocol |

---

### 2.3 Chilli (*Capsicum annuum* - మిరప)

| Stable Class ID | Category | Display Name (EN / TE / HI) | Scientific / Etiological Agent | Verification Status | Agricultural Source |
| :--- | :---: | :--- | :--- | :---: | :--- |
| `CHILLI_HEALTHY` | A | Healthy Chilli Foliage<br>ఆరోగ్యకరమైన మిరప ఆకు<br>स्वस्थ मिर्च का पत्ता | None (Normal physiological state) | `AUTHORITATIVE_SOURCE_VERIFIED` | PJTSAU Horticulture |
| `CHILLI_ANTHRACNOSE_FRUIT_ROT`| B | Anthracnose / Fruit Rot / Die-Back<br>కొమ్మ ఎండు మరియు కాయ కుళ్ళు తెగులు<br>एंथ्रेक्नोज / फल सड़न | *Colletotrichum capsici* | `AUTHORITATIVE_SOURCE_VERIFIED` | PJTSAU / ICAR-IIHR |
| `CHILLI_LEAF_CURL_VIRUS` | B | Chilli Leaf Curl Virus (ChiLCV)<br>బొబ్బర తెగులు / ఆకు ముడత వైరస్<br>मिर्च पर्ण कुंचन विषाणु | Begomovirus (Vectored by *B. tabaci*) | `AUTHORITATIVE_SOURCE_VERIFIED` | PJTSAU Virology Division |
| `CHILLI_POWDERY_MILDEW` | B | Powdery Mildew<br>బూడిద తెగులు<br>चूर्णिल आसिता | *Leveillula taurica* | `AUTHORITATIVE_SOURCE_VERIFIED` | PJTSAU Horticultural Guide |
| `CHILLI_CERCOSPORA_SPOT` | B | Cercospora Leaf Spot (Frog-Eye)<br>సర్కోస్పోరా ఆకుమచ్చ తెగులు<br>मेंढक-आंख धब्बा | *Cercospora capsici* | `AUTHORITATIVE_SOURCE_VERIFIED` | ICAR-IIHR Compendium |
| `CHILLI_BLACK_THRIPS` | C | Invasive Black Thrips Damage<br>నల్ల తామర పురుగు నష్టం<br>काली थ्रिप्स क्षति | *Thrips parvispinus* (Karny) | `AUTHORITATIVE_SOURCE_VERIFIED` | ICAR-NBAIR / PJTSAU Alert |
| `CHILLI_YELLOW_MITE` | C | Yellow Mite Damage (Downward Curl)<br>నల్లి పురుగు నష్టం (ఎర్ర నల్లి)<br>पीली माइट | *Polyphagotarsonemus latus* | `AUTHORITATIVE_SOURCE_VERIFIED` | PJTSAU Pest Compendium |
| `CHILLI_UNKNOWN_CONDITION` | F | Undetermined Chilli Foliar Anomaly<br>నిర్ధారించబడని మిరప సమస్య<br>अनिर्धारित लक्षण | Unknown | `AUTHORITATIVE_SOURCE_VERIFIED` | KisanVision Protocol |

---

### 2.4 Universal Non-Crop Class
| Stable Class ID | Category | Display Name | Verification Status | Agricultural Source |
| :--- | :---: | :--- | :---: | :--- |
| `GENERIC_NON_CROP_OR_BACKGROUND` | G | Non-Crop Subject (Weed / Soil / Hand / Machinery)<br>పంట కానిది / నేపధ్యం<br>गैर-फसल विषय | `AUTHORITATIVE_SOURCE_VERIFIED` | KisanVision Safety Guardrail |
