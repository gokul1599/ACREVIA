export interface UserSummary {
  id: str;
  phone: string;
  email?: string;
  full_name: string;
  language_preference: "te" | "en" | "hi";
  is_active: boolean;
  is_verified: boolean;
  roles: string[];
}

type str = string;

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
