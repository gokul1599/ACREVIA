"use client";

import React from "react";
import type { OptimizationProblem } from "../../lib/api/types";

interface ResourceOptimizationCardProps {
  problem?: OptimizationProblem | null;
  labels: {
    title: string;
    waterAllocation: string;
    pumpHours: string;
    flowRate: string;
    budgetAllocation: string;
    infeasible: string;
    bottleneckNotice: string;
    noActuationDisclaimer: string;
  };
}

export const ResourceOptimizationCard: React.FC<ResourceOptimizationCardProps> = ({
  problem,
  labels,
}) => {
  const result = problem?.result;
  const isFeasible = result?.feasibility_status === "FEASIBLE";
  const solution = result?.selected_solution_json;
  const conflicts = result?.conflicting_constraints_json ?? [];
  const tradeOffs = result?.trade_off_analysis_json;

  return (
    <div className="rounded-xl border border-neutral-200 bg-white p-5 shadow-sm space-y-4">
      <div className="flex items-center justify-between border-b border-neutral-100 pb-3">
        <div>
          <h2 className="text-lg font-bold text-neutral-900">{labels.title}</h2>
          <p className="text-xs text-neutral-500">
            {problem?.problem_type?.replace(/_/g, " ") ?? "Resource Allocation"} • Solver: {result?.solver_name ?? "Simplex LP"}
          </p>
        </div>
        <span
          className={`px-2.5 py-1 text-xs font-semibold rounded-full border ${
            isFeasible
              ? "bg-emerald-100 text-emerald-800 border-emerald-300"
              : "bg-rose-100 text-rose-800 border-rose-300"
          }`}
        >
          {result?.feasibility_status ?? "PENDING"}
        </span>
      </div>

      {/* Infeasibility Alert */}
      {!isFeasible && conflicts.length > 0 && (
        <div className="p-4 bg-rose-50 rounded-xl border border-rose-200 text-xs text-rose-900 space-y-2">
          <span className="font-bold block text-rose-800 text-sm">{labels.infeasible}</span>
          <p>{labels.bottleneckNotice}</p>
          <ul className="list-disc pl-5 space-y-1">
            {conflicts.map((c, i) => (
              <li key={i}>{c}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Feasible Allocations */}
      {isFeasible && solution && (
        <div className="space-y-3">
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
            {solution.total_water_used_m3 !== undefined && (
              <div className="p-3 bg-neutral-50 rounded-xl border border-neutral-200">
                <span className="text-xs text-neutral-500 block">Total Water Allocated</span>
                <span className="text-lg font-bold text-neutral-900">
                  {solution.total_water_used_m3} m³
                </span>
              </div>
            )}
            {solution.pump_hours_required !== undefined && (
              <div className="p-3 bg-neutral-50 rounded-xl border border-neutral-200">
                <span className="text-xs text-neutral-500 block">{labels.pumpHours}</span>
                <span className="text-lg font-bold text-neutral-900">
                  {solution.pump_hours_required} hrs
                </span>
              </div>
            )}
            {solution.mean_depth_mm !== undefined && (
              <div className="p-3 bg-neutral-50 rounded-xl border border-neutral-200">
                <span className="text-xs text-neutral-500 block">Average Depth</span>
                <span className="text-lg font-bold text-neutral-900">
                  {solution.mean_depth_mm} mm
                </span>
              </div>
            )}
          </div>

          {/* Per-Plot Depths */}
          {solution.allocated_depths_mm && (
            <div className="p-3 bg-neutral-50 rounded-lg border border-neutral-200 text-xs">
              <span className="font-semibold text-neutral-800 block mb-2">Allocated Depths per Plot:</span>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                {Object.entries(solution.allocated_depths_mm).map(([plotId, depth]) => (
                  <div key={plotId} className="flex justify-between p-2 bg-white rounded border border-neutral-200">
                    <span className="truncate text-neutral-600">Plot: {plotId.slice(0, 8)}...</span>
                    <span className="font-bold text-emerald-700">{String(depth)} mm</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Trade-off Analysis */}
      {tradeOffs && (
        <div className="p-3 bg-neutral-50 rounded-lg border border-neutral-200 text-xs text-neutral-600 space-y-1">
          <span className="font-semibold text-neutral-800 block">Trade-Off Analysis:</span>
          {tradeOffs.crop_stress_mitigation_pct !== undefined && (
            <div className="flex justify-between">
              <span>Stress Mitigated:</span>
              <span className="font-bold text-emerald-700">{tradeOffs.crop_stress_mitigation_pct}%</span>
            </div>
          )}
          {tradeOffs.water_reserve_remaining_m3 !== undefined && (
            <div className="flex justify-between">
              <span>Water Reserve Remaining:</span>
              <span className="font-bold text-neutral-800">{tradeOffs.water_reserve_remaining_m3} m³</span>
            </div>
          )}
        </div>
      )}

      {/* Safety Notice: Zero Actuation */}
      <div className="p-3 bg-blue-50 rounded-lg border border-blue-200 text-xs text-blue-800">
        <span className="font-semibold block mb-0.5">Decision-Support Boundary:</span>
        <p>{labels.noActuationDisclaimer}</p>
      </div>
    </div>
  );
};
