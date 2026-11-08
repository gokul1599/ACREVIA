# STAGE 02 — 28-CLASS AGRICULTURAL TAXONOMY AUDIT
## Canonical Class Register, Botanical Descriptions, Symptom Ambiguities & Boundary Definitions

**Stage:** 02 — Agricultural Dataset Engineering & Taxonomy Validation  
**Taxonomy Version:** `1.0.0`  
**Target Crops:** Cotton (*Gossypium hirsutum*), Rice (*Oryza sativa*), Chilli (*Capsicum annuum*)  
**Status:** Approved Canonical Taxonomy  

---

### 1. Canonical Taxonomy Register (All 28 Classes)

#### A. Cotton (*Gossypium hirsutum* / పత్తి / कपास) — 10 Classes

| Class ID | Category | Canonical Name | Trilingual Display Names | Scientific Agent | Distinguishing Symptoms | Agricultural Reference | Requires Expert Review |
|---|---|---|---|---|---|---|---|
| `COTTON_HEALTHY` | Healthy | Healthy Cotton Foliage | EN: Healthy Cotton Foliage<br>TE: ఆరోగ్యకరమైన పత్తి ఆకు<br>HI: स्वस्थ कपास का पत्ता | None | Vibrant green lamina with intact veins, absence of necrotic lesions, chlorosis, or insect chewing. | PJTSAU Cotton Production Guide | No |
| `COTTON_BACTERIAL_BLIGHT` | Disease | Bacterial Blight / Angular Leaf Spot | EN: Bacterial Blight<br>TE: బాక్టీరియా ఆకుమచ్చ తెగులు<br>HI: जीवाणु झुलसा | *Xanthomonas citri* pv. *malvacearum* | Small, angular water-soaked lesions bounded by veinlets, turning dark reddish-brown to black. | ICAR-CICR Technical Bulletin 24 | No |
| `COTTON_GREY_MILDEW` | Disease | Grey / Areolate Mildew | EN: Grey Mildew<br>TE: బూజు తెగులు<br>HI: धूसर फफूंद | *Ramularia areola* | Angular pale translucent spots on upper surface with distinct powdery whitish growth on leaf underside. | PJTSAU Vyavasaya Panchangam | No |
| `COTTON_ALTERNARIA_SPOT` | Disease | Alternaria Leaf Spot | EN: Alternaria Leaf Spot<br>TE: ఆల్టర్నేరియా ఆకుమచ్చ<br>HI: अल्टरनेरिया पत्ती धब्बा | *Alternaria macrospora* | Circular brown necrotic lesions with distinct target-like concentric rings (concentric zonation). | ICAR-CICR Disease Manual | No |
| `COTTON_LEAF_CURL_VIRUS` | Disease | Cotton Leaf Curl Virus (CLCuD) | EN: Leaf Curl Virus<br>TE: ఆకు ముడత వైరస్<br>HI: पत्ती मोड़ विषाणु | Begomovirus (CLCuD) | Upward leaf curling, thickened green veins on abaxial surface, enations (leaf-like outgrowths). | ICAR-CICR Annual Report | Yes |
| `COTTON_PINK_BOLLWORM` | Pest | Pink Bollworm Damage | EN: Pink Bollworm Damage<br>TE: గులాబీ రంగు పురుగు నష్టం<br>HI: गुलाबी सुंडी क्षति | *Pectinophora gossypiella* | Rosetted flowers, entry pinholes in green bolls with frass packing, internal lint staining. | ICAR-CICR PBW Protocol | No |
| `COTTON_JASSID_DAMAGE` | Pest | Leafhopper / Jassid Hopperburn | EN: Jassid Hopper Burn<br>TE: పచ్చ దోమ నష్టం<br>HI: हरा फुदका क्षति | *Amrasca biguttula biguttula* | Downward curling of leaf margins, yellowing turning brick-red necrosis (hopper burn). | PJTSAU Pest Management Guide | No |
| `COTTON_POTASSIUM_DEF` | Nutrient | Potassium Deficiency | EN: Potassium Deficiency<br>TE: పొటాషియం లోపం<br>HI: पोटैशियम की कमी | Potassium ($K^+$) deficit | Interveinal chlorosis on older leaves with marginal yellowing advancing to bronze necrosis. | ICAR Soil Science Division | Yes |
| `COTTON_LEAF_REDDENING` | Abiotic | Physiological Leaf Reddening | EN: Physiological Leaf Reddening<br>TE: పత్తి ఆకులు ఎర్రబడటం<br>HI: पत्तियों का लाल होना | Anthocyanin accumulation | Uniform bronze to dark red pigmentation triggered by sudden cold night temperatures and soil saturation. | PJTSAU Agronomy Advisory | Yes |
| `COTTON_UNKNOWN_CONDITION`| Unknown | Undetermined Foliar Anomaly | EN: Undetermined Anomaly<br>TE: నిర్ధారించబడని పత్తి సమస్య<br>HI: अनिर्धारित लक्षण | Undetermined | Atypical foliar lesion or stress symptom requiring expert agronomist review. | ACREVIA Safety Standard | Yes |

