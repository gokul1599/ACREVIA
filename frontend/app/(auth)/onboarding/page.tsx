"use client";

import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth/context";
import { useTranslation } from "@/lib/localization/context";
import { api } from "@/lib/api/client";
import { Button } from "@/components/ui/Button";
import { Locale } from "@/messages";
import {
  Sprout,
  CheckCircle2,
  MapPin,
  Layers,
  ArrowRight,
  ArrowLeft,
  AlertCircle,
} from "lucide-react";

export default function OnboardingPage() {
  const router = useRouter();
  const { user, isAuthenticated, isLoading: authLoading } = useAuth();
  const { t, locale, setLocale } = useTranslation();

  const [step, setStep] = useState<number>(1);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Form State
  const [farmName, setFarmName] = useState("");
  const [district, setDistrict] = useState("Warangal");
  const [mandal, setMandal] = useState("Geesugonda");
  const [village, setVillage] = useState("Dharmaram");
  const [acreage, setAcreage] = useState<number>(3.0);

  const [plotName, setPlotName] = useState("Plot 1 (North Field)");
  const [soilType, setSoilType] = useState<"BLACK_COTTON" | "RED_CHALKA" | "ALLUVIAL" | "LOAMY">("BLACK_COTTON");
  const [irrigation, setIrrigation] = useState<"BOREWELL" | "CANAL" | "RAINFED" | "DRIP" | "WELL">("BOREWELL");

  const [cropId, setCropId] = useState<"cotton" | "rice" | "chilli">("cotton");
  const [seasonType, setSeasonType] = useState<"KHARIF" | "RABI" | "SUMMER">("KHARIF");
  const [sowingDate, setSowingDate] = useState<string>(
    new Date().toISOString().split("T")[0]
  );

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push("/login");
    }
    if (user?.full_name && !farmName) {
      setFarmName(`${user.full_name}'s Farm`);
    }
  }, [authLoading, isAuthenticated, user, router, farmName]);

  const handleFinish = async () => {
    setError(null);
    setIsSubmitting(true);
    try {
      // 1. Create Farm
      const farm = await api.createFarm({
        name: farmName.trim() || "My Farm",
        district: district.trim(),
        mandal: mandal.trim(),
        village: village.trim(),
        total_acreage: acreage,
      });

      // 2. Create Plot
      const plot = await api.createPlot(farm.id, {
        name: plotName.trim() || "Plot 1",
        soil_type: soilType,
        irrigation_source: irrigation,
        acreage: acreage,
      });

      // 3. Create Crop Season
      await api.createCropSeason(plot.id, {
        crop_id: cropId,
        season_type: seasonType,
        sowing_date: sowingDate,
        current_stage: "VEGETATIVE",
      });

      // Redirect to Dashboard
      router.push("/dashboard");
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to initialize farm and crop.";
      setError(msg);
    } finally {
      setIsSubmitting(false);
    }
  };

  const telanganaDistricts = [
    "Warangal",
    "Karimnagar",
    "Khammam",
    "Nalgonda",
    "Adilabad",
    "Nizamabad",
    "Mahabubnagar",
    "Medak",
    "Suryapet",
    "Siddipet",
  ];

  return (
    <div className="min-h-[calc(100vh-4rem)] max-w-2xl mx-auto p-4 py-8">
      <div className="bg-white rounded-2xl shadow-card border border-[#E5E0D8] p-6 sm:p-8">
        {/* Header & Step Tracker */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <div className="w-10 h-10 rounded-xl bg-[#1E3A2B] text-white flex items-center justify-center shadow-xs">
                <Sprout className="w-6 h-6 text-[#86EFAC]" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-[#1E3A2B]">{t.onboarding.title}</h1>
                <p className="text-xs text-[#556059]">{t.onboarding.subtitle}</p>
              </div>
            </div>
            <span className="text-xs font-bold px-2.5 py-1 bg-[#E8F0EC] text-[#1E3A2B] rounded-full">
              Step {step} of 4
            </span>
          </div>

          {/* Progress Bar */}
          <div className="w-full bg-[#E5E0D8] h-2 rounded-full overflow-hidden">
            <div
              className="bg-[#1E3A2B] h-full transition-all duration-300"
              style={{ width: `${(step / 4) * 100}%` }}
            />
          </div>
        </div>

        {error && (
          <div className="mb-6 p-3 bg-[#FFE3E3] border border-[#FFA8A8] text-[#C92A2A] rounded-xl text-sm flex items-start gap-2">
            <AlertCircle className="w-5 h-5 shrink-0 mt-0.5" />
            <span>{error}</span>
          </div>
        )}

        {/* STEP 1: LANGUAGE */}
        {step === 1 && (
          <div className="space-y-4">
            <h2 className="text-lg font-bold text-[#1E3A2B] mb-2">{t.onboarding.step1}</h2>
            <p className="text-sm text-[#556059] mb-4">
              Select your primary language for advice, diagnostics, and voice interactions:
            </p>

            <div className="grid grid-cols-1 gap-3">
              {[
                { code: "te", title: "తెలుగు (Telugu - Telangana First)", desc: "పంట సూచనలు మరియు విజ్ఞానం తెలుగులో లభిస్తాయి." },
                { code: "en", title: "English", desc: "Scientific names, university POPs, and official advisories in English." },
                { code: "hi", title: "हिंदी (Hindi)", desc: "कृषि परामर्श और रोग निदान हिंदी में।" },
              ].map((lang) => (
                <button
                  key={lang.code}
                  type="button"
                  onClick={() => setLocale(lang.code as Locale)}
                  className={`p-4 rounded-xl border text-left transition-all flex items-center justify-between touch-target ${
                    locale === lang.code
                      ? "border-[#1E3A2B] bg-[#E8F0EC] ring-2 ring-[#1E3A2B]"
                      : "border-[#C8C0B5] hover:bg-[#FAFAF7]"
                  }`}
                >
                  <div>
                    <span className="font-bold text-base text-[#1E3A2B] block">{lang.title}</span>
                    <span className="text-xs text-[#556059] block mt-0.5">{lang.desc}</span>
                  </div>
                  {locale === lang.code && <CheckCircle2 className="w-6 h-6 text-[#1E3A2B] shrink-0" />}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* STEP 2: PROFILE CONFIRMATION */}
        {step === 2 && (
          <div className="space-y-4">
            <h2 className="text-lg font-bold text-[#1E3A2B] mb-2">{t.onboarding.step2}</h2>
            <div className="p-4 bg-[#FAFAF7] rounded-xl border border-[#E5E0D8] space-y-2">
              <div>
                <span className="text-xs text-[#78857E] uppercase block font-semibold">{t.auth.fullName}</span>
                <span className="text-base font-bold text-[#1A241F]">{user?.full_name || "N/A"}</span>
              </div>
              <div>
                <span className="text-xs text-[#78857E] uppercase block font-semibold">{t.auth.phone}</span>
                <span className="text-base font-bold text-[#1A241F]">{user?.phone || "N/A"}</span>
              </div>
              <div>
                <span className="text-xs text-[#78857E] uppercase block font-semibold">User Role</span>
                <span className="text-xs font-semibold px-2 py-0.5 bg-[#E8F0EC] text-[#1E3A2B] rounded-md inline-block">
                  Verified Farmer
                </span>
              </div>
            </div>
            <p className="text-xs text-[#556059]">
              ACREVIA protects your farm data. Your coordinates and field observations are never exposed to public registries.
            </p>
          </div>
        )}

        {/* STEP 3: FARM SETUP */}
        {step === 3 && (
          <div className="space-y-4">
            <h2 className="text-lg font-bold text-[#1E3A2B] mb-2">{t.onboarding.step3}</h2>

            <div>
              <label className="block text-xs font-semibold text-[#1A241F] uppercase mb-1">
                {t.onboarding.farmName}
              </label>
              <input
                type="text"
                value={farmName}
                onChange={(e) => setFarmName(e.target.value)}
                placeholder={t.onboarding.farmNamePlaceholder}
                className="w-full px-4 py-2.5 rounded-xl border border-[#C8C0B5] bg-[#FAFAF7] text-base focus:ring-2 focus:ring-[#1E3A2B] outline-none"
              />
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-semibold text-[#1A241F] uppercase mb-1">
                  {t.onboarding.district}
                </label>
                <select
                  value={district}
                  onChange={(e) => setDistrict(e.target.value)}
                  className="w-full px-4 py-2.5 rounded-xl border border-[#C8C0B5] bg-[#FAFAF7] text-base focus:ring-2 focus:ring-[#1E3A2B] outline-none"
                >
                  {telanganaDistricts.map((d) => (
                    <option key={d} value={d}>
                      {d}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-[#1A241F] uppercase mb-1">
                  {t.onboarding.mandal}
                </label>
                <input
                  type="text"
                  value={mandal}
                  onChange={(e) => setMandal(e.target.value)}
                  className="w-full px-4 py-2.5 rounded-xl border border-[#C8C0B5] bg-[#FAFAF7] text-base focus:ring-2 focus:ring-[#1E3A2B] outline-none"
                />
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-semibold text-[#1A241F] uppercase mb-1">
                  {t.onboarding.village}
                </label>
                <input
                  type="text"
                  value={village}
                  onChange={(e) => setVillage(e.target.value)}
                  className="w-full px-4 py-2.5 rounded-xl border border-[#C8C0B5] bg-[#FAFAF7] text-base focus:ring-2 focus:ring-[#1E3A2B] outline-none"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-[#1A241F] uppercase mb-1">
                  {t.onboarding.acreage}
                </label>
                <input
                  type="number"
                  step="0.5"
                  min="0.1"
                  value={acreage}
                  onChange={(e) => setAcreage(parseFloat(e.target.value) || 1.0)}
                  className="w-full px-4 py-2.5 rounded-xl border border-[#C8C0B5] bg-[#FAFAF7] text-base focus:ring-2 focus:ring-[#1E3A2B] outline-none"
                />
              </div>
            </div>
          </div>
        )}

        {/* STEP 4: FIRST CROP SEASON */}
        {step === 4 && (
          <div className="space-y-4">
            <h2 className="text-lg font-bold text-[#1E3A2B] mb-2">{t.onboarding.step4}</h2>

            <div>
              <label className="block text-xs font-semibold text-[#1A241F] uppercase mb-1">
                {t.onboarding.selectCrop}
              </label>
              <div className="grid grid-cols-3 gap-2">
                {[
                  { id: "cotton", label: "Cotton", telugu: "ప్రత్తి" },
                  { id: "rice", label: "Rice / Paddy", telugu: "వరి" },
                  { id: "chilli", label: "Chilli", telugu: "మిరప" },
                ].map((c) => (
                  <button
                    key={c.id}
                    type="button"
                    onClick={() => setCropId(c.id as "cotton" | "rice" | "chilli")}
                    className={`p-3 rounded-xl border text-center transition-all touch-target ${
                      cropId === c.id
                        ? "border-[#1E3A2B] bg-[#E8F0EC] ring-2 ring-[#1E3A2B]"
                        : "border-[#C8C0B5] hover:bg-[#FAFAF7]"
                    }`}
                  >
                    <span className="font-bold text-sm text-[#1E3A2B] block">{c.label}</span>
                    <span className="text-xs text-[#556059] block">{c.telugu}</span>
                  </button>
                ))}
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-semibold text-[#1A241F] uppercase mb-1">
                  {t.onboarding.soilType}
                </label>
                <select
                  value={soilType}
                  onChange={(e) => setSoilType(e.target.value as "BLACK_COTTON")}
                  className="w-full px-4 py-2.5 rounded-xl border border-[#C8C0B5] bg-[#FAFAF7] text-base focus:ring-2 focus:ring-[#1E3A2B] outline-none"
                >
                  <option value="BLACK_COTTON">Black Cotton Soil (నల్లరేగడి)</option>
                  <option value="RED_CHALKA">Red Chalka (ఎర్ర నేలలు)</option>
                  <option value="ALLUVIAL">Alluvial Soil (ఒండ్రు నేలలు)</option>
                  <option value="LOAMY">Loamy Soil (వరి గరప)</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-[#1A241F] uppercase mb-1">
                  {t.onboarding.irrigation}
                </label>
                <select
                  value={irrigation}
                  onChange={(e) => setIrrigation(e.target.value as "BOREWELL")}
                  className="w-full px-4 py-2.5 rounded-xl border border-[#C8C0B5] bg-[#FAFAF7] text-base focus:ring-2 focus:ring-[#1E3A2B] outline-none"
                >
                  <option value="BOREWELL">Borewell (బోరు బావి)</option>
                  <option value="CANAL">Canal Irrigation (కాల్వ నీరు)</option>
                  <option value="RAINFED">Rainfed (వర్షాధారం)</option>
                  <option value="DRIP">Drip Irrigation (బిందు సేద్యం)</option>
                </select>
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-semibold text-[#1A241F] uppercase mb-1">
                  {t.onboarding.seasonType}
                </label>
                <select
                  value={seasonType}
                  onChange={(e) => setSeasonType(e.target.value as "KHARIF")}
                  className="w-full px-4 py-2.5 rounded-xl border border-[#C8C0B5] bg-[#FAFAF7] text-base focus:ring-2 focus:ring-[#1E3A2B] outline-none"
                >
                  <option value="KHARIF">Kharif Season (వానాకాలం)</option>
                  <option value="RABI">Rabi Season (యాసంగి)</option>
                  <option value="SUMMER">Summer Season (ఎండకాలం)</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-[#1A241F] uppercase mb-1">
                  {t.onboarding.sowingDate}
                </label>
                <input
                  type="date"
                  value={sowingDate}
                  onChange={(e) => setSowingDate(e.target.value)}
                  className="w-full px-4 py-2.5 rounded-xl border border-[#C8C0B5] bg-[#FAFAF7] text-base focus:ring-2 focus:ring-[#1E3A2B] outline-none"
                />
              </div>
            </div>
          </div>
        )}

        {/* Navigation Buttons */}
        <div className="mt-8 pt-6 border-t border-[#E5E0D8] flex items-center justify-between gap-3">
          {step > 1 ? (
            <Button
              type="button"
              variant="outline"
              onClick={() => setStep(step - 1)}
              icon={<ArrowLeft className="w-4 h-4" />}
            >
              {t.common.back}
            </Button>
          ) : (
            <div />
          )}

          {step < 4 ? (
            <Button
              type="button"
              variant="primary"
              onClick={() => setStep(step + 1)}
              icon={<ArrowRight className="w-4 h-4" />}
            >
              Next
            </Button>
          ) : (
            <Button
              type="button"
              variant="primary"
              onClick={handleFinish}
              isLoading={isSubmitting}
              icon={<CheckCircle2 className="w-5 h-5 text-[#86EFAC]" />}
            >
              {t.onboarding.completeSetup}
            </Button>
          )}
        </div>
      </div>
    </div>
  );
}
