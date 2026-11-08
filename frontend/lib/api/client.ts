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
  FarmTwin,
  TwinSnapshotSummary,
  DataCompleteness,
  SimulationScenario,
  ScenarioComparison,
  OptimizationProblem,
  CropCalendarDefinition,
  CropTask,
  DecisionRecord,
  DecisionFeedback,
  FarmExpense,
  FinancialCorrection,
  SaleTransaction,
  MarketPriceObservation,
  MarketCompareResponse,
  HarvestPlan,
  HarvestSession,
  ProduceLot,
  LotMovement,
  ProduceLotPublic,
  QualityMeasurement,
  StorageLocation,
  StorageLot,
  EconomicsSummary,
  CropLossEvidencePackage,
  Community,
  CommunityPost,
  CommunityComment,
  KnowledgeContribution,
  AgriculturalOrganization,
  CollectiveActivity,
  CollectiveAggregateAnalytics,
  ResearchProject,
  ResearchConsent,
  LearningResource,
  TrainingEvent,
  RegionalSignal,
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

  // Stage 10 Methods
  async getFarmTwin(farmId: string): Promise<FarmTwin> {
    return this.request<FarmTwin>(`/twin/farms/${farmId}`);
  }

  async getTwinCompleteness(farmId: string): Promise<DataCompleteness> {
    return this.request<DataCompleteness>(`/twin/farms/${farmId}/completeness`);
  }

  async reconcileTwin(farmId: string): Promise<any> {
    return this.request<any>(`/twin/farms/${farmId}/reconcile`, { method: "POST" });
  }

  async listTwinSnapshots(farmId: string, limit = 10): Promise<TwinSnapshotSummary[]> {
    return this.request<TwinSnapshotSummary[]>(`/twin/farms/${farmId}/snapshots?limit=${limit}`);
  }

  async runSimulation(data: {
    plot_id: string;
    crop_season_id?: string;
    scenario_name: string;
    scenario_type?: string;
    baseline_snapshot_id?: string;
    input_parameters?: Record<string, any>;
    farmer_assumptions?: Record<string, any>;
    constraints?: Record<string, any>;
  }): Promise<SimulationScenario> {
    return this.request<SimulationScenario>("/simulations", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async getSimulation(id: string): Promise<SimulationScenario> {
    return this.request<SimulationScenario>(`/simulations/${id}`);
  }

  async compareSimulations(scenarioIds: string[]): Promise<ScenarioComparison> {
    return this.request<ScenarioComparison>("/simulations/compare", {
      method: "POST",
      body: JSON.stringify({ scenario_ids: scenarioIds }),
    });
  }

  async solveOptimizationProblem(data: {
    farm_id: string;
    plot_id?: string;
    problem_type?: string;
    objective_type?: string;
    decision_variables?: Record<string, any>;
    hard_constraints?: Record<string, any>;
    soft_constraints?: Record<string, any>;
  }): Promise<OptimizationProblem> {
    return this.request<OptimizationProblem>("/optimization/problems", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async getOptimizationProblem(id: string): Promise<OptimizationProblem> {
    return this.request<OptimizationProblem>(`/optimization/problems/${id}`);
  }

  async listCropCalendars(cropName?: string, zone?: string): Promise<CropCalendarDefinition[]> {
    const params = new URLSearchParams();
    if (cropName) params.append("crop_name", cropName);
    if (zone) params.append("zone", zone);
    return this.request<CropCalendarDefinition[]>(`/planning/calendars?${params.toString()}`);
  }

  async createCropTask(data: {
    crop_season_id: string;
    plot_id: string;
    calendar_def_id?: string;
    task_name: string;
    task_category?: string;
    due_date: string;
    notes?: string;
  }): Promise<CropTask> {
    return this.request<CropTask>("/planning/tasks", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async listCropTasks(params: { plot_id?: string; crop_season_id?: string } = {}): Promise<CropTask[]> {
    const query = new URLSearchParams();
    if (params.plot_id) query.append("plot_id", params.plot_id);
    if (params.crop_season_id) query.append("crop_season_id", params.crop_season_id);
    return this.request<CropTask[]>(`/planning/tasks?${query.toString()}`);
  }

  async completeCropTask(
    taskId: string,
    data: {
      actual_date?: string;
      labor_hours?: number;
      materials_used?: Array<Record<string, any>>;
      observations?: string;
    }
  ): Promise<CropTask> {
    return this.request<CropTask>(`/planning/tasks/${taskId}/complete`, {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async analyzeDecision(data: {
    plot_id: string;
    query_text: string;
    decision_category?: string;
  }): Promise<DecisionRecord> {
    return this.request<DecisionRecord>("/decisions/analyze", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async getDecisionRecord(id: string): Promise<DecisionRecord> {
    return this.request<DecisionRecord>(`/decisions/${id}`);
  }

  async recordDecisionFeedback(
    id: string,
    data: {
      farmer_action_taken: string;
      farmer_rating?: number;
      feedback_notes?: string;
      observed_outcome?: string;
    }
  ): Promise<DecisionFeedback> {
    return this.request<DecisionFeedback>(`/decisions/${id}/feedback`, {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  // ==========================================
  // STAGE 11: Agricultural Economics, Market, Harvest & Traceability Methods
  // ==========================================

  async createExpense(data: {
    farm_id: string;
    plot_id?: string;
    crop_season_id?: string;
    category: string;
    description: string;
    amount: string | number;
    currency?: string;
    quantity?: number;
    unit?: string;
    transaction_date: string;
    payment_status?: string;
    payment_method?: string;
    vendor_name?: string;
    receipt_url?: string;
  }): Promise<FarmExpense> {
    return this.request<FarmExpense>("/ledger/expenses", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async getExpenses(params: {
    farm_id: string;
    crop_season_id?: string;
    category?: string;
    limit?: number;
    offset?: number;
  }): Promise<FarmExpense[]> {
    const query = new URLSearchParams();
    query.set("farm_id", params.farm_id);
    if (params.crop_season_id) query.set("crop_season_id", params.crop_season_id);
    if (params.category) query.set("category", params.category);
    if (params.limit) query.set("limit", params.limit.toString());
    if (params.offset) query.set("offset", params.offset.toString());
    return this.request<FarmExpense[]>(`/ledger/expenses?${query.toString()}`);
  }

  async correctExpense(
    expenseId: string,
    data: { new_amount: string | number; reason: string }
  ): Promise<FarmExpense> {
    return this.request<FarmExpense>(`/ledger/expenses/${expenseId}/correct`, {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async createSaleTransaction(data: {
    crop_season_id: string;
    lot_id?: string;
    buyer_name: string;
    buyer_type?: string;
    quantity_sold: string | number;
    unit?: string;
    price_per_unit: string | number;
    gross_amount: string | number;
    deductions_amount?: string | number;
    sale_date: string;
    payment_status?: string;
    notes?: string;
  }): Promise<SaleTransaction> {
    return this.request<SaleTransaction>("/ledger/sales", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async getSales(cropSeasonId: string): Promise<SaleTransaction[]> {
    return this.request<SaleTransaction[]>(`/ledger/sales?crop_season_id=${encodeURIComponent(cropSeasonId)}`);
  }

  async getMarketPrices(params?: {
    crop_id?: string;
    district?: string;
    limit?: number;
  }): Promise<MarketPriceObservation[]> {
    const query = new URLSearchParams();
    if (params?.crop_id) query.set("crop_id", params.crop_id);
    if (params?.district) query.set("district", params.district);
    if (params?.limit) query.set("limit", params.limit.toString());
    const qs = query.toString() ? `?${query.toString()}` : "";
    return this.request<MarketPriceObservation[]>(`/market/prices${qs}`);
  }

  async compareMarketRealizations(params: {
    crop_id: string;
    quantity_quintals: string | number;
    plot_id?: string;
  }): Promise<MarketCompareResponse> {
    const query = new URLSearchParams();
    query.set("crop_id", params.crop_id);
    query.set("quantity_quintals", params.quantity_quintals.toString());
    if (params.plot_id) query.set("plot_id", params.plot_id);
    return this.request<MarketCompareResponse>(`/market/compare?${query.toString()}`);
  }

  async createHarvestPlan(data: {
    plot_id: string;
    crop_season_id: string;
    planned_start_date: string;
    planned_end_date: string;
    estimated_quantity_quintals: string | number;
    harvest_method?: string;
  }): Promise<HarvestPlan> {
    return this.request<HarvestPlan>("/harvest/plans", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async getHarvestPlans(cropSeasonId: string): Promise<HarvestPlan[]> {
    return this.request<HarvestPlan[]>(`/harvest/plans?crop_season_id=${encodeURIComponent(cropSeasonId)}`);
  }

  async createHarvestSession(data: {
    plot_id: string;
    crop_season_id: string;
    harvest_plan_id?: string;
    picking_number?: number;
    harvest_date: string;
    harvested_quantity: string | number;
    unit?: string;
    quantity_type?: string;
    loss_quantity?: string | number;
    notes?: string;
  }): Promise<HarvestSession> {
    return this.request<HarvestSession>("/harvest/sessions", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async getHarvestSessions(cropSeasonId: string): Promise<HarvestSession[]> {
    return this.request<HarvestSession[]>(`/harvest/sessions?crop_season_id=${encodeURIComponent(cropSeasonId)}`);
  }

  async recordQualityMeasurement(data: {
    session_id?: string;
    lot_id?: string;
    parameter_name: string;
    measured_value: string | number;
    unit: string;
    measurement_method?: string;
    instrument_details?: string;
  }): Promise<QualityMeasurement> {
    return this.request<QualityMeasurement>("/quality/measurements", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async getLotQualityMeasurements(lotId: string): Promise<QualityMeasurement[]> {
    return this.request<QualityMeasurement[]>(`/quality/measurements/${encodeURIComponent(lotId)}`);
  }

  async createStorageLocation(data: {
    farm_id: string;
    name: string;
    storage_type: string;
    capacity_quintals: string | number;
    district: string;
    is_temperature_controlled?: boolean;
  }): Promise<StorageLocation> {
    return this.request<StorageLocation>("/quality/storage/locations", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async assignToStorage(data: {
    lot_id: string;
    storage_location_id: string;
    quantity_stored: string | number;
    unit?: string;
    entry_date: string;
  }): Promise<StorageLot> {
    return this.request<StorageLot>("/quality/storage/lots", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async getProduceLot(lotId: string): Promise<ProduceLot> {
    return this.request<ProduceLot>(`/trace/lots/${encodeURIComponent(lotId)}`);
  }

  async recordLotMovement(
    lotId: string,
    data: {
      movement_type: string;
      source_location: string;
      destination_location: string;
      quantity_transferred: string | number;
      unit?: string;
      actor_name: string;
      notes?: string;
    }
  ): Promise<LotMovement> {
    return this.request<LotMovement>(`/trace/lots/${encodeURIComponent(lotId)}/movements`, {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async verifyPublicQrCode(qrToken: string): Promise<ProduceLotPublic> {
    return this.request<ProduceLotPublic>(`/trace/public/${encodeURIComponent(qrToken)}`);
  }

  async getSeasonEconomics(cropSeasonId: string): Promise<EconomicsSummary> {
    return this.request<EconomicsSummary>(`/economics/seasons/${encodeURIComponent(cropSeasonId)}`);
  }

  async createLossEvidencePackage(data: {
    farm_id: string;
    plot_id: string;
    crop_season_id: string;
    incident_date: string;
    incident_type: string;
    notes?: string;
  }): Promise<CropLossEvidencePackage> {
    return this.request<CropLossEvidencePackage>("/economics/evidence-package", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  // ================= Stage 12: Collaborative Agricultural Intelligence =================

  async listCommunities(params?: { category?: string; crop_id?: string }): Promise<Community[]> {
    const qs = new URLSearchParams();
    if (params?.category) qs.set("category", params.category);
    if (params?.crop_id) qs.set("crop_id", params.crop_id);
    const query = qs.toString() ? `?${qs.toString()}` : "";
    return this.request<Community[]>(`/connect/communities${query}`);
  }

  async joinCommunity(communityId: string): Promise<{ id: string; community_id: string; user_id: string; role: string }> {
    return this.request(`/connect/communities/${encodeURIComponent(communityId)}/join`, {
      method: "POST",
    });
  }

  async createCommunityPost(
    communityId: string,
    data: {
      title: string;
      content: string;
      post_type?: string;
      language?: string;
      crop_id?: string;
      growth_stage?: string;
    }
  ): Promise<CommunityPost> {
    return this.request<CommunityPost>(`/connect/communities/${encodeURIComponent(communityId)}/posts`, {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async listCommunityPosts(
    communityId: string,
    params?: { post_type?: string; limit?: number; offset?: number }
  ): Promise<CommunityPost[]> {
    const qs = new URLSearchParams();
    if (params?.post_type) qs.set("post_type", params.post_type);
    if (params?.limit) qs.set("limit", String(params.limit));
    if (params?.offset) qs.set("offset", String(params.offset));
    const query = qs.toString() ? `?${qs.toString()}` : "";
    return this.request<CommunityPost[]>(`/connect/communities/${encodeURIComponent(communityId)}/posts${query}`);
  }

  async addCommunityComment(postId: string, content: string): Promise<CommunityComment> {
    return this.request<CommunityComment>(`/connect/posts/${encodeURIComponent(postId)}/comments`, {
      method: "POST",
      body: JSON.stringify({ content }),
    });
  }

  async votePostHelpful(postId: string): Promise<{ post_id: string; helpful_count: number; message: string }> {
    return this.request(`/connect/posts/${encodeURIComponent(postId)}/helpful`, {
      method: "POST",
    });
  }

  async submitKnowledgeContribution(data: {
    contribution_type: string;
    title: string;
    description: string;
    original_language?: string;
    crop_id?: string;
    geographic_scope?: string;
    growth_stage?: string;
    evidence_references?: string[];
  }): Promise<KnowledgeContribution> {
    return this.request<KnowledgeContribution>("/commons/contributions", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async listKnowledgeContributions(params?: { status?: string; crop_id?: string }): Promise<KnowledgeContribution[]> {
    const qs = new URLSearchParams();
    if (params?.status) qs.set("status", params.status);
    if (params?.crop_id) qs.set("crop_id", params.crop_id);
    const query = qs.toString() ? `?${qs.toString()}` : "";
    return this.request<KnowledgeContribution[]>(`/commons/contributions${query}`);
  }

  async registerOrganization(data: {
    name: string;
    org_type: string;
    registration_number?: string;
    state?: string;
    district: string;
    description?: string;
    contact_email?: string;
    contact_phone?: string;
  }): Promise<AgriculturalOrganization> {
    return this.request<AgriculturalOrganization>("/collectives/organizations", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async listOrganizations(params?: { district?: string; org_type?: string }): Promise<AgriculturalOrganization[]> {
    const qs = new URLSearchParams();
    if (params?.district) qs.set("district", params.district);
    if (params?.org_type) qs.set("org_type", params.org_type);
    const query = qs.toString() ? `?${qs.toString()}` : "";
    return this.request<AgriculturalOrganization[]>(`/collectives/organizations${query}`);
  }

  async getCollectiveAnalytics(orgId: string): Promise<CollectiveAggregateAnalytics> {
    return this.request<CollectiveAggregateAnalytics>(`/collectives/organizations/${encodeURIComponent(orgId)}/analytics`);
  }

  async listResearchProjects(params?: { status?: string }): Promise<ResearchProject[]> {
    const qs = new URLSearchParams();
    if (params?.status) qs.set("status", params.status);
    const query = qs.toString() ? `?${qs.toString()}` : "";
    return this.request<ResearchProject[]>(`/research/projects${query}`);
  }

  async grantResearchConsent(projectId: string, consentScope: string): Promise<ResearchConsent> {
    return this.request<ResearchConsent>(`/research/projects/${encodeURIComponent(projectId)}/consent`, {
      method: "POST",
      body: JSON.stringify({ consent_scope: consentScope, consent_version: "1.0" }),
    });
  }

  async listLearningResources(params?: { crop_id?: string; language?: string; resource_type?: string }): Promise<LearningResource[]> {
    const qs = new URLSearchParams();
    if (params?.crop_id) qs.set("crop_id", params.crop_id);
    if (params?.language) qs.set("language", params.language);
    if (params?.resource_type) qs.set("resource_type", params.resource_type);
    const query = qs.toString() ? `?${qs.toString()}` : "";
    return this.request<LearningResource[]>(`/extension/resources${query}`);
  }

  async registerForTrainingEvent(eventId: string): Promise<{ id: string; event_id: string; user_id: string; attendance_status: string }> {
    return this.request(`/extension/events/${encodeURIComponent(eventId)}/register`, {
      method: "POST",
    });
  }

  async queryRegionalSignals(params?: { district?: string; crop_id?: string; confidence_tier?: string }): Promise<RegionalSignal[]> {
    const qs = new URLSearchParams();
    if (params?.district) qs.set("district", params.district);
    if (params?.crop_id) qs.set("crop_id", params.crop_id);
    if (params?.confidence_tier) qs.set("confidence_tier", params.confidence_tier);
    const query = qs.toString() ? `?${qs.toString()}` : "";
    return this.request<RegionalSignal[]>(`/regional-pulse/signals${query}`);
  }
}

export const api = new ApiClient();
