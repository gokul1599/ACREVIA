"""
ACREVIA - Agricultural Knowledge Graph Service.
Manages domain entities, causal/agronomic relationships, seeds initial Telangana
taxonomies, and executes multi-hop relational graph traversals for KrishiBrain RAG.
"""

from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, and_

from backend.app.models.knowledge_graph import KnowledgeEntity, KnowledgeRelationship
from backend.app.core.exceptions import NotFoundError, ValidationError


class KnowledgeGraphService:
    @staticmethod
    def create_entity(
        db: Session,
        entity_type: str,
        canonical_name: str,
        local_name_te: Optional[str] = None,
        local_name_hi: Optional[str] = None,
        scientific_name: Optional[str] = None,
        properties: Optional[Dict[str, Any]] = None
    ) -> KnowledgeEntity:
        """Registers a typed entity in the knowledge graph."""
        entity = KnowledgeEntity(
            entity_type=entity_type.upper(),
            canonical_name=canonical_name,
            local_name_te=local_name_te,
            local_name_hi=local_name_hi,
            scientific_name=scientific_name,
            properties_json=properties or {}
        )
        db.add(entity)
        db.commit()
        db.refresh(entity)
        return entity

    @staticmethod
    def create_relationship(
        db: Session,
        source_id: str,
        target_id: str,
        relationship_type: str,
        confidence_weight: float = 1.0,
        evidence_source: str = "PJTSAU Package of Practices",
        properties: Optional[Dict[str, Any]] = None
    ) -> KnowledgeRelationship:
        """Creates a directional relationship edge between two entities."""
        source = db.get(KnowledgeEntity, source_id)
        target = db.get(KnowledgeEntity, target_id)
        if not source or not target:
            raise NotFoundError("Source or target entity not found.")

        rel = KnowledgeRelationship(
            source_entity_id=source_id,
            target_entity_id=target_id,
            relationship_type=relationship_type.upper(),
            confidence_weight=confidence_weight,
            evidence_source=evidence_source,
            properties_json=properties or {}
        )
        db.add(rel)
        db.commit()
        db.refresh(rel)
        return rel

    @staticmethod
    def traverse_entity_hops(db: Session, entity_name_or_id: str) -> Dict[str, Any]:
        """Performs multi-hop relational expansion starting from an entity."""
        # Find root entity by id or canonical name
        root = db.get(KnowledgeEntity, entity_name_or_id)
        if not root:
            root = db.execute(
                select(KnowledgeEntity).where(KnowledgeEntity.canonical_name == entity_name_or_id)
            ).scalar_one_or_none()

        if not root:
            raise NotFoundError(f"Entity '{entity_name_or_id}' not found in knowledge graph.")

        # Query outbound edges
        outbound = db.execute(
            select(KnowledgeRelationship, KnowledgeEntity)
            .join(KnowledgeEntity, KnowledgeRelationship.target_entity_id == KnowledgeEntity.id)
            .where(KnowledgeRelationship.source_entity_id == root.id)
        ).all()

        hops = []
        for rel, target in outbound:
            hops.append({
                "relationship_type": rel.relationship_type,
                "confidence_weight": rel.confidence_weight,
                "evidence_source": rel.evidence_source,
                "target_entity": {
                    "id": target.id,
                    "entity_type": target.entity_type,
                    "canonical_name": target.canonical_name,
                    "local_name_te": target.local_name_te,
                    "local_name_hi": target.local_name_hi,
                    "scientific_name": target.scientific_name,
                    "properties": target.properties_json
                }
            })

        return {
            "root_entity": {
                "id": root.id,
                "entity_type": root.entity_type,
                "canonical_name": root.canonical_name,
                "local_name_te": root.local_name_te,
                "local_name_hi": root.local_name_hi,
                "scientific_name": root.scientific_name,
                "properties": root.properties_json
            },
            "hops": hops
        }

    @staticmethod
    def seed_initial_knowledge_graph(db: Session) -> None:
        """Seeds base agronomic ontology for Telangana priority crops."""
        existing = db.execute(select(KnowledgeEntity)).first()
        if existing:
            return  # Already seeded

        # Crops
        rice = KnowledgeGraphService.create_entity(
            db, "CROP", "Rice", "వరి", "चावल", "Oryza sativa", {"water_requirement": "High"}
        )
        cotton = KnowledgeGraphService.create_entity(
            db, "CROP", "Cotton", "ప్రత్తి", "कपास", "Gossypium hirsutum", {"soil_preference": "Black Cotton"}
        )
        chilli = KnowledgeGraphService.create_entity(
            db, "CROP", "Chilli", "మిరప", "मिर्च", "Capsicum annuum", {"susceptibility": "Anthracnose"}
        )

        # Diseases & Pests
        rice_blast = KnowledgeGraphService.create_entity(
            db, "DISEASE", "Rice Blast", "అగ్గి తెగులు", "झुलसा रोग", "Magnaporthe oryzae"
        )
        pink_bollworm = KnowledgeGraphService.create_entity(
            db, "PEST", "Pink Bollworm", "గులాబీ రంగు కాయ తొలుచు పురుగు", "गुलाबी सुंडी", "Pectinophora gossypiella"
        )
        anthracnose = KnowledgeGraphService.create_entity(
            db, "DISEASE", "Chilli Anthracnose", "కొమ్మ ఎండు / కాయ కుళ్లు తెగులు", "फल सड़न रोग", "Colletotrichum capsici"
        )

        # Weather Conditions
        high_humidity = KnowledgeGraphService.create_entity(
            db, "WEATHER_CONDITION", "High Relative Humidity (>85%)", "అధిక గాలి తేమ", "अधिक आर्द्रता"
        )
        leaf_wetness = KnowledgeGraphService.create_entity(
            db, "WEATHER_CONDITION", "Prolonged Leaf Wetness (>10 hrs)", "ఆకులపై ఎక్కువ సమయం తేమ", "पत्तियों पर नमी"
        )

        # Agronomic Practices
        tricyclazole = KnowledgeGraphService.create_entity(
            db, "AGRONOMIC_PRACTICE", "Tricyclazole 75% WP Spray", "ట్రైసైక్లాజోల్ పిచికారీ", "ट्राइसाइक्लाजोल छिड़काव"
        )
        pheromone_trap = KnowledgeGraphService.create_entity(
            db, "AGRONOMIC_PRACTICE", "Pheromone Trap Installation", "లింగాకర్షక బుట్టలు", "फेरोमोन ट्रैप"
        )
        propiconazole = KnowledgeGraphService.create_entity(
            db, "AGRONOMIC_PRACTICE", "Propiconazole 25% EC Application", "ప్రొపికొనజోల్ పిచికారీ", "प्रोपिकोनाजोल"
        )

        # Relationships
        # Rice -> Rice Blast -> High Humidity -> Tricyclazole
        KnowledgeGraphService.create_relationship(db, rice_blast.id, rice.id, "AFFECTS_CROP")
        KnowledgeGraphService.create_relationship(db, rice_blast.id, high_humidity.id, "FAVORED_BY_CONDITION")
        KnowledgeGraphService.create_relationship(db, rice_blast.id, leaf_wetness.id, "FAVORED_BY_CONDITION")
        KnowledgeGraphService.create_relationship(db, rice_blast.id, tricyclazole.id, "SUPPRESSED_BY_PRACTICE")

        # Cotton -> Pink Bollworm -> Pheromone Trap
        KnowledgeGraphService.create_relationship(db, pink_bollworm.id, cotton.id, "AFFECTS_CROP")
        KnowledgeGraphService.create_relationship(db, pink_bollworm.id, pheromone_trap.id, "SUPPRESSED_BY_PRACTICE")

        # Chilli -> Anthracnose -> High Humidity -> Propiconazole
        KnowledgeGraphService.create_relationship(db, anthracnose.id, chilli.id, "AFFECTS_CROP")
        KnowledgeGraphService.create_relationship(db, anthracnose.id, high_humidity.id, "FAVORED_BY_CONDITION")
        KnowledgeGraphService.create_relationship(db, anthracnose.id, propiconazole.id, "SUPPRESSED_BY_PRACTICE")
