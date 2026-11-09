"use client";

import React from "react";
import type { NutrientAssessment } from "../../lib/api/types";

interface NutrientIntelligenceCardProps {
  assessment: NutrientAssessment;
  labels: {
    title: string;
    prescriptions: string;
    splitSchedule: string;
    cropPack: string;
    micronutrients: string;
    safeguardsPassed: string;
    expertReview: string;
  };
}

export const NutrientIntelligenceCard: React.FC<NutrientIntelligenceCardProps> = ({
  assessment,
  labels,
}) => {
  let splitSchedule: any[];
  try {
    splitSchedule = JSON.parse(assessment.split_application_schedule_json || "[]");
  } catch {
    splitSchedule = [];
  }

  let micronutrientRecs: string[];
  try {
    micronutrientRecs = JSON.parse(assessment.micronutrient_recommendations_json || "[]");
  } catch {
    micronutrientRecs = [];
  }

  return (
    <div className="bg-white rounded-xl shadow-sm border border-indigo-100 p-5 space-y-4">
      <div className="flex items-center justify-between border-b pb-3 border-gray-100">
        <div>
          <h3 className="text-lg font-bold text-gray-900">{labels.title}</h3>
          <p className="text-xs text-gray-500">
            {labels.cropPack}: {assessment.crop_name || "Crop"} | Status: N: {assessment.nitrogen_status}, P: {assessment.phosphorus_status}, K: {assessment.potassium_status}
          </p>
        </div>
        <span className="px-3 py-1 text-xs font-semibold rounded-full bg-emerald-100 text-emerald-800">
          ✓ {labels.safeguardsPassed}
        </span>
      </div>

      <div className="grid grid-cols-3 gap-3">
        <div className="bg-indigo-50/50 p-3 rounded-lg border border-indigo-100 text-center">
          <span className="text-xs text-indigo-700 block font-medium">Nitrogen (N)</span>
          <span className="text-base font-bold text-gray-900">{assessment.recommended_n_kg_ha.toFixed(1)}</span>
          <span className="text-[10px] text-gray-500 block">kg/ha</span>
        </div>
        <div className="bg-indigo-50/50 p-3 rounded-lg border border-indigo-100 text-center">
          <span className="text-xs text-indigo-700 block font-medium">Phosphorus (P₂O₅)</span>
          <span className="text-base font-bold text-gray-900">{assessment.recommended_p2o5_kg_ha.toFixed(1)}</span>
          <span className="text-[10px] text-gray-500 block">kg/ha</span>
        </div>
        <div className="bg-indigo-50/50 p-3 rounded-lg border border-indigo-100 text-center">
          <span className="text-xs text-indigo-700 block font-medium">Potassium (K₂O)</span>
          <span className="text-base font-bold text-gray-900">{assessment.recommended_k2o_kg_ha.toFixed(1)}</span>
          <span className="text-[10px] text-gray-500 block">kg/ha</span>
        </div>
      </div>

      {splitSchedule.length > 0 && (
        <div className="space-y-2">
          <h4 className="text-xs font-bold text-gray-700 uppercase tracking-wide">{labels.splitSchedule}</h4>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
            {splitSchedule.map((s, idx) => (
              <div key={idx} className="bg-gray-50 p-2.5 rounded border border-gray-100 text-xs">
                <div className="font-semibold text-gray-800 flex justify-between">
                  <span>{s.stage}</span>
                  <span className="text-gray-500 font-normal">{s.timing}</span>
                </div>
                <div className="text-gray-600 mt-1">
                  N: {s.n_kg}kg | P: {s.p2o5_kg}kg | K: {s.k2o_kg}kg
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {micronutrientRecs.length > 0 && (
        <div className="bg-purple-50 p-3 rounded-lg border border-purple-100 text-xs space-y-1">
          <span className="font-bold text-purple-900 block">{labels.micronutrients}:</span>
          <ul className="list-disc list-inside text-purple-800 space-y-0.5">
            {micronutrientRecs.map((rec, idx) => (
              <li key={idx}>{rec}</li>
            ))}
          </ul>
        </div>
      )}

      <div className="pt-2 border-t border-gray-100 text-[10px] text-gray-400">
        Institutional Reference: {assessment.institutional_citation}
      </div>
    </div>
  );
};