---

#### B. Rice (*Oryza sativa* / వరి / धान) — 10 Classes

| Class ID | Category | Canonical Name | Trilingual Display Names | Scientific Agent | Distinguishing Symptoms | Agricultural Reference | Requires Expert Review |
|---|---|---|---|---|---|---|---|
| `RICE_HEALTHY` | Healthy | Healthy Rice Foliage | EN: Healthy Rice Foliage<br>TE: ఆరోగ్యకరమైన వరి ఆకు<br>HI: स्वस्थ धान का पत्ता | None | Uniform emerald green leaf blade without spots, stripes, or tip drying. | ICAR-IIRR Hyderabad | No |
| `RICE_BLAST_LEAF` | Disease | Rice Leaf Blast | EN: Leaf Blast<br>TE: ఆకు అగ్గి తెగులు<br>HI: धान का पत्ती झुलसा | *Magnaporthe oryzae* | Spindle-shaped elliptical lesions with greyish-white center and distinct reddish-brown borders. | ICAR-IIRR Technical Bulletin 89 | No |
| `RICE_BACTERIAL_BLIGHT` | Disease | Bacterial Leaf Blight (BLB) | EN: Bacterial Leaf Blight<br>TE: బాక్టీరియా ఆకు ఎండు తెగులు<br>HI: जीवाणु पत्ती झुलसा | *Xanthomonas oryzae* pv. *oryzae* | Water-soaked yellowish-white wavy marginal stripes beginning at leaf tips and advancing downward. | ICAR-IIRR SES Guide | No |
| `RICE_SHEATH_BLIGHT` | Disease | Sheath Blight | EN: Sheath Blight<br>TE: వరి పొడ తెగులు<br>HI: शीथ ब्लाइट | *Rhizoctonia solani* | Oval or irregular greenish-grey water-soaked spots on leaf sheaths forming banded snake-skin pattern. | ICAR-IIRR Pathology Compendium | No |
| `RICE_BROWN_SPOT` | Disease | Brown Spot | EN: Brown Spot<br>TE: గోధుమ రంగు మచ్చ తెగులు<br>HI: भूरा धब्बा रोग | *Bipolaris oryzae* | Small oval to circular brown spots resembling sesame seeds with yellow chlorotic halos. | PJTSAU Rice Guide | No |
| `RICE_FALSE_SMUT` | Disease | False Smut | EN: False Smut<br>TE: కాటుక తెగులు<br>HI: झूठा कंडुआ | *Ustilaginoidea virens* | Individual grains transformed into velvety yellowish-green to greenish-black spore balls. | PJTSAU Rice Compendium | No |
| `RICE_STEM_BORER_DEADHEART`| Pest | Yellow Stem Borer (Dead Heart) | EN: Stem Borer (Dead Heart)<br>TE: కాండం తొలుచు పురుగు<br>HI: तना छेदक | *Scirpophaga incertulas* | Central vegetative shoot dries and turns brown (dead heart); white erect empty panicles at harvest. | ICAR-IIRR Entomology Handbook | No |
| `RICE_BPH_HOPPERBURN` | Pest | Brown Planthopper (BPH) | EN: BPH Hopper Burn<br>TE: సుడి దోమ నష్టం<br>HI: भूरा फुदका (हॉपर बर्न) | *Nilaparvata lugens* | Circular patches of dried, yellowish-brown lodged tillers starting at field center. | ICAR-IIRR BPH Protocol | Yes |
| `RICE_ZINC_DEFICIENCY` | Nutrient | Zinc Deficiency (Khaira) | EN: Zinc Deficiency (Khaira)<br>TE: జింక్ లోపం (ఖైరా తెగులు)<br>HI: जिंक की कमी (खैरा) | Zinc ($Zn$) deficit | Chlorosis at base of young leaves followed by rusty brown pigmentation and stunted uneven growth. | ICAR-IIRR Soil Science Division | Yes |
| `RICE_UNKNOWN_CONDITION` | Unknown | Undetermined Rice Anomaly | EN: Undetermined Anomaly<br>TE: నిర్ధారించబడని వరి సమస్య<br>HI: अनिर्धारित लक्षण | Undetermined | Atypical foliar lesion or stress symptom requiring expert agronomist review. | ACREVIA Safety Standard | Yes |

---

#### C. Chilli (*Capsicum annuum* / మిరప / मिर्च) — 8 Classes

