"use client";

import React from "react";
import type { WaterBalanceSnapshot, WaterSource, IrrigationEvent } from "../../lib/api/types";

interface WaterManagementCardProps {
  waterBalance: WaterBalanceSnapshot;
  waterSources: WaterSource[];
  latestEvent?: IrrigationEvent;
  labels: {
    title: string;
    sources: string;
    irrigationEvents: string;
    flowMeter: string;
    volumeM3: string;
    equivDepth: string;
    waterBalance: string;
    soilMoisture: string;
    waterSaving: string;
    compareScenarios: string;
  };
}

export const WaterManagementCard: React.FC<WaterManagementCardProps> = ({
  waterBalance,
  waterSources,
  latestEvent,
  labels,
}) => {
  return (
    <div className="bg-white rounded-xl shadow-sm border border-cyan-100 p-5 space-y-4">
      <div className="flex items-center justify-between border-b pb-3 border-gray-100">
        <div>
          <h3 className="text-lg font-bold text-gray-900">{labels.title}</h3>
          <p className="text-xs text-gray-500">
            {labels.sources}: {waterSources.length} Active | Status: {waterBalance.accounting_status}
          </p>
        </div>
        <span
          className={`px-3 py-1 text-xs font-semibold rounded-full ${
            waterBalance.accounting_status === "COMPLETED_WITH_VALIDATED_INPUTS"
              ? "bg-cyan-100 text-cyan-800"
              : "bg-blue-100 text-blue-800"
          }`}
        >
          {waterBalance.accounting_status}
        </span>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <div className="bg-gray-50 p-3 rounded-lg border border-gray-100">
          <span className="text-xs text-gray-500 block">Applied Irrigation</span>
          <span className="text-base font-bold text-cyan-700">{waterBalance.irrigation_applied_mm.toFixed(1)} mm</span>
        </div>
        <div className="bg-gray-50 p-3 rounded-lg border border-gray-100">
          <span className="text-xs text-gray-500 block">Crop ETc</span>
          <span className="text-base font-bold text-gray-800">{waterBalance.crop_evapotranspiration_mm.toFixed(1)} mm</span>
        </div>
        <div className="bg-gray-50 p-3 rounded-lg border border-gray-100">
          <span className="text-xs text-gray-500 block">Soil Depletion</span>
          <span className="text-base font-bold text-amber-700">{waterBalance.current_depletion_percent.toFixed(1)}%</span>
        </div>
        <div className="bg-gray-50 p-3 rounded-lg border border-gray-100">
          <span className="text-xs text-gray-500 block">Allowed Depletion (MAD)</span>
          <span className="text-base font-bold text-gray-800">{waterBalance.management_allowed_depletion_percent.toFixed(1)}%</span>
        </div>
      </div>

      {latestEvent && (
        <div className="bg-cyan-50/60 p-3 rounded-lg border border-cyan-100 text-xs space-y-1">
          <div className="font-semibold text-cyan-900 flex justify-between">
            <span>Latest Irrigation: {latestEvent.irrigation_method}</span>
            <span>{latestEvent.duration_hours} Hours</span>
          </div>
          <div className="text-cyan-800 flex justify-between">
            <span>{labels.volumeM3}: {latestEvent.calculated_volume_m3.toFixed(1)} m³</span>
            <span>{labels.equivDepth}: {latestEvent.equivalent_depth_mm.toFixed(1)} mm</span>
          </div>
        </div>
      )}

      {waterSources.length > 0 && (
        <div className="pt-2 border-t border-gray-100 text-xs text-gray-500">
          <span className="font-medium text-gray-700">Primary Source: </span>
          {waterSources[0].source_name} ({waterSources[0].source_type}, Depth: {waterSources[0].depth_meters || "N/A"}m)
        </div>
      )}
    </div>
  );
};
