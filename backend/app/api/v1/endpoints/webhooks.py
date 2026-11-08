"""
ACREVIA - Webhook Endpoints & Delivery Audits.
Stage 14: Registration, HMAC secret issuance, outbox event dispatch, and SSRF prevention.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.database.session import get_db
from backend.app.models.user import User
from backend.app.models.interoperability import WebhookEndpoint, WebhookDelivery
from backend.app.schemas.interoperability import (
    WebhookEndpointCreate,
    WebhookEndpointCreatedResponse,
    WebhookEndpointResponse,
    WebhookDeliveryResponse,
    WebhookEventResponse,
)
from backend.app.security.dependencies import get_current_user
from backend.app.services.webhook_service import WebhookService, WebhookSecurityError

router = APIRouter(prefix="/webhooks", tags=["ACREVIA Webhooks"])


@router.post("/endpoints", response_model=WebhookEndpointCreatedResponse, status_code=status.HTTP_201_CREATED)
def register_webhook_endpoint(
    request: WebhookEndpointCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Registers a destination webhook receiver and returns the cleartext signing secret.
    Enforces SSRF prevention checks against private/internal IP spaces.
    """
    try:
        endpoint, secret = WebhookService.register_endpoint(
            db=db,
            user_id=current_user.id,
            url=request.url,
            event_types=request.event_types,
            partner_id=request.partner_id,
        )
        return WebhookEndpointCreatedResponse(
            id=endpoint.id,
            user_id=endpoint.user_id,
            partner_id=endpoint.partner_id,
            url=endpoint.url,
            event_types_json=endpoint.event_types_json,
            is_active=endpoint.is_active,
            failure_count=endpoint.failure_count,
            last_delivery_at=endpoint.last_delivery_at,
            created_at=endpoint.created_at,
            signing_secret=secret,
        )
    except WebhookSecurityError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/endpoints", response_model=List[WebhookEndpointResponse], status_code=status.HTTP_200_OK)
def list_webhook_endpoints(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return db.scalars(select(WebhookEndpoint).where(WebhookEndpoint.user_id == current_user.id)).all()


@router.delete("/endpoints/{endpoint_id}", response_model=WebhookEndpointResponse, status_code=status.HTTP_200_OK)
def deactivate_webhook_endpoint(
    endpoint_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    endpoint = db.get(WebhookEndpoint, endpoint_id)
    if not endpoint or endpoint.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Webhook endpoint not found")

    endpoint.is_active = False
    db.commit()
    db.refresh(endpoint)
    return endpoint


@router.post("/test-dispatch", response_model=WebhookEventResponse, status_code=status.HTTP_201_CREATED)
def test_dispatch_event(
    event_type: str = "crop.diagnosis.completed",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Emits a test outbox event and dispatches delivery to active webhook receivers.
    """
    event = WebhookService.publish_outbox_event(
        db=db,
        event_type=event_type,
        tenant_id=current_user.id,
        entity_type="CROP_OBSERVATION",
        entity_id="test-obs-14",
        payload={
            "crop": "COTTON",
            "condition": "Healthy Vegetative Growth",
            "confidence": 0.96,
            "disclaimer": "ACREVIA verified AI diagnosis"
        }
    )
    WebhookService.dispatch_event(db=db, event_id=event.id)
    db.refresh(event)
    return event


@router.get("/deliveries", response_model=List[WebhookDeliveryResponse], status_code=status.HTTP_200_OK)
def list_deliveries(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Deliveries for endpoints owned by current user
    stmt = (
        select(WebhookDelivery)
        .join(WebhookEndpoint)
        .where(WebhookEndpoint.user_id == current_user.id)
        .order_by(WebhookDelivery.delivered_at.desc())
        .limit(50)
    )
    return db.scalars(stmt).all()


@router.post("/deliveries/{delivery_id}/retry", response_model=WebhookDeliveryResponse, status_code=status.HTTP_200_OK)
def retry_delivery(
    delivery_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        new_delivery = WebhookService.retry_delivery(db=db, delivery_id=delivery_id)
        return new_delivery
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