| Class ID | Category | Canonical Name | Trilingual Display Names | Scientific Agent | Distinguishing Symptoms | Agricultural Reference | Requires Expert Review |
|---|---|---|---|---|---|---|---|
| `CHILLI_HEALTHY` | Healthy | Healthy Chilli Foliage | EN: Healthy Chilli Foliage<br>TE: ఆరోగ్యకరమైన మిరప ఆకు<br>HI: स्वस्थ मिर्च का पत्ता | None | Smooth, deep green leaf lamina with flat margins and absence of mottling, puckering, or rasping. | PJTSAU Horticultural Guide | No |
| `CHILLI_ANTHRACNOSE_FRUIT_ROT`| Disease | Anthracnose / Fruit Rot / Die-Back | EN: Anthracnose / Fruit Rot<br>TE: కొమ్మ ఎండు మరియు కాయ కుళ్ళు<br>HI: एंथ्रेक्नोज / फल सड़न | *Colletotrichum capsici* | Sunken circular necrotic spots on fruit with concentric rings of black acervuli; twig die-back from tips. | PJTSAU / ICAR-IIHR Bulletin | No |
| `CHILLI_LEAF_CURL_VIRUS` | Disease | Chilli Leaf Curl Virus (ChiLCV) | EN: Leaf Curl Virus<br>TE: బొబ్బర తెగులు / ఆకు ముడత<br>HI: मिर्च पर्ण कुंचन | Begomovirus (ChiLCV) | Severe puckering, thickened veins, upward leaf curling, crowding of leaves at apex, stunted bush. | PJTSAU Virology Division | Yes |
| `CHILLI_POWDERY_MILDEW` | Disease | Powdery Mildew | EN: Powdery Mildew<br>TE: బూడిద తెగులు<br>HI: चूर्णिल आसिता | *Leveillula taurica* | White powdery fungal patches on leaf underside with corresponding chlorotic yellow spots on top. | PJTSAU Horticultural Guide | No |
| `CHILLI_CERCOSPORA_SPOT` | Disease | Cercospora Leaf Spot (Frog-Eye) | EN: Cercospora (Frog-Eye)<br>TE: సర్కోస్పోరా ఆకుమచ్చ<br>HI: मेंढक-आंख धब्बा | *Cercospora capsici* | Circular lesions with light grey or bleached white centers and prominent dark brown borders. | ICAR-IIHR Pathology Compendium | No |
| `CHILLI_BLACK_THRIPS` | Pest | Invasive Black Thrips Damage | EN: Black Thrips Damage<br>TE: నల్ల తామర పురుగు నష్టం<br>HI: काली थ्रिप्स क्षति | *Thrips parvispinus* (Karny) | Upward boat-shaped leaf curling, rasping marks on flower petals and fruit, severe blossom drop. | ICAR-NBAIR / PJTSAU Alert | Yes |
| `CHILLI_YELLOW_MITE` | Pest | Yellow Mite Damage | EN: Yellow Mite (Downward Curl)<br>TE: నల్లి పురుగు నష్టం (ఎర్ర నల్లి)<br>HI: पीली माइट क्षति | *Polyphagotarsonemus latus* | Downward curling of margins (inverted boat shape), thick leathery brittle leaves, elongated petiole. | PJTSAU Pest Compendium | Yes |
| `CHILLI_UNKNOWN_CONDITION` | Unknown | Undetermined Chilli Anomaly | EN: Undetermined Anomaly<br>TE: నిర్ధారించబడని మిరప సమస్య<br>HI: अनिर्धारित लक्षण | Undetermined | Atypical foliar lesion or stress symptom requiring expert agronomist review. | ACREVIA Safety Standard | Yes |

---

### 2. Ambiguity Handling & Co-Occurrence Boundaries

1. **Cotton Leaf Reddening vs Jassid Damage vs Potassium Deficiency:**
   * *Differentiation:* Jassids cause marginal yellowing turning into brick-red necrosis accompanied by downward curling of leaf margins; physiological reddening causes uniform bronze-red discoloration triggered by cold temperatures without margin curling; potassium deficiency produces interveinal chlorosis on older leaves first.
   * *Resolution Policy:* When visual features are inconclusive, the model marks the sample as `AMBIGUOUS_MULTI_SYMPTOM` and routes it to `ExpertConnect`.
2. **Chilli Black Thrips vs Yellow Mite vs Leaf Curl Virus:**
   * *Differentiation:* Black Thrips produce upward boat-shaped leaf curling with petal rasping; Yellow Mites produce downward curling (inverted boat shape) with thick brittle leaves; Leaf Curl Virus causes severe enations, puckering, and bushy stunting.
   * *Resolution Policy:* Both Black Thrips and Yellow Mite damages are flagged with `requires_expert_review: true` to prevent improper chemical selection in rural Telangana.
