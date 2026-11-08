"use client";

import React, { useEffect } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth/context";
import { useTranslation } from "@/lib/localization/context";
import { Button } from "@/components/ui/Button";
import {
  Sprout,
  Camera,
  BotMessageSquare,
  ShieldCheck,
  Globe,
  ArrowRight,
  Activity,
} from "lucide-react";

export default function HomePage() {
  const router = useRouter();
  const { isAuthenticated, isLoading } = useAuth();
  const { t } = useTranslation();

  useEffect(() => {
    if (!isLoading && isAuthenticated) {
      router.push("/dashboard");
    }
  }, [isAuthenticated, isLoading, router]);

  return (
    <div className="max-w-4xl mx-auto px-4 py-8 sm:py-16 space-y-12">
      {/* Hero Section */}
      <div className="text-center space-y-5 max-w-2xl mx-auto">
        <div className="inline-flex items-center gap-2 px-3 py-1 bg-[#E8F0EC] border border-[#C2D9CD] rounded-full text-xs font-semibold text-[#1E3A2B]">
          <Sprout className="w-4 h-4 text-[#1E3A2B]" />
          <span>Telangana Agricultural Intelligence Platform</span>
        </div>

        <h1 className="text-3xl sm:text-5xl font-extrabold text-[#1E3A2B] tracking-tight leading-tight">
          Clinical Agronomy & AI Pathology for Smallholder Farmers
        </h1>

        <p className="text-base sm:text-lg text-[#556059] leading-relaxed">
          Ground-truth foliar disease diagnosis, verifiable university research citations (PJTSAU, ICAR), and mobile-first agrometeorological risk modeling for <strong>Cotton</strong>, <strong>Rice</strong>, and <strong>Chilli</strong>.
        </p>

        <div className="flex flex-wrap items-center justify-center gap-3 pt-2">
          <Link href="/register">
            <Button size="lg" variant="primary" icon={<ArrowRight className="w-5 h-5 text-[#86EFAC]" />}>
              {t.auth.register}
            </Button>
          </Link>
          <Link href="/login">
            <Button size="lg" variant="outline">
              {t.auth.signIn}
            </Button>
          </Link>
        </div>
      </div>

      {/* 3 Core Pillar Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-4">
        <div className="p-6 bg-white rounded-2xl border border-[#E5E0D8] shadow-card space-y-3">
          <div className="w-12 h-12 rounded-xl bg-[#E8F0EC] text-[#1E3A2B] flex items-center justify-center">
            <Camera className="w-6 h-6" />
          </div>
          <h2 className="font-bold text-lg text-[#1E3A2B]">CropVision Diagnosis</h2>
          <p className="text-xs text-[#556059] leading-relaxed">
            Instant foliar pathology detection using calibrated PyTorch computer vision. Provides confidence gauges and differential diagnoses.
          </p>
        </div>

        <div className="p-6 bg-white rounded-2xl border border-[#E5E0D8] shadow-card space-y-3">
          <div className="w-12 h-12 rounded-xl bg-[#E8F0EC] text-[#1E3A2B] flex items-center justify-center">
            <BotMessageSquare className="w-6 h-6" />
          </div>
          <h2 className="font-bold text-lg text-[#1E3A2B]">KrishiBrain RAG</h2>
          <p className="text-xs text-[#556059] leading-relaxed">
            Evidence-grounded agronomic assistant citing official packages of practices down to university physical page numbers. Zero hallucination tolerance.
          </p>
        </div>

        <div className="p-6 bg-white rounded-2xl border border-[#E5E0D8] shadow-card space-y-3">
          <div className="w-12 h-12 rounded-xl bg-[#E8F0EC] text-[#1E3A2B] flex items-center justify-center">
            <Globe className="w-6 h-6" />
          </div>
          <h2 className="font-bold text-lg text-[#1E3A2B]">Native Multilingual</h2>
          <p className="text-xs text-[#556059] leading-relaxed">
            Built for rural Telangana with full interface localization and voice input in <strong>Telugu</strong>, <strong>Hindi</strong>, and <strong>English</strong>.
          </p>
        </div>
      </div>

      {/* Trust & Regulatory Footer */}
      <div className="p-6 bg-[#E8F0EC] rounded-2xl border border-[#C2D9CD] flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-[#1E3A2B]">
        <div className="flex items-center gap-2">
          <ShieldCheck className="w-5 h-5 text-[#15803D] shrink-0" />
          <span>Compliant with Central Insecticides Board & Registration Committee (CIBRC) Label Guidelines.</span>
        </div>
        <span className="font-semibold text-[11px] text-[#556059]">
          ACREVIA v1.0.0 • Telangana-First
        </span>
      </div>
    </div>
  );
}
