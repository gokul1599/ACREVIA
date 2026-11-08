"use client";

import React, { useState, useEffect, useCallback, useRef } from "react";
import { useTranslation } from "@/lib/localization/context";
import { api } from "@/lib/api/client";
import { Farm, Observation, CropSeason } from "@/lib/api/types";
import { Button } from "@/components/ui/Button";
import {
  Activity,
  Camera,
  Calendar,
  AlertCircle,
  Plus,
  RefreshCw,
  Info,
  Clock,
  Sparkles,
  ArrowRight,
} from "lucide-react";

export default function CropPulsePage() {
  const { t } = useTranslation();

  const [farms, setFarms] = useState<Farm[]>([]);
  const [selectedFarmId, setSelectedFarmId] = useState<string>("");
  const [observations, setObservations] = useState<Observation[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [showAddModal, setShowAddModal] = useState<boolean>(false);

  // New Observation Form State
  const [notes, setNotes] = useState("");
  const [newImage, setNewImage] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const loadObservations = useCallback(async (farmId: string) => {
    setIsLoading(true);
    try {
      const list = await api.listObservations(farmId, 50);
      setObservations(list);
    } catch {
      // ignore
    } finally {
      setIsLoading(false);
    }
  }, []);

  const loadInitialData = useCallback(async () => {
    try {
      const farmList = await api.listFarms();
      setFarms(farmList);
      if (farmList.length > 0) {
        setSelectedFarmId(farmList[0].id);
        await loadObservations(farmList[0].id);
      } else {
        setIsLoading(false);
      }
    } catch {
      setIsLoading(false);
    }
  }, [loadObservations]);

  useEffect(() => {
    loadInitialData();
  }, [loadInitialData]);

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const f = e.target.files[0];
      setNewImage(f);
      const reader = new FileReader();
      reader.onload = (event) => {
        setImagePreview(event.target?.result as string);
      };
      reader.readAsDataURL(f);
    }
  };

  const handleCreateObservation = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedFarmId) return;

    setIsSubmitting(true);
    try {
      const obs = await api.createObservation({
        farm_id: selectedFarmId,
        notes: notes.trim() || "Routine Folia Observation",
      });

      if (newImage) {
        await api.uploadObservationMedia(obs.id, newImage, newImage.name, true);
      }

      setNotes("");
      setNewImage(null);
      setImagePreview(null);
      setShowAddModal(false);
      await loadObservations(selectedFarmId);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto p-4 space-y-6">
      {/* Page Header */}
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <div className="w-10 h-10 rounded-xl bg-[#1E3A2B] text-white flex items-center justify-center shadow-xs">
            <Activity className="w-6 h-6 text-[#86EFAC]" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-[#1E3A2B] tracking-tight">{t.croppulse.title}</h1>
            <p className="text-xs text-[#556059]">{t.croppulse.subtitle}</p>
          </div>
        </div>

        <Button
          type="button"
          variant="primary"
          size="md"
          onClick={() => setShowAddModal(true)}
          icon={<Plus className="w-4 h-4" />}
        >
          {t.croppulse.newRecord}
        </Button>
      </div>

      {/* Capture Consistency Advice */}
      <div className="p-4 bg-[#E8F0EC] border border-[#C2D9CD] rounded-2xl text-xs text-[#1E3A2B] flex items-start gap-2.5">
        <Info className="w-4 h-4 text-[#1E3A2B] shrink-0 mt-0.5" />
        <div>
          <strong className="block text-sm font-bold mb-0.5">Capture Consistency Reminder</strong>
          To enable trustworthy visual progression tracking, photograph the exact same tagged plant from a similar distance (approx. 30 cm) and consistent natural lighting.
        </div>
      </div>

      {/* Add Observation Modal / Drawer */}
      {showAddModal && (
        <div className="fixed inset-0 z-50 bg-black/60 flex items-center justify-center p-4 backdrop-blur-xs animate-in fade-in">
          <div className="bg-white rounded-2xl p-6 max-w-lg w-full space-y-4 shadow-elevated border border-[#E5E0D8]">
            <h2 className="text-lg font-bold text-[#1E3A2B]">{t.croppulse.newRecord}</h2>

            <form onSubmit={handleCreateObservation} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-[#1A241F] uppercase mb-1">
                  Field Notes & Interventions
                </label>
                <textarea
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  placeholder={t.croppulse.notesPlaceholder}
                  rows={3}
                  className="w-full px-3 py-2 text-sm rounded-xl border border-[#C8C0B5] bg-[#FAFAF7] outline-none focus:ring-2 focus:ring-[#1E3A2B]"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-[#1A241F] uppercase mb-1">
                  Plant Photograph
                </label>
                <input
                  type="file"
                  accept="image/*"
                  capture="environment"
                  ref={fileInputRef}
                  onChange={handleImageChange}
                  className="hidden"
                />

                {!imagePreview ? (
                  <button
                    type="button"
                    onClick={() => fileInputRef.current?.click()}
                    className="w-full border-2 border-dashed border-[#C8C0B5] rounded-xl p-6 text-center hover:bg-[#FAFAF7] transition-all touch-target"
                  >
                    <Camera className="w-6 h-6 text-[#1E3A2B] mx-auto mb-1" />
                    <span className="text-xs font-bold text-[#1E3A2B] block">Take or Upload Foliar Photo</span>
                  </button>
                ) : (
                  <div className="relative rounded-xl overflow-hidden border border-[#E5E0D8] max-h-48 flex items-center justify-center bg-black">
                    <img src={imagePreview} alt="Preview" className="max-h-48 object-contain" />
                  </div>
                )}
              </div>

              <div className="flex justify-end gap-2 pt-2 border-t border-[#E5E0D8]">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => setShowAddModal(false)}
                >
                  Cancel
                </Button>
                <Button type="submit" variant="primary" isLoading={isSubmitting}>
                  Save Observation
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Observation Timeline Cards */}
      <div className="space-y-4">
        {isLoading ? (
          <div className="space-y-3 animate-pulse">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-32 bg-white rounded-2xl border border-[#E5E0D8]" />
            ))}
          </div>
        ) : observations.length === 0 ? (
          <div className="p-8 bg-white rounded-2xl border border-[#E5E0D8] text-center space-y-3">
            <Activity className="w-10 h-10 text-[#C8C0B5] mx-auto" />
            <p className="text-sm font-semibold text-[#1A241F]">No CropPulse observations recorded yet.</p>
            <p className="text-xs text-[#556059]">Add your first plant health record to track changes over time.</p>
          </div>
        ) : (
          observations.map((obs, index) => (
            <div
              key={obs.id}
              className="bg-white rounded-2xl border border-[#E5E0D8] p-5 shadow-xs space-y-3"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-xs font-bold text-[#1E3A2B]">
                  <Calendar className="w-4 h-4 text-[#1E3A2B]" />
                  <span>{new Date(obs.created_at).toLocaleDateString()}</span>
                  <span className="text-[#78857E] font-normal">
                    {new Date(obs.created_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                  </span>
                </div>
                <span className="text-[11px] font-semibold px-2 py-0.5 bg-[#E8F0EC] text-[#1E3A2B] rounded-full">
                  Record #{observations.length - index}
                </span>
              </div>

              {obs.notes && (
                <p className="text-sm text-[#1A241F] font-medium leading-relaxed">
                  {obs.notes}
                </p>
              )}

              {obs.media.length > 0 && (
                <div className="flex gap-2 overflow-x-auto py-1">
                  {obs.media.map((m) => (
                    <div
                      key={m.id}
                      className="w-28 h-28 rounded-xl overflow-hidden border border-[#E5E0D8] bg-[#FAFAF7] shrink-0"
                    >
                      <img
                        src={api.getMediaFileUrl(obs.id, m.id)}
                        alt="Crop foliar"
                        className="w-full h-full object-cover"
                        loading="lazy"
                      />
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
}
