"use client";

import React from "react";
import type { SoilPlotHistoryResponse } from "../../lib/api/types";

interface SoilHealthCardProps {
  history: SoilPlotHistoryResponse;
  labels: {
    title: string;
    samples: string;
    labResults: string;
    ph: string;
    ec: string;
    organicCarbon: string;
    nitrogen: string;
    phosphorus: string;
    potassium: string;
    spatialWarning: string;
    provenance: string;
  };
}

export const SoilHealthCard: React.FC<SoilHealthCardProps> = ({ history, labels }) => {
  const latestResult = history.results.length > 0 ? history.results[history.results.length - 1] : null;

  return (
    <div className="bg-white rounded-xl shadow-sm border border-emerald-100 p-5 space-y-4">
      <div className="flex items-center justify-between border-b pb-3 border-gray-100">
        <div>
          <h3 className="text-lg font-bold text-gray-900">{labels.title}</h3>
          <p className="text-xs text-gray-500">
            {labels.samples}: {history.samples_count} | Plot: {history.plot_id}
          </p>
        </div>
        <span
          className={`px-3 py-1 text-xs font-semibold rounded-full ${
            history.latest_nitrogen_status === "SUFFICIENT"
              ? "bg-emerald-100 text-emerald-800"
              : "bg-amber-100 text-amber-800"
          }`}
        >
          {history.latest_nitrogen_status}
        </span>
      </div>

      {history.samples_count > 0 && history.results.some((r) => r.available_nitrogen_kg_ha < 250) && (
        <div className="bg-amber-50 border-l-4 border-amber-500 p-3 rounded text-xs text-amber-800">
          ⚠️ {labels.spatialWarning}
        </div>
      )}

      {latestResult ? (
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
          <div className="bg-gray-50 p-3 rounded-lg border border-gray-100">
            <span className="text-xs text-gray-500 block">{labels.ph}</span>
            <span className="text-base font-bold text-gray-800">{latestResult.ph.toFixed(1)}</span>
          </div>
          <div className="bg-gray-50 p-3 rounded-lg border border-gray-100">
            <span className="text-xs text-gray-500 block">{labels.ec}</span>
            <span className="text-base font-bold text-gray-800">{latestResult.electrical_conductivity_ec.toFixed(2)} dS/m</span>
          </div>
          <div className="bg-gray-50 p-3 rounded-lg border border-gray-100">
            <span className="text-xs text-gray-500 block">{labels.organicCarbon}</span>
            <span className="text-base font-bold text-emerald-700">{latestResult.organic_carbon_percent.toFixed(2)}%</span>
            <span className="text-[10px] text-gray-400 block">Trend: {history.soc_trend_percent > 0 ? `+${history.soc_trend_percent}%` : `${history.soc_trend_percent}%`}</span>
          </div>
          <div className="bg-gray-50 p-3 rounded-lg border border-gray-100">
            <span className="text-xs text-gray-500 block">{labels.nitrogen}</span>
            <span className="text-base font-bold text-gray-800">{latestResult.available_nitrogen_kg_ha.toFixed(1)}</span>
          </div>
          <div className="bg-gray-50 p-3 rounded-lg border border-gray-100">
            <span className="text-xs text-gray-500 block">{labels.phosphorus}</span>
            <span className="text-base font-bold text-gray-800">{latestResult.available_phosphorus_kg_ha.toFixed(1)}</span>
          </div>
          <div className="bg-gray-50 p-3 rounded-lg border border-gray-100">
            <span className="text-xs text-gray-500 block">{labels.potassium}</span>
            <span className="text-base font-bold text-gray-800">{latestResult.available_potassium_kg_ha.toFixed(1)}</span>
          </div>
        </div>
      ) : (
        <p className="text-sm text-gray-500 italic">No laboratory test results recorded yet.</p>
      )}

      {latestResult && (
        <div className="pt-2 border-t border-gray-100 text-xs text-gray-500 flex justify-between items-center">
          <span>{latestResult.laboratory_name} ({latestResult.accreditation_number})</span>
          <span className="text-emerald-600 font-medium">✓ {labels.provenance} Verified</span>
        </div>
      )}
    </div>
  );
};
