"use client";

import React from "react";
import type { KnowledgeContribution } from "../../lib/api/types";

interface KnowledgeContributionCardProps {
  contribution: KnowledgeContribution;
  onReview?: (contributionId: string, decision: string, comments: string) => Promise<void>;
  onHandoffKrishiBrain?: (contributionId: string) => Promise<void>;
  labels: {
    title: string;
    underReview: string;
    approved: string;
    krishiBrainIngested: string;
    evidenceReferences: string;
  };
}

export const KnowledgeContributionCard: React.FC<KnowledgeContributionCardProps> = ({
  contribution,
  onReview,
  onHandoffKrishiBrain,
  labels,
}) => {
  const getStatusBadge = () => {
    switch (contribution.status) {
      case "APPROVED":
        return <span className="px-2.5 py-0.5 text-xs font-semibold rounded-full bg-emerald-100 text-emerald-800 border border-emerald-300">✓ {labels.approved}</span>;
      case "PUBLISHED":
        return <span className="px-2.5 py-0.5 text-xs font-semibold rounded-full bg-blue-100 text-blue-800 border border-blue-300">★ {labels.krishiBrainIngested}</span>;
      case "REJECTED":
        return <span className="px-2.5 py-0.5 text-xs font-semibold rounded-full bg-rose-100 text-rose-800 border border-rose-300">✗ Rejected</span>;
      default:
        return <span className="px-2.5 py-0.5 text-xs font-semibold rounded-full bg-amber-100 text-amber-800 border border-amber-300">⏳ {labels.underReview}</span>;
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-emerald-100 p-5 space-y-4 hover:border-emerald-300 transition-colors">
      <div className="flex items-start justify-between gap-3">
        <div>
          <div className="flex items-center gap-2 flex-wrap">
            <span className="px-2.5 py-0.5 text-xs font-semibold rounded-full bg-purple-50 text-purple-800 border border-purple-200">
              {contribution.contribution_type}
            </span>
            {contribution.crop_id && (
              <span className="px-2 py-0.5 text-xs font-medium rounded-full bg-amber-50 text-amber-800 border border-amber-200">
                {contribution.crop_id.toUpperCase()}
              </span>
            )}
            <span className="text-xs text-gray-500">Scope: {contribution.geographic_scope}</span>
          </div>
          <h3 className="text-lg font-bold text-gray-900 mt-2">{contribution.title}</h3>
        </div>
        <div>{getStatusBadge()}</div>
      </div>

      <p className="text-gray-700 text-sm whitespace-pre-line leading-relaxed">{contribution.description}</p>

      {/* Evidence references */}
      {contribution.evidence_references && contribution.evidence_references.length > 0 && (
        <div className="bg-emerald-50/50 rounded-lg p-3 border border-emerald-100">
          <h4 className="text-xs font-semibold text-emerald-900 mb-1.5 flex items-center gap-1.5">
            <span>📚</span> {labels.evidenceReferences}
          </h4>
          <ul className="list-disc list-inside text-xs text-emerald-800 space-y-0.5">
            {contribution.evidence_references.map((ref, idx) => (
              <li key={idx}>{ref}</li>
            ))}
          </ul>
        </div>
      )}

      {/* KrishiBrain Ingestion Status */}
      {contribution.krishi_brain_ingested && (
        <div className="flex items-center gap-2 p-2.5 rounded-lg bg-blue-50 border border-blue-200 text-blue-900 text-xs font-medium">
          <span>🧠</span>
          <span>Verified and indexed into KrishiBrain RAG as Document <code>{contribution.krishi_brain_doc_id?.slice(0, 8)}...</code></span>
        </div>
      )}

      {/* Admin / Expert Actions */}
      <div className="pt-2 border-t border-gray-100 flex items-center justify-between gap-3 flex-wrap">
        <span className="text-[11px] text-gray-500">License: {contribution.usage_permission}</span>
        <div className="flex gap-2">
          {onReview && contribution.status === "SUBMITTED" && (
            <button
              type="button"
              onClick={() => onReview(contribution.id, "APPROVE", "Scientifically grounded and safe for regional conditions.")}
              className="px-3 py-1 text-xs font-medium rounded-md bg-emerald-600 text-white hover:bg-emerald-700"
            >
              Approve Contribution
            </button>
          )}
          {onHandoffKrishiBrain && contribution.status === "APPROVED" && (
            <button
              type="button"
              onClick={() => onHandoffKrishiBrain(contribution.id)}
              className="px-3 py-1 text-xs font-medium rounded-md bg-blue-600 text-white hover:bg-blue-700"
            >
              Ingest into KrishiBrain
            </button>
          )}
        </div>
      </div>
    </div>
  );
};
