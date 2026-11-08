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

// Stage 9 Types: Phase II Advanced Precision Agriculture
export interface PlotGeometry {
  id: string;
  plot_id: string;
  geometry_type: string;
  centroid: { latitude: number; longitude: number };
  calculated_area_hectares: number;
  calculated_area_acres: number;
  bbox: number[];
  is_valid: boolean;
  properties?: Record<string, any>;
}

export interface LocationPermission {
  id: string;
  farm_id: string;
  user_id: string;
  granularity: "EXACT_BOUNDARY" | "COARSE_VILLAGE" | "REVOKED";
  is_active: boolean;
  notes?: string;
}

export interface SatelliteObservationItem {
  id: string;
  observation_date: string;
  mean_ndvi: number;
  min_ndvi: number;
  max_ndvi: number;
  std_ndvi: number;
  mean_evi: number;
  mean_ndmi: number;
  cloud_masked_pixel_ratio: number;
  trend_classification: "VIGOR_INCREASING" | "STABLE" | "DECLINING_STRESS" | "HARVEST_CLEARING";
}

export interface SatelliteTimeSeries {
  plot_id: string;
  trend_summary: string;
  observations_count: number;
  evidence_disclaimer: string;
  time_series: SatelliteObservationItem[];
}

export interface SensorDevice {
  id: string;
  farm_id: string;
  plot_id?: string;
  device_serial_number: string;
  device_category: "SOIL_PROBE" | "WEATHER_STATION" | "LEAF_WETNESS" | "NPK_PROBE";
  status: "ACTIVE" | "INACTIVE" | "DECOMMISSIONED" | "ERROR";
  firmware_version?: string;
  last_heartbeat_at?: string;
  auth_token?: string;
}

export interface SensorMeasurement {
  id: string;
  timestamp: string;
  soil_moisture_pct?: number;
  soil_temperature_c?: number;
  ambient_temperature_c?: number;
  relative_humidity_pct?: number;
  leaf_wetness_pct?: number;
  solar_radiation_w_m2?: number;
  data_quality_flag: "VALID" | "SUSPECT_STUCK" | "SUSPECT_SPIKE" | "UNCALIBRATED" | "OUT_OF_BOUNDS";
}

export interface SensorPlotTelemetryHistory {
  plot_id: string;
  count: number;
  measurements: SensorMeasurement[];
}

export interface FusionContradiction {
  conflict_type: string;
  description: string;
  resolution: string;
}

export interface FusionExplanation {
  id: string;
  plot_id: string;
  evaluation_timestamp: string;
  overall_vigor_status: string;
  primary_stress_driver: string;
  evidence_sources: Record<string, any>;
  contradictions_detected: FusionContradiction[];
  farmer_explanation: {
    en: string;
    te: string;
    hi: string;
  };
  epistemic_qualifications: Record<string, any>;
}

export interface HarvestMeasurement {
  id: string;
  plot_id: string;
  season_id: string;
  harvest_date: string;
  yield_quintals_per_acre: number;
  total_harvest_kg: number;
  provenance_tier: "TIER_1_VERIFIED_WEIGHBRIDGE" | "TIER_2_CCE_CUT" | "TIER_3_FARMER_REPORT";
  verification_document_url?: string;
}

export interface YieldForecastResponse {
  plot_id: string;
  crop_name: string;
  forecast_status: "WITHHELD_INSUFFICIENT_DATA" | "READY_FOR_PILOT" | "RESEARCH_ONLY";
  is_forecast_available: boolean;
  sample_count_available: number;
  minimum_sample_threshold_required: number;
  withholding_reason?: string;
  predicted_yield_min?: number;
  predicted_yield_max?: number;
  confidence_score?: number;
  scientific_disclaimer: string;
}

export interface KnowledgeEntity {
  id: string;
  entity_type: string;
  canonical_name: string;
  local_name_te?: string;
  local_name_hi?: string;
  scientific_name?: string;
  properties?: Record<string, any>;
}

export interface KnowledgeTraversalHop {
  relationship_type: string;
  confidence_weight: number;
  evidence_source: string;
  target_entity: KnowledgeEntity;
}

export interface KnowledgeTraversalResponse {
  root_entity: KnowledgeEntity;
  hops: KnowledgeTraversalHop[];
}

// ==========================================
// STAGE 10: DIGITAL TWIN, SIMULATE, OPTIMIZE, PLAN & DECISIONS
// ==========================================

export type ProvenanceType =
  | "MEASURED"
  | "FARMER_REPORTED"
  | "EXPERT_REVIEWED"
  | "AI_ESTIMATED"
  | "PROVIDER_OBSERVATION"
  | "SIMULATED"
  | "INFERRED"
  | "UNKNOWN";

export interface TwinStateRecord {
  id: string;
  snapshot_id: string;
  entity_type: string;
  entity_id: string;
  property_name: string;
  property_value_json: Record<string, any>;
  unit?: string;
  provenance_type: ProvenanceType;
  source_reference?: string;
  observed_at: string;
  quality_status: string;
}

export interface TwinSnapshotSummary {
  id: string;
  twin_id: string;
  farm_id: string;
  plot_id?: string;
  crop_season_id?: string;
  snapshot_version: number;
  data_completeness_pct: number;
  payload_hash: string;
  generated_at: string;
  source_manifest_json: Record<string, any>;
}

