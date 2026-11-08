"""
ACREVIA - Agricultural Knowledge Graph Pydantic Schemas.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, ConfigDict


class KnowledgeEntityResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    entity_type: str
    canonical_name: str
    local_name_te: Optional[str] = None
    local_name_hi: Optional[str] = None
    scientific_name: Optional[str] = None
    properties: Optional[Dict[str, Any]] = None


class KnowledgeTraversalHop(BaseModel):
    relationship_type: str
    confidence_weight: float
    evidence_source: str
    target_entity: KnowledgeEntityResponse


class KnowledgeTraversalResponse(BaseModel):
    root_entity: KnowledgeEntityResponse
    hops: List[KnowledgeTraversalHop]


class KnowledgeEntityCreate(BaseModel):
    entity_type: str
    canonical_name: str
    local_name_te: Optional[str] = None
    local_name_hi: Optional[str] = None
    scientific_name: Optional[str] = None
    properties: Optional[Dict[str, Any]] = None


class KnowledgeRelationshipCreate(BaseModel):
    source_entity_id: str
    target_entity_id: str
    relationship_type: str
    confidence_weight: float = 1.0
    evidence_source: str = "PJTSAU Package of Practices / ICAR Advisory"
    properties: Optional[Dict[str, Any]] = None
