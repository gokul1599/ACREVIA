"use client";

import React from "react";
import type { ResilienceAssessment } from "../../lib/api/types";

interface ResilienceAssessmentCardProps {
  assessment: ResilienceAssessment;
  labels: {
    title: string;
    assessResilience: string;
    overallScore: string;
    evidenceQuality: string;
    highConfidence: string;
    topVulnerabilities: string;
    simulations: string;
  };
}

export const ResilienceAssessmentCard: React.FC<ResilienceAssessmentCardProps> = ({
  assessment,
  labels,
}) => {
  let vulnerabilities: string[];
  try {
    vulnerabilities = JSON.parse(assessment.top_vulnerabilities_json || "[]");
  } catch {
    vulnerabilities = [];
  }

  let recommendations: string[];
  try {
    recommendations = JSON.parse(assessment.adaptation_recommendations_json || "[]");
  } catch {
    recommendations = [];
  }

  return (
    <div className="bg-white rounded-xl shadow-sm border border-teal-100 p-5 space-y-4">
      <div className="flex items-center justify-between border-b pb-3 border-gray-100">
        <div>
          <h3 className="text-lg font-bold text-gray-900">{labels.title}</h3>
          <p className="text-xs text-gray-500">
            {labels.evidenceQuality}: {(assessment.evidence_quality_score * 100).toFixed(0)}% ({assessment.confidence_category})
          </p>
        </div>
        <div className="text-right">
          <span className="text-3xl font-black text-teal-700">{assessment.overall_resilience_score.toFixed(1)}</span>
          <span className="text-xs text-gray-400 block">/ 100 Score</span>
        </div>
      </div>

      <div className="grid grid-cols-5 gap-2 text-center">
        <div className="bg-gray-50 p-2 rounded border border-gray-100">
          <span className="text-[10px] text-gray-500 block">Soil</span>
          <span className="text-sm font-bold text-gray-800">{assessment.soil_score}</span>
        </div>
        <div className="bg-gray-50 p-2 rounded border border-gray-100">
          <span className="text-[10px] text-gray-500 block">Water</span>
          <span className="text-sm font-bold text-gray-800">{assessment.water_score}</span>
        </div>
        <div className="bg-gray-50 p-2 rounded border border-gray-100">
          <span className="text-[10px] text-gray-500 block">Climate</span>
          <span className="text-sm font-bold text-gray-800">{assessment.climate_score}</span>
        </div>
        <div className="bg-gray-50 p-2 rounded border border-gray-100">
          <span className="text-[10px] text-gray-500 block">Nutrient</span>
          <span className="text-sm font-bold text-gray-800">{assessment.nutrient_score}</span>
        </div>
        <div className="bg-gray-50 p-2 rounded border border-gray-100">
          <span className="text-[10px] text-gray-500 block">Practice</span>
          <span className="text-sm font-bold text-gray-800">{assessment.practice_score}</span>
        </div>
      </div>

      {vulnerabilities.length > 0 && (
        <div className="bg-rose-50/70 p-3 rounded-lg border border-rose-100 text-xs space-y-1">
          <span className="font-bold text-rose-900 block">⚠️ {labels.topVulnerabilities}:</span>
          <ul className="list-disc list-inside text-rose-800 space-y-0.5">
            {vulnerabilities.map((vuln, idx) => (
              <li key={idx}>{vuln}</li>
            ))}
          </ul>
        </div>
      )}

      {recommendations.length > 0 && (
        <div className="bg-teal-50/70 p-3 rounded-lg border border-teal-100 text-xs space-y-1">
          <span className="font-bold text-teal-900 block">💡 Prioritized Climate Adaptation Plan:</span>
          <ul className="list-disc list-inside text-teal-800 space-y-0.5">
            {recommendations.map((rec, idx) => (
              <li key={idx}>{rec}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};
