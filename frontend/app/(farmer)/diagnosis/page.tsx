"use client";

import React, { useState, useRef, useEffect, useCallback, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useTranslation } from "@/lib/localization/context";
import { useOnlineStatus } from "@/hooks/useOnlineStatus";
import { api } from "@/lib/api/client";
import { OfflineQueue } from "@/lib/offline/queue";
import { Farm, Diagnosis, CropSeason } from "@/lib/api/types";
import { Button } from "@/components/ui/Button";
import {
  Camera,
  AlertTriangle,
  CheckCircle2,
  RefreshCw,
  Info,
  ShieldAlert,
  BotMessageSquare,
  UserCheck,
} from "lucide-react";

function DiagnosisContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { t, locale } = useTranslation();
  const isOnline = useOnlineStatus();

  const [_farms, setFarms] = useState<Farm[]>([]);
  const [selectedFarmId, setSelectedFarmId] = useState<string>("");
  const [cropType, setCropType] = useState<"cotton" | "rice" | "chilli">("cotton");
  const [selectedSeason, setSelectedSeason] = useState<CropSeason | null>(null);

  const [imageFile, setImageFile] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [diagnosisResult, setDiagnosisResult] = useState<Diagnosis | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [expertRequested, setExpertRequested] = useState<boolean>(false);
  const [offlineSaved, setOfflineSaved] = useState<boolean>(false);

  const loadInitialFarms = useCallback(async () => {
    try {
      const farmList = await api.listFarms();
      setFarms(farmList);
      if (farmList.length > 0) {
        setSelectedFarmId(farmList[0].id);
        const plotList = await api.listPlots(farmList[0].id).catch(() => []);
        if (plotList.length > 0) {
          const seasons = await api.listCropSeasons(plotList[0].id).catch(() => []);
          if (seasons.length > 0) {
            setSelectedSeason(seasons[0]);
            setCropType(seasons[0].crop_id);
          }
        }
      }
    } catch {
      // ignore
    }
  }, []);

  const loadExistingDiagnosis = useCallback(async (diagId: string) => {
    try {
      const res = await api.getDiagnosis(diagId);
      setDiagnosisResult(res);
    } catch {
      // ignore
    }
  }, []);

  useEffect(() => {
    loadInitialFarms();
    const existingDiagId = searchParams.get("id");
    if (existingDiagId) {
      loadExistingDiagnosis(existingDiagId);
    }
  }, [loadInitialFarms, loadExistingDiagnosis, searchParams]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setImageFile(file);
      const reader = new FileReader();
      reader.onload = (event) => {
        setImagePreview(event.target?.result as string);
      };
      reader.readAsDataURL(file);
      setError(null);
      setDiagnosisResult(null);
    }
  };

  const handleRunDiagnosis = async () => {
    if (!imageFile && !imagePreview) {
      setError("Please capture or upload a foliar photo first.");
      return;
    }

    if (!selectedFarmId) {
      setError("Please select a farm holding.");
      return;
    }

    setError(null);
    setIsAnalyzing(true);
    setDiagnosisResult(null);

    // 1. If Offline, queue draft
    if (!isOnline) {
      OfflineQueue.saveDraft({
        type: "DIAGNOSIS_REQUEST",
        farm_id: selectedFarmId,
        crop_season_id: selectedSeason?.id,
        crop_type: cropType,
        notes: `Offline diagnosis request for ${cropType}`,
        image_data_base64: imagePreview || undefined,
        image_filename: imageFile?.name || "foliar.jpg",
      });
      setOfflineSaved(true);
      setIsAnalyzing(false);
      return;
    }

    try {
      // 2. Create Observation
      const obs = await api.createObservation({
        farm_id: selectedFarmId,
        crop_season_id: selectedSeason?.id,
        notes: `CropVision Foliar Assessment for ${cropType}`,
      });

      // 3. Upload Foliar Media
      let mediaId: string | undefined;
      if (imageFile) {
        const media = await api.uploadObservationMedia(
          obs.id,
          imageFile,
          imageFile.name,
          true
        );
        mediaId = media.id;
      }

      // 4. Request ML Inference & Calibration
      const diagnosis = await api.requestDiagnosis({
        observation_id: obs.id,
        media_id: mediaId,
        crop_type: cropType,
        language: locale,
      });

      setDiagnosisResult(diagnosis);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Diagnosis failed. Please check network.";
      setError(msg);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const candidate = diagnosisResult?.prediction?.candidates?.[0];
  const decisionState = diagnosisResult?.prediction?.decision_state || "CONFIDENT_PREDICTION";

  return (
    <div className="max-w-3xl mx-auto p-4 space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl font-bold text-[#1E3A2B] tracking-tight">{t.diagnosis.title}</h1>
        <p className="text-sm text-[#556059] mt-1">{t.diagnosis.subtitle}</p>
      </div>

      {error && (
        <div className="p-4 bg-[#FFE3E3] border border-[#FFA8A8] text-[#C92A2A] rounded-xl text-sm flex items-start gap-2">
          <AlertTriangle className="w-5 h-5 shrink-0 mt-0.5" />
          <span>{error}</span>
        </div>
      )}

      {offlineSaved && (
        <div className="p-4 bg-[#FEF3C7] border border-[#FCD34D] text-[#92400E] rounded-xl text-sm flex items-start gap-3">
          <Info className="w-5 h-5 shrink-0 mt-0.5 text-[#D97706]" />
          <div>
            <strong>Offline Diagnosis Saved Locally:</strong> Your foliar photo and assessment parameters are stored on this device. They will automatically upload and process as soon as internet connectivity returns.
          </div>
        </div>
      )}

      {/* Input Form & Image Capture */}
      <div className="bg-white rounded-2xl border border-[#E5E0D8] p-5 shadow-card space-y-5">
        {/* Crop Selection */}
        <div>
          <label className="block text-xs font-semibold text-[#1A241F] uppercase mb-2">
            {t.diagnosis.stepSelectCrop}
          </label>
          <div className="grid grid-cols-3 gap-2">
            {[
              { id: "cotton", label: "Cotton", vernacular: "ప్రత్తి / कपास" },
              { id: "rice", label: "Rice / Paddy", vernacular: "వరి / धान" },
              { id: "chilli", label: "Chilli", vernacular: "మిరప / मिर्च" },
            ].map((c) => (
              <button
                key={c.id}
                type="button"
                onClick={() => setCropType(c.id as "cotton" | "rice" | "chilli")}
                className={`p-3 rounded-xl border text-center transition-all touch-target ${
                  cropType === c.id
                    ? "border-[#1E3A2B] bg-[#E8F0EC] ring-2 ring-[#1E3A2B]"
                    : "border-[#C8C0B5] hover:bg-[#FAFAF7]"
                }`}
              >
                <span className="font-bold text-sm text-[#1E3A2B] block">{c.label}</span>
                <span className="text-[11px] text-[#556059] block">{c.vernacular}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Capture Box */}
        <div>
          <label className="block text-xs font-semibold text-[#1A241F] uppercase mb-2">
            {t.diagnosis.stepCapture}
          </label>

          <input
            type="file"
            accept="image/*"
            capture="environment"
            ref={fileInputRef}
            onChange={handleFileChange}
            className="hidden"
          />

          {!imagePreview ? (
            <div
              onClick={() => fileInputRef.current?.click()}
              className="border-2 border-dashed border-[#C8C0B5] hover:border-[#1E3A2B] rounded-2xl p-8 text-center cursor-pointer bg-[#FAFAF7] transition-all space-y-3 group"
            >
              <div className="w-14 h-14 bg-[#E8F0EC] text-[#1E3A2B] rounded-2xl mx-auto flex items-center justify-center group-hover:scale-105 transition-transform">
                <Camera className="w-7 h-7" />
              </div>
              <div>
                <span className="font-bold text-base text-[#1E3A2B] block">
                  Tap to Take or Upload Foliar Photo
                </span>
                <span className="text-xs text-[#556059] block mt-1">
                  Supports Android Camera, Gallery & Files (JPEG, PNG, WebP)
                </span>
              </div>
            </div>
          ) : (
            <div className="space-y-3">
              <div className="relative rounded-2xl overflow-hidden border border-[#E5E0D8] bg-black max-h-80 flex items-center justify-center">
                <img
                  src={imagePreview}
                  alt="Captured Crop Foliage"
                  className="max-h-80 w-auto object-contain"
                />
              </div>
              <div className="flex gap-2">
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={() => fileInputRef.current?.click()}
                  icon={<RefreshCw className="w-4 h-4" />}
                >
                  Retake Photo
                </Button>
              </div>
            </div>
          )}

          <div className="mt-3 p-3 bg-[#FAFAF7] rounded-xl border border-[#E5E0D8] text-xs text-[#556059] flex items-start gap-2">
            <Info className="w-4 h-4 text-[#1E3A2B] shrink-0 mt-0.5" />
            <span>{t.diagnosis.captureGuidance}</span>
          </div>
        </div>

        <Button
          type="button"
          variant="primary"
          size="lg"
          className="w-full"
          onClick={handleRunDiagnosis}
          isLoading={isAnalyzing}
          disabled={!imagePreview}
          icon={<Camera className="w-5 h-5 text-[#86EFAC]" />}
        >
          {isAnalyzing ? t.diagnosis.analyzing : t.diagnosis.submitAnalysis}
        </Button>
      </div>

      {/* DIAGNOSIS RESULT DISPLAY */}
      {diagnosisResult && (
        <div className="bg-white rounded-2xl border border-[#E5E0D8] p-6 shadow-card space-y-5 animate-in fade-in">
          {/* Top Label & Disclaimer */}
          <div className="flex flex-wrap items-center justify-between gap-2 pb-4 border-b border-[#E5E0D8]">
            <div>
              <span className="text-xs font-bold text-[#1E3A2B] uppercase tracking-wider block">
                {t.diagnosis.resultTitle}
              </span>
              <span className="text-[11px] text-[#C92A2A] font-semibold flex items-center gap-1 mt-0.5">
                <ShieldAlert className="w-3.5 h-3.5" />
                {t.diagnosis.aiDisclaimer}
              </span>
            </div>

            <span
              className={`px-3 py-1 rounded-full text-xs font-bold uppercase ${
                decisionState === "CONFIDENT_PREDICTION"
                  ? "bg-[#DCFCE7] text-[#15803D]"
                  : decisionState === "LOW_CONFIDENCE"
                  ? "bg-[#FEF3C7] text-[#D97706]"
                  : "bg-[#FFE3E3] text-[#C92A2A]"
              }`}
            >
              {decisionState.replace(/_/g, " ")}
            </span>
          </div>

          {/* Primary Condition */}
          {candidate ? (
            <div className="p-4 bg-[#FAFAF7] rounded-xl border border-[#E5E0D8] space-y-2">
              <span className="text-xs text-[#78857E] font-semibold uppercase block">
                {t.diagnosis.topCandidate}
              </span>
              <h2 className="text-xl font-bold text-[#1E3A2B]">
                {locale === "te"
                  ? candidate.display_name_te
                  : locale === "hi"
                  ? candidate.display_name_hi
                  : candidate.display_name_en}
              </h2>
              <p className="text-xs text-[#556059]">
                Scientific: <em>{candidate.pathogen_or_cause || candidate.class_id}</em>
              </p>

              <div className="pt-2 flex items-center gap-3">
                <div className="flex-1 bg-[#E5E0D8] h-2.5 rounded-full overflow-hidden">
                  <div
                    className="bg-[#1E3A2B] h-full"
                    style={{ width: `${Math.round(candidate.calibrated_prob * 100)}%` }}
                  />
                </div>
                <span className="text-sm font-bold text-[#1E3A2B]">
                  {Math.round(candidate.calibrated_prob * 100)}% Confidence
                </span>
              </div>
            </div>
          ) : (
            <div className="p-4 bg-[#FEF3C7] rounded-xl text-sm text-[#92400E]">
              Image features are inconclusive or out-of-distribution. An agronomist should review this crop photo.
            </div>
          )}

          {/* CIBRC Regulatory Advisory */}
          {diagnosisResult.prediction?.cibrc_advisory && (
            <div className="p-4 bg-[#E8F0EC] rounded-xl text-xs text-[#1E3A2B] space-y-2 border border-[#C2D9CD]">
              <div className="flex items-center gap-2 font-bold text-sm">
                <CheckCircle2 className="w-4 h-4 text-[#1E3A2B]" />
                <span>{t.diagnosis.cibrcAdvisory}</span>
              </div>
              <p className="leading-relaxed">{diagnosisResult.prediction.cibrc_advisory}</p>
              <p className="text-[11px] text-[#556059] italic border-t border-[#C2D9CD] pt-2">
                {t.diagnosis.cibrcDisclaimer}
              </p>
            </div>
          )}

          {/* Differential Alternatives */}
          {diagnosisResult.prediction?.candidates && diagnosisResult.prediction.candidates.length > 1 && (
            <div>
              <span className="text-xs font-bold text-[#556059] uppercase tracking-wider block mb-2">
                {t.diagnosis.differentialCandidates}
              </span>
              <div className="space-y-1.5">
                {diagnosisResult.prediction.candidates.slice(1).map((diff) => (
                  <div
                    key={diff.rank}
                    className="p-2.5 bg-[#FAFAF7] rounded-lg border border-[#E5E0D8] flex items-center justify-between text-xs"
                  >
                    <span className="font-semibold text-[#1A241F]">
                      {locale === "te"
                        ? diff.display_name_te
                        : locale === "hi"
                        ? diff.display_name_hi
                        : diff.display_name_en}
                    </span>
                    <span className="text-[#78857E] font-medium">
                      {Math.round(diff.calibrated_prob * 100)}% Probability
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Action Pathways */}
          <div className="pt-2 flex flex-wrap gap-2.5">
            <Button
              type="button"
              variant="outline"
              size="md"
              onClick={() => {
                const qName = candidate?.display_name_en || cropType;
                router.push(`/knowledge?q=${encodeURIComponent(`How to manage ${qName} in ${cropType}?`)}`);
              }}
              icon={<BotMessageSquare className="w-4 h-4" />}
            >
              {t.diagnosis.askKrishiBrainAbout}
            </Button>

            <Button
              type="button"
              variant="secondary"
              size="md"
              onClick={() => setExpertRequested(true)}
              disabled={expertRequested}
              icon={<UserCheck className="w-4 h-4 text-[#1E3A2B]" />}
            >
              {expertRequested ? "Agronomist Review Requested" : t.diagnosis.requestExpert}
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}

export default function DiagnosisPage() {
  return (
    <Suspense
      fallback={
        <div className="max-w-3xl mx-auto p-8 text-center text-sm text-[#556059]">
          Loading CropVision diagnosis interface...
        </div>
      }
    >
      <DiagnosisContent />
    </Suspense>
  );
}
