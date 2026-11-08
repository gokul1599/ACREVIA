"use client";

import React, { useState } from "react";
import type { FarmTwin, DataCompleteness } from "../../lib/api/types";

interface DigitalTwinDashboardProps {
  twin?: FarmTwin | null;
  completeness?: DataCompleteness | null;
  onReconcile?: () => Promise<void>;
  labels: {
    title: string;
    status: string;
    version: string;
    completeness: string;
    reconcile: string;
    snapshots: string;
    provenance: string;
  };
}

export const DigitalTwinDashboard: React.FC<DigitalTwinDashboardProps> = ({
  twin,
  completeness,
  onReconcile,
  labels,
}) => {
  const [reconciling, setReconciling] = useState(false);

  const handleReconcile = async () => {
    if (!onReconcile || reconciling) return;
    setReconciling(true);
    try {
      await onReconcile();
    } finally {
      setReconciling(false);
    }
  };

  const statusColor = (status?: string) => {
    switch (status) {
      case "SYNCHRONIZED":
        return "bg-emerald-100 text-emerald-800 border-emerald-300";
      case "STALE":
        return "bg-amber-100 text-amber-800 border-amber-300";
      case "RECONCILING":
        return "bg-sky-100 text-sky-800 border-sky-300";
      default:
        return "bg-neutral-100 text-neutral-800 border-neutral-300";
    }
  };

  const score = completeness?.overall_score ?? twin?.completeness_score ?? 0;

  return (
    <div className="rounded-xl border border-neutral-200 bg-white p-5 shadow-sm space-y-4">
      <div className="flex items-center justify-between border-b border-neutral-100 pb-3">
        <div>
          <h2 className="text-lg font-bold text-neutral-900">{labels.title}</h2>
          <p className="text-xs text-neutral-500">
            {labels.version}: v{twin?.twin_version ?? 1} • {twin?.active_plots_count ?? 0} Plots Active
          </p>
        </div>
        <div className="flex items-center gap-2">
          <span className={`px-2.5 py-1 text-xs font-semibold rounded-full border ${statusColor(twin?.state_status)}`}>
            {twin?.state_status ?? "SYNCHRONIZED"}
          </span>
          {onReconcile && (
            <button
              onClick={handleReconcile}
              disabled={reconciling}
              className="px-3 py-1 text-xs font-medium bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 disabled:opacity-50 transition-colors"
            >
              {reconciling ? "Syncing..." : labels.reconcile}
            </button>
          )}
        </div>
      </div>

      {/* Completeness Meter */}
      <div className="space-y-2">
        <div className="flex justify-between text-xs font-medium text-neutral-700">
          <span>{labels.completeness}</span>
          <span className="font-bold text-emerald-700">{score}%</span>
        </div>
        <div className="w-full bg-neutral-100 rounded-full h-2.5 overflow-hidden">
          <div
            className={`h-2.5 rounded-full ${score >= 65 ? "bg-emerald-600" : "bg-amber-500"}`}
            style={{ width: `${Math.min(100, Math.max(0, score))}%` }}
          />
        </div>
        {completeness?.missing_critical_fields && completeness.missing_critical_fields.length > 0 && (
          <p className="text-xs text-amber-700">
            Missing: {completeness.missing_critical_fields.join(", ")}
          </p>
        )}
      </div>

      {/* Dimension Breakdown */}
      {completeness?.dimensions && (
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 pt-2 border-t border-neutral-100 text-xs">
          {Object.entries(completeness.dimensions).map(([dim, val]) => (
            <div key={dim} className="p-2 bg-neutral-50 rounded-lg border border-neutral-200">
              <span className="text-neutral-500 capitalize block truncate">
                {dim.replace(/_/g, " ")}
              </span>
              <span className="font-semibold text-neutral-800">{val}%</span>
            </div>
          ))}
        </div>
      )}

      {/* Snapshot Reference */}
      {twin?.latest_snapshot && (
        <div className="p-3 bg-neutral-50 rounded-lg border border-neutral-200 text-xs text-neutral-600 space-y-1">
          <div className="flex justify-between">
            <span className="font-medium text-neutral-800">Latest Immutable Snapshot:</span>
            <span>v{twin.latest_snapshot.snapshot_version}</span>
          </div>
          <div className="truncate font-mono text-[11px] text-neutral-500">
            Hash: {twin.latest_snapshot.payload_hash}
          </div>
        </div>
      )}
    </div>
  );
};
