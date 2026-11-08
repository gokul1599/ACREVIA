"use client";

import React, { useState } from "react";
import type { ResearchProject, ResearchConsent } from "../../lib/api/types";

interface ResearchWorkspaceCardProps {
  project: ResearchProject;
  consent?: ResearchConsent;
  onGrantConsent?: (projectId: string, scope: string) => Promise<void>;
  onRevokeConsent?: (consentId: string) => Promise<void>;
  labels: {
    title: string;
    grantConsent: string;
    consentActive: string;
    revokeConsent: string;
    dataSplits: string;
    annotationDisagreement: string;
  };
}

export const ResearchWorkspaceCard: React.FC<ResearchWorkspaceCardProps> = ({
  project,
  consent,
  onGrantConsent,
  onRevokeConsent,
  labels,
}) => {
  const [selectedScope, setSelectedScope] = useState("ANNOTATED_IMAGES");
  const [submitting, setSubmitting] = useState(false);

  const handleGrant = async () => {
    if (!onGrantConsent) return;
    setSubmitting(true);
    try {
      await onGrantConsent(project.id, selectedScope);
    } finally {
      setSubmitting(false);
    }
  };

  const handleRevoke = async () => {
    if (!onRevokeConsent || !consent) return;
    setSubmitting(true);
    try {
      await onRevokeConsent(consent.id);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-emerald-100 p-5 space-y-4 hover:border-emerald-300 transition-colors">
      <div className="flex items-start justify-between gap-3">
        <div>
          <div className="flex items-center gap-2 flex-wrap">
            <span className="px-2.5 py-0.5 text-xs font-semibold rounded-full bg-indigo-50 text-indigo-800 border border-indigo-200">
              {project.institution_name}
            </span>
            <span className="text-xs text-gray-500">📍 {project.geographic_scope}</span>
          </div>
          <h3 className="text-lg font-bold text-gray-900 mt-2">{project.title}</h3>
        </div>
        {consent?.is_active ? (
          <span className="px-2.5 py-0.5 text-xs font-semibold rounded-full bg-emerald-100 text-emerald-800 border border-emerald-300 flex items-center gap-1">
            ✓ {labels.consentActive}
          </span>
        ) : (
          <span className="px-2.5 py-0.5 text-xs font-semibold rounded-full bg-gray-100 text-gray-700 border border-gray-300">
            No Active Consent
          </span>
        )}
      </div>

      <p className="text-gray-700 text-sm leading-relaxed">{project.research_objectives}</p>

      {/* Supported crops */}
      <div className="flex items-center gap-2 flex-wrap">
        <span className="text-xs font-semibold text-gray-600">Research Focus Crops:</span>
        {project.supported_crops.map((crop) => (
          <span
            key={crop}
            className="px-2 py-0.5 text-xs font-medium rounded-full bg-emerald-50 text-emerald-800 border border-emerald-200"
          >
            {crop.toUpperCase()}
          </span>
        ))}
      </div>

      {/* Dataset Governance notice */}
      <div className="p-3 bg-gray-50 rounded-lg border border-gray-200 text-xs text-gray-700 space-y-1">
        <span className="font-semibold text-gray-900 block">{labels.dataSplits}</span>
        <p>
          Dataset contributions adhere to farm-disjoint partitioning (Train / Validation / Test) to prevent data leakage and benchmark over-optimism.
        </p>
      </div>

      {/* Consent Action Bar */}
      <div className="pt-3 border-t border-gray-100 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
        {consent?.is_active ? (
          <div className="flex items-center justify-between w-full">
            <span className="text-xs text-emerald-800 font-medium">
              Consented Scope: <strong>{consent.consent_scope}</strong> (v{consent.consent_version})
            </span>
            {onRevokeConsent && (
              <button
                type="button"
                onClick={handleRevoke}
                disabled={submitting}
                className="px-3 py-1.5 text-xs font-semibold rounded-lg bg-rose-50 text-rose-700 border border-rose-200 hover:bg-rose-100 transition-colors"
              >
                {labels.revokeConsent}
              </button>
            )}
          </div>
        ) : onGrantConsent ? (
          <div className="flex items-center gap-2 w-full flex-wrap sm:flex-nowrap">
            <select
              value={selectedScope}
              onChange={(e) => setSelectedScope(e.target.value)}
              className="text-xs border border-gray-300 rounded-lg p-2 bg-white flex-1"
            >
              <option value="ANNOTATED_IMAGES">Annotated Images Only</option>
              <option value="OBSERVATIONS_ONLY">Field Observations Only</option>
              <option value="SENSOR_DATA">IoT & Weather Telemetry</option>
              <option value="HARVEST_METRICS">Aggregated Yield Outcomes</option>
              <option value="FULL_RESEARCH">Full Research Participation</option>
            </select>
            <button
              type="button"
              onClick={handleGrant}
              disabled={submitting}
              className="px-4 py-2 text-xs font-semibold rounded-lg bg-emerald-600 text-white hover:bg-emerald-700 transition-colors whitespace-nowrap"
            >
              {labels.grantConsent}
            </button>
          </div>
        ) : null}
      </div>
    </div>
  );
};