export interface DataCompleteness {
  farm_id: string;
  overall_score: number;
  dimensions: Record<string, number>;
  missing_critical_fields: string[];
  recommendations: string[];
}

export interface FarmTwin {
  id: string;
  farm_id: string;
  twin_version: number;
  state_status: "SYNCHRONIZED" | "STALE" | "RECONCILING" | "ERROR";
  last_synchronized_at: string;
  completeness_score: number;
  latest_snapshot?: TwinSnapshotSummary;
  active_plots_count: number;
}

export interface SimulationResult {
  id: string;
  scenario_id: string;
  model_name: string;
  model_version: string;
  outputs_json: {
    root_zone_depletion_mm?: number;
    total_available_water_mm?: number;
    readily_available_water_mm?: number;
    relative_transpiration_ratio?: number;
    water_stress_index?: number;
    stress_days_count?: number;
    waterlogging_risk_pct?: number;
    depletion_trajectory_days?: number[];
    accumulated_gdd_horizon?: number;
    mean_daily_gdd?: number;
    estimated_drainage_hours?: number;
    waterlogging_risk_level?: string;
  };
  uncertainty_metadata_json: Record<string, any>;
  evidence_sources_json: Array<Record<string, any>>;
  execution_duration_ms: number;
  completed_at: string;
}

export interface SimulationScenario {
  id: string;
  plot_id: string;
  crop_season_id?: string;
  creator_id: string;
  scenario_type: "IRRIGATION_WATER_BALANCE" | "THERMAL_GDD_STAGE" | "WATERLOGGING_STRESS";
  scenario_name: string;
  status: "PENDING" | "RUNNING" | "COMPLETED" | "FAILED";
  baseline_snapshot_id?: string;
  input_parameters_json: Record<string, any>;
  farmer_assumptions_json: Record<string, any>;
  constraints_json: Record<string, any>;
  result?: SimulationResult;
  created_at: string;
}

export interface ScenarioComparison {
  scenarios: Array<{
    scenario_id: string;
    scenario_name: string;
    scenario_type: string;
    key_metrics: Record<string, any>;
    uncertainty_bounds: Record<string, any>;
  }>;
  comparison_summary: Record<string, any>;
  trade_off_recommendation?: string;
}

export interface OptimizationResult {
  id: string;
  problem_id: string;
  feasibility_status: "FEASIBLE" | "INFEASIBLE";
  selected_solution_json: Record<string, any>;
  alternative_solutions_json: Array<Record<string, any>>;
  conflicting_constraints_json: string[];
  trade_off_analysis_json: Record<string, any>;
  solver_name: string;
  solved_at: string;
}

export interface OptimizationProblem {
  id: string;
  farm_id: string;
  plot_id?: string;
  problem_type: "WATER_ALLOCATION" | "INPUT_BUDGET_ALLOCATION" | "IRRIGATION_WINDOW";
  objective_type: string;
  status: "PENDING" | "SOLVED" | "INFEASIBLE" | "FAILED";
  decision_variables_json: Record<string, any>;
  hard_constraints_json: Record<string, any>;
  soft_constraints_json: Record<string, any>;
  result?: OptimizationResult;
  created_at: string;
}

export interface CropCalendarDefinition {
  id: string;
  crop_id: string;
  variety_id?: string;
  agro_climatic_zone: string;
  growth_stage: string;
  typical_duration_days: number;
  recommended_tasks_json: Array<{
    task_name: string;
    category: string;
    offset_days: number;
  }>;
  source_citation: string;
  version: string;
}

export interface CropTask {
  id: string;
  crop_season_id: string;
  plot_id: string;
  calendar_def_id?: string;
  task_name: string;
  task_category: "LAND_PREP" | "SOWING" | "IRRIGATION" | "FERTILIZATION" | "PLANT_PROTECTION" | "HARVEST";
  due_date: string;
  completed_date?: string;
  status: "PLANNED" | "DUE" | "IN_PROGRESS" | "COMPLETED" | "SKIPPED" | "RESCHEDULED" | "CANCELLED";
  weather_conflict_flag: boolean;
  conflict_reason?: string;
  execution_details_json: Record<string, any>;
  notes?: string;
  created_at: string;
}

export interface DecisionRecord {
  id: string;
  plot_id: string;
  query_text: string;
  decision_category: string;
  recommendation_state:
    | "INFORMATIONAL"
    | "EVIDENCE_SUPPORTED"
    | "SCENARIO_RESULT"
    | "REQUIRES_MORE_INFORMATION"
    | "REQUIRES_EXPERT_REVIEW"
    | "INSUFFICIENT_EVIDENCE"
    | "NOT_SUPPORTED";
  grounded_explanation_en: string;
  grounded_explanation_te: string;
  grounded_explanation_hi: string;
  evidence_sources_json: Array<{
    source_title: string;
    chapter?: string;
    chunk_id?: string;
    citation?: string;
  }>;
  uncertainty_disclosures_json: string[];
  expert_escalation_case_id?: string;
  evaluated_at: string;
}

export interface DecisionFeedback {
  id: string;
  decision_id: string;
  farmer_action_taken: "ADOPTED" | "PARTIALLY_ADOPTED" | "REJECTED" | "INAPPLICABLE";
  farmer_rating?: number;
  feedback_notes?: string;
  observed_outcome?: string;
  recorded_at: string;
}
