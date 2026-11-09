"use client";

import React, { useState } from "react";
import type { DecisionRecord } from "../../lib/api/types";

interface DecisionIntelligenceCardProps {
  decision: DecisionRecord;
  language?: "en" | "te" | "hi";
  onFeedback?: (decisionId: string, feedback: { farmer_action_taken: string; farmer_rating?: number; feedback_notes?: string }) => Promise<void>;
  labels: {
    title: string;
    analyzeQuery: string;
    recommendationState: string;
    groundedExplanation: string;
    evidencePanel: string;
    uncertaintyDisclosures: string;
    expertEscalation: string;
    feedback: string;
  };
}

export const DecisionIntelligenceCard: React.FC<DecisionIntelligenceCardProps> = ({
  decision,
  language = "en",
  onFeedback,
  labels,
}) => {
  const [actionTaken, setActionTaken] = useState<string>("ADOPTED");
  const [rating, _setRating] = useState<number>(5);
  const [feedbackNotes, _setFeedbackNotes] = useState<string>("");
  const [feedbackSubmitted, setFeedbackSubmitted] = useState<boolean>(false);
  const [submitting, setSubmitting] = useState<boolean>(false);

  const getExplanation = () => {
    if (language === "te") return decision.grounded_explanation_te;
    if (language === "hi") return decision.grounded_explanation_hi;
    return decision.grounded_explanation_en;
  };

  const getStateBadge = (state: string) => {
    switch (state) {
      case "EVIDENCE_SUPPORTED":
        return "bg-emerald-100 text-emerald-800 border-emerald-300";
      case "REQUIRES_EXPERT_REVIEW":
        return "bg-amber-100 text-amber-800 border-amber-300";
      case "REQUIRES_MORE_INFORMATION":
        return "bg-sky-100 text-sky-800 border-sky-300";
      case "NOT_SUPPORTED":
      case "INSUFFICIENT_EVIDENCE":
        return "bg-rose-100 text-rose-800 border-rose-300";
      default:
        return "bg-neutral-100 text-neutral-800 border-neutral-300";
    }
  };

  const handleFeedbackSubmit = async () => {
    if (!onFeedback || submitting) return;
    setSubmitting(true);
    try {
      await onFeedback(decision.id, {
        farmer_action_taken: actionTaken,
        farmer_rating: rating,
        feedback_notes: feedbackNotes,
      });
      setFeedbackSubmitted(true);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="rounded-xl border border-neutral-200 bg-white p-5 shadow-sm space-y-4">
      <div className="flex items-center justify-between border-b border-neutral-100 pb-3">
        <div>
          <h2 className="text-lg font-bold text-neutral-900">{labels.title}</h2>
          <p className="text-xs text-neutral-500">
            Category: {decision.decision_category.replace(/_/g, " ")}
          </p>
        </div>
        <span className={`px-2.5 py-1 text-xs font-semibold rounded-full border ${getStateBadge(decision.recommendation_state)}`}>
          {decision.recommendation_state.replace(/_/g, " ")}
        </span>
      </div>

      {/* Query Display */}
      <div className="p-3 bg-neutral-50 rounded-lg border border-neutral-200 text-xs">
        <span className="font-semibold text-neutral-700 block mb-1">Farmer Inquiry:</span>
        <p className="text-neutral-900 italic">"{decision.query_text}"</p>
      </div>

      {/* Grounded Explanation */}
      <div className="space-y-1">
        <span className="text-xs font-semibold text-neutral-700 block">{labels.groundedExplanation}:</span>
        <p className="text-sm leading-relaxed text-neutral-800 font-medium bg-emerald-50/40 p-3.5 rounded-xl border border-emerald-100">
          {getExplanation()}
        </p>
      </div>

      {/* Expert Escalation Notice */}
      {decision.expert_escalation_case_id && (
        <div className="p-3 bg-amber-50 rounded-lg border border-amber-200 text-xs text-amber-900 space-y-1">
          <span className="font-bold block">{labels.expertEscalation}</span>
          <p>
            Case #{decision.expert_escalation_case_id.slice(0, 8)} opened in ExpertConnect for review by a verified agricultural specialist.
          </p>
        </div>
      )}

      {/* Evidence Sources Panel */}
      {decision.evidence_sources_json && decision.evidence_sources_json.length > 0 && (
        <div className="p-3 bg-neutral-50 rounded-lg border border-neutral-200 text-xs space-y-2">
          <span className="font-semibold text-neutral-800 block">{labels.evidencePanel}:</span>
          <ul className="space-y-1 text-neutral-600">
            {decision.evidence_sources_json.map((src, i) => (
              <li key={i} className="flex items-start gap-1.5">
                <span className="text-emerald-700 font-bold">•</span>
                <span>
                  <strong className="text-neutral-800">{src.source_title}</strong>
                  {src.chapter ? ` — ${src.chapter}` : ""}
                </span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Uncertainty Disclosures */}
      {decision.uncertainty_disclosures_json && decision.uncertainty_disclosures_json.length > 0 && (
        <div className="p-3 bg-neutral-50 rounded-lg border border-neutral-200 text-[11px] text-neutral-500">
          <span className="font-semibold text-neutral-700 block mb-1">{labels.uncertaintyDisclosures}:</span>
          <ul className="list-disc pl-4 space-y-0.5">
            {decision.uncertainty_disclosures_json.map((u, i) => (
              <li key={i}>{u}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Farmer Feedback Section */}
      {onFeedback && !feedbackSubmitted && (
        <div className="pt-3 border-t border-neutral-100 space-y-2 text-xs">
          <span className="font-semibold text-neutral-800 block">{labels.feedback}:</span>
          <div className="flex gap-2">
            {["ADOPTED", "PARTIALLY_ADOPTED", "REJECTED"].map((act) => (
              <button
                key={act}
                onClick={() => setActionTaken(act)}
                className={`px-3 py-1.5 rounded-lg border text-xs font-medium transition-colors ${
                  actionTaken === act
                    ? "bg-emerald-600 text-white border-emerald-600"
                    : "bg-white text-neutral-700 border-neutral-200 hover:bg-neutral-50"
                }`}
              >
                {act.replace(/_/g, " ")}
              </button>
            ))}
          </div>
          <div className="flex justify-end pt-1">
            <button
              onClick={handleFeedbackSubmit}
              disabled={submitting}
              className="px-3 py-1 text-xs font-medium bg-neutral-900 text-white rounded-lg hover:bg-neutral-800 disabled:opacity-50"
            >
              {submitting ? "Submitting..." : "Submit Feedback"}
            </button>
          </div>
        </div>
      )}

      {feedbackSubmitted && (
        <div className="p-2 bg-emerald-50 border border-emerald-200 rounded text-center text-xs text-emerald-800 font-medium">
          ✓ Feedback recorded. Thank you for contributing to agricultural intelligence verification.
        </div>
      )}
    </div>
  );
};
