export interface UserSummary {
  id: string;
  phone: string;
  email?: string;
  full_name: string;
  language_preference: "te" | "en" | "hi";
  is_active: boolean;
  is_verified: boolean;
  roles: string[];
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  expires_in_seconds: number;
  user: UserSummary;
}

export interface Farm {
  id: string;
  owner_id: string;
  name: string;
  state: string;
  district: string;
  mandal: string;
  village: string;
  total_acreage: number;
  is_archived: boolean;
  created_at: string;
  updated_at: string;
}

export interface Plot {
  id: string;
  farm_id: string;
  name: string;
  soil_type: "BLACK_COTTON" | "RED_CHALKA" | "ALLUVIAL" | "LOAMY";
  irrigation_source: "BOREWELL" | "CANAL" | "RAINFED" | "DRIP" | "WELL";
  acreage?: number;
  created_at: string;
}

export interface CropSeason {
  id: string;
  plot_id: string;
  crop_id: "cotton" | "rice" | "chilli";
  variety_id?: string;
  season_type: "KHARIF" | "RABI" | "SUMMER";
  sowing_date: string;
  current_stage: string;
  status: string;
  created_at: string;
}

export interface ObservationMedia {
  id: string;
  observation_id: string;
  storage_path: string;
  file_size_bytes: number;
  mime_type: string;
  sha256_hash: string;
  is_primary: boolean;
  created_at: string;
}

export interface Observation {
  id: string;
  farm_id: string;
  plot_id?: string;
  crop_season_id?: string;
  observer_id: string;
  notes?: string;
  symptom_tags?: string;
  created_at: string;
  media: ObservationMedia[];
}

export interface PredictionCandidate {
  rank: number;
  class_id: string;
  display_name_en: string;
  display_name_te: string;
  display_name_hi: string;
  pathogen_or_cause?: string;
  calibrated_prob: number;
}

export interface Prediction {
  id: string;
  model_version: string;
  decision_state: string;
  top_confidence: number;
  normalized_entropy?: number;
  prediction_margin?: number;
  cibrc_advisory: string;
  candidates: PredictionCandidate[];
}

export interface ExpertReview {
  id: string;
  diagnosis_request_id: string;
  expert_id: string;
  status: "CONFIRMED" | "OVERRIDDEN";
  verified_class_id?: string;
  expert_notes?: string;
  reviewed_at?: string;
}

export interface Diagnosis {
  id: string;
  observation_id: string;
  media_id?: string;
  status: string;
  requested_at: string;
  completed_at?: string;
  prediction?: Prediction;
  expert_review?: ExpertReview;
}

export interface Citation {
  source_title: string;
  publisher: string;
  canonical_url?: string;
  document_version: number;
  page_start?: number;
  page_end?: number;
  heading_path?: string;
  content_snippet: string;
  relevance_score: number;
}

export interface KnowledgeQueryResponse {
  query_id: string;
  answer_status: "ANSWERED" | "PARTIALLY_ANSWERED" | "INSUFFICIENT_EVIDENCE" | "REQUIRES_EXPERT_REVIEW";
  language: "te" | "en" | "hi";
  answer: string;
  evidence_strength: "STRONG" | "MODERATE" | "WEAK" | "INSUFFICIENT";
  citations: Citation[];
  limitations: string[];
  follow_up_questions: string[];
  requires_expert_review: boolean;
  execution_time_ms: number;
}

export interface FarmWeatherReport {
  farm_id: string;
  district: string;
  temperature: number;
  humidity: number;
  precipitation: number;
  wind_speed: number;
  source: string;
  pest_risk_level: "LOW" | "MODERATE" | "HIGH";
  weather_risk_level: "LOW" | "MODERATE" | "HIGH";
  advisory: string;
}

// ================= STAGE 7: RISKCAST TYPES =================

export interface RiskAlert {
  id: string;
  farm_id: string;
  plot_id: string;
  risk_assessment_id: string;
  alert_level: "LOW" | "MODERATE" | "HIGH";
  title: string;
  message_en: string;
  message_te: string;
  message_hi: string;
  recommended_actions: string[];
  is_acknowledged: boolean;
  acknowledged_at?: string;
  is_dismissed: boolean;
  dismissed_at?: string;
  created_at: string;
}

export interface PlotRiskSummary {
  plot_id: string;
  plot_name: string;
  crop_id?: string;
  growth_stage?: string;
  current_risk_level: "LOW" | "MODERATE" | "HIGH" | "INSUFFICIENT_DATA";
  top_threat?: string;
  advisory: string;
  active_alerts_count: number;
}

export interface FarmRiskOverview {
  farm_id: string;
  district: string;
  current_weather?: {
    temperature_celsius: number;
    relative_humidity: number;
    precipitation_mm: number;
    wind_speed_kmh: number;
    leaf_wetness_hours: number;
    source_provider: string;
    observation_time: string;
  };
  plots_risk_summary: PlotRiskSummary[];
  active_alerts: RiskAlert[];
}

