"use client";

import React from "react";
import type { YieldForecastResponse } from "../../lib/api/types";

interface YieldFeasibilityBannerProps {
  forecast: YieldForecastResponse;
  labels: {
    yieldResearch: string;
    yieldWithheld: string;
    yieldWithheldReason: string;
    provenanceTier: string;
  };
}

export const YieldFeasibilityBanner: React.FC<YieldFeasibilityBannerProps> = ({
  forecast,
  labels,
}) => {
  return (
    <div className="rounded-xl border border-neutral-200 bg-white p-5 shadow-sm">
      <div className="flex items-center justify-between pb-3 border-b border-neutral-100">
        <div>
          <h3 className="font-semibold text-neutral-900">{labels.yieldResearch}</h3>
          <p className="text-xs text-neutral-500">Governed Yield Feasibility Protocol</p>
        </div>
        <span
          className={`px-2.5 py-1 text-xs font-semibold rounded ${
            forecast.is_forecast_available
              ? "bg-emerald-100 text-emerald-800"
              : "bg-neutral-100 text-neutral-700"
          }`}
        >
          {forecast.forecast_status}
        </span>
      </div>

      {!forecast.is_forecast_available ? (
        <div className="mt-4 rounded-lg bg-neutral-50 p-4 border border-neutral-200 text-xs text-neutral-700 space-y-2">
          <div className="font-semibold text-neutral-900 flex items-center gap-1.5">
            <svg className="w-4 h-4 text-neutral-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            {labels.yieldWithheld}
          </div>
          <p className="leading-relaxed text-neutral-600">
            {forecast.withholding_reason || labels.yieldWithheldReason}
          </p>
          <div className="pt-2 border-t border-neutral-200 flex items-center justify-between text-neutral-500">
            <span>Verified Ground-Truth Samples: {forecast.sample_count_available}</span>
            <span>Required Threshold: {forecast.minimum_sample_threshold_required}</span>
          </div>
        </div>
      ) : (
        <div className="mt-4 grid grid-cols-2 gap-3 text-center">
          <div className="rounded-lg bg-emerald-50 p-3 border border-emerald-100">
            <span className="text-xs text-neutral-500 block">Forecast Range</span>
            <span className="text-lg font-bold text-emerald-800">
              {forecast.predicted_yield_min} - {forecast.predicted_yield_max} q/acre
            </span>
          </div>
          <div className="rounded-lg bg-neutral-50 p-3 border border-neutral-100">
            <span className="text-xs text-neutral-500 block">Confidence Score</span>
            <span className="text-lg font-bold text-neutral-900">
              {forecast.confidence_score ? `${(forecast.confidence_score * 100).toFixed(0)}%` : "—"}
            </span>
          </div>
        </div>
      )}

      <p className="mt-3 text-[11px] text-neutral-400 italic">
        {forecast.scientific_disclaimer}
      </p>
    </div>
  );
};
