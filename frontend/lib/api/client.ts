import {
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
} from "./types";

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
    full_name: string;
    password: string;
    email?: string;
    language_preference?: string;
    role?: string;
  }): Promise<UserSummary> {
    return this.request<UserSummary>("/auth/register", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async getCurrentUser(): Promise<UserSummary> {
    return this.request<UserSummary>("/auth/me");
  }

  // --- Farms ---
  async listFarms(): Promise<Farm[]> {
    return this.request<Farm[]>("/farms/");
  }

  async getFarm(farmId: string): Promise<Farm> {
    return this.request<Farm>(`/farms/${farmId}`);
  }

  async createFarm(data: {
    name: string;
    district: string;
    mandal: string;
    village: string;
    total_acreage?: number;
  }): Promise<Farm> {
    return this.request<Farm>("/farms/", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  // --- Plots ---
  async listPlots(farmId: string): Promise<Plot[]> {
    return this.request<Plot[]>(`/farms/${farmId}/plots`);
  }

  async createPlot(
    farmId: string,
    data: { name: string; soil_type: string; irrigation_source: string; acreage?: number }
  ): Promise<Plot> {
    return this.request<Plot>(`/farms/${farmId}/plots`, {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  // --- Crop Seasons ---
  async listCropSeasons(plotId: string): Promise<CropSeason[]> {
    return this.request<CropSeason[]>(`/plots/${plotId}/seasons`);
  }

  async createCropSeason(
    plotId: string,
    data: { crop_id: string; season_type: string; sowing_date: string; current_stage?: string }
  ): Promise<CropSeason> {
    return this.request<CropSeason>(`/plots/${plotId}/seasons`, {
      method: "POST",
      body: JSON.stringify({ ...data, plot_id: plotId }),
    });
  }

  // --- Observations ---
  async listObservations(farmId: string, limit: number = 20): Promise<Observation[]> {
    return this.request<Observation[]>(`/observations/?farm_id=${encodeURIComponent(farmId)}&limit=${limit}`);
  }

  async getObservation(obsId: string): Promise<Observation> {
    return this.request<Observation>(`/observations/${obsId}`);
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
    file: File | Blob,
    filename: string = "foliar.jpg",
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
    return `${BASE_URL}/api/v1/observations/${obsId}/media/${mediaId}/file`;
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
}

export const api = new ApiClient();
