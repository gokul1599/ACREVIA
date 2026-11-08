"use client";

import React from "react";
import type { RegionalSignal } from "../../lib/api/types";

interface RegionalPulseCardProps {
  signal: RegionalSignal;
  labels: {
    title: string;
    confidenceTier: string;
    distinctFarms: string;
    outbreakSuppressionNotice: string;
    recommendedAction: string;
  };
}

export const RegionalPulseCard: React.FC<RegionalPulseCardProps> = ({ signal, labels }) => {
  const getConfidenceBadge = () => {
    switch (signal.confidence_tier) {
      case "OFFICIAL_ADVISORY":
        return <span className="px-2.5 py-0.5 text-xs font-semibold rounded-full bg-blue-100 text-blue-800 border border-blue-300">🏛 Official Advisory</span>;
      case "EXPERT_REVIEWED":
        return <span className="px-2.5 py-0.5 text-xs font-semibold rounded-full bg-emerald-100 text-emerald-800 border border-emerald-300">✓ Expert Confirmed</span>;
      case "AI_ASSISTED":
        return <span className="px-2.5 py-0.5 text-xs font-semibold rounded-full bg-purple-100 text-purple-800 border border-purple-300">🤖 AI Assisted</span>;
      default:
        return <span className="px-2.5 py-0.5 text-xs font-semibold rounded-full bg-amber-100 text-amber-800 border border-amber-300">🌾 Multiple Farmer Reports</span>;
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-emerald-100 p-5 space-y-4 hover:border-emerald-300 transition-colors">
      <div className="flex items-start justify-between gap-3">
        <div>
          <div className="flex items-center gap-2 flex-wrap">
            <span className="px-2.5 py-0.5 text-xs font-semibold rounded-full bg-orange-50 text-orange-800 border border-orange-200">
              {signal.signal_category}
            </span>
            <span className="px-2 py-0.5 text-xs font-medium rounded-full bg-emerald-50 text-emerald-800 border border-emerald-200">
              {signal.crop_id.toUpperCase()}
            </span>
            <span className="text-xs text-gray-500">
              📍 {signal.district}, {signal.state}
            </span>
          </div>
          <h3 className="text-lg font-bold text-gray-900 mt-2">{signal.signal_title}</h3>
        </div>
        <div>{getConfidenceBadge()}</div>
      </div>

      <p className="text-gray-700 text-sm whitespace-pre-line leading-relaxed">{signal.signal_summary}</p>

      {/* Outbreak Claim Suppression Notice */}
      {signal.is_outbreak_claim_suppressed && (
        <div className="p-3 rounded-lg bg-amber-50 border border-amber-200 text-amber-900 text-xs flex items-start gap-2">
          <span>⚠️</span>
          <span>{labels.outbreakSuppressionNotice}</span>
        </div>
      )}

      {/* Evidence & Metrics Bar */}
      <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 bg-gray-50 p-3 rounded-lg border border-gray-100 text-xs">
        <div>
          <span className="text-gray-500 block">{labels.distinctFarms}</span>
          <span className="font-bold text-gray-900">{signal.distinct_farms_count} Distinct Farms</span>
        </div>
        <div>
          <span className="text-gray-500 block">Observation Surge</span>
          <span className="font-bold text-gray-900">{signal.source_observation_count} Records</span>
        </div>
        <div className="col-span-2 sm:col-span-1">
          <span className="text-gray-500 block">Observation Window</span>
          <span className="font-bold text-gray-900">{signal.observed_start_date} to {signal.observed_end_date}</span>
        </div>
      </div>

      {/* Recommended Precautionary Action */}
      <div className="p-3 rounded-lg bg-emerald-50/60 border border-emerald-200">
        <h4 className="text-xs font-bold uppercase tracking-wider text-emerald-900 mb-1">
          {labels.recommendedAction}
        </h4>
        <p className="text-xs text-emerald-800 leading-normal">{signal.recommended_action}</p>
      </div>
    </div>
  );
};
