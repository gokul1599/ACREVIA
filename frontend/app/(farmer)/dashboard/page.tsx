"use client";

import React, { useState, useEffect, useCallback } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth/context";
import { useTranslation } from "@/lib/localization/context";
import { api } from "@/lib/api/client";
import { Farm, Plot, CropSeason, Observation, FarmWeatherReport } from "@/lib/api/types";
import { Button } from "@/components/ui/Button";
import {
  Camera,
  BotMessageSquare,
  Activity,
  Layers,
  CloudSun,
  AlertTriangle,
  ArrowRight,
  Droplets,
  Wind,
  Thermometer,
  Calendar,
} from "lucide-react";

export default function DashboardPage() {
  const router = useRouter();
  const { user, isAuthenticated, isLoading: authLoading } = useAuth();
  const { t } = useTranslation();

  const [farms, setFarms] = useState<Farm[]>([]);
  const [selectedFarm, setSelectedFarm] = useState<Farm | null>(null);
  const [plots, setPlots] = useState<Plot[]>([]);
  const [cropSeasons, setCropSeasons] = useState<CropSeason[]>([]);
  const [observations, setObservations] = useState<Observation[]>([]);
  const [weather, setWeather] = useState<FarmWeatherReport | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [weatherLoading, setWeatherLoading] = useState<boolean>(false);

  const loadFarmData = useCallback(async (farmId: string) => {
    try {
      setWeatherLoading(true);
      const [plotList, obsList, weatherData] = await Promise.allSettled([
        api.listPlots(farmId),
        api.listObservations(farmId, 5),
        api.getFarmWeather(farmId),
      ]);

      if (plotList.status === "fulfilled") {
        setPlots(plotList.value);
        if (plotList.value.length > 0) {
          const seasons = await api.listCropSeasons(plotList.value[0].id).catch(() => []);
          setCropSeasons(seasons);
        }
      }

      if (obsList.status === "fulfilled") {
        setObservations(obsList.value);
      }

      if (weatherData.status === "fulfilled") {
        setWeather(weatherData.value);
      } else {
        setWeather(null);
      }
    } finally {
      setWeatherLoading(false);
    }
  }, []);

  const loadInitialData = useCallback(async () => {
    setIsLoading(true);
    try {
      const userFarms = await api.listFarms();
      setFarms(userFarms);
      if (userFarms.length > 0) {
        setSelectedFarm(userFarms[0]);
        await loadFarmData(userFarms[0].id);
      } else {
        router.push("/onboarding");
      }
    } catch (err) {
      console.warn("Failed to load farms", err);
    } finally {
      setIsLoading(false);
    }
  }, [loadFarmData, router]);

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push("/login");
      return;
    }
    if (isAuthenticated) {
      loadInitialData();
    }
  }, [authLoading, isAuthenticated, router, loadInitialData]);

  if (isLoading) {
    return (
      <div className="max-w-4xl mx-auto p-4 space-y-4 animate-pulse">
        <div className="h-28 bg-white rounded-2xl border border-[#E5E0D8]" />
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="h-24 bg-white rounded-xl border border-[#E5E0D8]" />
          ))}
        </div>
        <div className="h-44 bg-white rounded-2xl border border-[#E5E0D8]" />
      </div>
    );
  }

  const primarySeason = cropSeasons[0] || null;

  return (
    <div className="max-w-4xl mx-auto p-4 space-y-6">
      {/* 1. Welcome & Farm Context Banner */}
      <div className="bg-[#1E3A2B] text-white rounded-2xl p-6 shadow-card relative overflow-hidden">
        <div className="relative z-10">
          <span className="text-xs font-semibold text-[#86EFAC] uppercase tracking-wider block mb-1">
            {t.dashboard.welcome}, {user?.full_name || "Farmer"}
          </span>
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div>
              <h1 className="text-2xl font-bold tracking-tight">
                {selectedFarm?.name || "My Farm"}
              </h1>
              <p className="text-xs text-[#E8F0EC] mt-0.5">
                {selectedFarm?.village}, {selectedFarm?.mandal} mandal, {selectedFarm?.district} district • {selectedFarm?.total_acreage} Acres
              </p>
            </div>

            {farms.length > 1 && (
              <select
                value={selectedFarm?.id}
                onChange={(e) => {
                  const f = farms.find((item) => item.id === e.target.value);
                  if (f) {
                    setSelectedFarm(f);
                    loadFarmData(f.id);
                  }
                }}
                className="bg-[#284D3A] text-white border border-[#3E795C] px-3 py-1.5 rounded-lg text-xs font-medium outline-none"
              >
                {farms.map((f) => (
                  <option key={f.id} value={f.id}>
                    {f.name}
                  </option>
                ))}
              </select>
            )}
          </div>

          {primarySeason && (
            <div className="mt-4 pt-4 border-t border-[#284D3A] flex flex-wrap items-center gap-3 text-xs">
              <span className="px-2.5 py-1 bg-[#284D3A] rounded-md font-semibold text-[#86EFAC] capitalize">
                {primarySeason.crop_id} ({primarySeason.season_type})
              </span>
              <span className="text-[#E8F0EC]">
                Stage: <strong className="text-white capitalize">{primarySeason.current_stage}</strong>
              </span>
              <span className="text-[#E8F0EC]">
                Sown: {primarySeason.sowing_date}
              </span>
            </div>
          )}
        </div>
      </div>

      {/* 2. Quick Action Grid */}
      <div>
        <h2 className="text-xs font-bold text-[#556059] uppercase tracking-wider mb-3">
          {t.dashboard.quickActions}
        </h2>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <Link
            href="/diagnosis"
            className="p-4 bg-white rounded-xl border border-[#E5E0D8] shadow-xs hover:border-[#1E3A2B] hover:shadow-card transition-all flex flex-col justify-between group touch-target"
          >
            <div className="w-10 h-10 rounded-xl bg-[#E8F0EC] text-[#1E3A2B] flex items-center justify-center mb-3 group-hover:bg-[#1E3A2B] group-hover:text-white transition-colors">
              <Camera className="w-5 h-5" />
            </div>
            <div>
              <span className="font-bold text-sm text-[#1A241F] block">{t.dashboard.scanCrop}</span>
              <span className="text-[11px] text-[#78857E]">CropVision AI</span>
            </div>
          </Link>

          <Link
            href="/knowledge"
            className="p-4 bg-white rounded-xl border border-[#E5E0D8] shadow-xs hover:border-[#1E3A2B] hover:shadow-card transition-all flex flex-col justify-between group touch-target"
          >
            <div className="w-10 h-10 rounded-xl bg-[#E8F0EC] text-[#1E3A2B] flex items-center justify-center mb-3 group-hover:bg-[#1E3A2B] group-hover:text-white transition-colors">
              <BotMessageSquare className="w-5 h-5" />
            </div>
            <div>
              <span className="font-bold text-sm text-[#1A241F] block">{t.dashboard.askAssistant}</span>
              <span className="text-[11px] text-[#78857E]">KrishiBrain RAG</span>
            </div>
          </Link>

          <Link
            href="/croppulse"
            className="p-4 bg-white rounded-xl border border-[#E5E0D8] shadow-xs hover:border-[#1E3A2B] hover:shadow-card transition-all flex flex-col justify-between group touch-target"
          >
            <div className="w-10 h-10 rounded-xl bg-[#E8F0EC] text-[#1E3A2B] flex items-center justify-center mb-3 group-hover:bg-[#1E3A2B] group-hover:text-white transition-colors">
              <Activity className="w-5 h-5" />
            </div>
            <div>
              <span className="font-bold text-sm text-[#1A241F] block">{t.dashboard.addObservation}</span>
              <span className="text-[11px] text-[#78857E]">CropPulse</span>
            </div>
          </Link>

          <Link
            href="/crops"
            className="p-4 bg-white rounded-xl border border-[#E5E0D8] shadow-xs hover:border-[#1E3A2B] hover:shadow-card transition-all flex flex-col justify-between group touch-target"
          >
            <div className="w-10 h-10 rounded-xl bg-[#E8F0EC] text-[#1E3A2B] flex items-center justify-center mb-3 group-hover:bg-[#1E3A2B] group-hover:text-white transition-colors">
              <Layers className="w-5 h-5" />
            </div>
            <div>
              <span className="font-bold text-sm text-[#1A241F] block">{t.nav.crops}</span>
              <span className="text-[11px] text-[#78857E]">{plots.length} Plots</span>
            </div>
          </Link>
        </div>
      </div>

      {/* 3. Agrometeorological Risk Card */}
      <div className="bg-white rounded-2xl border border-[#E5E0D8] p-5 shadow-card">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <CloudSun className="w-5 h-5 text-[#1E3A2B]" />
            <h2 className="font-bold text-base text-[#1E3A2B]">{t.dashboard.weatherTitle}</h2>
          </div>
          {weather?.pest_risk_level && (
            <span
              className={`px-2.5 py-1 rounded-full text-xs font-bold uppercase ${
                weather.pest_risk_level === "HIGH"
                  ? "bg-[#FFE3E3] text-[#C92A2A]"
                  : weather.pest_risk_level === "MODERATE"
                  ? "bg-[#FEF3C7] text-[#D97706]"
                  : "bg-[#DCFCE7] text-[#15803D]"
              }`}
            >
              {t.dashboard.pestRisk}: {weather.pest_risk_level}
            </span>
          )}
        </div>

        {weatherLoading ? (
          <div className="h-20 flex items-center justify-center text-xs text-[#78857E]">
            Updating meteorological indicators...
          </div>
        ) : weather ? (
          <div className="space-y-4">
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 pt-2 border-t border-[#E5E0D8]">
              <div className="p-2.5 bg-[#FAFAF7] rounded-xl flex items-center gap-2">
                <Thermometer className="w-4 h-4 text-[#D97706]" />
                <div>
                  <span className="text-[10px] text-[#78857E] block">{t.dashboard.temperature}</span>
                  <span className="font-bold text-sm text-[#1A241F]">{weather.temperature}°C</span>
                </div>
              </div>
              <div className="p-2.5 bg-[#FAFAF7] rounded-xl flex items-center gap-2">
                <Droplets className="w-4 h-4 text-[#1D4ED8]" />
                <div>
                  <span className="text-[10px] text-[#78857E] block">{t.dashboard.humidity}</span>
                  <span className="font-bold text-sm text-[#1A241F]">{weather.humidity}%</span>
                </div>
              </div>
              <div className="p-2.5 bg-[#FAFAF7] rounded-xl flex items-center gap-2">
                <CloudSun className="w-4 h-4 text-[#33634B]" />
                <div>
                  <span className="text-[10px] text-[#78857E] block">{t.dashboard.precipitation}</span>
                  <span className="font-bold text-sm text-[#1A241F]">{weather.precipitation} mm</span>
                </div>
              </div>
              <div className="p-2.5 bg-[#FAFAF7] rounded-xl flex items-center gap-2">
                <Wind className="w-4 h-4 text-[#70533C]" />
                <div>
                  <span className="text-[10px] text-[#78857E] block">{t.dashboard.windSpeed}</span>
                  <span className="font-bold text-sm text-[#1A241F]">{weather.wind_speed} km/h</span>
                </div>
              </div>
            </div>

            <div className="p-3 bg-[#E8F0EC] rounded-xl text-xs text-[#1E3A2B] leading-relaxed flex items-start gap-2">
              <AlertTriangle className="w-4 h-4 text-[#1E3A2B] shrink-0 mt-0.5" />
              <div>
                <strong>{t.dashboard.advisory}:</strong> {weather.advisory}
              </div>
            </div>
          </div>
        ) : (
          <p className="text-xs text-[#78857E] italic">{t.dashboard.weatherUnavailable}</p>
        )}
      </div>

      {/* 4. Recent Field Observations */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <h2 className="text-xs font-bold text-[#556059] uppercase tracking-wider">
            {t.dashboard.recentObservations}
          </h2>
          <Link href="/croppulse" className="text-xs font-semibold text-[#1E3A2B] hover:underline flex items-center gap-1">
            <span>View All</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        {observations.length === 0 ? (
          <div className="p-6 bg-white rounded-2xl border border-[#E5E0D8] text-center space-y-3">
            <Camera className="w-8 h-8 text-[#C8C0B5] mx-auto" />
            <p className="text-xs text-[#556059] max-w-sm mx-auto">{t.dashboard.noObservations}</p>
            <Link href="/diagnosis">
              <Button size="sm" variant="primary" icon={<Camera className="w-4 h-4" />}>
                {t.dashboard.scanCrop}
              </Button>
            </Link>
          </div>
        ) : (
          <div className="space-y-2">
            {observations.map((obs) => (
              <div
                key={obs.id}
                className="p-4 bg-white rounded-xl border border-[#E5E0D8] shadow-xs flex items-center justify-between gap-3"
              >
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-[#FAFAF7] border border-[#E5E0D8] flex items-center justify-center shrink-0">
                    <Calendar className="w-5 h-5 text-[#1E3A2B]" />
                  </div>
                  <div>
                    <span className="font-semibold text-sm text-[#1A241F] block">
                      {obs.notes || "Field Observation"}
                    </span>
                    <span className="text-[11px] text-[#78857E]">
                      {new Date(obs.created_at).toLocaleDateString()} • {obs.media.length} Photos
                    </span>
                  </div>
                </div>

                <Link href={`/diagnosis?obs=${obs.id}`}>
                  <Button size="sm" variant="secondary">
                    View
                  </Button>
                </Link>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
