"use client";

import React, { useState } from "react";
import type { EconomicsSummary, CropLossEvidencePackage } from "../../lib/api/types";

interface CropSeasonEconomicsCardProps {
  summary: EconomicsSummary;
  evidencePackage?: CropLossEvidencePackage;
  onGenerateEvidence?: (incidentDate: string, incidentType: string, notes?: string) => Promise<void>;
  labels: {
    title: string;
    subtitle: string;
    costOfCultivation: string;
    grossRevenue: string;
    netFarmMargin: string;
    costPerQuintal: string;
    marginPerQuintal: string;
    completenessScore: string;
    generateEvidence: string;
    hashVerified: string;
  };
}

export const CropSeasonEconomicsCard: React.FC<CropSeasonEconomicsCardProps> = ({
  summary,
  evidencePackage,
  onGenerateEvidence,
  labels,
}) => {
  const [showEvidenceModal, setShowEvidenceModal] = useState(false);
  const [incidentDate, setIncidentDate] = useState(new Date().toISOString().split("T")[0]);
  const [incidentType, setIncidentType] = useState("EXCESS_RAINFALL");
  const [notes, setNotes] = useState("");
  const [generating, setGenerating] = useState(false);

  const netRealizationNum = parseFloat(summary.net_realization || "0");
  const isProfitable = netRealizationNum >= 0;

  const handleGenerateEvidenceSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (onGenerateEvidence) {
      setGenerating(true);
      try {
        await onGenerateEvidence(incidentDate, incidentType, notes || undefined);
        setShowEvidenceModal(false);
      } finally {
        setGenerating(false);
      }
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-emerald-100 p-6 space-y-6">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-xl font-bold text-slate-800">{labels.title}</h2>
            <span className={`px-2.5 py-0.5 text-xs font-bold rounded-full ${
              summary.completeness_badge === "COMPLETE"
                ? "bg-emerald-100 text-emerald-800"
                : summary.completeness_badge === "PARTIAL_DATA"
                ? "bg-amber-100 text-amber-800"
                : "bg-rose-100 text-rose-800"
            }`}>
              {summary.completeness_badge.replace("_", " ")} ({summary.data_completeness_pct}%)
            </span>
          </div>
          <p className="text-sm text-slate-500">{labels.subtitle} • {summary.crop_name}</p>
        </div>
        <button
          onClick={() => setShowEvidenceModal(true)}
          className="inline-flex items-center px-4 py-2 bg-slate-900 hover:bg-black text-white text-sm font-medium rounded-lg shadow-sm transition gap-2"
        >
          <svg className="w-4 h-4 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          {labels.generateEvidence}
        </button>
      </div>

      {/* Primary KPI Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="p-4 bg-rose-50 border border-rose-200 rounded-lg">
          <span className="text-xs font-semibold uppercase text-rose-700">{labels.costOfCultivation}</span>
          <p className="text-2xl font-black text-rose-950 mt-1 font-mono">₹{parseFloat(summary.total_expenses).toLocaleString("en-IN", { minimumFractionDigits: 2 })}</p>
          <span className="text-xs text-rose-700">Cost: ₹{parseFloat(summary.cost_per_unit).toFixed(0)} / {summary.unit}</span>
        </div>
        <div className="p-4 bg-sky-50 border border-sky-200 rounded-lg">
          <span className="text-xs font-semibold uppercase text-sky-700">{labels.grossRevenue}</span>
          <p className="text-2xl font-black text-sky-950 mt-1 font-mono">₹{parseFloat(summary.gross_revenue).toLocaleString("en-IN", { minimumFractionDigits: 2 })}</p>
          <span className="text-xs text-sky-700">Sold: {parseFloat(summary.total_sold_quantity).toFixed(1)} {summary.unit}</span>
        </div>
        <div className={`p-4 border rounded-lg ${isProfitable ? "bg-emerald-50 border-emerald-200" : "bg-amber-50 border-amber-200"}`}>
          <span className={`text-xs font-semibold uppercase ${isProfitable ? "text-emerald-700" : "text-amber-700"}`}>{labels.netFarmMargin}</span>
          <p className={`text-2xl font-black mt-1 font-mono ${isProfitable ? "text-emerald-950" : "text-amber-950"}`}>
            ₹{netRealizationNum.toLocaleString("en-IN", { minimumFractionDigits: 2 })}
          </p>
          <span className={`text-xs ${isProfitable ? "text-emerald-700" : "text-amber-700"}`}>
            Margin: ₹{parseFloat(summary.net_margin_per_unit).toFixed(0)} / {summary.unit}
          </span>
        </div>
      </div>

      {/* Expense Category Breakdown */}
      {summary.category_breakdown && summary.category_breakdown.length > 0 && (
        <div className="space-y-3">
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500">Cultivation Cost Distribution</h3>
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
            {summary.category_breakdown.map((b) => (
              <div key={b.category} className="p-3 bg-slate-50 rounded-lg border border-slate-200">
                <span className="text-[11px] font-semibold text-slate-600 block">{b.category}</span>
                <span className="text-sm font-bold text-slate-900 font-mono mt-0.5 block">
                  ₹{parseFloat(b.total_amount).toFixed(0)}
                </span>
                <span className="text-[10px] text-slate-400 font-mono">{b.percentage_of_total}% of budget</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Evidence Package Banner if generated */}
      {evidencePackage && (
        <div className="p-4 bg-slate-900 text-white rounded-xl space-y-2 border border-slate-800">
          <div className="flex justify-between items-center text-xs">
            <span className="font-bold text-emerald-400 uppercase tracking-wider">PMFBY CROP LOSS EVIDENCE BUNDLE</span>
            <span className="text-slate-400 font-mono">Issued {evidencePackage.generated_at.split("T")[0]}</span>
          </div>
          <div className="text-xs text-slate-300">
            Incident: <strong className="text-white">{evidencePackage.incident_type}</strong> on {evidencePackage.incident_date}
          </div>
          <div className="text-[10px] font-mono text-emerald-400 break-all bg-slate-950 p-2 rounded border border-slate-800">
            SHA-256: {evidencePackage.package_hash}
          </div>
        </div>
      )}

      {/* Disclaimers */}
      <div className="pt-2 border-t border-slate-100">
        <ul className="text-[11px] text-slate-400 list-disc list-inside space-y-1">
          {summary.economic_disclaimers.map((d, i) => (
            <li key={i}>{d}</li>
          ))}
        </ul>
      </div>

      {/* Insurance Evidence Modal */}
      {showEvidenceModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-2xl max-w-md w-full p-6 space-y-4 shadow-2xl">
            <div className="flex justify-between items-start">
              <div>
                <h3 className="text-lg font-bold text-slate-900">{labels.generateEvidence}</h3>
                <p className="text-xs text-slate-500">Builds a tamper-evident audit package for PMFBY crop insurance claims.</p>
              </div>
              <button onClick={() => setShowEvidenceModal(false)} className="text-slate-400 hover:text-slate-600 font-bold">✕</button>
            </div>

            <form onSubmit={handleGenerateEvidenceSubmit} className="space-y-3">
              <div>
                <label className="block text-xs font-medium text-slate-700">Incident Date</label>
                <input
                  type="date"
                  required
                  value={incidentDate}
                  onChange={(e) => setIncidentDate(e.target.value)}
                  className="mt-1 w-full border border-slate-300 rounded-lg p-2 text-sm"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-700">Adverse Weather / Incident Type</label>
                <select
                  value={incidentType}
                  onChange={(e) => setIncidentType(e.target.value)}
                  className="mt-1 w-full border border-slate-300 rounded-lg p-2 text-sm"
                >
                  <option value="EXCESS_RAINFALL">Excess Rainfall / Waterlogging</option>
                  <option value="CYCLONE_WIND">Severe Cyclone / Lodging Winds</option>
                  <option value="HAILSTORM">Localized Hailstorm</option>
                  <option value="EXTREME_DROUGHT">Dry Spell / Terminal Drought</option>
                  <option value="PEST_OUTBREAK">Pest Outbreak (Bollworm / Leaf Spot)</option>
                </select>
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-700">Field Loss Description</label>
                <textarea
                  rows={2}
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  placeholder="e.g. Unseasonal rain inundated cotton bolls during 2nd picking window causing boll rot."
                  className="mt-1 w-full border border-slate-300 rounded-lg p-2 text-sm"
                />
              </div>
              <div className="flex justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowEvidenceModal(false)}
                  className="px-4 py-2 border border-slate-300 rounded-lg text-sm text-slate-600"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={generating}
                  className="px-4 py-2 bg-slate-900 hover:bg-black text-white rounded-lg text-sm font-medium"
                >
                  {generating ? "Generating SHA-256 Bundle..." : "Generate Signed Bundle"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
