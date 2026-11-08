"use client";

import React from "react";
import type { ClimateExposureAssessment } from "../../lib/api/types";

interface ClimateResilienceCardProps {
  assessment: ClimateExposureAssessment;
  labels: {
    title: string;
    baselines: string;
    exposureAssessment: string;
    vulnerabilityScore: string;
    drySpell: string;
    heatStress: string;
    waterlogging: string;
    adaptation: string;
  };
}

export const ClimateResilienceCard: React.FC<ClimateResilienceCardProps> = ({
  assessment,
  labels,
}) => {
  const isHighRisk = assessment.severity_level === "CRITICAL" || assessment.severity_level === "HIGH";

  return (
    <div className="bg-white rounded-xl shadow-sm border border-amber-100 p-5 space-y-4">
      <div className="flex items-center justify-between border-b pb-3 border-gray-100">
        <div>
          <h3 className="text-lg font-bold text-gray-900">{labels.title}</h3>
          <p className="text-xs text-gray-500">
            Hazard: {assessment.hazard_type} | Stage: {assessment.crop_stage}
          </p>
        </div>
        <span
          className={`px-3 py-1 text-xs font-semibold rounded-full ${
            isHighRisk ? "bg-red-100 text-red-800" : "bg-amber-100 text-amber-800"
          }`}
        >
          {assessment.severity_level}
        </span>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
        <div className="bg-gray-50 p-3 rounded-lg border border-gray-100">
          <span className="text-xs text-gray-500 block">{labels.vulnerabilityScore}</span>
          <span className="text-base font-bold text-gray-900">
            {(assessment.vulnerability_score * 100).toFixed(0)} / 100
          </span>
        </div>
        <div className="bg-gray-50 p-3 rounded-lg border border-gray-100">
          <span className="text-xs text-gray-500 block">Forecast Tmax</span>
          <span className="text-base font-bold text-gray-900">
            {assessment.forecast_tmax ? `${assessment.forecast_tmax.toFixed(1)}°C` : "N/A"}
          </span>
        </div>
        <div className="bg-gray-50 p-3 rounded-lg border border-gray-100">
          <span className="text-xs text-gray-500 block">Rainless Days</span>
          <span className="text-base font-bold text-gray-900">
            {assessment.consecutive_rainless_days ?? 0} Days
          </span>
        </div>
      </div>

      <div className="bg-amber-50/80 p-3 rounded-lg border border-amber-200 text-xs space-y-1">
        <span className="font-bold text-amber-900 block">💡 {labels.adaptation}</span>
        <p className="text-amber-800 leading-relaxed">{assessment.recommended_adaptation}</p>
        <span className="text-[10px] text-amber-600 block mt-1">Citation: {assessment.institutional_citation}</span>
      </div>
    </div>
  );
};
