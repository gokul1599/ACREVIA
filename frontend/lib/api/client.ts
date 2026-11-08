import type {
  TokenResponse,
  UserSummary,
  Farm,
  Plot,
  CropSeason,
  Observation,
  ObservationMedia,
  Diagnosis,
  KnowledgeQueryResponse,
  FarmWeatherReport,
  FarmRiskOverview,
  RiskAssessment,
  RiskAlert,
  RiskRule,
  ExpertProfile,
  ExpertCaseItem,
  ExpertCaseDossier,
  ExpertAssessment,
  ExpertAssessmentRevision,
  InterventionRecord,
  OutcomeObservation,
  InterventionTimeline,
  PlotGeometry,
  LocationPermission,
  SatelliteTimeSeries,
  SensorDevice,
  SensorPlotTelemetryHistory,
  FusionExplanation,
  HarvestMeasurement,
  YieldForecastResponse,
  KnowledgeEntity,
  KnowledgeTraversalResponse,
} from "./types.ts";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "";

class ApiClient {
  private token: string | null = null;

  constructor() {
    if (typeof window !== "undefined") {
      try {
        this.token = localStorage.getItem("acrevia_token");
      } catch {
        // ignore
      }
    }
  }

  setToken(token: string | null) {
    this.token = token;
    if (typeof window !== "undefined") {
      try {
        if (token) {
          localStorage.setItem("acrevia_token", token);
        } else {
          localStorage.removeItem("acrevia_token");
        }
      } catch {
        // ignore
      }
    }
  }

