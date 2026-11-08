"""
ACREVIA - Agricultural Interoperability Schemas.
Stage 14: Partners, API Applications, Scoped Credentials, Data Sharing Grants, and Webhooks.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


# ============================================================================
# Partner Registry Schemas
# ============================================================================

class PartnerRegisterRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=150)
    partner_type: str = Field(..., description="LABORATORY, UNIVERSITY, KVK, WEATHER_PROVIDER, SATELLITE_PROVIDER, IOT_MANUFACTURER, FPO, RESEARCH_INSTITUTION, DEVELOPER")
    description: Optional[str] = None
    website: Optional[str] = None
    contact_email: str = Field(..., max_length=100)
    contact_phone: Optional[str] = None
    legal_entity_number: Optional[str] = None


class PartnerVerifyRequest(BaseModel):
    verification_status: str = Field(..., description="VERIFIED, UNDER_REVIEW, SUSPENDED, REVOKED")
    verification_notes: Optional[str] = None


class PartnerIntegrationCreate(BaseModel):
    connector_type: str = Field(..., description="SOIL_LAB, MARKET_DATA, WEATHER_STATION, SATELLITE_PROVIDER, IOT_TELEMETRY, KNOWLEDGE_BASE, CUSTOM_ADAPTER")
    display_name: str = Field(..., min_length=2, max_length=150)
    capabilities: List[str] = Field(default_factory=list)
    adapter_config: Dict[str, Any] = Field(default_factory=dict)


class PartnerIntegrationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    partner_id: str
    connector_type: str
    display_name: str
    capabilities_json: str
    status: str
    health_status: str
    last_health_check_at: Optional[datetime] = None
    created_at: datetime


class PartnerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    name: str
    partner_type: str
    description: Optional[str] = None
    website: Optional[str] = None
    contact_email: str
    contact_phone: Optional[str] = None
    legal_entity_number: Optional[str] = None
    verification_status: str
    verification_notes: Optional[str] = None
    verified_at: Optional[datetime] = None
    created_at: datetime


# ============================================================================
# Developer & API Credential Schemas
# ============================================================================

class ApiApplicationCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=120)
    description: Optional[str] = None
    partner_id: Optional[str] = None
    is_sandbox: bool = False
    redirect_uris: List[str] = Field(default_factory=list)


class ApiApplicationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    user_id: str
    partner_id: Optional[str] = None
    name: str
    description: Optional[str] = None
    is_sandbox: bool
    is_active: bool
    redirect_uris_json: str
    created_at: datetime


class ApiCredentialCreate(BaseModel):
    scopes: List[str] = Field(
        default=["crops:read", "diagnostics:read", "weather:read", "market:read"],
        description="Allowed permission scopes e.g. crops:read, diagnostics:read, soil:read, farm:write"
    )
    rate_limit_per_minute: int = Field(default=60, ge=10, le=1000)
    expires_in_days: Optional[int] = Field(default=365, ge=1, le=1825)


class ApiCredentialResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    application_id: str
    client_id: str
    secret_prefix: str
    scopes_json: str
    rate_limit_per_minute: int
    is_active: bool
    expires_at: Optional[datetime] = None
    last_used_at: Optional[datetime] = None
    created_at: datetime


class ApiCredentialCreatedResponse(ApiCredentialResponse):
    client_secret: str = Field(..., description="Cleartext secret returned ONLY ONCE upon creation")


# ============================================================================
# Consent & Data Sharing Grants Schemas
# ============================================================================

class DataSharingGrantCreate(BaseModel):
    partner_id: str
    farm_id: Optional[str] = None
    plot_id: Optional[str] = None
    data_categories: List[str] = Field(
        default=["FARM_PROFILE", "OBSERVATIONS"],
        description="FARM_PROFILE, SOIL_HEALTH, WATER_RESOURCES, OBSERVATIONS, DIAGNOSTICS, HARVEST_YIELD, FINANCIAL_SUMMARY"
    )
    purpose: str = Field(..., min_length=5, max_length=255)
    anonymize_pii: bool = True
    redact_exact_gps: bool = True
    expires_in_days: Optional[int] = Field(default=90, ge=1, le=730)


class DataSharingGrantRevoke(BaseModel):
    reason: str = Field(..., min_length=3, max_length=500)


class DataSharingGrantResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    user_id: str
    partner_id: str
    farm_id: Optional[str] = None
    plot_id: Optional[str] = None
    data_categories_json: str
    purpose: str
    anonymize_pii: bool
    redact_exact_gps: bool
    is_revoked: bool
    granted_at: datetime
    expires_at: Optional[datetime] = None
    revoked_at: Optional[datetime] = None
    revocation_reason: Optional[str] = None


# ============================================================================
# Webhook Schemas
# ============================================================================

class WebhookEndpointCreate(BaseModel):
    url: str = Field(..., max_length=500, description="HTTPS destination endpoint")
    event_types: List[str] = Field(
        default=["crop.diagnosis.completed", "farm.risk.alert", "market.price.updated"],
        description="Event types subscribed to"
    )
    partner_id: Optional[str] = None


class WebhookEndpointResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    user_id: str
    partner_id: Optional[str] = None
    url: str
    event_types_json: str
    is_active: bool
    failure_count: int
    last_delivery_at: Optional[datetime] = None
    created_at: datetime


class WebhookEndpointCreatedResponse(WebhookEndpointResponse):
    signing_secret: str = Field(..., description="Cleartext webhook signing secret for HMAC verification")


class WebhookDeliveryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    endpoint_id: str
    event_id: str
    attempt_number: int
    response_status_code: Optional[int] = None
    response_body_snippet: Optional[str] = None
    duration_ms: int
    status: str
    delivered_at: datetime


class WebhookEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    event_type: str
    event_version: str
    tenant_id: str
    entity_type: str
    entity_id: str
    payload_json: str
    status: str
    created_at: datetime


# ============================================================================
# Standards & Canonical Data Schemas
# ============================================================================

class UnitConversionRequest(BaseModel):
    value: float
    from_unit: str
    to_unit: str
    category: str = Field("MASS", description="MASS, AREA, VOLUME, CONCENTRATION, CONDUCTIVITY, TEMPERATURE, RATE")


class UnitConversionResponse(BaseModel):
    original_value: float
    original_unit: str
    converted_value: float
    converted_unit: str
    category: str
    conversion_factor: float


class CropTaxonomyResponse(BaseModel):
    standard_code: str
    scientific_name: str
    names: Dict[str, str]
    varieties: List[Dict[str, str]]
    canonical_units: Dict[str, str]
