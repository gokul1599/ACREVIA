"use client";

import React, { useState, useEffect, useCallback } from "react";
import { useTranslation } from "@/lib/localization/context";
import { api } from "@/lib/api/client";
import { Farm, Plot, CropSeason } from "@/lib/api/types";
import { Button } from "@/components/ui/Button";
import {
  Layers,
  Sprout,
  Plus,
  MapPin,
} from "lucide-react";

export default function CropsPage() {
  const { t } = useTranslation();

  const [farms, setFarms] = useState<Farm[]>([]);
  const [selectedFarmId, setSelectedFarmId] = useState<string>("");
  const [plots, setPlots] = useState<Plot[]>([]);
  const [seasonsByPlot, setSeasonsByPlot] = useState<Record<string, CropSeason[]>>({});
  const [isLoading, setIsLoading] = useState<boolean>(true);

  // Add Plot Modal State
  const [showPlotModal, setShowPlotModal] = useState(false);
  const [newPlotName, setNewPlotName] = useState("");
  const [newSoilType, setNewSoilType] = useState<"BLACK_COTTON" | "RED_CHALKA" | "ALLUVIAL" | "LOAMY">("BLACK_COTTON");
  const [newIrrigation, setNewIrrigation] = useState<"BOREWELL" | "CANAL" | "RAINFED" | "DRIP" | "WELL">("BOREWELL");
  const [isCreatingPlot, setIsCreatingPlot] = useState(false);

  const loadFarmPlots = useCallback(async (farmId: string) => {
    setIsLoading(true);
    try {
      const plotList = await api.listPlots(farmId);
      setPlots(plotList);

      const seasonsMap: Record<string, CropSeason[]> = {};
      for (const plot of plotList) {
        const seasons = await api.listCropSeasons(plot.id).catch(() => []);
        seasonsMap[plot.id] = seasons;
      }
      setSeasonsByPlot(seasonsMap);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const loadInitialData = useCallback(async () => {
    try {
      const farmList = await api.listFarms();
      setFarms(farmList);
      if (farmList.length > 0) {
        setSelectedFarmId(farmList[0].id);
        await loadFarmPlots(farmList[0].id);
      } else {
        setIsLoading(false);
      }
    } catch {
      setIsLoading(false);
    }
  }, [loadFarmPlots]);

  useEffect(() => {
    loadInitialData();
  }, [loadInitialData]);

  const handleCreatePlot = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedFarmId || !newPlotName.trim()) return;

    setIsCreatingPlot(true);
    try {
      await api.createPlot(selectedFarmId, {
        name: newPlotName.trim(),
        soil_type: newSoilType,
        irrigation_source: newIrrigation,
      });
      setNewPlotName("");
      setShowPlotModal(false);
      await loadFarmPlots(selectedFarmId);
    } finally {
      setIsCreatingPlot(false);
    }
  };

  const _selectedFarm = farms.find((f) => f.id === selectedFarmId);

  return (
    <div className="max-w-3xl mx-auto p-4 space-y-6">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <div className="w-10 h-10 rounded-xl bg-[#1E3A2B] text-white flex items-center justify-center shadow-xs">
            <Layers className="w-6 h-6 text-[#86EFAC]" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-[#1E3A2B] tracking-tight">{t.nav.crops}</h1>
            <p className="text-xs text-[#556059]">Farm Holdings, Plots & Phenological Crop Seasons</p>
          </div>
        </div>

        <Button
          type="button"
          variant="primary"
          size="md"
          onClick={() => setShowPlotModal(true)}
          icon={<Plus className="w-4 h-4" />}
        >
          Add Plot
        </Button>
      </div>

      {/* Farm Selection Bar */}
      {farms.length > 1 && (
        <div className="flex items-center gap-2 bg-white p-2 rounded-xl border border-[#E5E0D8]">
          <MapPin className="w-4 h-4 text-[#1E3A2B] ml-2" />
          <span className="text-xs font-semibold text-[#78857E]">Farm:</span>
          <select
            value={selectedFarmId}
            onChange={(e) => {
              setSelectedFarmId(e.target.value);
              loadFarmPlots(e.target.value);
            }}
            className="flex-1 bg-transparent text-sm font-bold text-[#1E3A2B] outline-none"
          >
            {farms.map((f) => (
              <option key={f.id} value={f.id}>
                {f.name} ({f.village}, {f.district})
              </option>
            ))}
          </select>
        </div>
      )}

      {/* Add Plot Modal */}
      {showPlotModal && (
        <div className="fixed inset-0 z-50 bg-black/60 flex items-center justify-center p-4 backdrop-blur-xs animate-in fade-in">
          <div className="bg-white rounded-2xl p-6 max-w-md w-full space-y-4 shadow-elevated border border-[#E5E0D8]">
            <h2 className="text-lg font-bold text-[#1E3A2B]">Add Cultivation Plot</h2>
            <form onSubmit={handleCreatePlot} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-[#1A241F] uppercase mb-1">
                  Plot Name
                </label>
                <input
                  type="text"
                  value={newPlotName}
                  onChange={(e) => setNewPlotName(e.target.value)}
                  placeholder="e.g. South Paddy Basin"
                  required
                  className="w-full px-3 py-2 text-sm rounded-xl border border-[#C8C0B5] bg-[#FAFAF7] outline-none focus:ring-2 focus:ring-[#1E3A2B]"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-[#1A241F] uppercase mb-1">
                  Soil Type
                </label>
                <select
                  value={newSoilType}
                  onChange={(e) => setNewSoilType(e.target.value as "BLACK_COTTON")}
                  className="w-full px-3 py-2 text-sm rounded-xl border border-[#C8C0B5] bg-[#FAFAF7] outline-none"
                >
                  <option value="BLACK_COTTON">Black Cotton Soil (నల్లరేగడి)</option>
                  <option value="RED_CHALKA">Red Chalka (ఎర్ర నేలలు)</option>
                  <option value="ALLUVIAL">Alluvial Soil (ఒండ్రు నేలలు)</option>
                  <option value="LOAMY">Loamy Soil (వరి గరప)</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-[#1A241F] uppercase mb-1">
                  Irrigation Method
                </label>
                <select
                  value={newIrrigation}
                  onChange={(e) => setNewIrrigation(e.target.value as "BOREWELL")}
                  className="w-full px-3 py-2 text-sm rounded-xl border border-[#C8C0B5] bg-[#FAFAF7] outline-none"
                >
                  <option value="BOREWELL">Borewell (బోరు బావి)</option>
                  <option value="CANAL">Canal Irrigation (కాల్వ నీరు)</option>
                  <option value="RAINFED">Rainfed (వర్షాధారం)</option>
                  <option value="DRIP">Drip Irrigation (బిందు సేద్యం)</option>
                </select>
              </div>

              <div className="flex justify-end gap-2 pt-2 border-t border-[#E5E0D8]">
                <Button type="button" variant="outline" onClick={() => setShowPlotModal(false)}>
                  Cancel
                </Button>
                <Button type="submit" variant="primary" isLoading={isCreatingPlot}>
                  Create Plot
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Plots and Crop Cycles Listing */}
      <div className="space-y-4">
        {isLoading ? (
          <div className="space-y-3 animate-pulse">
            {[1, 2].map((i) => (
              <div key={i} className="h-40 bg-white rounded-2xl border border-[#E5E0D8]" />
            ))}
          </div>
        ) : plots.length === 0 ? (
          <div className="p-8 bg-white rounded-2xl border border-[#E5E0D8] text-center space-y-3">
            <Layers className="w-10 h-10 text-[#C8C0B5] mx-auto" />
            <p className="text-sm font-semibold text-[#1A241F]">No plots found on this farm.</p>
            <Button size="sm" variant="primary" onClick={() => setShowPlotModal(true)}>
              Create First Plot
            </Button>
          </div>
        ) : (
          plots.map((plot) => {
            const seasons = seasonsByPlot[plot.id] || [];
            return (
              <div
                key={plot.id}
                className="bg-white rounded-2xl border border-[#E5E0D8] p-5 shadow-xs space-y-4"
              >
                <div className="flex flex-wrap items-center justify-between gap-2 border-b border-[#E5E0D8] pb-3">
                  <div>
                    <h3 className="font-bold text-base text-[#1E3A2B]">{plot.name}</h3>
                    <p className="text-xs text-[#556059]">
                      Soil: <span className="font-medium text-[#1A241F] capitalize">{plot.soil_type.replace(/_/g, " ")}</span> • Irrigation: <span className="font-medium text-[#1A241F] capitalize">{plot.irrigation_source}</span>
                    </p>
                  </div>
                  <span className="text-xs font-semibold px-2.5 py-1 bg-[#E8F0EC] text-[#1E3A2B] rounded-full">
                    {seasons.length} Seasons Tracked
                  </span>
                </div>

                {/* Seasons */}
                {seasons.length === 0 ? (
                  <p className="text-xs text-[#78857E] italic">No crop seasons recorded on this plot.</p>
                ) : (
                  <div className="space-y-2">
                    {seasons.map((s) => (
                      <div
                        key={s.id}
                        className="p-3 bg-[#FAFAF7] rounded-xl border border-[#E5E0D8] flex flex-wrap items-center justify-between gap-3 text-xs"
                      >
                        <div className="flex items-center gap-2.5">
                          <Sprout className="w-5 h-5 text-[#1E3A2B] shrink-0" />
                          <div>
                            <span className="font-bold text-sm text-[#1A241F] capitalize block">
                              {s.crop_id} ({s.season_type})
                            </span>
                            <span className="text-[#78857E]">
                              Sown: {s.sowing_date} • Status: <strong className="text-[#15803D] uppercase">{s.status}</strong>
                            </span>
                          </div>
                        </div>

                        <div className="flex items-center gap-2">
                          <span className="px-2.5 py-1 bg-white border border-[#C8C0B5] rounded-md font-semibold text-[#1E3A2B]">
                            Stage: {s.current_stage}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
