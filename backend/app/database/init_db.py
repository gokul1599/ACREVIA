"""
ACREVIA - Database Initialization & Seed Scripts.
Ensures core roles, supported crops, and evidence-grounded risk rules are present upon deployment.
"""

from typing import Optional
from sqlalchemy.orm import Session
from backend.app.database.base import Base
from backend.app.database.session import engine as default_engine, SessionLocal as default_session_factory
from backend.app.models.user import Role
from backend.app.models.crop import Crop
from backend.app.models.risk_rule import RiskRule


def _seed_data(session: Session):
    """Seeds baseline roles, target crops, and PJTSAU risk rules if not present."""
    # 1. Seed System Roles
    roles_data = [
        ("FARMER", "Smallholder farmer or cultivator managing farms and plots"),
        ("AGRICULTURAL_EXPERT", "KVK or university agronomist reviewing foliar diagnoses"),
        ("RESEARCHER", "Agricultural research scientist studying pathology patterns"),
        ("ADMIN", "Platform administrator managing system security and operations")
    ]
    for role_id, desc in roles_data:
        existing = session.get(Role, role_id)
        if not existing:
            session.add(Role(id=role_id, description=desc))

    # 2. Seed Telangana Target Crops
    crops_data = [
        ("cotton", "Cotton", "పత్తి", "कपास", "Gossypium hirsutum"),
        ("rice", "Rice / Paddy", "వరి", "चावल / धान", "Oryza sativa"),
        ("chilli", "Chilli", "మిరప", "मिर्च", "Capsicum annuum")
    ]
    for cid, en, te, hi, sci in crops_data:
        existing = session.get(Crop, cid)
        if not existing:
            session.add(Crop(
                id=cid,
                name_en=en,
                name_te=te,
                name_hi=hi,
                scientific_name=sci
            ))

    # 3. Seed Agronomic Risk Rules (PJTSAU / ICAR Provenance)
    rules_data = [
        {
            "rule_code": "RIC-BLST-01",
            "crop": "rice",
            "target_threat": "Rice Blast (Pyricularia oryzae)",
            "applicable_growth_stages": "Tillering,Panicle Initiation,Flowering",
            "min_temp": 20.0,
            "max_temp": 28.0,
            "min_humidity": 88.0,
            "min_leaf_wetness_hours": 8.0,
            "min_consecutive_wet_days": 2,
            "severity_level": "HIGH",
            "advisory_en": "High atmospheric humidity and prolonged leaf wetness elevate Rice Blast risk. Inspect lower leaf collars for spindle-shaped lesions with grey centers. Avoid excessive nitrogen fertilizer.",
            "advisory_te": "అధిక తేమ మరియు ఆకులపై ఎక్కువసేపు నీటి నిల్వ కారణంగా వరి అగ్గితెగులు ప్రమాదం ఎక్కువ. నత్రజని ఎరువుల అధిక వాడకాన్ని నివారించండి.",
            "advisory_hi": "उच्च आर्द्रता और पत्तियों पर नमी के कारण धान में ब्लास्ट रोग का जोखिम अधिक है। नाइट्रोजन उर्वरकों के अत्यधिक उपयोग से बचें।",
            "evidence_citations_json": '["PJTSAU Rice Diagnostic Bulletin (2022)", "ICAR-IIRR Hyderabad Blast Surveillance"]',
            "version": "1.0",
        },
        {
            "rule_code": "RIC-SHBL-01",
            "crop": "rice",
            "target_threat": "Sheath Blight (Rhizoctonia solani)",
            "applicable_growth_stages": "Tillering,Maximum Tillering,Heading",
            "min_temp": 28.0,
            "max_temp": 35.0,
            "min_humidity": 85.0,
            "min_leaf_wetness_hours": 6.0,
            "min_consecutive_wet_days": 1,
            "severity_level": "HIGH",
            "advisory_en": "Warm temperatures with high humidity promote Sheath Blight development near water level. Maintain field aeration and avoid deep standing water.",
            "advisory_te": "వేడి వాతావరణం మరియు అధిక తేమ వల్ల పొడ తెగులు ఆశించే అవకాశం ఉంది. పొలంలో మురుగు నీరు నిల్వ ఉండకుండా చూసుకోండి.",
            "advisory_hi": "गर्म तापमान और उच्च आर्द्रता शीथ ब्लाइट को बढ़ावा देती है। खेत में जलभराव न होने दें।",
            "evidence_citations_json": '["PJTSAU Plant Pathology Compendium", "ICAR-NRRI Cuttack Guidelines"]',
            "version": "1.0",
        },
        {
            "rule_code": "COT-CLSP-01",
            "crop": "cotton",
            "target_threat": "Cercospora Leaf Spot (Cercospora gossypina)",
            "applicable_growth_stages": "Vegetative,Squaring,Boll Formation",
            "min_temp": 24.0,
            "max_temp": 32.0,
            "min_humidity": 80.0,
            "min_leaf_wetness_hours": 6.0,
            "min_consecutive_wet_days": 2,
            "severity_level": "HIGH",
            "advisory_en": "Humid spells and moderate temperatures favor fungal leaf spots. Monitor lower canopy for circular brown spots with purple margins. Practice clean cultivation.",
            "advisory_te": "తేమతో కూడిన వాతావరణం వల్ల పత్తిలో ఆకుమచ్చ తెగులు వ్యాప్తి చెందే అవకాశం ఉంది. కింద ఆకులను గమనించి తగు నివారణ చర్యలు చేపట్టండి.",
            "advisory_hi": "आर्द्र मौसम कपास में पत्ती धब्बा रोग के अनुकूल है। निचली पत्तियों का नियमित निरीक्षण करें।",
            "evidence_citations_json": '["PJTSAU Cotton Advisory (2023)", "ICAR-CICR Nagpur Bulletin"]',
            "version": "1.0",
        },
        {
            "rule_code": "COT-BLW-01",
            "crop": "cotton",
            "target_threat": "Bollworm Complex (Helicoverpa armigera / Pectinophora)",
            "applicable_growth_stages": "Squaring,Flowering,Boll Formation",
            "min_temp": 25.0,
            "max_temp": 35.0,
            "min_humidity": 65.0,
            "min_leaf_wetness_hours": 2.0,
            "min_consecutive_wet_days": 1,
            "severity_level": "MODERATE",
            "advisory_en": "Warm humid conditions favor bollworm egg hatching and larval activity. Install pheromone traps (5/acre) to monitor adult moth catches. Check squares for flared bracts.",
            "advisory_te": "వేడి మరియు తేమ వల్ల శనగపచ్చ పురుగు, గులాబీ రంగు పురుగుల బెడద రావచ్చు. ఎకరానికి 5 లింగాకర్షక బుట్టలను అమర్చండి.",
            "advisory_hi": "गर्म और आर्द्र मौसम सुंडी के प्रकोप के अनुकूल है। फेरोमोन ट्रैप लगाएं और निगरानी रखें।",
            "evidence_citations_json": '["ICAR-CICR Cotton IPM Manual", "PJTSAU ETL Protocols"]',
            "version": "1.0",
        },
        {
            "rule_code": "CHL-ANTH-01",
            "crop": "chilli",
            "target_threat": "Anthracnose / Fruit Rot (Colletotrichum capsici)",
            "applicable_growth_stages": "Flowering,Fruit Set,Fruit Ripening",
            "min_temp": 26.0,
            "max_temp": 32.0,
            "min_humidity": 80.0,
            "min_leaf_wetness_hours": 8.0,
            "min_consecutive_wet_days": 2,
            "severity_level": "HIGH",
            "advisory_en": "High relative humidity and wet canopy predispose chilli fruits to circular sunken rot lesions. Rogue out infected fruits and avoid overhead irrigation during humid afternoons.",
            "advisory_te": "అధిక తేమ వల్ల మిరపలో కాయకుళ్ళు / ఆంత్రక్నోస్ తెగులు ఆశించే ప్రమాదం ఉంది. తెగులు సోకిన కాయలను ఏరి నాశనం చేయండి.",
            "advisory_hi": "उच्च आर्द्रता से मिर्च में फल सड़न (एंथ्रेक्नोज) का खतरा बढ़ जाता है। संक्रमित फलों को नष्ट करें।",
            "evidence_citations_json": '["PJTSAU Chilli Package of Practices", "ICAR-IIHR Bangalore Compendium"]',
            "version": "1.0",
        },
        {
            "rule_code": "CHL-THRP-01",
            "crop": "chilli",
            "target_threat": "Chilli Thrips & Murda Leaf Curl (Scirtothrips dorsalis)",
            "applicable_growth_stages": "Nursery,Vegetative,Flowering",
            "min_temp": 28.0,
            "max_temp": 36.0,
            "min_humidity": 40.0,
            "min_leaf_wetness_hours": 0.0,
            "min_consecutive_wet_days": 0,
            "severity_level": "HIGH",
            "advisory_en": "Dry atmospheric weather with warm temperatures accelerates Thrips breeding, causing upward leaf curling. Install blue sticky traps (10/acre) and spray Neem oil (5ml/L) as a preventive measure.",
            "advisory_te": "పొడి వాతావరణం వల్ల మిరపలో తామర పురుగుల ఉధృతి పెరిగి ఆకు ముడుత వస్తుంది. ఎకరానికి 10 నీలిరంగు జిగురు అట్టలను ఏర్పాటు చేయండి.",
            "advisory_hi": "शुष्क और गर्म मौसम में थ्रिप्स का प्रकोप बढ़ता है जिससे पत्तियां मुड़ जाती हैं। नीले चिपचिपे ट्रैप लगाएं।",
            "evidence_citations_json": '["PJTSAU Integrated Pest Management Guidelines", "ICAR-IIHR Murda Vector Control"]',
            "version": "1.0",
        }
    ]

    for r in rules_data:
        existing = session.query(RiskRule).filter_by(rule_code=r["rule_code"]).first()
        if not existing:
            session.add(RiskRule(**r))

    session.commit()


def init_db(engine_or_session=None, session_factory=None):
    """Creates tables if not existing and seeds baseline roles, crops, and risk rules."""
    if isinstance(engine_or_session, Session):
        _seed_data(engine_or_session)
    else:
        eng = engine_or_session or default_engine
        Base.metadata.create_all(bind=eng)
        factory = session_factory or default_session_factory
        with factory() as session:
            _seed_data(session)
