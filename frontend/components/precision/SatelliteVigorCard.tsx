"use client";

import React from "react";
import type { SatelliteObservationItem } from "../../lib/api/types";

interface SatelliteVigorCardProps {
  observation?: SatelliteObservationItem | null;
  trendSummary?: string;
  disclaimer: string;
  labels: {
    title: string;
    ndviTrend: string;
    satelliteDisclaimer: string;
    canopyVigor: string;
  };
}

export const SatelliteVigorCard: React.FC<SatelliteVigorCardProps> = ({
  observation,
  trendSummary = "STABLE",
  disclaimer,
  labels,
}) => {
  const getBadgeColor = (trend: string) => {
    switch (trend) {
      case "VIGOR_INCREASING":
        return "bg-emerald-100 text-emerald-800 border-emerald-300";
      case "DECLINING_STRESS":
        return "bg-amber-100 text-amber-800 border-amber-300";
      case "HARVEST_CLEARING":
        return "bg-blue-100 text-blue-800 border-blue-300";
      default:
        return "bg-neutral-100 text-neutral-800 border-neutral-300";
    }
  };

  return (
    <div className="rounded-xl border border-neutral-200 bg-white p-5 shadow-sm">
      <div className="flex items-center justify-between pb-3 border-b border-neutral-100">
        <div>
          <h3 className="font-semibold text-neutral-900">{labels.title}</h3>
          <p className="text-xs text-neutral-500">Sentinel-2 10m L2A Analysis</p>
        </div>
        <span
          className={`px-2.5 py-1 text-xs font-medium rounded-full border ${getBadgeColor(
            trendSummary
          )}`}
        >
          {trendSummary}
        </span>
      </div>

      {observation ? (
        <div className="mt-4 grid grid-cols-3 gap-3 text-center">
          <div className="rounded-lg bg-emerald-50/50 p-2.5 border border-emerald-100">
            <span className="text-xs text-neutral-500 block">Mean NDVI</span>
            <span className="text-lg font-bold text-emerald-700">
              {observation.mean_ndvi.toFixed(2)}
            </span>
          </div>
          <div className="rounded-lg bg-blue-50/50 p-2.5 border border-blue-100">
            <span className="text-xs text-neutral-500 block">Mean EVI</span>
            <span className="text-lg font-bold text-blue-700">
              {observation.mean_evi.toFixed(2)}
            </span>
          </div>
          <div className="rounded-lg bg-teal-50/50 p-2.5 border border-teal-100">
            <span className="text-xs text-neutral-500 block">Moisture NDMI</span>
            <span className="text-lg font-bold text-teal-700">
              {observation.mean_ndmi.toFixed(2)}
            </span>
          </div>
        </div>
      ) : (
        <div className="py-6 text-center text-sm text-neutral-500">
          No recent clear-sky satellite acquisitions available for this plot.
        </div>
      )}

      {/* Non-Negotiable Evidence Disclaimer Box */}
      <div className="mt-4 rounded-lg bg-neutral-50 p-3 border border-neutral-200 flex items-start gap-2.5">
        <svg
          className="w-4 h-4 text-neutral-600 mt-0.5 shrink-0"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        </svg>
        <p className="text-xs text-neutral-600 leading-relaxed font-normal">
          {disclaimer}
        </p>
      </div>
    </div>
  );
};
