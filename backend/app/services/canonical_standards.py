"""
ACREVIA - Canonical Agricultural Standards, Taxonomy & Unit Registry.
Stage 14: Canonical agricultural data dictionary, unit conversions, and multi-language crop taxonomies.
"""

from typing import Any, Dict, List, Optional, Tuple


class CanonicalStandardsService:
    """
    Provides deterministic unit conversions, crop taxonomy lookups,
    and schema validation rules conforming to ICAR and global AgGateway/OpenAg standards.
    """

    # Conversion tables relative to SI base unit of category
    CONVERSION_FACTORS: Dict[str, Dict[str, float]] = {
        "MASS": {
            "kg": 1.0,
            "gram": 0.001,
            "quintal": 100.0,
            "tonne": 1000.0,
            "pound": 0.45359237,
            "bag_75kg": 75.0,
            "bag_50kg": 50.0,
        },
        "AREA": {
            "ha": 1.0,
            "acre": 0.40468564224,
            "sq_meter": 0.0001,
            "gunta": 0.01011714105,  # 1/40th acre (Telangana / Andhra local standard)
        },
        "VOLUME": {
            "liter": 1.0,
            "ml": 0.001,
            "cubic_meter": 1000.0,
            "gallon_us": 3.78541,
        },
        "CONDUCTIVITY": {
            "ds_m": 1.0,      # deciSiemens/m
            "ms_cm": 1.0,     # milliSiemens/cm (1:1 with dS/m)
            "us_cm": 0.001,   # microSiemens/cm
        },
        "CONCENTRATION": {
            "ppm": 1.0,       # parts per million (mg/kg or mg/L)
            "mg_kg": 1.0,
            "mg_l": 1.0,
            "percent": 10000.0,  # 1% = 10,000 ppm
            "kg_ha": 1.0,     # agricultural soil test standard for available macronutrients
        },
        "RATE": {
            "kg_ha": 1.0,
            "quintal_acre": 247.105,  # 1 quintal/acre = 100 kg / 0.404686 ha = ~247.105 kg/ha
            "tonne_ha": 1000.0,
        }
    }

    CROP_TAXONOMY: Dict[str, Dict[str, Any]] = {
        "COTTON": {
            "standard_code": "COTTON",
            "botanical_name": "Gossypium hirsutum",
            "family": "Malvaceae",
            "names": {
                "en": "Cotton",
                "te": "ప్రత్తి (పత్తి)",
                "hi": "कपास"
            },
            "canonical_yield_unit": "quintal_acre",
            "varieties": [
                {"code": "RCH-659", "name": "RCH-659 BG II", "type": "Hybrid"},
                {"code": "MALLIKA", "name": "Mallika BG II", "type": "Hybrid"},
                {"code": "BHAKTI", "name": "Bhakti BG II", "type": "Hybrid"},
                {"code": "KAVERI_JAADOO", "name": "Kaveri Jaadoo", "type": "Hybrid"},
                {"code": "DESI_COTTON", "name": "G. arboreum Local", "type": "Desi Variety"}
            ],
            "optimal_soil_ph": {"min": 6.0, "max": 8.2},
            "salinity_threshold_ds_m": 7.7
        },
        "RICE": {
            "standard_code": "RICE",
            "botanical_name": "Oryza sativa",
            "family": "Poaceae",
            "names": {
                "en": "Rice / Paddy",
                "te": "వరి",
                "hi": "धान / चावल"
            },
            "canonical_yield_unit": "quintal_acre",
            "varieties": [
                {"code": "BPT-5204", "name": "Samba Mahsuri (BPT 5204)", "type": "Fine Grain"},
                {"code": "RNR-15048", "name": "Telangana Sona (RNR 15048 - Low GI)", "type": "Super Fine"},
                {"code": "MTU-1010", "name": "Cottondora Sannalu (MTU 1010)", "type": "Short Duration"},
                {"code": "KNM-118", "name": "Kunaram Sannalu (KNM 118)", "type": "High Yield"},
                {"code": "JGL-18047", "name": "Bathukamma (JGL 18047)", "type": "Medium Slender"}
            ],
            "optimal_soil_ph": {"min": 5.5, "max": 7.5},
            "salinity_threshold_ds_m": 3.0
        },
        "CHILLI": {
            "standard_code": "CHILLI",
            "botanical_name": "Capsicum annuum",
            "family": "Solanaceae",
            "names": {
                "en": "Chilli",
                "te": "మిరప",
                "hi": "मिर्च"
            },
            "canonical_yield_unit": "quintal_acre",
            "varieties": [
                {"code": "TEJA_S17", "name": "Teja (S17 Hot)", "type": "Pungent Export"},
                {"code": "GUNTUR_HOPE", "name": "Guntur Hope (LCA 334)", "type": "Dual Purpose"},
                {"code": "BYADGI", "name": "Byadgi (High Oleoresin)", "type": "Coloring / Export"},
                {"code": "ARMOOR", "name": "Armoor Local", "type": "Regional Selection"},
                {"code": "US-341", "name": "US-341 Hybrid", "type": "Commercial Hybrid"}
            ],
            "optimal_soil_ph": {"min": 6.5, "max": 7.8},
            "salinity_threshold_ds_m": 1.5
        }
    }

    CANONICAL_DATA_DICTIONARY: Dict[str, Dict[str, Any]] = {
        "soil_test": {
            "fields": {
                "ph": {"type": "float", "unit": "pH scale (0-14)", "required": True},
                "ec_ds_m": {"type": "float", "unit": "dS/m", "required": True},
                "organic_carbon_percent": {"type": "float", "unit": "%", "required": True},
                "nitrogen_kg_ha": {"type": "float", "unit": "kg/ha", "required": False},
                "phosphorus_kg_ha": {"type": "float", "unit": "kg/ha", "required": False},
                "potassium_kg_ha": {"type": "float", "unit": "kg/ha", "required": False},
                "zinc_ppm": {"type": "float", "unit": "ppm", "required": False},
                "boron_ppm": {"type": "float", "unit": "ppm", "required": False},
            }
        },
        "crop_observation": {
            "fields": {
                "crop_code": {"type": "string", "enum": ["COTTON", "RICE", "CHILLI"], "required": True},
                "growth_stage": {"type": "string", "required": True},
                "pest_or_disease_detected": {"type": "string", "required": False},
                "severity_score": {"type": "float", "min": 0.0, "max": 1.0, "required": False},
                "symptom_notes": {"type": "string", "required": False},
            }
        },
        "market_price": {
            "fields": {
                "market_name": {"type": "string", "required": True},
                "district": {"type": "string", "required": True},
                "commodity": {"type": "string", "required": True},
                "modal_price_inr_quintal": {"type": "float", "required": True},
                "arrival_tonnes": {"type": "float", "required": False},
                "price_date": {"type": "date_str", "required": True},
            }
        },
        "harvest_record": {
            "fields": {
                "crop_code": {"type": "string", "required": True},
                "quantity": {"type": "float", "required": True},
                "unit": {"type": "string", "required": True},
                "grade": {"type": "string", "required": False},
                "harvest_date": {"type": "date_str", "required": True},
            }
        }
    }

    @classmethod
    def convert_unit(cls, value: float, from_unit: str, to_unit: str, category: str = "MASS") -> Tuple[float, float]:
        """
        Converts value from one unit to another within the specified category.
        Returns: (converted_value, conversion_factor)
        """
        cat_key = category.upper()
        if cat_key not in cls.CONVERSION_FACTORS:
            raise ValueError(f"Unsupported measurement category: '{category}'. Valid: {list(cls.CONVERSION_FACTORS.keys())}")

        factors = cls.CONVERSION_FACTORS[cat_key]
        f_unit = from_unit.lower()
        t_unit = to_unit.lower()

        if f_unit not in factors:
            raise ValueError(f"Unknown from_unit '{from_unit}' for category '{cat_key}'. Valid: {list(factors.keys())}")
        if t_unit not in factors:
            raise ValueError(f"Unknown to_unit '{to_unit}' for category '{cat_key}'. Valid: {list(factors.keys())}")

        # Base conversion: value * (from_factor / to_factor)
        factor = factors[f_unit] / factors[t_unit]
        converted = value * factor
        return round(converted, 6), round(factor, 6)

    @classmethod
    def get_crop_taxonomy(cls, crop_code: Optional[str] = None) -> Any:
        """
        Returns full taxonomy for all crops or a specific crop code.
        """
        if crop_code:
            code_upper = crop_code.upper()
            if code_upper in cls.CROP_TAXONOMY:
                return cls.CROP_TAXONOMY[code_upper]
            # Match by English, Telugu, or Hindi name
            for k, data in cls.CROP_TAXONOMY.items():
                if any(code_upper in name.upper() for name in data["names"].values()):
                    return data
            raise ValueError(f"Crop code or name '{crop_code}' not found in canonical taxonomy")
        return cls.CROP_TAXONOMY

    @classmethod
    def validate_canonical_record(cls, entity_type: str, record: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validates an incoming record against the canonical data dictionary.
        Returns: (is_valid, list_of_errors)
        """
        entity_key = entity_type.lower()
        if entity_key not in cls.CANONICAL_DATA_DICTIONARY:
            return False, [f"Unknown entity type '{entity_type}'. Valid: {list(cls.CANONICAL_DATA_DICTIONARY.keys())}"]

        spec = cls.CANONICAL_DATA_DICTIONARY[entity_key]["fields"]
        errors: List[str] = []

        for field_name, field_spec in spec.items():
            if field_spec.get("required") and (field_name not in record or record[field_name] is None):
                errors.append(f"Missing required field: '{field_name}'")

        return len(errors) == 0, errors
