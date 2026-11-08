"""
ACREVIA - KrishiBrain Ingestion Pipeline Service.
Orchestrates document extraction, structure-aware chunking, vector embedding, and versioning.
"""

import hashlib
from typing import List, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from backend.app.models.user import User
from backend.app.models.knowledge_source import KnowledgeSource
from backend.app.models.knowledge_document import KnowledgeDocument, KnowledgeDocumentVersion
from backend.app.models.knowledge_chunk import KnowledgeChunk
from backend.app.models.knowledge_embedding import KnowledgeEmbedding
from backend.app.models.ingestion_job import IngestionJob
from backend.app.schemas.knowledge import (
    KnowledgeSourceCreateRequest,
    KnowledgeSourceUpdateRequest,
    KnowledgeDocumentCreateRequest,
)
from backend.app.services.knowledge.extraction.extractors import DocumentExtractor
from backend.app.services.knowledge.chunking.chunker import StructureAwareChunker
from backend.app.services.knowledge.embeddings.embedding_provider import get_embedding_provider
from backend.app.services.audit_service import AuditService
from backend.app.core.logging import logger


class IngestionService:
    @staticmethod
    def register_source(data: KnowledgeSourceCreateRequest, current_user: User, db: Session) -> KnowledgeSource:
        source = KnowledgeSource(
            publisher_name=data.publisher_name,
            publisher_type=data.publisher_type,
            official_domain=data.official_domain,
            authority_level=data.authority_level,
            licensing_status=data.licensing_status,
            approval_status="APPROVED"  # Auto-approved for seed/admin registrations
        )
        db.add(source)
        db.commit()
        db.refresh(source)

        AuditService.record_action(
            db=db,
            user_id=current_user.id,
            action="REGISTER_KNOWLEDGE_SOURCE",
            resource_type="KNOWLEDGE_SOURCE",
            resource_id=source.id,
            metadata={"publisher": source.publisher_name}
        )
        return source

    @staticmethod
    def update_source_status(
        source_id: str,
        data: KnowledgeSourceUpdateRequest,
        current_user: User,
        db: Session
    ) -> KnowledgeSource:
        source = db.get(KnowledgeSource, source_id)
        if not source:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Knowledge source not found.")

        if data.approval_status:
            source.approval_status = data.approval_status
            if data.approval_status == "APPROVED":
                source.reviewer_id = current_user.id
                source.approved_at = datetime.now(timezone.utc)
        if data.authority_level is not None:
            source.authority_level = data.authority_level
        if data.licensing_status is not None:
            source.licensing_status = data.licensing_status

        db.commit()
        db.refresh(source)
        return source

    @staticmethod
    def ingest_document(
        doc_data: KnowledgeDocumentCreateRequest,
        file_bytes: bytes,
        filename: str,
        current_user: User,
        db: Session
    ) -> IngestionJob:
        source = db.get(KnowledgeSource, doc_data.source_id)
        if not source:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Knowledge source not found.")

        # 1. Content hashing and document creation
        content_hash = hashlib.sha256(file_bytes).hexdigest()

        doc = KnowledgeDocument(
            source_id=source.id,
            title=doc_data.title,
            canonical_url=doc_data.canonical_url,
            document_type=doc_data.document_type,
            primary_language=doc_data.primary_language,
            crop_scope=doc_data.crop_scope,
            region_scope=doc_data.region_scope,
            topic_scope=doc_data.topic_scope,
            status=source.approval_status
        )
        db.add(doc)
        db.flush()

        doc_version = KnowledgeDocumentVersion(
            document_id=doc.id,
            version_number=1,
            content_hash=content_hash,
            original_file_path=filename,
            extraction_status="EXTRACTING",
            review_status=source.approval_status
        )
        db.add(doc_version)
        db.flush()

        doc.current_version_id = doc_version.id

        job = IngestionJob(
            document_id=doc.id,
            document_version_id=doc_version.id,
            status="PROCESSING",
            stage="EXTRACTING",
            progress_pct=10
        )
        db.add(job)
        db.commit()

        # 2. Extract sections
        try:
            sections = DocumentExtractor.extract(file_bytes, filename, doc_data.document_type)
            job.stage = "CHUNKING"
            job.progress_pct = 40
            db.commit()

            # 3. Chunk sections
            chunker = StructureAwareChunker(target_chunk_tokens=250, overlap_tokens=40)
            chunks_data = chunker.chunk_sections(sections)
            job.stage = "EMBEDDING"
            job.progress_pct = 70
            db.commit()

            # 4. Generate embeddings and persist chunks
            embed_provider = get_embedding_provider()
            for c_data in chunks_data:
                chunk_record = KnowledgeChunk(
                    document_version_id=doc_version.id,
                    chunk_index=c_data.chunk_index,
                    parent_section=c_data.parent_section,
                    heading_path=c_data.heading_path,
                    content=c_data.content,
                    language=doc_data.primary_language,
                    crop_scope=doc_data.crop_scope,
                    region_scope=doc_data.region_scope,
                    growth_stage_scope="ALL",
                    page_start=c_data.page_start,
                    page_end=c_data.page_end,
                    token_count=c_data.token_count,
                    content_hash=c_data.content_hash,
                    approval_status=source.approval_status
                )
                db.add(chunk_record)
                db.flush()

                # Generate vector
                vec = embed_provider.embed_text(c_data.content)
                emb_record = KnowledgeEmbedding(
                    chunk_id=chunk_record.id,
                    embedding_profile_id=embed_provider.profile_id,
                    embedding=vec,
                    model_name=embed_provider.profile_id,
                    model_version="1.0.0",
                    dimensions=embed_provider.dimensions
                )
                db.add(emb_record)

            doc_version.extraction_status = "EXTRACTED"
            job.status = "COMPLETED"
            job.stage = "PERSISTED"
            job.progress_pct = 100
            db.commit()
            db.refresh(job)

        except Exception as e:
            logger.error(f"Ingestion pipeline error for document {doc.id}: {e}")
            job.status = "FAILED"
            job.error_message = str(e)
            doc_version.extraction_status = "FAILED"
            db.commit()
            db.refresh(job)

        AuditService.record_action(
            db=db,
            user_id=current_user.id,
            action="INGEST_DOCUMENT",
            resource_type="KNOWLEDGE_DOCUMENT",
            resource_id=doc.id,
            metadata={"title": doc.title, "status": job.status}
        )
        return job

    @staticmethod
    def list_sources(db: Session, status_filter: Optional[str] = None) -> List[KnowledgeSource]:
        query = db.query(KnowledgeSource)
        if status_filter:
            query = query.filter(KnowledgeSource.approval_status == status_filter)
        return query.all()

    @staticmethod
    def list_documents(db: Session, crop: Optional[str] = None, status_filter: Optional[str] = None) -> List[KnowledgeDocument]:
        query = db.query(KnowledgeDocument)
        if crop:
            query = query.filter(KnowledgeDocument.crop_scope.in_([crop, "all"]))
        if status_filter:
            query = query.filter(KnowledgeDocument.status == status_filter)
        return query.all()

    @staticmethod
    def get_job_status(job_id: str, db: Session) -> IngestionJob:
        job = db.get(IngestionJob, job_id)
        if not job:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ingestion job not found.")
        return job
