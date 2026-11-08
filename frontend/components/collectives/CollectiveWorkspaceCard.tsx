"use client";

import React from "react";
import type { AgriculturalOrganization, CollectiveAggregateAnalytics } from "../../lib/api/types";

interface CollectiveWorkspaceCardProps {
  organization: AgriculturalOrganization;
  analytics?: CollectiveAggregateAnalytics;
  onJoin?: (orgId: string) => Promise<void>;
  labels: {
    title: string;
    memberFarms: string;
    aggregatedAcreage: string;
    cohortPrivacyNotice: string;
    insufficientCohort: string;
    activities: string;
  };
}

export const CollectiveWorkspaceCard: React.FC<CollectiveWorkspaceCardProps> = ({
  organization,
  analytics,
  onJoin,
  labels,
}) => {
  const isCohortValid = analytics?.privacy_cohort_status === "VALID_COHORT_GE_5";

  return (
    <div className="bg-white rounded-xl shadow-sm border border-emerald-100 p-5 space-y-4 hover:border-emerald-300 transition-colors">
      <div className="flex items-start justify-between gap-3">
        <div>
          <div className="flex items-center gap-2 flex-wrap">
            <span className="px-2.5 py-0.5 text-xs font-semibold rounded-full bg-teal-50 text-teal-800 border border-teal-200">
              {organization.org_type}
            </span>
            <span className="text-xs text-gray-500">
              📍 {organization.district}, {organization.state}
            </span>
            <span
              className={`px-2 py-0.5 text-xs font-semibold rounded-full ${
                organization.verification_status === "APPROVED"
                  ? "bg-emerald-100 text-emerald-800 border border-emerald-300"
                  : "bg-amber-100 text-amber-800 border border-amber-300"
              }`}
            >
              {organization.verification_status}
            </span>
          </div>
          <h3 className="text-lg font-bold text-gray-900 mt-2">{organization.name}</h3>
        </div>
        {onJoin && (
          <button
            type="button"
            onClick={() => onJoin(organization.id)}
            className="px-3 py-1.5 text-xs font-semibold rounded-lg bg-emerald-600 text-white hover:bg-emerald-700 transition-colors"
          >
            Join Collective
          </button>
        )}
      </div>

      {organization.description && (
        <p className="text-gray-600 text-sm">{organization.description}</p>
      )}

      {/* Aggregate Farm Metrics with Strict Privacy Guardrail */}
      {analytics && (
        <div className="bg-gray-50 rounded-xl p-4 border border-gray-200 space-y-3">
          <h4 className="text-xs font-bold uppercase tracking-wider text-gray-700">
            Collective Production Overview
          </h4>

          <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
            <div className="bg-white p-3 rounded-lg border border-gray-100">
              <span className="text-xs text-gray-500 block">{labels.memberFarms}</span>
              <span className="text-lg font-bold text-gray-900">{analytics.total_member_farms}</span>
            </div>

            <div className="bg-white p-3 rounded-lg border border-gray-100">
              <span className="text-xs text-gray-500 block">{labels.aggregatedAcreage}</span>
              <span className="text-lg font-bold text-emerald-700">
                {isCohortValid ? `${analytics.aggregated_acreage} Acres` : "🔒 Suppressed"}
              </span>
            </div>

            <div className="bg-white p-3 rounded-lg border border-gray-100 col-span-2 sm:col-span-1">
              <span className="text-xs text-gray-500 block">Cohort Privacy</span>
              <span
                className={`text-xs font-semibold px-2 py-0.5 rounded-full inline-block mt-1 ${
                  isCohortValid
                    ? "bg-emerald-50 text-emerald-700 border border-emerald-200"
                    : "bg-amber-50 text-amber-700 border border-amber-200"
                }`}
              >
                {isCohortValid ? "Protected (N ≥ 5)" : "Suppressed (N < 5)"}
              </span>
            </div>
          </div>

          {/* Crop distribution if cohort valid */}
          {isCohortValid && Object.keys(analytics.crop_distribution).length > 0 && (
            <div className="pt-2">
              <span className="text-xs font-semibold text-gray-600 block mb-1.5">Active Crop Acreage</span>
              <div className="flex gap-2 flex-wrap">
                {Object.entries(analytics.crop_distribution).map(([crop, acreage]) => (
                  <span
                    key={crop}
                    className="px-2.5 py-1 text-xs bg-emerald-50 text-emerald-800 rounded-md border border-emerald-200 font-medium"
                  >
                    {crop.toUpperCase()}: {acreage} ac
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Privacy Notice Banner */}
          <div className="p-2.5 rounded-lg bg-blue-50 border border-blue-200 text-blue-900 text-xs">
            {isCohortValid ? labels.cohortPrivacyNotice : labels.insufficientCohort}
          </div>
        </div>
      )}
    </div>
  );
};