  getToken(): string | null {
    return this.token;
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${BASE_URL}/api/v1${endpoint}`;
    const headers: Record<string, string> = {
      ...(options.headers as Record<string, string>),
    };

    if (this.token && !headers["Authorization"]) {
      headers["Authorization"] = `Bearer ${this.token}`;
    }

    if (!(options.body instanceof FormData) && !headers["Content-Type"]) {
      headers["Content-Type"] = "application/json";
    }

    const res = await fetch(url, {
      ...options,
      headers,
    });

    if (res.status === 401) {
      this.setToken(null);
      if (typeof window !== "undefined" && !window.location.pathname.startsWith("/login")) {
        window.location.href = "/login?expired=1";
      }
      throw new Error("Session expired or unauthorized. Please log in again.");
    }

    if (!res.ok) {
      let errorMsg = `API request failed with status ${res.status}`;
      try {
        const errorData = await res.json();
        errorMsg = errorData.detail || errorData.message || errorMsg;
      } catch {
        // non-json response
      }
      throw new Error(errorMsg);
    }

    return res.json() as Promise<T>;
  }

  // --- Auth ---
  async login(credentials: { phone?: string; email?: string; password: string }): Promise<TokenResponse> {
    const res = await this.request<TokenResponse>("/auth/login", {
      method: "POST",
      body: JSON.stringify(credentials),
    });
    this.setToken(res.access_token);
    return res;
  }

  async register(data: {
    phone: string;
    password: string;
    full_name: string;
    email?: string;
    language_preference?: "te" | "en" | "hi" | string;
    role?: string;
  }): Promise<TokenResponse> {
    const res = await this.request<TokenResponse>("/auth/register", {
      method: "POST",
      body: JSON.stringify(data),
    });
    this.setToken(res.access_token);
    return res;
  }

  async getMe(): Promise<UserSummary> {
    return this.request<UserSummary>("/auth/me");
  }

  async getCurrentUser(): Promise<UserSummary> {
    return this.getMe();
  }

  logout() {
    this.setToken(null);
  }

  // --- Farms & Plots ---
  async listFarms(): Promise<Farm[]> {
    return this.request<Farm[]>("/farms/");
  }

  async createFarm(data: {
    name: string;
    district: string;
    mandal: string;
    village: string;
    total_acreage: number;
    state?: string;
  }): Promise<Farm> {
    return this.request<Farm>("/farms/", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async getFarm(farmId: string): Promise<Farm> {
    return this.request<Farm>(`/farms/${farmId}`);
  }

  async listPlots(farmId: string): Promise<Plot[]> {
    return this.request<Plot[]>(`/farms/${farmId}/plots`);
  }

  async createPlot(
    farmId: string,
    data: {
      name: string;
      soil_type?: string;
      irrigation_source?: string;
      acreage?: number;
    }
  ): Promise<Plot> {
    return this.request<Plot>(`/farms/${farmId}/plots`, {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async listSeasons(plotId: string): Promise<CropSeason[]> {
    return this.request<CropSeason[]>(`/plots/${plotId}/seasons`);
  }

  async listCropSeasons(plotId: string): Promise<CropSeason[]> {
    return this.listSeasons(plotId);
  }

  async createSeason(
    plotId: string,
    data: {
      crop_id: string;
      season_type: string;
      sowing_date: string;
      current_stage: string;
    }
  ): Promise<CropSeason> {
    return this.request<CropSeason>(`/plots/${plotId}/seasons`, {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async createCropSeason(
    plotId: string,
    data: {
      crop_id: string;
      season_type: string;
      sowing_date: string;
      current_stage: string;
    }
  ): Promise<CropSeason> {
    return this.createSeason(plotId, data);
  }

  // --- Observations ---
  async listObservations(farmId: string, limit: number = 20): Promise<Observation[]> {
    return this.request<Observation[]>(`/observations/?farm_id=${farmId}&limit=${limit}`);
  }

  async createObservation(data: {
    farm_id: string;
    plot_id?: string;
    crop_season_id?: string;
    notes?: string;
    symptom_tags?: string;
  }): Promise<Observation> {
    return this.request<Observation>("/observations/", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async uploadObservationMedia(
    obsId: string,
    file: Blob,
    filename: string = "observation.jpg",
    isPrimary: boolean = true
  ): Promise<ObservationMedia> {
    const formData = new FormData();
    formData.append("file", file, filename);
    formData.append("is_primary", String(isPrimary));

    return this.request<ObservationMedia>(`/observations/${obsId}/media`, {
      method: "POST",
      body: formData,
    });
  }

  getMediaFileUrl(obsId: string, mediaId: string): string {
    return `${BASE_URL}/api/v1/observations/${obsId}/media/${mediaId}/stream`;
  }

  // --- Diagnoses ---
  async requestDiagnosis(data: {
    observation_id: string;
    media_id?: string;
    crop_type: "cotton" | "rice" | "chilli";
    language?: "te" | "en" | "hi";
  }): Promise<Diagnosis> {
    return this.request<Diagnosis>("/diagnoses/", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async getDiagnosis(diagnosisId: string): Promise<Diagnosis> {
    return this.request<Diagnosis>(`/diagnoses/${diagnosisId}`);
  }

  // --- Knowledge (KrishiBrain) ---
  async queryKnowledge(data: {
    question: string;
    language: "te" | "en" | "hi";
    crop?: string;
    growth_stage?: string;
    max_citations?: number;
  }): Promise<KnowledgeQueryResponse> {
    return this.request<KnowledgeQueryResponse>("/knowledge/query", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async submitKnowledgeFeedback(data: {
    query_id: string;
    rating: number;
    is_helpful: boolean;
    citation_accuracy_score?: number;
    comments?: string;
  }): Promise<{ id: string }> {
    return this.request<{ id: string }>("/knowledge/feedback", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  // --- Weather ---
  async getFarmWeather(farmId: string): Promise<FarmWeatherReport> {
    return this.request<FarmWeatherReport>(`/farms/${farmId}/weather`);
  }

  // ================= STAGE 7: RISKCAST API =================

  async getFarmRiskOverview(farmId: string): Promise<FarmRiskOverview> {
    return this.request<FarmRiskOverview>(`/riskcast/farms/${farmId}/overview`);
  }

  async evaluatePlotRisk(plotId: string): Promise<RiskAssessment> {
    return this.request<RiskAssessment>(`/riskcast/evaluate/${plotId}`, {
      method: "POST",
    });
  }

  async listRiskAlerts(farmId: string): Promise<RiskAlert[]> {
    return this.request<RiskAlert[]>(`/riskcast/alerts?farm_id=${farmId}`);
  }

  async acknowledgeRiskAlert(alertId: string): Promise<RiskAlert> {
    return this.request<RiskAlert>(`/riskcast/alerts/${alertId}/acknowledge`, {
      method: "POST",
    });
  }

  async dismissRiskAlert(alertId: string): Promise<RiskAlert> {
    return this.request<RiskAlert>(`/riskcast/alerts/${alertId}/dismiss`, {
      method: "POST",
    });
  }

  async listRiskRules(crop?: string): Promise<RiskRule[]> {
    const query = crop ? `?crop=${crop}` : "";
    return this.request<RiskRule[]>(`/riskcast/rules${query}`);
  }

  // ================= STAGE 7: EXPERTCONNECT API =================

  async applyForExpert(data: {
    registration_number?: string;
    highest_degree: string;
    institution: string;
    specializations?: string[];
    districts_covered?: string[];
  }): Promise<ExpertProfile> {
    return this.request<ExpertProfile>("/expertconnect/apply", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async getMyExpertProfile(): Promise<ExpertProfile> {
    return this.request<ExpertProfile>("/expertconnect/profile/me");
  }

  async listExpertCases(params?: {
    status?: string;
    crop_id?: string;
    priority?: string;
  }): Promise<ExpertCaseItem[]> {
    const query = new URLSearchParams(params as any).toString();
    return this.request<ExpertCaseItem[]>(`/expertconnect/cases${query ? `?${query}` : ""}`);
  }

  async claimExpertCase(caseId: string): Promise<ExpertCaseItem> {
    return this.request<ExpertCaseItem>(`/expertconnect/cases/${caseId}/claim`, {
      method: "POST",
    });
  }

  async getExpertCaseDossier(caseId: string): Promise<ExpertCaseDossier> {
    return this.request<ExpertCaseDossier>(`/expertconnect/cases/${caseId}`);
  }

  async submitExpertAssessment(
    caseId: string,
    data: {
      confirmed_crop: string;
      primary_condition: string;
      differential_diagnoses?: string[];
      confidence_rating: number;
      urgency_level: string;
      management_plan: string;
      ipm_strategy: string;
      cibrc_advisories: string;
    }
  ): Promise<ExpertAssessment> {
    return this.request<ExpertAssessment>(`/expertconnect/cases/${caseId}/assess`, {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async reviseExpertAssessment(
    caseId: string,
    data: {
      confirmed_crop: string;
      primary_condition: string;
      differential_diagnoses?: string[];
      confidence_rating: number;
      urgency_level: string;
      management_plan: string;
      ipm_strategy: string;
      cibrc_advisories: string;
      revision_reason: string;
    }
  ): Promise<ExpertAssessment> {
    return this.request<ExpertAssessment>(`/expertconnect/cases/${caseId}/assess`, {
      method: "PUT",
      body: JSON.stringify(data),
    });
  }

  async getExpertAssessmentRevisions(caseId: string): Promise<ExpertAssessmentRevision[]> {
    return this.request<ExpertAssessmentRevision[]>(`/expertconnect/cases/${caseId}/revisions`);
  }

  // ================= STAGE 7: INTERVENTIONS API =================

  async createIntervention(data: {
    plot_id: string;
    category: "BIOLOGICAL" | "CHEMICAL" | "CULTURAL" | "IRRIGATION" | "FERTILIZER";
    trade_name: string;
    active_ingredient?: string;
    dosage: number;
    unit?: string;
    application_method: string;
    application_date: string;
    target_condition?: string;
    phi_days?: number;
    rei_hours?: number;
    notes?: string;
  }): Promise<InterventionRecord> {
    return this.request<InterventionRecord>("/interventions/", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async listPlotInterventions(plotId: string): Promise<InterventionRecord[]> {
    return this.request<InterventionRecord[]>(`/interventions/plots/${plotId}`);
  }

  async getIntervention(interventionId: string): Promise<InterventionRecord> {
    return this.request<InterventionRecord>(`/interventions/${interventionId}`);
  }

  async recordInterventionOutcome(
    interventionId: string,
    data: {
      follow_up_observation_id: string;
      evaluation_date: string;
      observed_status: "IMPROVING" | "STABLE" | "WORSENING" | "INCONCLUSIVE";
      visual_change_notes: string;
      confounding_factors?: string;
      farmer_assessment?: string;
    }
  ): Promise<OutcomeObservation> {
    return this.request<OutcomeObservation>(`/interventions/${interventionId}/outcomes`, {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async getInterventionTimeline(interventionId: string): Promise<InterventionTimeline> {
    return this.request<InterventionTimeline>(`/interventions/${interventionId}/timeline`);
  }

  async getSystemInfo(): Promise<{
    project_name: string;
    description: string;
    target_geography: string;
    supported_crops: string[];
    supported_languages: string[];
    version: string;
    status: string;
  }> {
    return this.request("/system/info");
  }

  async getSystemObservability(): Promise<{
    service: string;
    version: string;
    environment: string;
    database_pool: Record<string, number>;
    supported_crops: string[];
    supported_languages: string[];
    storage_provider: string;
    status: string;
  }> {
    return this.request("/system/observability");
  }

  // ==========================================
  // STAGE 9: PRECISION AGRICULTURE & INTELLIGENCE
  // ==========================================

  async savePlotGeometry(plotId: string, coordinates: number[][][]): Promise<PlotGeometry> {
    return this.request<PlotGeometry>(`/geospatial/plots/${plotId}/geometry`, {
      method: "POST",
      body: JSON.stringify({ type: "Polygon", coordinates }),
    });
  }

  async getPlotGeometry(plotId: string): Promise<PlotGeometry> {
    return this.request<PlotGeometry>(`/geospatial/plots/${plotId}/geometry`);
  }

  async updateLocationPermission(
    farmId: string,
    granularity: "EXACT_BOUNDARY" | "COARSE_VILLAGE" | "REVOKED",
    notes?: string
  ): Promise<LocationPermission> {
    return this.request<LocationPermission>(`/geospatial/farms/${farmId}/permissions`, {
      method: "POST",
      body: JSON.stringify({ granularity, notes }),
    });
  }

  async getSatelliteTimeSeries(plotId: string, days = 60): Promise<SatelliteTimeSeries> {
    return this.request<SatelliteTimeSeries>(`/satellite/plots/${plotId}/time-series?days=${days}`);
  }

  async getLatestSatelliteObservation(plotId: string): Promise<any> {
    return this.request(`/satellite/plots/${plotId}/latest`);
  }

  async registerSensorDevice(
    farmId: string,
    data: { device_serial_number: string; device_category: string; plot_id?: string; firmware_version?: string }
  ): Promise<SensorDevice> {
    return this.request<SensorDevice>(`/sense/farms/${farmId}/devices`, {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async listFarmSensorDevices(farmId: string): Promise<SensorDevice[]> {
    return this.request<SensorDevice[]>(`/sense/farms/${farmId}/devices`);
  }

  async getPlotSensorTelemetry(plotId: string, hours = 48): Promise<SensorPlotTelemetryHistory> {
    return this.request<SensorPlotTelemetryHistory>(`/sense/plots/${plotId}/telemetry?hours=${hours}`);
  }

  async getPlotFusionAssessment(plotId: string): Promise<FusionExplanation> {
    return this.request<FusionExplanation>(`/fusion/plots/${plotId}/assessment`);
  }

  async recordHarvestMeasurement(
    plotId: string,
    data: {
      season_id: string;
      harvest_date: string;
      yield_quintals_per_acre: number;
      total_harvest_kg: number;
      provenance_tier: string;
      verification_document_url?: string;
      notes?: string;
    }
  ): Promise<HarvestMeasurement> {
    return this.request<HarvestMeasurement>(`/predict/plots/${plotId}/harvests`, {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async getYieldForecast(plotId: string, threshold = 50): Promise<YieldForecastResponse> {
    return this.request<YieldForecastResponse>(`/predict/plots/${plotId}/forecast?threshold=${threshold}`);
  }

  async traverseKnowledgeGraph(entity: string): Promise<KnowledgeTraversalResponse> {
    return this.request<KnowledgeTraversalResponse>(`/knowledge-graph/traverse?entity=${encodeURIComponent(entity)}`);
  }
}

export const api = new ApiClient();
