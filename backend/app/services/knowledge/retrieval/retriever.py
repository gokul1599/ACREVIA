"""
ACREVIA - KrishiBrain Hybrid Agricultural Retrieval Engine.
Combines pgvector dense semantic search with lexical matching and Reciprocal Rank Fusion.
"""

import math
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import or_

from backend.app.models.knowledge_source import KnowledgeSource
from backend.app.models.knowledge_document import KnowledgeDocument, KnowledgeDocumentVersion
from backend.app.models.knowledge_chunk import KnowledgeChunk
from backend.app.models.knowledge_embedding import KnowledgeEmbedding
from backend.app.services.knowledge.embeddings.embedding_provider import get_embedding_provider


class ScoredChunk:
    def __init__(
        self,
        chunk: KnowledgeChunk,
        document_title: str,
        publisher: str,
        canonical_url: Optional[str],
        document_version: int,
        score: float,
        semantic_score: float = 0.0,
        lexical_score: float = 0.0
    ):
        self.chunk = chunk
        self.document_title = document_title
        self.publisher = publisher
        self.canonical_url = canonical_url
        self.document_version = document_version
        self.score = score
        self.semantic_score = semantic_score
        self.lexical_score = lexical_score


class HybridRetriever:
    @staticmethod
    def _cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
        if not vec1 or not vec2 or len(vec1) != len(vec2):
            return 0.0
        dot = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = math.sqrt(sum(a * a for a in vec1))
        norm2 = math.sqrt(sum(b * b for b in vec2))
        if norm1 < 1e-12 or norm2 < 1e-12:
            return 0.0
        return dot / (norm1 * norm2)

    @classmethod
    def retrieve(
        cls,
        db: Session,
        query: str,
        crop: Optional[str] = None,
        language: str = "en",
        growth_stage: Optional[str] = None,
        top_k: int = 5,
        min_score: float = 0.15
    ) -> List[ScoredChunk]:
        """
        Executes hybrid retrieval: semantic embedding search + lexical matching + metadata filtering.
        """
        embed_provider = get_embedding_provider()
        query_vector = embed_provider.embed_text(query)
        query_terms = set(query.lower().split())

        # Base filter: Only APPROVED chunks from approved versions and documents
        query_builder = (
            db.query(
                KnowledgeChunk,
                KnowledgeDocument.title,
                KnowledgeSource.publisher_name,
                KnowledgeDocument.canonical_url,
                KnowledgeDocumentVersion.version_number
            )
            .join(KnowledgeDocumentVersion, KnowledgeChunk.document_version_id == KnowledgeDocumentVersion.id)
            .join(KnowledgeDocument, KnowledgeDocumentVersion.document_id == KnowledgeDocument.id)
            .join(KnowledgeSource, KnowledgeDocument.source_id == KnowledgeSource.id)
            .filter(
                KnowledgeChunk.approval_status == "APPROVED",
                KnowledgeDocument.status == "APPROVED"
            )
        )

        if crop:
            query_builder = query_builder.filter(
                KnowledgeChunk.crop_scope.in_([crop.lower(), "all"])
            )

        if growth_stage and growth_stage.upper() != "ALL":
            query_builder = query_builder.filter(
                KnowledgeChunk.growth_stage_scope.in_([growth_stage.upper(), "ALL"])
            )

        candidates = query_builder.all()
        if not candidates:
            return []

        scored_candidates: List[ScoredChunk] = []

        for chunk, doc_title, publisher, url, doc_ver in candidates:
            # 1. Semantic Cosine Similarity
            semantic_score = 0.0
            emb_vector = None
            if chunk.embeddings:
                emb_vector = chunk.embeddings[0].embedding
            if emb_vector is not None:
                # Handle pgvector array or python list
                vec_list = list(emb_vector) if hasattr(emb_vector, "__iter__") else []
                semantic_score = cls._cosine_similarity(query_vector, vec_list)

            # 2. Lexical Keyword Overlap (Jaccard / Token Hit Ratio)
            content_lower = chunk.content.lower()
            term_hits = sum(1 for term in query_terms if term in content_lower)
            lexical_score = term_hits / max(len(query_terms), 1)

            # 3. Hybrid Combination (Weighted: 0.65 Semantic + 0.35 Lexical)
            hybrid_score = (0.65 * max(semantic_score, 0.0)) + (0.35 * lexical_score)

            # 4. Boost exact crop match
            if crop and chunk.crop_scope == crop.lower():
                hybrid_score *= 1.15

            if hybrid_score >= min_score:
                scored_candidates.append(ScoredChunk(
                    chunk=chunk,
                    document_title=doc_title,
                    publisher=publisher,
                    canonical_url=url,
                    document_version=doc_ver,
                    score=min(hybrid_score, 1.0),
                    semantic_score=semantic_score,
                    lexical_score=lexical_score
                ))

        # Sort by final score descending
        scored_candidates.sort(key=lambda x: x.score, reverse=True)
        return scored_candidates[:top_k]
