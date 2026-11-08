"use client";

import React from "react";
import type { FusionExplanation } from "../../lib/api/types";

interface EvidenceFusionSummaryProps {
  assessment: FusionExplanation;
  locale: "en" | "te" | "hi";
  labels: {
    title: string;
    overallVigor: string;
    conflictResolved: string;
  };
}

export const EvidenceFusionSummary: React.FC<EvidenceFusionSummaryProps> = ({
  assessment,
  locale,
  labels,
}) => {
  const farmerText =
    assessment.farmer_explanation[locale] || assessment.farmer_explanation.en;

  return (
    <div className="rounded-xl border border-neutral-200 bg-white p-5 shadow-sm">
      <div className="flex items-center justify-between pb-3 border-b border-neutral-100">
        <div>
          <h3 className="font-semibold text-neutral-900">{labels.title}</h3>
          <p className="text-xs text-neutral-500">Cross-Modality Agricultural Intelligence</p>
        </div>
        <span className="px-2.5 py-1 text-xs font-semibold rounded bg-neutral-900 text-white">
          {assessment.overall_vigor_status}
        </span>
      </div>

      <div className="mt-4 p-4 rounded-lg bg-emerald-50/40 border border-emerald-100">
        <p className="text-sm text-neutral-800 leading-relaxed font-medium">
          {farmerText}
        </p>
      </div>

      {assessment.contradictions_detected && assessment.contradictions_detected.length > 0 && (
        <div className="mt-4 space-y-2">
          <span className="text-xs font-medium text-neutral-600 block">
            {labels.conflictResolved}:
          </span>
          {assessment.contradictions_detected.map((c, idx) => (
            <div
              key={idx}
              className="rounded-lg bg-neutral-50 p-3 border border-neutral-200 text-xs text-neutral-700"
            >
              <div className="font-semibold text-neutral-900">{c.conflict_type}</div>
              <div className="mt-0.5 text-neutral-600">{c.description}</div>
              <div className="mt-1 text-emerald-800 font-medium">Resolution: {c.resolution}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