export interface TriggeredRuleDetail {
  rule_code: string;
  target_threat: string;
  severity_level: string;
  advisory_en: string;
  advisory_te: string;
  advisory_hi: string;
  citations: string[];
}

export interface RiskAssessment {
  id: string;
  plot_id: string;
  farm_id: string;
  crop_season_id?: string;
  evaluation_timestamp: string;
  overall_risk_level: "LOW" | "MODERATE" | "HIGH" | "INSUFFICIENT_DATA";
  weather_data_id?: string;
  weather_summary?: Record<string, any>;
  rules_triggered: TriggeredRuleDetail[];
  advisory_en: string;
  advisory_te: string;
  advisory_hi: string;
  limitations_notice: string;
}

export interface RiskRule {
  id: string;
  rule_code: string;
  crop: string;
  target_threat: string;
  applicable_growth_stages: string;
  min_temp?: number;
  max_temp?: number;
  min_humidity?: number;
  min_leaf_wetness_hours?: number;
  severity_level: string;
  advisory_en: string;
  advisory_te: string;
  advisory_hi: string;
  evidence_citations: string[];
  version: string;
  is_active: boolean;
}

// ================= STAGE 7: EXPERTCONNECT TYPES =================

export interface ExpertProfile {
  id: string;
  user_id: string;
  full_name: string;
  email?: string;
  phone: string;
  registration_number?: string;
  highest_degree: string;
  institution: string;
  specializations: string[];
  districts_covered: string[];
  verification_status: "APPLICATION_SUBMITTED" | "UNDER_REVIEW" | "APPROVED" | "SUSPENDED" | "REVOKED";
  verified_at?: string;
  rejection_reason?: string;
}

export interface ExpertCaseItem {
  id: string;
  observation_id: string;
  farm_id: string;
  farm_name: string;
  district: string;
  plot_id?: string;
  crop_id: string;
  priority: "ROUTINE" | "URGENT";
  status: "QUEUED" | "ASSIGNED" | "IN_REVIEW" | "COMPLETED" | "ESCALATED";
  assigned_expert_id?: string;
  assigned_expert_name?: string;
  created_at: string;
}

export interface ExpertCaseDossier {
  case_id: string;
  observation_id: string;
  farm_id: string;
  farm_name: string;
  district: string;
  plot_id?: string;
  plot_name?: string;
  crop_id: string;
  growth_stage?: string;
  priority: "ROUTINE" | "URGENT";
  status: string;
  assigned_expert_id?: string;
  assigned_expert_name?: string;
  farmer_notes?: string;
  symptom_tags?: string;
  foliar_media: Array<{
    id: string;
    mime_type: string;
    file_size_bytes: number;
    sha256_hash: string;
    storage_path: string;
  }>;
  ai_prediction?: Record<string, any>;
  krishi_brain_citations: Array<{
    source_title: string;
    content_excerpt: string;
    cibrc_approved: boolean;
  }>;
  weather_context?: Record<string, any>;
  assessment?: Record<string, any>;
  created_at: string;
}

export interface ExpertAssessment {
  id: string;
  case_id: string;
  expert_id: string;
  expert_name: string;
  expert_degree: string;
  expert_institution: string;
  confirmed_crop: string;
  primary_condition: string;
  differential_diagnoses: string[];
  confidence_rating: number;
  urgency_level: "LOW" | "ROUTINE" | "HIGH" | "EMERGENCY";
  management_plan: string;
  ipm_strategy: string;
  cibrc_advisories: string;
  revision_count: number;
  created_at: string;
  updated_at: string;
}

export interface ExpertAssessmentRevision {
  id: string;
  assessment_id: string;
  revision_number: number;
  previous_assessment: Record<string, any>;
  revision_reason: string;
  revised_by_user_id: string;
  revised_by_name: string;
  revised_at: string;
}

// ================= STAGE 7: INTERVENTIONS TYPES =================

export interface OutcomeObservation {
  id: string;
  intervention_id: string;
  follow_up_observation_id: string;
  evaluation_date: string;
  observed_status: "IMPROVING" | "STABLE" | "WORSENING" | "INCONCLUSIVE";
  visual_change_notes: string;
  confounding_factors: string;
  farmer_assessment?: string;
  days_post_intervention: number;
  created_at: string;
}

export interface InterventionRecord {
  id: string;
  plot_id: string;
  farm_id: string;
  farmer_id: string;
  category: "BIOLOGICAL" | "CHEMICAL" | "CULTURAL" | "IRRIGATION" | "FERTILIZER";
  trade_name: string;
  active_ingredient?: string;
  dosage: number;
  unit: string;
  application_method: string;
  application_date: string;
  target_condition?: string;
  phi_days: number;
  rei_hours: number;
  notes?: string;
  created_at: string;
  outcomes?: OutcomeObservation[];
}

export interface InterventionTimeline {
  intervention: InterventionRecord;
  outcomes: OutcomeObservation[];
  initial_observation_media: Array<{ id: string; mime_type: string; url: string }>;
  latest_observation_media: Array<{ id: string; mime_type: string; url: string }>;
  confounding_variables_notice: string;
}
