"""
ACREVIA - Agricultural Knowledge Graph REST API.
Provides typed domain entities, causal & agronomic relationships,
and multi-hop graph traversal.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import select

from backend.app.database.session import get_db
from backend.app.models.user import User
from backend.app.models.knowledge_graph import KnowledgeEntity
from backend.app.schemas.knowledge_graph import (
    KnowledgeEntityResponse,
    KnowledgeEntityCreate,
    KnowledgeRelationshipCreate,
    KnowledgeTraversalResponse,
    KnowledgeTraversalHop
)
from backend.app.security.dependencies import get_current_user
from backend.app.services.knowledge_graph_service import KnowledgeGraphService

router = APIRouter(prefix="/knowledge-graph", tags=["Knowledge Graph"])


@router.get("/entities", response_model=List[KnowledgeEntityResponse])
def list_entities(
    entity_type: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Lists knowledge graph entities with optional type filtering."""
    stmt = select(KnowledgeEntity)
    if entity_type:
        stmt = stmt.where(KnowledgeEntity.entity_type == entity_type.upper())
    stmt = stmt.limit(limit)

    entities = list(db.execute(stmt).scalars().all())
    return [
        KnowledgeEntityResponse(
            id=e.id,
            entity_type=e.entity_type,
            canonical_name=e.canonical_name,
            local_name_te=e.local_name_te,
            local_name_hi=e.local_name_hi,
            scientific_name=e.scientific_name,
            properties=e.properties_json
        )
        for e in entities
    ]


@router.post("/entities", response_model=KnowledgeEntityResponse, status_code=status.HTTP_201_CREATED)
def create_entity(
    payload: KnowledgeEntityCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Registers a new typed entity in the knowledge graph."""
    entity = KnowledgeGraphService.create_entity(
        db=db,
        entity_type=payload.entity_type,
        canonical_name=payload.canonical_name,
        local_name_te=payload.local_name_te,
        local_name_hi=payload.local_name_hi,
        scientific_name=payload.scientific_name,
        properties=payload.properties
    )
    return KnowledgeEntityResponse(
        id=entity.id,
        entity_type=entity.entity_type,
        canonical_name=entity.canonical_name,
        local_name_te=entity.local_name_te,
        local_name_hi=entity.local_name_hi,
        scientific_name=entity.scientific_name,
        properties=entity.properties_json
    )


@router.post("/relationships", status_code=status.HTTP_201_CREATED)
def create_relationship(
    payload: KnowledgeRelationshipCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Creates a typed relational edge between two knowledge entities."""
    rel = KnowledgeGraphService.create_relationship(
        db=db,
        source_id=payload.source_entity_id,
        target_id=payload.target_entity_id,
        relationship_type=payload.relationship_type,
        confidence_weight=payload.confidence_weight,
        evidence_source=payload.evidence_source,
        properties=payload.properties
    )
    return {
        "status": "CREATED",
        "relationship_id": rel.id,
        "relationship_type": rel.relationship_type
    }


@router.get("/traverse", response_model=KnowledgeTraversalResponse)
def traverse_knowledge_graph(
    entity: str = Query(..., min_length=2, description="Entity canonical name or UUID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Performs multi-hop relational expansion starting from an entity."""
    traversal = KnowledgeGraphService.traverse_entity_hops(db=db, entity_name_or_id=entity)
    return KnowledgeTraversalResponse(
        root_entity=KnowledgeEntityResponse(**traversal["root_entity"]),
        hops=[
            KnowledgeTraversalHop(
                relationship_type=h["relationship_type"],
                confidence_weight=h["confidence_weight"],
                evidence_source=h["evidence_source"],
                target_entity=KnowledgeEntityResponse(**h["target_entity"])
            )
            for h in traversal["hops"]
        ]
    )
