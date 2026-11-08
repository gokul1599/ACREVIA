"use client";

import React from "react";
import type { SeasonalSustainabilityScorecard, AgriculturalPracticeDefinition } from "../../lib/api/types";

interface SustainablePracticesCardProps {
  scorecard: SeasonalSustainabilityScorecard;
  practices: AgriculturalPracticeDefinition[];
  labels: {
    title: string;
    practices: string;
    logPractice: string;
    carbonMeasurement: string;
    socPercent: string;
    emissions: string;
    scorecard: string;
    disclaimer: string;
  };
}

export const SustainablePracticesCard: React.FC<SustainablePracticesCardProps> = ({
  scorecard,
  practices,
  labels,
}) => {
  return (
    <div className="bg-white rounded-xl shadow-sm border border-emerald-100 p-5 space-y-4">
      <div className="flex items-center justify-between border-b pb-3 border-gray-100">
        <div>
          <h3 className="text-lg font-bold text-gray-900">{labels.title}</h3>
          <p className="text-xs text-gray-500">
            Season: {scorecard.season} {scorecard.year} | Verified Practices: {scorecard.verified_practices.length}
          </p>
        </div>
        <div className="text-right">
          <span className="text-2xl font-black text-emerald-700">{scorecard.sustainability_index.toFixed(0)}</span>
          <span className="text-xs text-gray-400 block">/ 100 Index</span>
        </div>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-5 gap-2">
        <div className="bg-emerald-50/50 p-2.5 rounded text-center border border-emerald-100">
          <span className="text-[10px] text-gray-500 block">Soil Cover</span>
          <span className="text-sm font-bold text-emerald-800">{scorecard.soil_cover_score}</span>
        </div>
        <div className="bg-emerald-50/50 p-2.5 rounded text-center border border-emerald-100">
          <span className="text-[10px] text-gray-500 block">Water Eff.</span>
          <span className="text-sm font-bold text-emerald-800">{scorecard.water_efficiency_score}</span>
        </div>
        <div className="bg-emerald-50/50 p-2.5 rounded text-center border border-emerald-100">
          <span className="text-[10px] text-gray-500 block">Nutrient Bal.</span>
          <span className="text-sm font-bold text-emerald-800">{scorecard.nutrient_balance_score}</span>
        </div>
        <div className="bg-emerald-50/50 p-2.5 rounded text-center border border-emerald-100">
          <span className="text-[10px] text-gray-500 block">IPM Adoption</span>
          <span className="text-sm font-bold text-emerald-800">{scorecard.ipm_adoption_score}</span>
        </div>
        <div className="bg-emerald-50/50 p-2.5 rounded text-center border border-emerald-100">
          <span className="text-[10px] text-gray-500 block">Biodiversity</span>
          <span className="text-sm font-bold text-emerald-800">{scorecard.biodiversity_score}</span>
        </div>
      </div>

      {scorecard.verified_practices.length > 0 && (
        <div className="space-y-1">
          <span className="text-xs font-semibold text-gray-700 block">Verified On-Farm Practices:</span>
          <div className="flex flex-wrap gap-1.5">
            {scorecard.verified_practices.map((code, idx) => (
              <span key={idx} className="bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded text-xs">
                ✓ {code}
              </span>
            ))}
          </div>
        </div>
      )}

      <div className="p-3 bg-gray-50 rounded-lg border border-gray-100 text-[11px] text-gray-500 italic">
        ⚠️ {scorecard.disclaimer}
      </div>
    </div>
  );
};
