"""
ACREVIA - Agricultural Interoperability, Open API & Partner Ecosystem Models.
Stage 14: Integration Partners, API Applications, Scoped Credentials, Data Sharing Grants, and Webhooks.
"""

from datetime import datetime, timezone
import uuid
from typing import List, Optional
from sqlalchemy import String, Text, Boolean, Integer, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.database.base import Base, TimestampMixin


class IntegrationPartner(Base, TimestampMixin):
    """
    Governed agricultural integration partner (Universities, Soil Labs, KVKs, IoT vendors, FPOs).
    """
    __tablename__ = "integration_partners"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    partner_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # LABORATORY, UNIVERSITY, KVK, WEATHER_PROVIDER, SATELLITE_PROVIDER, IOT_MANUFACTURER, FPO, RESEARCH_INSTITUTION, DEVELOPER
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    website: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    contact_email: Mapped[str] = mapped_column(String(100), nullable=False)
    contact_phone: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    legal_entity_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    verification_status: Mapped[str] = mapped_column(
        String(30), default="APPLICATION_SUBMITTED", nullable=False
    )  # APPLICATION_SUBMITTED, UNDER_REVIEW, VERIFIED, SUSPENDED, REVOKED
    verification_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    verified_by_user_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    # Relationships
    integrations: Mapped[List["PartnerIntegration"]] = relationship(
        "PartnerIntegration", back_populates="partner", cascade="all, delete-orphan"
    )
    applications: Mapped[List["ApiApplication"]] = relationship(
        "ApiApplication", back_populates="partner"
    )
    webhook_endpoints: Mapped[List["WebhookEndpoint"]] = relationship(
        "WebhookEndpoint", back_populates="partner", cascade="all, delete-orphan"
    )
    data_grants: Mapped[List["DataSharingGrant"]] = relationship(
        "DataSharingGrant", back_populates="partner", cascade="all, delete-orphan"
    )


class PartnerIntegration(Base, TimestampMixin):
    """
    Standardized adapter capability registration for an integration partner.
    """
    __tablename__ = "partner_integrations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    partner_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("integration_partners.id", ondelete="CASCADE"), index=True, nullable=False
    )
    connector_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # SOIL_LAB, MARKET_DATA, WEATHER_STATION, SATELLITE_PROVIDER, IOT_TELEMETRY, KNOWLEDGE_BASE, CUSTOM_ADAPTER
    display_name: Mapped[str] = mapped_column(String(150), nullable=False)
    capabilities_json: Mapped[str] = mapped_column(Text, default="[]", nullable=False)
    adapter_config_json: Mapped[str] = mapped_column(Text, default="{}", nullable=False)

    status: Mapped[str] = mapped_column(
        String(30), default="ACTIVE", nullable=False
    )  # ACTIVE, PAUSED, REVOKED, DEPRECATED
    last_health_check_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    health_status: Mapped[str] = mapped_column(
        String(30), default="HEALTHY", nullable=False
    )  # HEALTHY, DEGRADED, UNAVAILABLE

    # Relationships
    partner: Mapped["IntegrationPartner"] = relationship("IntegrationPartner", back_populates="integrations")


class ApiApplication(Base, TimestampMixin):
    """
    Registered third-party or internal API client application.
    """
    __tablename__ = "api_applications"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    partner_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("integration_partners.id", ondelete="SET NULL"), index=True, nullable=True
    )
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_sandbox: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    redirect_uris_json: Mapped[str] = mapped_column(Text, default="[]", nullable=False)

    # Relationships
    partner: Mapped[Optional["IntegrationPartner"]] = relationship("IntegrationPartner", back_populates="applications")
    credentials: Mapped[List["ApiCredential"]] = relationship(
        "ApiCredential", back_populates="application", cascade="all, delete-orphan"
    )


