"""
ACREVIA - KrishiBrain Agricultural Knowledge Intelligence Endpoints.
"""

import time
from typing import List, Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.database.session import get_db
from backend.app.models.user import User
from backend.app.models.knowledge_feedback import KnowledgeFeedback
from backend.app.schemas.knowledge import (
    KnowledgeQueryRequest,
    KnowledgeQueryResponse,
    KnowledgeSourceCreateRequest,
    KnowledgeSourceUpdateRequest,
    KnowledgeSourceResponse,
    KnowledgeDocumentCreateRequest,
    KnowledgeDocumentResponse,
    IngestionJobResponse,
    KnowledgeFeedbackCreateRequest,
    KnowledgeFeedbackResponse,
)
from backend.app.security.dependencies import get_current_user, require_roles, verify_farm_access
from backend.app.security.permissions import SystemRole
from backend.app.services.knowledge.ingestion.ingestion_service import IngestionService
from backend.app.services.knowledge.retrieval.retriever import HybridRetriever
from backend.app.services.knowledge.generation.generator import KnowledgeGenerator
from backend.app.services.audit_service import AuditService

router = APIRouter(prefix="/knowledge", tags=["KrishiBrain Knowledge & RAG"])


# -----------------------------------------------------------------------------
# 1. Knowledge Query Endpoint
# -----------------------------------------------------------------------------
@router.post("/query", response_model=KnowledgeQueryResponse)
def query_knowledge(
    data: KnowledgeQueryRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Submits an agricultural knowledge query.
    Retrieves evidence from approved institutional documents and returns a grounded response with page-level citations.
    """
    start_time = time.perf_counter()

    # Validate optional farm context authorization
    if data.farm_id:
        verify_farm_access(farm_id=data.farm_id, user=current_user, db=db)

    # 1. Execute Hybrid Retrieval
    chunks = HybridRetriever.retrieve(
        db=db,
        query=data.question,
        crop=data.crop,
        language=data.language,
        growth_stage=data.growth_stage,
        top_k=5
    )

    # 2. Synthesize Grounded Response
    response = KnowledgeGenerator.generate_response(
        req=data,
        chunks=chunks,
        start_time=start_time
    )

    AuditService.record_action(
        db=db,
        user_id=current_user.id,
        farm_id=data.farm_id,
        action="KNOWLEDGE_QUERY",
        resource_type="KNOWLEDGE_QUERY",
        resource_id=response.query_id,
        metadata={"crop": data.crop, "status": response.answer_status}
    )
    return response


# -----------------------------------------------------------------------------
# 2. Source Governance Endpoints
# -----------------------------------------------------------------------------
@router.post("/sources", response_model=KnowledgeSourceResponse, status_code=status.HTTP_201_CREATED)
def register_knowledge_source(
    data: KnowledgeSourceCreateRequest,
    current_user: User = Depends(require_roles(SystemRole.ADMIN.value, SystemRole.AGRICULTURAL_EXPERT.value)),
    db: Session = Depends(get_db)
):
    """
    Registers an approved agricultural publisher institution (ICAR, PJTSAU, KVK, etc.).
    Restricted to Administrators and Agricultural Experts.
    """
    return IngestionService.register_source(data=data, current_user=current_user, db=db)


@router.get("/sources", response_model=List[KnowledgeSourceResponse])
def list_knowledge_sources(
    status_filter: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Lists registered agricultural institutions and their verification status.
    """
    return IngestionService.list_sources(db=db, status_filter=status_filter)


@router.patch("/sources/{source_id}", response_model=KnowledgeSourceResponse)
def update_source_status(
    source_id: str,
    data: KnowledgeSourceUpdateRequest,
    current_user: User = Depends(require_roles(SystemRole.ADMIN.value)),
    db: Session = Depends(get_db)
):
    """
    Updates knowledge source approval status (APPROVED, SUSPENDED, EXPIRED). Admin only.
    """
    return IngestionService.update_source_status(
        source_id=source_id,
        data=data,
        current_user=current_user,
        db=db
    )


# -----------------------------------------------------------------------------
# 3. Document Ingestion Endpoints
# -----------------------------------------------------------------------------
@router.post("/ingest", response_model=IngestionJobResponse, status_code=status.HTTP_202_ACCEPTED)
async def ingest_document(
    source_id: str = Form(...),
    title: str = Form(...),
    document_type: str = Form("PDF"),
    primary_language: str = Form("en"),
    crop_scope: str = Form("cotton"),
    region_scope: str = Form("Telangana"),
    topic_scope: Optional[str] = Form(None),
    file: UploadFile = File(...),
    current_user: User = Depends(require_roles(SystemRole.ADMIN.value, SystemRole.AGRICULTURAL_EXPERT.value)),
    db: Session = Depends(get_db)
):
    """
    Uploads and processes an agricultural document (PDF, DOCX, HTML, Markdown).
    Executes structure-aware chunking and vector embedding persistence.
    """
    content = await file.read()
    if not content:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded document is empty.")

    doc_data = KnowledgeDocumentCreateRequest(
        source_id=source_id,
        title=title,
        document_type=document_type,
        primary_language=primary_language,
        crop_scope=crop_scope,
        region_scope=region_scope,
        topic_scope=topic_scope
    )

    return IngestionService.ingest_document(
        doc_data=doc_data,
        file_bytes=content,
        filename=file.filename or "publication.pdf",
        current_user=current_user,
        db=db
    )


@router.get("/jobs/{job_id}", response_model=IngestionJobResponse)
def get_ingestion_job(
    job_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Polls the progress status of an asynchronous document ingestion job.
    """
    return IngestionService.get_job_status(job_id=job_id, db=db)


@router.get("/documents", response_model=List[KnowledgeDocumentResponse])
def list_documents(
    crop: Optional[str] = None,
    status_filter: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Lists indexed knowledge publications with crop and language filters.
    """
    return IngestionService.list_documents(db=db, crop=crop, status_filter=status_filter)


# -----------------------------------------------------------------------------
# 4. Knowledge Feedback Endpoint
# -----------------------------------------------------------------------------
@router.post("/feedback", response_model=KnowledgeFeedbackResponse, status_code=status.HTTP_201_CREATED)
def submit_knowledge_feedback(
    data: KnowledgeFeedbackCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Records farmer or expert feedback regarding citation accuracy or retrieval relevance.
    """
    feedback = KnowledgeFeedback(
        query_id=data.query_id,
        user_id=current_user.id,
        issue_category=data.issue_category,
        user_comments=data.user_comments,
        reviewer_status="SUBMITTED"
    )
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    return feedback
