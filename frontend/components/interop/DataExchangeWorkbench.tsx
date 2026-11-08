"use client";

import React, { useState } from "react";
import type { DataExchangeJob } from "../../lib/api/types";

interface DataExchangeWorkbenchProps {
  jobs: DataExchangeJob[];
  labels: {
    title: string;
    subtitle: string;
    exportData: string;
    importData: string;
    format: string;
    redactPii: string;
    redactGps: string;
    preserveConflicts: string;
    checksum: string;
    manifest: string;
  };
  onRequestExport: (format: string, redactPii: boolean, redactGps: boolean) => void;
  onRequestImport: (payload: string, category: string) => void;
}

export const DataExchangeWorkbench: React.FC<DataExchangeWorkbenchProps> = ({
  jobs,
  labels,
  onRequestExport,
  onRequestImport,
}) => {
  const [activeTab, setActiveTab] = useState<"EXPORT" | "IMPORT">("EXPORT");
  const [exportFormat, setExportFormat] = useState<string>("JSON");
  const [redactPii, setRedactPii] = useState<boolean>(true);
  const [redactGps, setRedactGps] = useState<boolean>(true);
  const [importPayload, setImportPayload] = useState<string>("");
  const [importCategory, setImportCategory] = useState<string>("SOIL_TESTS");

  return (
    <div className="bg-white rounded-xl shadow-sm border border-indigo-100 p-5 space-y-4">
      <div className="flex items-center justify-between border-b pb-3 border-gray-100">
        <div>
          <h3 className="text-lg font-bold text-gray-900">{labels.title}</h3>
          <p className="text-xs text-gray-500">{labels.subtitle}</p>
        </div>
        <div className="flex rounded-lg bg-gray-100 p-0.5">
          <button
            onClick={() => setActiveTab("EXPORT")}
            className={`px-3 py-1 rounded-md text-xs font-semibold transition-all ${
              activeTab === "EXPORT"
                ? "bg-white text-indigo-700 shadow-sm"
                : "text-gray-500 hover:text-gray-900"
            }`}
          >
            {labels.exportData}
          </button>
          <button
            onClick={() => setActiveTab("IMPORT")}
            className={`px-3 py-1 rounded-md text-xs font-semibold transition-all ${
              activeTab === "IMPORT"
                ? "bg-white text-indigo-700 shadow-sm"
                : "text-gray-500 hover:text-gray-900"
            }`}
          >
            {labels.importData}
          </button>
        </div>
      </div>

      {activeTab === "EXPORT" ? (
        <div className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            <div>
              <label className="block text-xs font-semibold text-gray-700 mb-1">{labels.format}</label>
              <select
                value={exportFormat}
                onChange={(e) => setExportFormat(e.target.value)}
                className="w-full text-xs p-2 border border-gray-200 rounded-lg bg-gray-50 focus:bg-white focus:ring-1 focus:ring-indigo-500"
              >
                <option value="JSON">Canonical JSON Package</option>
                <option value="CSV">Flattened CSV Table</option>
                <option value="GEOJSON">Spatial GeoJSON Features</option>
                <option value="ARCHIVE">Cryptographic ZIP Archive</option>
              </select>
            </div>
            <div className="flex items-center pt-5">
              <label className="inline-flex items-center text-xs font-medium text-gray-700 cursor-pointer">
                <input
                  type="checkbox"
                  checked={redactPii}
                  onChange={(e) => setRedactPii(e.target.checked)}
                  className="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500 mr-2"
                />
                {labels.redactPii}
              </label>
            </div>
            <div className="flex items-center pt-5">
              <label className="inline-flex items-center text-xs font-medium text-gray-700 cursor-pointer">
                <input
                  type="checkbox"
                  checked={redactGps}
                  onChange={(e) => setRedactGps(e.target.checked)}
                  className="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500 mr-2"
                />
                {labels.redactGps}
              </label>
            </div>
          </div>

          <button
            onClick={() => onRequestExport(exportFormat, redactPii, redactGps)}
            className="w-full py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-xs font-semibold shadow-sm transition-colors"
          >
            {labels.exportData}
          </button>
        </div>
      ) : (
        <div className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-semibold text-gray-700 mb-1">Target Category</label>
              <select
                value={importCategory}
                onChange={(e) => setImportCategory(e.target.value)}
                className="w-full text-xs p-2 border border-gray-200 rounded-lg bg-gray-50"
              >
                <option value="SOIL_TESTS">Soil Laboratory Test Records</option>
                <option value="OBSERVATIONS">Crop Scouting Observations</option>
                <option value="MARKET_PRICES">Market Mandi Prices</option>
                <option value="HARVEST_RECORDS">Harvest & Yield Data</option>
              </select>
            </div>
            <div className="flex items-center pt-5">
              <span className="text-[11px] text-emerald-700 bg-emerald-50 px-2.5 py-1.5 rounded border border-emerald-200 font-medium">
                ✓ {labels.preserveConflicts}
              </span>
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-gray-700 mb-1">Payload (JSON or CSV)</label>
            <textarea
              rows={4}
              value={importPayload}
              onChange={(e) => setImportPayload(e.target.value)}
              placeholder='[{"sample_code": "TS-SL-001", "ph": 7.2, "ec_ds_m": 0.65, "organic_carbon_percent": 0.54}]'
              className="w-full font-mono text-xs p-2.5 border border-gray-200 rounded-lg bg-gray-50 focus:bg-white"
            />
          </div>

          <button
            onClick={() => onRequestImport(importPayload, importCategory)}
            disabled={!importPayload.trim()}
            className="w-full py-2 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white rounded-lg text-xs font-semibold shadow-sm transition-colors"
          >
            {labels.importData}
          </button>
        </div>
      )}

      {/* Recent Exchange Jobs Log */}
      <div className="pt-2">
        <h4 className="text-xs font-semibold uppercase text-gray-500 tracking-wider mb-2">Recent Portability Jobs</h4>
        <div className="space-y-2">
          {jobs.length === 0 ? (
            <div className="text-xs text-gray-400 py-3 text-center">No export or import jobs performed yet.</div>
          ) : (
            jobs.slice(0, 5).map((j) => (
              <div key={j.id} className="p-2.5 rounded bg-gray-50 border border-gray-100 flex items-center justify-between text-xs">
                <div>
                  <span className="font-semibold text-gray-800">{j.job_type} ({j.format})</span>
                  <span className="text-[10px] text-gray-500 block">
                    Processed: {j.records_processed} • Conflicts: {j.conflicts_detected} • Status: {j.status}
                  </span>
                </div>
                {j.checksum_sha256 && (
                  <span className="font-mono text-[9px] bg-white px-2 py-0.5 rounded border border-gray-200 text-gray-600" title={j.checksum_sha256}>
                    SHA-256: {j.checksum_sha256.slice(0, 10)}...
                  </span>
                )}
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};