class ApiCredential(Base):
    """
    Scoped API key / client credentials with SHA-256 hashed secret.
    """
    __tablename__ = "api_credentials"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    application_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("api_applications.id", ondelete="CASCADE"), index=True, nullable=False
    )
    client_id: Mapped[str] = mapped_column(String(80), unique=True, index=True, nullable=False)
    hashed_secret: Mapped[str] = mapped_column(String(128), nullable=False)
    secret_prefix: Mapped[str] = mapped_column(String(16), nullable=False)
    scopes_json: Mapped[str] = mapped_column(Text, default='["crops:read", "diagnostics:read"]', nullable=False)
    rate_limit_per_minute: Mapped[int] = mapped_column(Integer, default=60, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    last_used_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    # Relationships
    application: Mapped["ApiApplication"] = relationship("ApiApplication", back_populates="credentials")


class DataSharingGrant(Base):
    """
    Farmer-granted explicit consent record for sharing categorized farm data with an approved partner.
    """
    __tablename__ = "data_sharing_grants"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    partner_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("integration_partners.id", ondelete="CASCADE"), index=True, nullable=False
    )
    farm_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("farms.id", ondelete="CASCADE"), index=True, nullable=True
    )
    plot_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("plots.id", ondelete="SET NULL"), nullable=True
    )

    data_categories_json: Mapped[str] = mapped_column(
        Text, default='["FARM_PROFILE", "OBSERVATIONS"]', nullable=False
    )  # FARM_PROFILE, SOIL_HEALTH, WATER_RESOURCES, OBSERVATIONS, DIAGNOSTICS, HARVEST_YIELD, FINANCIAL_SUMMARY
    purpose: Mapped[str] = mapped_column(String(255), nullable=False)
    anonymize_pii: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    redact_exact_gps: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_revoked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    granted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    revoked_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    revocation_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    partner: Mapped["IntegrationPartner"] = relationship("IntegrationPartner", back_populates="data_grants")


class WebhookEndpoint(Base, TimestampMixin):
    """
    Registered webhook receiver destination with HMAC secret verification.
    """
    __tablename__ = "webhook_endpoints"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    partner_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("integration_partners.id", ondelete="CASCADE"), index=True, nullable=True
    )
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    secret_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    event_types_json: Mapped[str] = mapped_column(
        Text, default='["diagnosis.completed", "risk.alert"]', nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    failure_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_delivery_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    partner: Mapped[Optional["IntegrationPartner"]] = relationship(
        "IntegrationPartner", back_populates="webhook_endpoints"
    )
    deliveries: Mapped[List["WebhookDelivery"]] = relationship(
        "WebhookDelivery", back_populates="endpoint", cascade="all, delete-orphan"
    )


class WebhookEvent(Base):
    """
    Transactional Outbox event recorded atomically alongside agricultural state changes.
    """
    __tablename__ = "webhook_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    event_type: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    event_version: Mapped[str] = mapped_column(String(20), default="1.0", nullable=False)
    tenant_id: Mapped[str] = mapped_column(String(36), index=True, nullable=False)
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    entity_id: Mapped[str] = mapped_column(String(36), nullable=False)
    payload_json: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(
        String(30), default="PENDING", index=True, nullable=False
    )  # PENDING, PROCESSING, DELIVERED, FAILED
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    # Relationships
    deliveries: Mapped[List["WebhookDelivery"]] = relationship(
        "WebhookDelivery", back_populates="event", cascade="all, delete-orphan"
    )


class WebhookDelivery(Base):
    """
    Audit record of an attempted delivery to a WebhookEndpoint.
    """
    __tablename__ = "webhook_deliveries"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    endpoint_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("webhook_endpoints.id", ondelete="CASCADE"), index=True, nullable=False
    )
    event_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("webhook_events.id", ondelete="CASCADE"), index=True, nullable=False
    )
    attempt_number: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    response_status_code: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    response_body_snippet: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    duration_ms: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    status: Mapped[str] = mapped_column(
        String(30), default="SUCCESS", nullable=False
    )  # SUCCESS, FAILED, RETRY_PENDING
    delivered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    # Relationships
    endpoint: Mapped["WebhookEndpoint"] = relationship("WebhookEndpoint", back_populates="deliveries")
    event: Mapped["WebhookEvent"] = relationship("WebhookEvent", back_populates="deliveries")
