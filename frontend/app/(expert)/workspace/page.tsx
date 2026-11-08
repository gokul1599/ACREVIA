"use client";

import React, { useState, useEffect, useCallback, Suspense } from "react";
import { useAuth } from "@/lib/auth/context";
import { api } from "@/lib/api/client";
import type {
  ExpertCaseItem,
  ExpertCaseDossier,
  ExpertAssessment,
  ExpertAssessmentRevision,
} from "@/lib/api/types";
import { en } from "@/messages/en";
import { te } from "@/messages/te";
import { hi } from "@/messages/hi";

function ExpertWorkspaceContent() {
  const { user } = useAuth();
  const [lang] = useState<"te" | "en" | "hi">(user?.language_preference || "en");
  const t = lang === "te" ? te : lang === "hi" ? hi : en;

  const [cases, setCases] = useState<ExpertCaseItem[]>([]);
  const [selectedCaseId, setSelectedCaseId] = useState<string | null>(null);
  const [dossier, setDossier] = useState<ExpertCaseDossier | null>(null);
  const [revisions, setRevisions] = useState<ExpertAssessmentRevision[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [filterCrop, setFilterCrop] = useState<string>("");
  const [filterPriority, setFilterPriority] = useState<string>("");

  // Assessment Form State
  const [confirmedCrop, setConfirmedCrop] = useState("cotton");
  const [primaryCondition, setPrimaryCondition] = useState("");
  const [differentialTags, setDifferentialTags] = useState("");
  const [confidenceRating, setConfidenceRating] = useState(4);
  const [urgencyLevel, setUrgencyLevel] = useState<"LOW" | "ROUTINE" | "HIGH" | "EMERGENCY">("ROUTINE");
  const [managementPlan, setManagementPlan] = useState("");
  const [ipmStrategy, setIpmStrategy] = useState("");
  const [cibrcAdvisories, setCibrcAdvisories] = useState("");
  const [revisionReason, setRevisionReason] = useState("");
  const [message, setMessage] = useState<string | null>(null);

  const loadCases = useCallback(async () => {
    setIsLoading(true);
    try {
      const items = await api.listExpertCases({
        crop_id: filterCrop || undefined,
        priority: filterPriority || undefined,
      });
      setCases(items);
      if (items.length > 0 && !selectedCaseId) {
        setSelectedCaseId(items[0].id);
      }
    } catch {
      // Mock fallback for UI if unauthenticated in preview
      setCases([]);
    } finally {
      setIsLoading(false);
    }
  }, [filterCrop, filterPriority, selectedCaseId]);

  const loadDossier = useCallback(async (caseId: string) => {
    setIsLoading(true);
    try {
      const d = await api.getExpertCaseDossier(caseId);
      setDossier(d);
      setConfirmedCrop(d.crop_id || "cotton");
      if (d.assessment) {
        setPrimaryCondition(d.assessment.primary_condition || "");
        setDifferentialTags((d.assessment.differential_diagnoses || []).join(", "));
        setConfidenceRating(d.assessment.confidence_rating || 4);
        setUrgencyLevel(d.assessment.urgency_level || "ROUTINE");
        setManagementPlan(d.assessment.management_plan || "");
        setIpmStrategy(d.assessment.ipm_strategy || "");
        setCibrcAdvisories(d.assessment.cibrc_advisories || "");
        // Fetch revisions
        const revs = await api.getExpertAssessmentRevisions(caseId).catch(() => []);
        setRevisions(revs);
      } else {
        setPrimaryCondition("");
        setDifferentialTags("");
        setManagementPlan("");
        setIpmStrategy("");
        setCibrcAdvisories("");
        setRevisions([]);
      }
    } catch {
      setDossier(null);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    loadCases();
  }, [loadCases]);

  useEffect(() => {
    if (selectedCaseId) {
      loadDossier(selectedCaseId);
    }
  }, [selectedCaseId, loadDossier]);

  const handleClaim = async (caseId: string) => {
    try {
      await api.claimExpertCase(caseId);
      setMessage("Case claimed successfully. You are now the assigned agronomist.");
      loadCases();
      loadDossier(caseId);
    } catch (e: any) {
      setMessage(`Claim failed: ${e.message}`);
    }
  };

  const handleSubmitAssessment = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedCaseId) return;

    setIsSubmitting(true);
    setMessage(null);
    try {
      const diffArray = differentialTags
        .split(",")
        .map((s) => s.trim())
        .filter(Boolean);

      if (dossier?.assessment) {
        // Revision
        if (!revisionReason.trim()) {
          setMessage("Revision reason is required to update an existing assessment.");
          setIsSubmitting(false);
          return;
        }
        await api.reviseExpertAssessment(selectedCaseId, {
          confirmed_crop: confirmedCrop,
          primary_condition: primaryCondition,
          differential_diagnoses: diffArray,
          confidence_rating: confidenceRating,
          urgency_level: urgencyLevel,
          management_plan: managementPlan,
          ipm_strategy: ipmStrategy,
          cibrc_advisories: cibrcAdvisories,
          revision_reason: revisionReason,
        });
        setMessage("Assessment revision committed to immutable audit log.");
      } else {
        // Initial Submission
        await api.submitExpertAssessment(selectedCaseId, {
          confirmed_crop: confirmedCrop,
          primary_condition: primaryCondition,
          differential_diagnoses: diffArray,
          confidence_rating: confidenceRating,
          urgency_level: urgencyLevel,
          management_plan: managementPlan,
          ipm_strategy: ipmStrategy,
          cibrc_advisories: cibrcAdvisories,
        });
        setMessage("Diagnostic report certified and dispatched to farmer.");
      }
      loadCases();
      loadDossier(selectedCaseId);
    } catch (err: any) {
      setMessage(`Submission failed: ${err.message}`);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100 p-4 md:p-8">
      <header className="mb-8 border-b border-slate-800 pb-4 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-emerald-400">ACREVIA ExpertConnect</h1>
          <p className="text-sm text-slate-400">{t.expertconnect.subtitle}</p>
        </div>
        <div className="flex items-center gap-3">
          <span className="text-xs bg-emerald-950 text-emerald-300 border border-emerald-700 px-3 py-1 rounded-full font-mono">
            PJTSAU / ICAR Accredited Network
          </span>
        </div>
      </header>

      {message && (
        <div className="mb-6 p-4 rounded-xl bg-emerald-950/80 border border-emerald-600 text-emerald-200 text-sm">
          {message}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Triage Queue */}
        <aside className="lg:col-span-4 bg-slate-800/80 border border-slate-700 rounded-2xl p-4 flex flex-col h-[82vh]">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-semibold text-slate-200">{t.expertconnect.queueTitle}</h2>
            <span className="text-xs text-slate-400 font-mono">{cases.length} cases</span>
          </div>

          <div className="flex gap-2 mb-4">
            <select
              value={filterCrop}
              onChange={(e) => setFilterCrop(e.target.value)}
              className="bg-slate-900 border border-slate-700 text-xs rounded-lg px-2 py-1.5 text-slate-300"
            >
              <option value="">All Crops</option>
              <option value="cotton">Cotton</option>
              <option value="rice">Rice</option>
              <option value="chilli">Chilli</option>
            </select>
            <select
              value={filterPriority}
              onChange={(e) => setFilterPriority(e.target.value)}
              className="bg-slate-900 border border-slate-700 text-xs rounded-lg px-2 py-1.5 text-slate-300"
            >
              <option value="">All Priorities</option>
              <option value="URGENT">Urgent</option>
              <option value="ROUTINE">Routine</option>
            </select>
          </div>

          <div className="overflow-y-auto flex-1 space-y-3 pr-1">
            {isLoading && cases.length === 0 ? (
              <p className="text-xs text-slate-400 text-center py-8">Loading consultation cases...</p>
            ) : cases.length === 0 ? (
              <p className="text-xs text-slate-400 text-center py-8">No active cases matching filter.</p>
            ) : (
              cases.map((c) => (
                <div
                  key={c.id}
                  onClick={() => setSelectedCaseId(c.id)}
                  className={`p-3 rounded-xl border text-xs cursor-pointer transition ${
                    selectedCaseId === c.id
                      ? "bg-slate-700/80 border-emerald-500 shadow-md"
                      : "bg-slate-900/60 border-slate-800 hover:border-slate-700"
                  }`}
                >
                  <div className="flex justify-between items-start mb-1.5">
                    <span className="font-bold uppercase tracking-wider text-emerald-300">{c.crop_id}</span>
                    <span
                      className={`px-2 py-0.5 rounded text-[10px] font-semibold ${
                        c.priority === "URGENT"
                          ? "bg-rose-950 text-rose-300 border border-rose-800"
                          : "bg-slate-800 text-slate-400"
                      }`}
                    >
                      {c.priority}
                    </span>
                  </div>
                  <div className="text-slate-300 font-medium truncate">{c.farm_name}</div>
                  <div className="text-slate-500 text-[11px] mb-2">{c.district} District</div>
                  <div className="flex justify-between items-center text-[10px]">
                    <span
                      className={`font-mono px-1.5 py-0.5 rounded ${
                        c.status === "COMPLETED"
                          ? "text-emerald-400 bg-emerald-950"
                          : c.status === "ASSIGNED"
                          ? "text-amber-400 bg-amber-950"
                          : "text-slate-400 bg-slate-800"
                      }`}
                    >
                      {c.status}
                    </span>
                    <span className="text-slate-500">
                      {new Date(c.created_at).toLocaleDateString()}
                    </span>
                  </div>
                </div>
              ))
            )}
          </div>
        </aside>

        {/* Center & Right Column: Evidence Dossier & Assessment Form */}
        <main className="lg:col-span-8 bg-slate-800/80 border border-slate-700 rounded-2xl p-6 overflow-y-auto h-[82vh]">
          {dossier ? (
            <div className="space-y-6">
              {/* Case Header */}
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-700 pb-4">
                <div>
                  <div className="flex items-center gap-2">
                    <h2 className="text-lg font-bold text-slate-100">
                      Case #{dossier.case_id.slice(0, 8)}
                    </h2>
                    <span className="text-xs bg-slate-700 px-2.5 py-0.5 rounded-full font-mono uppercase text-emerald-300">
                      {dossier.crop_id}
                    </span>
                  </div>
                  <p className="text-xs text-slate-400 mt-1">
                    {dossier.farm_name} · {dossier.district} District · Plot: {dossier.plot_name || "N/A"}
                  </p>
                </div>

                <div className="flex items-center gap-3">
                  {dossier.status === "QUEUED" && (
                    <button
                      onClick={() => handleClaim(dossier.case_id)}
                      className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl text-xs font-semibold shadow-md transition"
                    >
                      {t.expertconnect.claimCase}
                    </button>
                  )}
                  {dossier.assigned_expert_name && (
                    <span className="text-xs text-slate-300 bg-slate-900 border border-slate-700 px-3 py-1.5 rounded-xl">
                      Agronomist: <strong className="text-emerald-400">{dossier.assigned_expert_name}</strong>
                    </span>
                  )}
                </div>
              </div>

              {/* Multimodal Evidence Panel */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Visual Imagery */}
                <div className="bg-slate-900/80 p-4 rounded-xl border border-slate-800">
                  <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-3">
                    Foliar Foliage Imagery
                  </h3>
                  {dossier.foliar_media.length > 0 ? (
                    <div className="aspect-video bg-black/60 rounded-lg flex items-center justify-center border border-slate-800 overflow-hidden relative">
                      <img
                        src={dossier.foliar_media[0].storage_path}
                        alt="Foliar Pathology Sample"
                        className="object-contain w-full h-full"
                        onError={(e) => {
                          (e.target as any).src = "https://placehold.co/600x400/0f172a/34d399?text=Foliar+Specimen";
                        }}
                      />
                    </div>
                  ) : (
                    <div className="aspect-video bg-slate-950 rounded-lg flex items-center justify-center text-xs text-slate-500">
                      No foliar image uploaded
                    </div>
                  )}
                  <p className="text-xs text-slate-400 mt-3 italic">
                    Farmer Notes: &ldquo;{dossier.farmer_notes || "No notes provided"}&rdquo;
                  </p>
                </div>

                {/* AI CropVision Prediction */}
                <div className="bg-slate-900/80 p-4 rounded-xl border border-slate-800 flex flex-col justify-between">
                  <div>
                    <h3 className="text-xs font-bold uppercase tracking-wider text-emerald-400 mb-2">
                      CropVision ML Decision Support
                    </h3>
                    {dossier.ai_prediction ? (
                      <div className="space-y-2 text-xs">
                        <div className="flex justify-between border-b border-slate-800 pb-1.5">
                          <span className="text-slate-400">Decision State:</span>
                          <span className="font-mono text-emerald-300 font-semibold">
                            {dossier.ai_prediction.decision_state}
                          </span>
                        </div>
                        <div className="flex justify-between border-b border-slate-800 pb-1.5">
                          <span className="text-slate-400">Calibrated Confidence:</span>
                          <span className="font-mono text-slate-200">
                            {(dossier.ai_prediction.top_confidence * 100).toFixed(1)}%
                          </span>
                        </div>
                        <div className="flex justify-between border-b border-slate-800 pb-1.5">
                          <span className="text-slate-400">Normalized Entropy:</span>
                          <span className="font-mono text-slate-200">
                            {dossier.ai_prediction.normalized_entropy?.toFixed(3) || "N/A"}
                          </span>
                        </div>
                        <div className="mt-3">
                          <span className="text-slate-400 block mb-1">Top Differential Candidates:</span>
                          <ul className="space-y-1">
                            {(dossier.ai_prediction.candidates || []).slice(0, 3).map((c: any) => (
                              <li key={c.class_id} className="flex justify-between bg-slate-800/50 px-2 py-1 rounded">
                                <span className="text-slate-300">{c.display_name_en}</span>
                                <span className="font-mono text-emerald-400">
                                  {(c.calibrated_prob * 100).toFixed(1)}%
                                </span>
                              </li>
                            ))}
                          </ul>
                        </div>
                      </div>
                    ) : (
                      <p className="text-xs text-slate-500 py-4">No AI vision inference attached.</p>
                    )}
                  </div>

                  <div className="mt-4 p-2.5 rounded-lg bg-amber-950/40 border border-amber-800/60 text-[11px] text-amber-300">
                    AI predictions are informational aids. Human agronomist judgment remains authoritative.
                  </div>
                </div>
              </div>

              {/* KrishiBrain Evidence Citations */}
              {dossier.krishi_brain_citations.length > 0 && (
                <div className="bg-slate-900/60 p-4 rounded-xl border border-slate-800">
                  <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-2">
                    KrishiBrain Literature & CIBRC Guidance
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
                    {dossier.krishi_brain_citations.map((cite, i) => (
                      <div key={i} className="p-2.5 rounded-lg bg-slate-800/40 border border-slate-700/60">
                        <strong className="text-emerald-300 block mb-1">{cite.source_title}</strong>
                        <p className="text-slate-400 text-[11px] line-clamp-3">{cite.content_excerpt}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Certified Expert Assessment Editor */}
              <form onSubmit={handleSubmitAssessment} className="bg-slate-900 p-6 rounded-2xl border border-slate-700 space-y-4">
                <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                  <h3 className="font-bold text-slate-200">
                    {dossier.assessment ? t.expertconnect.reviseAssessment : t.expertconnect.submitAssessment}
                  </h3>
                  {dossier.assessment && (
                    <span className="text-xs bg-amber-950 text-amber-300 border border-amber-800 px-2 py-0.5 rounded font-mono">
                      Revision #{dossier.assessment.revision_count}
                    </span>
                  )}
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-medium text-slate-300 mb-1">
                      {t.expertconnect.confirmedCrop}
                    </label>
                    <select
                      value={confirmedCrop}
                      onChange={(e) => setConfirmedCrop(e.target.value)}
                      className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-xs text-slate-100"
                    >
                      <option value="cotton">Cotton (Gossypium hirsutum)</option>
                      <option value="rice">Rice (Oryza sativa)</option>
                      <option value="chilli">Chilli (Capsicum annuum)</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-xs font-medium text-slate-300 mb-1">
                      {t.expertconnect.primaryCondition}
                    </label>
                    <input
                      type="text"
                      value={primaryCondition}
                      onChange={(e) => setPrimaryCondition(e.target.value)}
                      required
                      placeholder="e.g. Cercospora Leaf Spot / Thrips / Nitrogen Deficiency"
                      className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-xs text-slate-100"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <label className="block text-xs font-medium text-slate-300 mb-1">
                      Differential Causes (Comma-separated)
                    </label>
                    <input
                      type="text"
                      value={differentialTags}
                      onChange={(e) => setDifferentialTags(e.target.value)}
                      placeholder="e.g. Alternaria, Potassium Deficiency"
                      className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-xs text-slate-100"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-medium text-slate-300 mb-1">
                      Confidence Rating (1 - 5)
                    </label>
                    <select
                      value={confidenceRating}
                      onChange={(e) => setConfidenceRating(Number(e.target.value))}
                      className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-xs text-slate-100"
                    >
                      <option value={5}>5 - Confirmed Pathological Evidence</option>
                      <option value={4}>4 - High Confidence Clinical Pattern</option>
                      <option value={3}>3 - Moderate (Probable Differential)</option>
                      <option value={2}>2 - Low (Field Specimen Needed)</option>
                      <option value={1}>1 - Inconclusive</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-xs font-medium text-slate-300 mb-1">
                      Urgency Grade
                    </label>
                    <select
                      value={urgencyLevel}
                      onChange={(e) => setUrgencyLevel(e.target.value as any)}
                      className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-xs text-slate-100"
                    >
                      <option value="ROUTINE">Routine Monitoring</option>
                      <option value="HIGH">High (Action within 48h)</option>
                      <option value="EMERGENCY">Emergency (Quarantine / Rapid Spread)</option>
                      <option value="LOW">Low Risk</option>
                    </select>
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">
                    Integrated Pest Management (IPM) & Cultural Strategy (First Line)
                  </label>
                  <textarea
                    rows={2}
                    value={ipmStrategy}
                    onChange={(e) => setIpmStrategy(e.target.value)}
                    required
                    placeholder="Describe non-chemical cultural sanitation, drainage, bio-pesticides (Neem, Trichoderma), and trap crops..."
                    className="w-full bg-slate-800 border border-slate-700 rounded-xl p-3 text-xs text-slate-100"
                  />
                </div>

                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">
                    {t.expertconnect.managementPlan}
                  </label>
                  <textarea
                    rows={3}
                    value={managementPlan}
                    onChange={(e) => setManagementPlan(e.target.value)}
                    required
                    placeholder="Comprehensive treatment protocol and step-by-step instructions for the cultivator..."
                    className="w-full bg-slate-800 border border-slate-700 rounded-xl p-3 text-xs text-slate-100"
                  />
                </div>

                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">
                    CIBRC Chemical Advisories & Pre-Harvest Intervals (PHI)
                  </label>
                  <textarea
                    rows={2}
                    value={cibrcAdvisories}
                    onChange={(e) => setCibrcAdvisories(e.target.value)}
                    required
                    placeholder="If chemical spray is essential, specify registered active ingredient, precise dosage per acre, and mandatory PHI days..."
                    className="w-full bg-slate-800 border border-slate-700 rounded-xl p-3 text-xs text-slate-100"
                  />
                </div>

                {dossier.assessment && (
                  <div>
                    <label className="block text-xs font-medium text-amber-300 mb-1">
                      Revision Rationale (Mandatory for Updates)
                    </label>
                    <input
                      type="text"
                      value={revisionReason}
                      onChange={(e) => setRevisionReason(e.target.value)}
                      placeholder="e.g. Follow-up photograph revealed sporulating lesions, adjusting to systemic fungicide."
                      className="w-full bg-slate-800 border border-amber-700/60 rounded-xl px-3 py-2 text-xs text-amber-200"
                    />
                  </div>
                )}

                <div className="pt-2 flex justify-end">
                  <button
                    type="submit"
                    disabled={isSubmitting}
                    className="px-6 py-2.5 bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white rounded-xl text-xs font-bold shadow-lg transition"
                  >
                    {isSubmitting
                      ? "Certifying..."
                      : dossier.assessment
                      ? "Commit Immutable Revision"
                      : "Sign & Issue Certified Assessment"}
                  </button>
                </div>
              </form>

              {/* Revision History Log */}
              {revisions.length > 0 && (
                <div className="bg-slate-900/60 p-4 rounded-xl border border-slate-800">
                  <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-3">
                    {t.expertconnect.revisions} ({revisions.length})
                  </h4>
                  <div className="space-y-2">
                    {revisions.map((r) => (
                      <div key={r.id} className="text-xs p-3 rounded-lg bg-slate-800/40 border border-slate-700/60">
                        <div className="flex justify-between items-center text-slate-400 text-[11px] mb-1">
                          <span>Revision #{r.revision_number} by <strong>{r.revised_by_name}</strong></span>
                          <span>{new Date(r.revised_at).toLocaleString()}</span>
                        </div>
                        <p className="text-amber-300 text-xs">Reason: &ldquo;{r.revision_reason}&rdquo;</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="h-full flex items-center justify-center text-slate-500 text-xs">
              Select a case from the triage queue to view the clinical evidence dossier.
            </div>
          )}
        </main>
      </div>
    </div>
  );
}

export default function ExpertWorkspacePage() {
  return (
    <Suspense fallback={<div className="p-8 text-white">Loading Expert Workspace...</div>}>
      <ExpertWorkspaceContent />
    </Suspense>
  );
}
