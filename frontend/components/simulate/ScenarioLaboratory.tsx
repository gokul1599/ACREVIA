"use client";

import React from "react";
import type { SimulationScenario } from "../../lib/api/types";

interface ScenarioLaboratoryProps {
  scenario?: SimulationScenario | null;
  labels: {
    title: string;
    waterBalance: string;
    depletion: string;
    transpirationRatio: string;
    stressIndex: string;
    gddProjection: string;
    waterloggingRisk: string;
    compareScenarios: string;
    disclaimer: string;
  };
}

export const ScenarioLaboratory: React.FC<ScenarioLaboratoryProps> = ({
  scenario,
  labels,
}) => {
  const result = scenario?.result;
  const outputs = result?.outputs_json;
  const uncertainty = result?.uncertainty_metadata_json;

  return (
    <div className="rounded-xl border border-neutral-200 bg-white p-5 shadow-sm space-y-4">
      <div className="flex items-center justify-between border-b border-neutral-100 pb-3">
        <div>
          <h2 className="text-lg font-bold text-neutral-900">{labels.title}</h2>
          <p className="text-xs text-neutral-500">
            {scenario?.scenario_name ?? "Scenario Evaluation"} • Model: {result?.model_name ?? "FAO-56 Dual-Kc"}
          </p>
        </div>
        <span className="px-2.5 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800 border border-blue-200">
          {scenario?.status ?? "READY"}
        </span>
      </div>

      {/* Primary Metrics Grid */}
      {outputs && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          {outputs.root_zone_depletion_mm !== undefined && (
            <div className="p-3 bg-neutral-50 rounded-xl border border-neutral-200">
              <span className="text-xs text-neutral-500 block">{labels.depletion}</span>
              <span className="text-lg font-bold text-neutral-900">
                {outputs.root_zone_depletion_mm} mm
              </span>
            </div>
          )}

          {outputs.water_stress_index !== undefined && (
            <div className="p-3 bg-neutral-50 rounded-xl border border-neutral-200">
              <span className="text-xs text-neutral-500 block">{labels.stressIndex}</span>
              <span
                className={`text-lg font-bold ${
                  outputs.water_stress_index > 0.4 ? "text-amber-600" : "text-emerald-700"
                }`}
              >
                {outputs.water_stress_index}
              </span>
            </div>
          )}

          {outputs.relative_transpiration_ratio !== undefined && (
            <div className="p-3 bg-neutral-50 rounded-xl border border-neutral-200">
              <span className="text-xs text-neutral-500 block">{labels.transpirationRatio}</span>
              <span className="text-lg font-bold text-neutral-900">
                {outputs.relative_transpiration_ratio}
              </span>
            </div>
          )}

          {outputs.waterlogging_risk_pct !== undefined && (
            <div className="p-3 bg-neutral-50 rounded-xl border border-neutral-200">
              <span className="text-xs text-neutral-500 block">{labels.waterloggingRisk}</span>
              <span className="text-lg font-bold text-neutral-900">
                {outputs.waterlogging_risk_pct}%
              </span>
            </div>
          )}

          {outputs.accumulated_gdd_horizon !== undefined && (
            <div className="p-3 bg-neutral-50 rounded-xl border border-neutral-200">
              <span className="text-xs text-neutral-500 block">{labels.gddProjection}</span>
              <span className="text-lg font-bold text-neutral-900">
                {outputs.accumulated_gdd_horizon} GDD
              </span>
            </div>
          )}
        </div>
      )}

      {/* Depletion Trajectory Bar Chart */}
      {outputs?.depletion_trajectory_days && outputs.depletion_trajectory_days.length > 0 && (
        <div className="space-y-2 pt-2 border-t border-neutral-100">
          <div className="flex justify-between text-xs text-neutral-600">
            <span className="font-medium">14-Day Soil Moisture Depletion Trajectory:</span>
            <span className="text-neutral-400">Values in mm</span>
          </div>
          <div className="flex items-end gap-1.5 h-16 pt-2 bg-neutral-50 p-2 rounded-lg border border-neutral-200">
            {outputs.depletion_trajectory_days.map((val, idx) => {
              const maxVal = Math.max(...(outputs.depletion_trajectory_days ?? [60]), 50);
              const heightPct = Math.min(100, Math.max(10, (val / maxVal) * 100));
              return (
                <div key={idx} className="flex-1 flex flex-col items-center h-full justify-end group">
                  <div
                    className={`w-full rounded-t transition-all ${
                      val > 40 ? "bg-amber-500" : "bg-emerald-500"
                    }`}
                    style={{ height: `${heightPct}%` }}
                    title={`Day ${idx + 1}: ${val}mm`}
                  />
                  <span className="text-[9px] text-neutral-400 mt-1">D{idx + 1}</span>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Uncertainty Bounds */}
      {uncertainty && (
        <div className="p-3 bg-sky-50 rounded-lg border border-sky-200 text-xs text-sky-900">
          <span className="font-semibold block mb-0.5">Uncertainty Bounds:</span>
          <p>
            Confidence Interval: [{uncertainty.confidence_band_lower ?? 0.28} - {uncertainty.confidence_band_upper ?? 0.42}] • p-value: {uncertainty.p_value ?? 0.05}
          </p>
        </div>
      )}

      {/* Disclaimer Banner */}
      <div className="p-3 bg-amber-50 rounded-lg border border-amber-200 text-xs text-amber-800">
        <span className="font-semibold block mb-0.5">Scientific Disclaimer:</span>
        <p>{labels.disclaimer}</p>
      </div>
    </div>
  );
};
