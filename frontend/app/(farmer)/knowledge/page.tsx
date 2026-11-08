"use client";

import React, { useState, useEffect, useCallback, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import { useTranslation } from "@/lib/localization/context";
import { api } from "@/lib/api/client";
import { KnowledgeQueryResponse } from "@/lib/api/types";
import { Button } from "@/components/ui/Button";
import { VoiceAdapter } from "@/features/voice/voiceAdapter";
import {
  BotMessageSquare,
  Mic,
  MicOff,
  Send,
  Volume2,
  VolumeX,
  BookOpen,
  CheckCircle2,
  AlertTriangle,
  ExternalLink,
  ThumbsUp,
  ThumbsDown,
  Sparkles,
} from "lucide-react";

function KnowledgeContent() {
  const searchParams = useSearchParams();
  const { t, locale } = useTranslation();

  const [question, setQuestion] = useState("");
  const [selectedCrop, setSelectedCrop] = useState<string>("cotton");
  const [isQuerying, setIsQuerying] = useState(false);
  const [result, setResult] = useState<KnowledgeQueryResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Voice State
  const [isListening, setIsListening] = useState(false);
  const [voiceSupported, setVoiceSupported] = useState(false);
  const [isPlayingAudio, setIsPlayingAudio] = useState(false);
  const [recognizer, setRecognizer] = useState<{ start: () => void; stop: () => void } | null>(null);

  // Feedback State
  const [feedbackSubmitted, setFeedbackSubmitted] = useState(false);

  const handleQuery = useCallback(async (qText?: string) => {
    const textToSearch = qText || question;
    if (!textToSearch.trim()) return;

    setError(null);
    setIsQuerying(true);
    setFeedbackSubmitted(false);
    VoiceAdapter.stopSpeaking();
    setIsPlayingAudio(false);

    try {
      const resp = await api.queryKnowledge({
        question: textToSearch.trim(),
        language: locale,
        crop: selectedCrop,
      });
      setResult(resp);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to query KrishiBrain.";
      setError(msg);
    } finally {
      setIsQuerying(false);
    }
  }, [question, locale, selectedCrop]);

  useEffect(() => {
    setVoiceSupported(VoiceAdapter.isSpeechRecognitionSupported());
    const initialQuery = searchParams.get("q");
    if (initialQuery) {
      setQuestion(initialQuery);
      handleQuery(initialQuery);
    }
  }, [searchParams, handleQuery]);

  const toggleVoiceRecording = () => {
    if (isListening && recognizer) {
      recognizer.stop();
      setIsListening(false);
      return;
    }

    const rec = VoiceAdapter.createRecognizer(
      locale,
      (transcript) => {
        setQuestion(transcript);
        setIsListening(false);
        // Automatically query on voice completion
        handleQuery(transcript);
      },
      (err) => {
        setError(`Voice Input: ${err}`);
        setIsListening(false);
      },
      () => {
        setIsListening(false);
      }
    );

    if (rec) {
      setRecognizer(rec);
      rec.start();
      setIsListening(true);
      setError(null);
    } else {
      setError("Speech recognition is not supported in this browser. Please type your query.");
    }
  };

  const toggleAudioPlayback = () => {
    if (!result?.answer) return;

    if (isPlayingAudio) {
      VoiceAdapter.stopSpeaking();
      setIsPlayingAudio(false);
    } else {
      const success = VoiceAdapter.speakText(result.answer, locale);
      if (success) {
        setIsPlayingAudio(true);
      }
    }
  };

  const handleFeedback = async (isHelpful: boolean) => {
    if (!result?.query_id || feedbackSubmitted) return;
    try {
      await api.submitKnowledgeFeedback({
        query_id: result.query_id,
        rating: isHelpful ? 5 : 2,
        is_helpful: isHelpful,
        citation_accuracy_score: isHelpful ? 1.0 : 0.0,
      });
      setFeedbackSubmitted(true);
    } catch {
      // ignore
    }
  };

  return (
    <div className="max-w-3xl mx-auto p-4 space-y-6">
      {/* Page Title */}
      <div>
        <div className="flex items-center gap-2">
          <div className="w-10 h-10 rounded-xl bg-[#1E3A2B] text-white flex items-center justify-center shadow-xs">
            <BotMessageSquare className="w-6 h-6 text-[#86EFAC]" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-[#1E3A2B] tracking-tight">{t.knowledge.title}</h1>
            <p className="text-xs text-[#556059]">{t.knowledge.subtitle}</p>
          </div>
        </div>
      </div>

      {/* Query Bar */}
      <div className="bg-white rounded-2xl border border-[#E5E0D8] p-4 shadow-card space-y-3">
        {/* Crop Context Tag */}
        <div className="flex items-center gap-2">
          <span className="text-xs font-semibold text-[#78857E]">Crop Context:</span>
          {["cotton", "rice", "chilli"].map((crop) => (
            <button
              key={crop}
              type="button"
              onClick={() => setSelectedCrop(crop)}
              className={`px-2.5 py-1 text-xs font-semibold rounded-lg capitalize transition-colors touch-target ${
                selectedCrop === crop
                  ? "bg-[#1E3A2B] text-white"
                  : "bg-[#FAFAF7] text-[#556059] border border-[#E5E0D8] hover:bg-[#E8F0EC]"
              }`}
            >
              {crop}
            </button>
          ))}
        </div>

        {/* Input & Voice Controls */}
        <div className="relative flex items-center gap-2">
          <input
            type="text"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleQuery()}
            placeholder={t.knowledge.searchPlaceholder}
            className="flex-1 px-4 py-3 rounded-xl border border-[#C8C0B5] bg-[#FAFAF7] focus:bg-white text-base focus:ring-2 focus:ring-[#1E3A2B] outline-none transition-all pr-12"
          />

          {voiceSupported && (
            <button
              type="button"
              onClick={toggleVoiceRecording}
              className={`p-3 rounded-xl transition-all touch-target ${
                isListening
                  ? "bg-[#C92A2A] text-white animate-pulse"
                  : "bg-[#E8F0EC] text-[#1E3A2B] hover:bg-[#D5E5DC]"
              }`}
              title={isListening ? t.knowledge.voiceCancel : "Speak query in Telugu / Hindi / English"}
              aria-label="Voice Input"
            >
              {isListening ? <MicOff className="w-5 h-5" /> : <Mic className="w-5 h-5" />}
            </button>
          )}

          <Button
            type="button"
            variant="primary"
            onClick={() => handleQuery()}
            isLoading={isQuerying}
            className="h-12 px-5 shrink-0"
            icon={<Send className="w-4 h-4" />}
          >
            Ask
          </Button>
        </div>

        {isListening && (
          <div className="p-2.5 bg-[#FFE3E3] rounded-xl text-xs text-[#C92A2A] font-semibold flex items-center gap-2 animate-pulse">
            <Mic className="w-4 h-4" />
            <span>{t.knowledge.voiceListening}</span>
          </div>
        )}

        {error && (
          <div className="p-3 bg-[#FFE3E3] border border-[#FFA8A8] text-[#C92A2A] rounded-xl text-xs flex items-start gap-2">
            <AlertTriangle className="w-4 h-4 shrink-0 mt-0.5" />
            <span>{error}</span>
          </div>
        )}
      </div>

      {/* RESULT CARD */}
      {result && (
        <div className="bg-white rounded-2xl border border-[#E5E0D8] p-6 shadow-card space-y-5 animate-in fade-in">
          {/* Header & Status Badge */}
          <div className="flex flex-wrap items-center justify-between gap-2 pb-4 border-b border-[#E5E0D8]">
            <div className="flex items-center gap-2">
              <span
                className={`px-3 py-1 rounded-full text-xs font-bold uppercase ${
                  result.answer_status === "ANSWERED"
                    ? "bg-[#DCFCE7] text-[#15803D]"
                    : result.answer_status === "REQUIRES_EXPERT_REVIEW"
                    ? "bg-[#FFE3E3] text-[#C92A2A]"
                    : "bg-[#FEF3C7] text-[#D97706]"
                }`}
              >
                {result.answer_status === "ANSWERED"
                  ? t.knowledge.statusAnswered
                  : result.answer_status === "REQUIRES_EXPERT_REVIEW"
                  ? t.knowledge.statusHighRisk
                  : t.knowledge.statusInsufficient}
              </span>

              <span className="text-xs text-[#78857E]">
                {t.knowledge.evidenceLevel}: <strong>{result.evidence_strength}</strong>
              </span>
            </div>

            {/* Read Aloud Button */}
            <button
              type="button"
              onClick={toggleAudioPlayback}
              className="flex items-center gap-1.5 px-3 py-1.5 bg-[#E8F0EC] text-[#1E3A2B] rounded-lg text-xs font-semibold hover:bg-[#D5E5DC] transition-colors touch-target"
            >
              {isPlayingAudio ? (
                <>
                  <VolumeX className="w-4 h-4 text-[#C92A2A]" />
                  <span>Stop Speaking</span>
                </>
              ) : (
                <>
                  <Volume2 className="w-4 h-4 text-[#1E3A2B]" />
                  <span>Listen to Advisory</span>
                </>
              )}
            </button>
          </div>

          {/* Answer Text */}
          <div className="text-base text-[#1A241F] leading-relaxed whitespace-pre-wrap font-sans">
            {result.answer}
          </div>

          {/* Citations Drawer */}
          {result.citations && result.citations.length > 0 && (
            <div className="space-y-3 pt-4 border-t border-[#E5E0D8]">
              <span className="text-xs font-bold text-[#556059] uppercase tracking-wider flex items-center gap-1.5">
                <BookOpen className="w-4 h-4 text-[#1E3A2B]" />
                {t.knowledge.citations} ({result.citations.length})
              </span>

              <div className="space-y-2">
                {result.citations.map((cite, idx) => (
                  <div
                    key={idx}
                    className="p-3 bg-[#FAFAF7] rounded-xl border border-[#E5E0D8] text-xs space-y-1.5"
                  >
                    <div className="flex flex-wrap items-center justify-between gap-2">
                      <span className="font-bold text-[#1E3A2B]">
                        {cite.source_title}
                      </span>
                      <span className="text-[11px] text-[#78857E]">
                        {cite.publisher} • v{cite.document_version}
                        {cite.page_start && ` • Page ${cite.page_start}`}
                      </span>
                    </div>

                    {cite.heading_path && (
                      <span className="text-[11px] text-[#556059] font-medium block">
                        Hierarchy: {cite.heading_path}
                      </span>
                    )}

                    <p className="text-[#556059] italic bg-white p-2 rounded-lg border border-[#E5E0D8] leading-relaxed">
                      &ldquo;{cite.content_snippet}&rdquo;
                    </p>

                    {cite.canonical_url && (
                      <a
                        href={cite.canonical_url}
                        target="_blank"
                        rel="noreferrer"
                        className="text-[11px] text-[#1E3A2B] font-semibold hover:underline inline-flex items-center gap-1 pt-1"
                      >
                        <span>View Publication Source</span>
                        <ExternalLink className="w-3 h-3" />
                      </a>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Limitations & Field Context */}
          {result.limitations && result.limitations.length > 0 && (
            <div className="p-3 bg-[#FAFAF7] rounded-xl border border-[#E5E0D8] text-xs text-[#556059] space-y-1">
              <span className="font-bold text-[#1A241F] block">{t.knowledge.limitations}:</span>
              <ul className="list-disc list-inside space-y-0.5">
                {result.limitations.map((lim, i) => (
                  <li key={i}>{lim}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Follow-up Questions */}
          {result.follow_up_questions && result.follow_up_questions.length > 0 && (
            <div className="space-y-2 pt-2">
              <span className="text-xs font-bold text-[#556059] uppercase tracking-wider block flex items-center gap-1.5">
                <Sparkles className="w-3.5 h-3.5 text-[#1E3A2B]" />
                {t.knowledge.followUp}
              </span>
              <div className="flex flex-wrap gap-2">
                {result.follow_up_questions.map((fq, i) => (
                  <button
                    key={i}
                    type="button"
                    onClick={() => {
                      setQuestion(fq);
                      handleQuery(fq);
                    }}
                    className="px-3 py-1.5 bg-[#E8F0EC] hover:bg-[#D5E5DC] text-[#1E3A2B] rounded-lg text-xs font-medium text-left transition-colors touch-target"
                  >
                    {fq}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Feedback Section */}
          <div className="pt-4 border-t border-[#E5E0D8] flex items-center justify-between text-xs">
            <span className="text-[#556059] font-medium">{t.knowledge.helpful}</span>
            {feedbackSubmitted ? (
              <span className="text-[#15803D] font-bold flex items-center gap-1">
                <CheckCircle2 className="w-4 h-4" />
                {t.knowledge.feedbackSuccess}
              </span>
            ) : (
              <div className="flex items-center gap-2">
                <button
                  type="button"
                  onClick={() => handleFeedback(true)}
                  className="px-3 py-1 bg-[#FAFAF7] border border-[#C8C0B5] hover:bg-[#E8F0EC] rounded-lg flex items-center gap-1.5 text-xs font-semibold text-[#1E3A2B] touch-target"
                >
                  <ThumbsUp className="w-3.5 h-3.5" />
                  <span>Yes</span>
                </button>
                <button
                  type="button"
                  onClick={() => handleFeedback(false)}
                  className="px-3 py-1 bg-[#FAFAF7] border border-[#C8C0B5] hover:bg-[#FFE3E3] rounded-lg flex items-center gap-1.5 text-xs font-semibold text-[#C92A2A] touch-target"
                >
                  <ThumbsDown className="w-3.5 h-3.5" />
                  <span>No</span>
                </button>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default function KnowledgePage() {
  return (
    <Suspense
      fallback={
        <div className="max-w-3xl mx-auto p-8 text-center text-sm text-[#556059]">
          Loading KrishiBrain assistant...
        </div>
      }
    >
      <KnowledgeContent />
    </Suspense>
  );
}
